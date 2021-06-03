import os
import time
import lxml
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyzabbix import ZabbixAPI
from dotenv import load_dotenv


# Credentials
load_dotenv('.env_unifi')

# UNFI controller credentials
UNIFI_URL_LOGIN = os.getenv('UNIFI_URL_LOGIN')
UNIFI_URL_AP = os.getenv('UNIFI_URL_AP')
UNIFI_USER_NAME = os.getenv('UNIFI_USER_NAME')
UNIFI_PASSWORD = os.getenv('UNIFI_PASSWORD')

# Zabbix server credentials
ZABBIX_URL = os.getenv('ZABBIX_URL')
ZABBIX_USER_NAME = os.getenv('ZABBIX_USER_NAME')
ZABBIX_PASSWORD = os.getenv('ZABBIX_PASSWORD')
zabbix_api = ZabbixAPI(ZABBIX_URL)
zabbix_api.login(ZABBIX_USER_NAME, ZABBIX_PASSWORD)

TEMPLATE_ID_1 = "10587"  # Template UBQT UNIFI SNMP V1 HN
TEMPLATE_ID_2 = "10186"  # Template Module ICMP Ping
GROUP_ID = "58"     # Host group UNIFI

def get_html():
    """
    Getting html from UNIFI_URL_AP for parcing AP
    :return: html code
    """
    driverOptions = webdriver.ChromeOptions()
    driverOptions.headless = False  #True
    driverOptions.binary = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe" #"/usr/bin/google-chrome-stable"
    driverOptions.binary_location = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe" #"/usr/bin/google-chrome-stable"
    driverOptions.add_argument("--no-sandbox")
    driverOptions.add_argument("--disable-dev-shm-usage")
    # driverOptions.add_argument("--disable-setuid-sandbox")
    # driverOptions.add_argument("start-maximized")
    driverOptions.add_argument("--disable-gpu")   # applicable to windows os only
    driverOptions.add_argument("--disable-extensions")
    driverOptions.add_argument("disable-infobars")
    driverOptions.add_argument('--ignore-certificate-errors')

    with webdriver.Chrome(options=driverOptions) as driver:
        driver.get(UNIFI_URL_LOGIN)
    
        time.sleep(1)

        username_input = driver.find_element_by_name("username")
        username_input.clear()
        username_input.send_keys(UNIFI_USER_NAME)

        password_input = driver.find_element_by_name("password")
        password_input.clear()
        password_input.send_keys(UNIFI_PASSWORD)
        password_input.send_keys(Keys.ENTER)

        time.sleep(5)
        driver.get(UNIFI_URL_AP)
        time.sleep(7)
        html = driver.page_source

    return html

def create_update_zabbix(ap_mac, ap_name, ap_ip):
    """
    Create new items or update it if changed ip or name of APs in UNIFI controller
    :param ap_mac: AP MAC address 
    :param ap_name: AP name
    :param ap_ip: AP IP address
    :return: nothing
    """
    hosts = zabbix_api.host.get(filter={"host": ap_mac}, selectInterfaces=["interfaceid"])

    if hosts:
        host_name = hosts[0]["name"]  # Visible name
        host_id = hosts[0]["hostid"]
        host_interface = zabbix_api.do_request(method="hostinterface.get", params={"hostids": host_id}).get("result")
        host_ip = host_interface[0]['ip']
        host_interfaceid = host_interface[0]['interfaceid']

        if host_name != ap_name:
            zabbix_api.do_request(method="host.update", params={
                "hostid": host_id,
                "name": ap_name  # Visible name
            })
            print("Update hostname " + ap_name)
        if host_ip != ap_ip:
            zabbix_api.do_request(method="hostinterface.update", params={
                "interfaceid": host_interfaceid,
                "ip": ap_ip
            })
            print("Update IP " + ap_name)
        # Append templates
        zabbix_api.do_request(method="host.update", params={
            "hostid": host_id,
            "templates": [{"templateid": TEMPLATE_ID_1},
                          {"templateid": TEMPLATE_ID_2}],
        })
    else:
        zabbix_api.do_request(method="host.create", params={
            "host": ap_mac,   # zabbix Host name
            "name": ap_name,  # zabbix Visible name
            "groups": [{"groupid": GROUP_ID}],
            "interfaces": [{
                "type": 2,
                "main": 1,
                "useip": 1,
                "ip": ap_ip,
                "dns": "",
                "port": "161",
                "details": {"community": "{$SNMP_COMMUNITY}", "version": 2}
            }],
            "templates": [{"templateid": TEMPLATE_ID_1},
                          {"templateid": TEMPLATE_ID_2}],
            "description": "Created by script"
        })
        print("Create new host " + ap_name)

soup = BeautifulSoup(get_html(), "lxml")
aps = soup.find_all("tr", class_="clickable")

for ap in aps: # [:1]
    # getting AP params
    ap_mac = ap.attrs.get("data-id").replace(":","").upper()
    ap_name = ap.find("td", class_="deviceName").text
    ap_ip = ap.find("td", class_="deviceIp").text
    
    # create or update zabbix items
    create_update_zabbix(ap_mac, ap_name, ap_ip)
