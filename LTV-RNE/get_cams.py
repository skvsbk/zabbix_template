#!/usr/bin/env python3

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


ip_address = sys.argv[1]
action = sys.argv[2]

actionList = ["discovery", "element"]
if action not in actionList:
    print("Arguments error")
    sys.exit()

username = "admin"
password = "Admin272218"
url_login = 'http://' + ip_address + '/#login'
url_cams = 'http://' + ip_address + '/#config/channel/list'
url_stat = 'http://' + ip_address + '/#config/system/channel/status'

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

try:
    driver = webdriver.Chrome(executable_path="/opt/WebDriver/bin/chromedriver", options=driverOptions)
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

    if action == "discovery":
        driver.get(url_cams)
        time.sleep(4)
        html = driver.page_source
    else:
        driver.get(url_stat)
        time.sleep(4)
        html = driver.page_source
finally:
    driver.close()
    driver.quit()

cams_list = []
elements_dict = dict()
cam_count = 1

soup = BeautifulSoup(html, "lxml")
cams = soup.find_all("tr", class_="grid-row")

if action == "discovery":
    for cam in cams:
        cam_dict = dict()
        try:
            cam_number = cam.find_all("td", class_="grid-general-text")[1].text
        except:
            cam_number = None
        try:
            cam_name = cam.find_all("td", class_="grid-general-text")[2].text
        except:
            cam_name = None
        try:
            cam_ip = cam.find_all("td", class_="grid-general-text")[3].text
        except:
            cam_ip = None
        try:
            cam_model = cam.find_all("td", class_="grid-general-text")[7].text
        except:
            cam_model = None
        cam_dict["{#CAMNUMBER}"] = cam_number
        cam_dict["{#CAMNAME}"] = cam_name.replace("\xa0", " ").strip()
        cam_dict["{#CAMIP}"] = cam_ip
        cam_dict["{#CAMMODEL}"] = cam_model
        cams_list.append(cam_dict)
else:
    for cam in cams:
        try:
            cam_status = cam.find_all("td")[3].text
        except:
            cam_status = ""
        elements_dict[cam_count] = 1 if cam_status.replace("\xa0", " ") == "Online" else 0
        cam_count +=1

result = json.dumps(cams_list, indent=4, ensure_ascii=False)

print('{"data":' + result + "}") if action == "discovery" else print(json.dumps(elements_dict, indent=4, ensure_ascii=False))
