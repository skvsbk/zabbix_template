#!/usr/bin/env python3

'''

get_cams.py <IP_address> <discovery|element|status>

'''

import sys
import time
import json
import lxml
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_html(url):
    driverOptions = webdriver.ChromeOptions()
    driverOptions.headless = True
    driverOptions.binary = "/usr/bin/google-chrome-stable"
    driverOptions.binary_location = "/usr/bin/google-chrome-stable"
    driverOptions.add_argument("--no-sandbox")
    driverOptions.add_argument("--disable-setuid-sandbox")
    driverOptions.add_argument("--disable-dev-shm-usage")
    driverOptions.add_argument("start-maximized")
    driverOptions.add_argument("--disable-extensions")
    driverOptions.add_argument("disable-infobars")
    driverOptions.add_argument("disable-popup-blocking")
    driverOptions.add_argument("--disable-extensions")
    with webdriver.Chrome(executable_path="/opt/WebDriver/bin/chromedriver", options=driverOptions) as driver:
        driver.get(url_login)

        time.sleep(4)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()

        time.sleep(2)
        username_input = driver.find_element_by_id("txtUserName")
        username_input.clear()
        username_input.send_keys(username)

        time.sleep(2)
        password_input = driver.find_element_by_id("txtPassword")
        password_input.clear()
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
        driver.get(url)
        time.sleep(5)

        return driver.page_source

def get_items(html, tag, class_):
    soup = BeautifulSoup(html, "lxml")
    return soup.find_all(tag, class_=class_)

try:
    ip_address = sys.argv[1]
    action = sys.argv[2]
except:
    print("Empty arguments")
    sys.exit()


actionList = ["discovery", "element", "status"]
if action not in actionList:
    print("Arguments error")
    sys.exit()

username = "admin"
password = "password"
url_login = 'http://' + ip_address + '/#login'
url_cams = 'http://' + ip_address + '/#config/channel/list'
url_stat = 'http://' + ip_address + '/#config/system/channel/status'
url_bandwith = 'http://' + ip_address + '/#config/net/status'
url_sysinfo = 'http://' + ip_address + '/#config/system/information'

elements_list = []
elements_dict = dict()
cam_count = 1

if action == "discovery":
    html = get_html(url_cams)
    items = get_items(html, "tr", "grid-row")
    for item in items:
        items_dict = dict()
        try:
            cam_number = item.find_all("td", class_="grid-general-text")[1].text
        except:
            cam_number = None
        try:
            cam_name = item.find_all("td", class_="grid-general-text")[2].text
        except:
            cam_name = None
        try:
            cam_ip = item.find_all("td", class_="grid-general-text")[3].text
        except:
            cam_ip = None
        try:
            cam_model = item.find_all("td", class_="grid-general-text")[7].text
        except:
            cam_model = None
        items_dict["{#CAMNUMBER}"] = cam_number
        items_dict["{#CAMNAME}"] = cam_name.replace("\xa0", " ").strip()
        items_dict["{#CAMIP}"] = cam_ip
        items_dict["{#CAMMODEL}"] = cam_model
        elements_list.append(items_dict)

    print('{"data":' + json.dumps(elements_list, indent=4, ensure_ascii=False) + "}")

elif action == "element":
    html = get_html(url_stat)
    items = get_items(html, "tr", "grid-row")
    for item in items:
        try:
            cam_status = item.find_all("td")[3].text
        except:
            cam_status = ""
        elements_dict[cam_count] = 1 if cam_status.replace("\xa0", " ").strip() == "Online" else 0
        cam_count +=1

    print(json.dumps(elements_dict, indent=4, ensure_ascii=False))

else:
    html = get_html(url_bandwith)
    items = get_items(html, "td", "grid-general-text")
    for n in range(0, len(items)-1, 2):
        key = items[n].get('title').replace("\xa0", " ").strip()
        val = items[n+1].get('title').replace("\xa0", " ").strip()
        if key == 'Total Bandwidth':
            elements_dict['BWINTOTAL'] = val.replace("Mb", " ").strip()
        if key == 'Real-time Remain Bandwidth' or key == 'Remain Bandwidth':
            elements_dict['BWINREM'] = val.replace("Mb", " ").strip()
        if key == 'Total Send Bandwidth':
            elements_dict['BWOUTTOTAL'] = val.replace("Mb", " ").strip()
        if key == 'Real-time Remain Send Bandwidth' or key == 'Remain Send Bandwidth':
            elements_dict['BWOUTREM'] = val.replace("Mb", " ").strip()

    print(json.dumps(elements_dict, indent=4, ensure_ascii=False))
