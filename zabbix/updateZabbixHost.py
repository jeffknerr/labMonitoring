#!/usr/bin/python3
"""
Jeff Knerr
Summer 2021

Adds host group to existing hosts in zabbix.

Assumes you have ~/zabbixAuth file, which contains:
URL of your zabbix server (e.g., https://myserver.edu/zabbix)
username
password

Typical uses:
    ./updateZabbixHosts.py -f hostfile -g "Another Group" 
    ./updateZabbixHosts.py -h host -g "Group3" -g "Group4"

- if given host already exists, will update the host
- if given host doesn't already exist, will quit
- if given group doesn't exist, will quit (won't make group)

So you need to make the groups in zabbix FIRST!!
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
@click.option('--group','-g',multiple=True,default=[],
        help="group(s)",show_default=True)
@click.option('--template','-t',multiple=True,default=['Linux by Zabbix agent'],
        help="template",show_default=True)
def main(hostfile, host, group, template):
    if hostfile==None and host==None:
        print("Need either a host or a file of hostnames!")
        sys.exit()
    if hostfile != None:
        hostList = readFile(hostfile)
    else:
        hostList = [host]
    zabbixAPI = login()
    checkExistingHosts(hostList, zabbixAPI)
    gIDs = []
    for item in group:
        groupID = getGroupID(item, zabbixAPI)
        gIDs.append(groupID)
    tIDs = []
    for item in template:
        templateID = getTemplateID(item, zabbixAPI)
        tIDs.append(templateID)
    for host in hostList:
        updateZabbixHost(host, gIDs, zabbixAPI, tIDs)

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

def checkExistingHosts(hostList, zabbixAPI):
    """
    Checks to make sure hosts in provided list already exist in zabbix.
    """
    hostDictionary = {'host': hostList}
    existingHostsDict = zabbixAPI.host.get(output=["hostid", "host"], filter=hostDictionary)
    existingHosts = [ x['host'] for x in existingHostsDict ]
    # need to traverse from back to front so deletions don't mess up things...
    for i in range(len(hostList)-1,-1,-1):
        hostname = hostList[i]
        if hostname not in existingHosts:
            print("removing non-existant host %s" % hostname)
            hostList.remove(hostname)
    if len(hostList)==0:
        print("There are no hosts to update! Exiting...")
        sys.exit(0)

def getTemplateID(template, zabbixAPI):
    """Search for template by name and try to find ID."""
    templateArray = [template]
    templateDictionary = {'host': templateArray}
    ret = zabbixAPI.template.get(output="templateids", filter=templateDictionary)
    if len(ret)==0:
        print("Template not found (%s)" % (template))
        sys.exit()
    return ret[0]['templateid'] 

def getGroupID(group, zabbixAPI):
    """Search for group by name and try to find id."""
    groupArray = [group]
    groupDictionary = {'name': groupArray}
    ret = zabbixAPI.hostgroup.get(output="groupid", filter=groupDictionary)
    if len(ret)==0:
        print("Group not found (%s)" % (group))
        sys.exit()
    return ret[0]['groupid']

def updateZabbixHost(host, gIDs, zabbixAPI, tIDs):
    """add gIDs to existing hosts"""

    # get just *this* host's current groups
    hdict = {'host': [host]}
    hostid = zabbixAPI.host.get(output=["hostid"], filter=hdict)
    hid = hostid[0]['hostid']
    ret = zabbixAPI.hostgroup.get(hostids=hid)
    groupArray = zabbixAPI.hostgroup.get(output="groupid", hostids=hid)
    # now add the new groups
    for groupID in gIDs:
        groupArray.append({'groupid':groupID})

    # now the templates
    templateArray = zabbixAPI.template.get(output="templateid", hostids=hid)
    for templateID in tIDs:
        templateArray.append({'templateid':templateID})

    ourHost = {'hostid':hid,'groups':groupArray,'templates':templateArray}
   
    print("Updating %s in zabbix..." % (host))
    ret = zabbixAPI.host.update(ourHost)

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
