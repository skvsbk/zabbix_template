#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import lxml
import urllib3
import json
import sys


urllib3.disable_warnings()

try:
    ip_address = sys.argv[1]
    action = sys.argv[2]
except:
    print("Empty arguments")
    sys.exit()

actionList = ["discovery", "element"]
if action not in actionList:
    print("Arguments error")
    sys.exit()

url =f"https://{ip_address}/PRESENTATION/ADVANCED/INFO_PRTINFO/TOP"

request = requests.get(url, verify=False)
soup = BeautifulSoup(request.content, "lxml")
inks = soup.find_all("div", class_="tank")

json_string_discovery = '{"data":['
json_string_element = dict()

for ink in inks:
    cartridge_name = ink.find("img", {"class": "color"})["src"]
    cartridge_level = ink.find("img", {"class" : "color"})["height"]

    if cartridge_name.find("Ink_K") != -1:
        cartridge_name = "Black"
    if cartridge_name.find("Ink_M") != -1:
        cartridge_name = "Magenta"
    if cartridge_name.find("Ink_C") != -1:
        cartridge_name = "Cyan"
    if cartridge_name.find("Ink_Y") != -1:
        cartridge_name = "Yellow"
    if cartridge_name.find("Ink_Waste") != -1:
        cartridge_name = "Waste"
        if int(cartridge_level) <= 2 or cartridge_level == None:
            cartridge_level = 50

    json_string_element[cartridge_name] = int(cartridge_level)*2
    if cartridge_name != "Waste" and action == "discovery":
        json_string_discovery += '{"{#COLOR}":"' + cartridge_name + '"},'

if len(inks) == 1 or len(inks) == 4:
    json_string_element["Waste"] = 100

print(json_string_discovery[:-1] + "]}") if action == "discovery" else print(json.dumps(json_string_element, indent=4))

