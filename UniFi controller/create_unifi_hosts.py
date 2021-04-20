#!/usr/bin/env python3

import time
import lxml
import sys
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pyzabbix import ZabbixAPI


# UNFI controller credentials
url_login = "https://unifi.acticomp.local:8443"
url_ap = "https://unifi.acticomp.local:8443/manage/site/default/devices/1/100"
username = "admin"
password = "1q2w3e4r5t"

# Zabbix server credentials
url_zabbix = "http://zabbix.acticomp.local"
zapi = ZabbixAPI(url_zabbix)
zapi.login("skv", "Qwerty123")
template_id = "10587"
group_id = "58"

def get_html(url_login, url_ap):
    driverOptions = webdriver.ChromeOptions()
    driverOptions.headless = True
    driverOptions.binary = "/usr/bin/google-chrome-stable"
    driverOptions.binary_location = "/usr/bin/google-chrome-stable"
    driverOptions.add_argument("--no-sandbox")
    driverOptions.add_argument("--disable-dev-shm-usage")
    driverOptions.add_argument("--disable-setuid-sandbox")
    driverOptions.add_argument("start-maximized")
    #driverOptions.add_argument("--disable-gpu")   # applicable to windows os only
    driverOptions.add_argument("--disable-extensions")
    driverOptions.add_argument("disable-infobars")
    driverOptions.add_argument('--ignore-certificate-errors')

    with webdriver.Chrome(options=driverOptions) as driver: 
        driver.get(url_login)
        time.sleep(1)

        username_input = driver.find_element_by_name("username")
        username_input.clear()
        username_input.send_keys(username)

        password_input = driver.find_element_by_name("password")
        password_input.clear()
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)

        time.sleep(5)
        driver.get(url_ap)
        time.sleep(7)
        html = driver.page_source

    return html

def create_update_zabbix(ap_mac, ap_name, ap_ip):
    hosts = zapi.host.get(filter={"host": ap_mac}, selectInterfaces=["interfaceid"])

    if hosts:
        host_name = hosts[0]["name"]  # Visible name
        host_id = hosts[0]["hostid"]
        host_interface = zapi.do_request(method="hostinterface.get", params={"hostids": host_id}).get("result")
        host_ip = host_interface[0]['ip']
        host_interfaceid = host_interface[0]['interfaceid']

        if host_name != ap_name:
            zapi.do_request(method="host.update", params={
                "hostid": host_id,
                "name": ap_name  # Visible name
            })
            print("Update hostname " + ap_name)

        if host_ip != ap_ip:
            zapi.do_request(method="hostinterface.update", params={
                "interfaceid": host_interfaceid,
                "ip": ap_ip
            })
            print("Update IP " + ap_name)
    else:
        zapi.do_request(method="host.create", params={
            "host": ap_mac,   # Host name
            "name": ap_name,  # Visible name
            "groups": [{"groupid": group_id}],
            "interfaces": [{
                "type": 2,
                "main": 1,
                "useip": 1,
                "ip": ap_ip,
                "dns": "",
                "port": "161",
                "details": {"community": "{$SNMP_COMMUNITY}", "version": 2}
            }],
            "templates": [{"templateid": template_id}],
            "description": "Created by script"
        })
        print("Create new host " + ap_name)

soup = BeautifulSoup(get_html(url_login, url_ap), "lxml")
aps = soup.find_all("tr", class_="clickable")

for ap in aps:
    ap_mac = ap.attrs.get("data-id").replace(":","").upper()
    ap_name = ap.find("td", class_="deviceName").text
    ap_ip = ap.find("td", class_="deviceIp").text

    create_update_zabbix(ap_mac, ap_name, ap_ip)

