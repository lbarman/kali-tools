#!/usr/bin/env python3

import os
import os.path
import sys
import subprocess


REMOTE_URL='git://git.kali.org/packages/{PACKAGE}.git'
PACKAGE_FOLDER='dist/'

packages = {}
packages['info_gathering'] = ['acccheck', 'ace-voip', 'amap', 'automater', 'bing-ip2hosts', 'braa', 'casefile', 'cdpsnarf', 'cisco-torch', 'cookie-cadger', 'copy-router-config', 'dmitry', 'dnmap', 'dnsenum', 'dnsmap', 'dnsrecon', 'dnstracer', 'dnswalk', 'dotdotpwn', 'enum4linux', 'enumiax', 'exploitdb', 'fierce', 'firewalk', 'fragroute', 'fragrouter', 'ghost -phisher', 'golismero', 'goofile', 'hping3', 'intrace', 'ismtp', 'lbd', 'maltego-teeth', 'masscan', 'metagoofil', 'miranda', 'nmap', 'ntop', 'p0f', 'parsero', 'recon-ng', 'set', 'smtp-user-enum', 'snmpcheck', 'sslcaudit', 'sslsplit', 'sslstrip', 'sslyze', 'thc-ipv6', 'theharvester', 'tlssled', 'twofi', 'urlcrazy', 'wireshark', 'wol-e', 'xplico']


postInstall = {}
postInstall["nmap"] = ["./configure", "make", "make install"]
postInstall["nikto"] = ["echo \"#!/bin/sh\ncd program; ./nikto.pl\" > nikto.sh", "chmod u+x nikto.sh"]

print ('''

1) Information Gathering            8) Exploitation Tools
2) Vulnerability Analysis           9) Forensics Tools
3) Wireless Attacks                 10) Stress Testing
4) Web Applications                 11) Password Attacks
5) Sniffing & Spoofing              12) Reverse Engineering
6) Maintaining Access               13) Hardware Hacking
7) Reporting Tools                  14) Extra
                                    
0) All

''')

def isInstalled(program):
    try:
        # pipe output to /dev/null for silence
        null = open("/dev/null", "w")
        subprocess.Popen(program, stdout=null, stderr=null)
        null.close()
        return True

    except OSError:
        return False

def isGitInstalled():
    if not isInstalled("git"):
        print("git is required for this script to work. Please install it manually, e.g.:")
        print("   $ sudo apt-get install git")
        print("        or")
        print("   $ sudo dnf install git")
        print(" etc.")
        print("Exiting, status 1.")
        sys.exit(1)

def gitClone(repo, localDir):
    try:
        # pipe output to /dev/null for silence
        null = open("/dev/null", "w")
        subprocess.call(["git", "clone", repo, localDir])
        null.close()

    except OSError:
        print("Could not clone...")
        print("Exiting, status 1.")
        sys.exit(1)

def installIfNeeded(package):
    dirName = PACKAGE_FOLDER+package

    if isInstalled(package):
        print(package, "seems already installed. Skipping")
        return

    print("Testing if", package, "exists locally...")
    if not os.path.isfile(dirName) :
        url = REMOTE_URL.replace("{PACKAGE}", package)
        print("Not found, gonna clone in", dirName)
        gitClone(url, dirName)

        if package in postInstall:
            print("Found post-install script(s)")
            for s in postInstall[package]:
                os.system("cd " + dirName + " && " + s)


isGitInstalled()
installIfNeeded("nikto")