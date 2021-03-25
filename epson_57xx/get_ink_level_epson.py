#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import lxml
import urllib3
import json
import sys


urllib3.disable_warnings()

ip_address  =  sys.argv[1]
action = sys.argv[2]  #1 - discovery, 2 - element

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
    json_string_element[cartridge_name] = int(cartridge_level)*2
    if cartridge_name != "Waste" and action == "1":
        json_string_discovery += '{"{#COLOR}":"' + cartridge_name + '"},'

print(json_string_discovery[:-1] + "]}") if action == "1" else print(json.dumps(json_string_element, indent=4))

