#!/usr/bin/python3

"""All Machines: freeMemory single stat"""                  

from utils import *
from dashboard import *
from panel import *   
from pyzabbix import ZabbixAPI 
import os

postURL = "http://localhost:3000/api/dashboards/db"
base = "https://blade.cs.swarthmore.edu/grafana/"
                          
def main():
    zabAuth = os.environ["HOME"] + "/zabbixAuth"
    grafAuth = os.environ["HOME"] + "/grafanaToken"
    zabbixAPI, token, URL = getCredentials(zabAuth, grafAuth)
    hosts = getHosts(zabbixAPI)
    db = DashBoard(title="All Machines: free memory", token=token, panelsPerRow=16, panelHeight = 2)
    panels = []
    for host in hosts:
        q = Query(host, "Available memory", alias="freeMem")
        link = base+host
        p = SingleStatPanel(title=host, 
                queryArray=[q], 
                colorMode="background",
                units="decbits",
                calcs="lastNotNull",
                colors = ["dark-red","dark-yellow","dark-orange","dark-green","dark-blue","rgb(50,50,50)"],
                thresholds = ["null",8000000000,16000000000,32000000000,64000000000,128000000000],
                absLink=link)
        panels.append(p)
    db.addPanels(panels)
    db.push(postURL)
main()
