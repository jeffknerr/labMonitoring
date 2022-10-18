#!/usr/bin/python3
"""
Herbie Rand
Jeff Knerr
Summer 2019

Adds hosts to zabbix server.  

Assumes you have ~/zabbixAuth file, which contains:
URL of your zabbix server (e.g., https://myserver.edu/zabbix)
username
password

Typical uses:
    ./addHosts.py -f hostfile -g "My Group" -t "My Template"
    ./addHosts.py -h host -g "Group1" -g "Group2" -t "Temp1" -t "Temp2"

- if given host already exists, you can leave as is or replace
- if given template doesn't exist, will quit (won't make template)
- if given group doesn't exist, will quit (won't make group)

So you need to make the groups and templates FIRST, 
in zabbix (or use the templates that come with zabbix)

TODO: --snmp does not work???
"""

from pyzabbix import ZabbixAPI
import argparse
import subprocess
import os, sys
import socket
import click

@click.command()
@click.option('-f','--hostfile', default=None, help="file with hostnames to add")
@click.option('-h','--host', default=None, help="host to add")
@click.option('--group','-g',multiple=True,default=['all'],
        help="group(s)",show_default=True)
@click.option('--template','-t',multiple=True,default=['Linux by Zabbix agent'],
        help="template",show_default=True)
@click.option('--snmp/--no-snmp', default=False, 
        help="use SNMP (default is to use ZabbixAgent)")
@click.option('--replace/--no-replace', default=False, 
        help="replace existing host (default is to leave as is)")
def main(hostfile, host, group, template, snmp, replace):
    if hostfile==None and host==None:
        print("Need either a host or a file of hostnames!")
        sys.exit()
    if hostfile != None:
        hostList = readFile(hostfile)
    else:
        hostList = [host]
    zabbixAPI = login()
    hostList = handleExistingHosts(hostList, zabbixAPI, replace)
    tIDs = []
    for item in template:
        templateID = getTemplateID(item, zabbixAPI)
        tIDs.append(templateID)
    gIDs = []
    for item in group:
        groupID = getGroupID(item, zabbixAPI)
        gIDs.append(groupID)
    for host in hostList:
        addHostToZabbix(host, tIDs, gIDs, zabbixAPI, snmp)

# ------------------------------------- #

def login():
    """log into Zabbix API as superAdmin, return API object"""
    fn = os.environ["HOME"] + "/zabbixAuth"
    uname,pw,ZURL = readAuth(fn)
    zabbixAPI = ZabbixAPI(ZURL)
    try:
        zabbixAPI.login(uname, pw)
        return zabbixAPI
    except:
        print("Problem with zabbix API login...")
        sys.exit(1)

def readAuth(filename):
    """read in authentication info"""
    try:
        inf = open(filename, "r")
        url = inf.readline().strip()
        uname = inf.readline().strip()
        pw = inf.readline().strip()
        inf.close()
        return uname, pw, url
    except:
        print("Problem reading auth file...")
        sys.exit(1)

def readFile(hostfile):
    """read hosts into list of hostnames"""
    hostList = []
    try: 
        hostFile = open(hostfile, 'r')
    except IOError:
        print("Error opening hostfile (%s), exiting..." % hostfile)
        sys.exit(2)
    for line in hostFile:
        hostList.append(line.strip())
    hostFile.close() 
    return hostList

def handleExistingHosts(hostList, zabbixAPI, replace):
    """
    Checks to see if hosts in provided list already exist in zabbix.
    If so, give option to replace or leave as is.
    """
    hostDictionary = {'host': hostList}
    existingHosts = zabbixAPI.host.get(output=["hostid", "host"], filter=hostDictionary)
    if (len(existingHosts)==0):
        return hostList
    else:
        if replace:
            # delete existing hosts from zabbix
            for hdict in existingHosts:
                zabbixAPI.host.delete(int(hdict['hostid']))
        else:
            # take existing hosts out of hostList
            for hdict in existingHosts:
                host = hdict['host']
                if host in hostList:
                    hostList.remove(host)
    if len(hostList)==0:
        #print("There are no hosts to add! Exiting...")
        sys.exit(0)

    return hostList

def getTemplateID(template, zabbixAPI):
    """Search for template by name and try to find ID."""
    templateArray = [template]
    templateDictionary = {'host': templateArray}
    ret = zabbixAPI.template.get(output=["templateid"], filter=templateDictionary)
    if len(ret)==0:
        print("Template not found (%s)" % (template))
        sys.exit()
    return ret[0]['templateid'] 

def getGroupID(group, zabbixAPI):
    """Search for group by name and try to find id."""
    groupArray = [group]
    groupDictionary = {'name': groupArray}
    ret = zabbixAPI.hostgroup.get(output=["groupid"], filter=groupDictionary)
    if len(ret)==0:
        print("Group not found (%s)" % (group))
        sys.exit()
    return ret[0]['groupid']

def addHostToZabbix(host, tIDs, gIDs, zabbixAPI, snmp):
    """Creates a host according to parameters"""
    # default to zabbixAgent
    typenum = 1
    portnum = 10050
    if snmp:
        typenum = 2
        portnum = 161
   
    interfaceArray = [{'type':typenum,       # 1 for Zabbix Agent, 2 for SNMP
                        'main':1,            # make this interface default 
                        'useip':1,           # 1 to use IP (instead of dns)
                        'ip':checkIP(host),  # ip address
                        'dns':"",            # no dns required if you supply ip
                        'port':portnum}]     # 161 snmp, 10050 for zabbix agent

    groupArray=[]
    for groupID in gIDs:
        groupArray.append({'groupid':groupID})

    ourHost = {'host':host,'description':'host made with addZabbixHosts',
            'inventory_mode':1,'interfaces':interfaceArray,'groups':groupArray}
   
    if tIDs!=[-1]:
        ourHost['templates']=[]
        for templateID in tIDs:
            ourHost['templates'].append({'templateid':templateID})
    
    print("Creating %s in zabbix..." % (host))
    ret = zabbixAPI.host.create(ourHost)

    return

def checkIP(oneHost):
    """get host IP address"""
    try:                                 
        ip = socket.gethostbyname(oneHost)
        return ip
    except:
        print("Couldn't find %s's IP..." % (oneHost))
        sys.exit()

# ------------------------------------- #
main()
