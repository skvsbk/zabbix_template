#!/usr/bin/python3

import pymysql
import sys

# Аргументы - IP коммутатора, номер порта

IP_address  =  sys.argv[1]	# '10.12.32.7'
Port_number =  sys.argv[2]	# '107'

# Параметры подключения к DB
DBHost = '10.12.0.21' # 'localhost'
DBName = 'eltex'
DBUser = 'zabbix'
DBPassword = 'zabbixDBpass'

# Подключение к DB
connection = pymysql.connect(
    host = DBHost,
    user = DBUser,
    password = DBPassword,
    db = DBName,
    cursorclass = pymysql.cursors.DictCursor)

MAC_list = []

try:
    with connection.cursor() as cursor:
        query = "SELECT * FROM mac_table WHERE ip = '" + IP_address + "' AND port = '" + Port_number +"'"
        cursor.execute(query)
        for row in cursor:
            MAC_list.append(row['mac'])
        print(MAC_list) if len(MAC_list)>0 else print('null')

finally:
    connection.close()
