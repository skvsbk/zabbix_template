#!/usr/bin/python3

from pysnmp.hlapi import * 
from dotenv import load_dotenv 
import pymysql 


# Credentials
load_dotenv('.env')

# SNMP connection
community_string = 'public'
port_snmp = 161
OID_FdbPort = '1.3.6.1.2.1.17.4.3.1.2'
OID_Exclude = '1.3.6.1.2.1.17.4.3.1.3' 

# DB connection
DBHost = os.getenv('DBHost') 
DBName = os.getenv('DBName') 
DBUser = os.getenv('DBUser')  
DBPassword = os.getenv('DBPassword')  

# IP Eltex
ip_address_hosts  = ['10.12.32.2','10.12.32.3','10.12.32.4','10.12.32.5','10.12.32.6','10.12.32.7','10.12.32.10','10.12.0.2','10.12.0.3']

def snmp_getnextcmd(community, ip, port, OID):
    return nextCmd(SnmpEngine(),
                    CommunityData(community),
                    UdpTransportTarget((ip, port)),
                    ContextData(),
                    ObjectType(ObjectIdentity(OID)))

# Connect to DB
connection = pymysql.connect(
    host = DBHost,
    user = DBUser,
    password = DBPassword,
    db = DBName,
    cursorclass = pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        # Loop IP Eltex
        for ip_address in ip_address_hosts:
            # Delete rows from DB for each Eltex
            query_del = "DELETE FROM mac_table WHERE ip = %s"
            cursor.executemany(query_del, [(ip_address)])
            connection.commit()
            # Get OIDs with port numbers
            getPort = snmp_getnextcmd(community_string, ip_address, port_snmp, OID_FdbPort)
            i = 0
            stop = 0  # for stop loop
            FinalyString = []
            for i in range(10000):
                try:
                    errorIndication, errorStatus, errorIndex, varBinds = next(getPort)
                    for name, val in varBinds:
                        MAC_byte = ''
                        MAC_addr = ''
                        if str(name).find(OID_Exclude) == 0:    # reached end of list OIDs
                            stop = 1
                            break

                        OID_received = str(name).split('.')
                        k = -6 # count bytes of mac-address
                        while k < 0:
                            MAC_byte = hex(int(OID_received[k])).replace('0x', '')
                            MAC_addr += MAC_byte if len(MAC_byte) == 2 else '0' + MAC_byte
                            k += 1
                        FinalyString.append((ip_address, MAC_addr, str(val)))
                    if stop:
                        break
                    i += 1
                except Exception:
                    print('No SNMP response received before timeout')
                    break
            # Store IP, MAC and Port to DB
            query = 'INSERT INTO mac_table(ip, mac, port) VALUES(%s, %s, %s)'
            cursor.executemany(query, FinalyString)
            connection.commit()
finally:
    connection.close()
