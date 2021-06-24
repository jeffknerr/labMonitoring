
from pyzabbix import ZabbixAPI
import sys

DEFAULTGROUP = "SwatCSComputers"

def getCredentials(zabAuth, grafAuth):
    """                              
    Parameters: Zabbix Authentication file with two lines,
        <URL>                                            
        <username>                                      
        <password>                                     
    Grafana Authentication file with two lines,       
        <token>                                      
        <URL>                                       
    Returns: ZabbixAPI Object, token, and url      
    """                                           
    zabbixAPI = None                             
    try:                                        
        inFile = open(zabAuth, "r")            
        ZURL = inFile.readline().strip()      
        username = inFile.readline().strip() 
        password = inFile.readline().strip()
        inFile.close()                   
    except IOError:                     
        print("Couldn't open %s..." % zabAuth) 
        sys.exit(0)                           
    zabbixAPI = ZabbixAPI(ZURL)             
    zabbixAPI.login(username, password)    

    try:                                                   
        inFile = open(grafAuth, "r")
        token = inFile.readline().strip()
        URL = inFile.readline().strip()
        inFile.close()
    except IOError:
        print("Couldn't open %s..." % grafAuth)
        sys.exit(0)

    return zabbixAPI, token, URL

def getHosts(zabbixAPI):
    """
    Parameters: zabbixAPI object
    Returns: a list of zabbix hosts in the DEFAULTGROUP 
    """
    linuxGroup = zabbixAPI.hostgroup.get(output=["groupid"], filter={"name":[DEFAULTGROUP]})
    groupIDArray = [linuxGroup[0]["groupid"]]
    linuxMachines = zabbixAPI.host.get(output=["host"], groupids=groupIDArray)
    hostNames = []
    for host in linuxMachines:
        hostNames.append(host["host"])
    hostNames.sort()
    return hostNames
