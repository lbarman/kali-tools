#!/usr/bin/env python3

import os
import os.path
import sys
import subprocess

# global constants
REMOTE_URL='git://git.kali.org/packages/{PACKAGE}.git'
PACKAGE_FOLDER='dist/'

# package definitions
packages = {}
packages['info_gathering'] = ['acccheck', 'ace-voip', 'amap', 'automater', 'bing-ip2hosts', 'braa', 'casefile', 'cdpsnarf', 'cisco-torch', 'cookie-cadger', 'copy-router-config', 'dmitry', 'dnmap', 'dnsenum', 'dnsmap', 'dnsrecon', 'dnstracer', 'dnswalk', 'dotdotpwn', 'enum4linux', 'enumiax', 'exploitdb', 'fierce', 'firewalk', 'fragroute', 'fragrouter', 'ghost -phisher', 'golismero', 'goofile', 'hping3', 'intrace', 'ismtp', 'lbd', 'maltego-teeth', 'masscan', 'metagoofil', 'miranda', 'nmap', 'ntop', 'p0f', 'parsero', 'recon-ng', 'set', 'smtp-user-enum', 'snmpcheck', 'sslcaudit', 'sslsplit', 'sslstrip', 'sslyze', 'thc-ipv6', 'theharvester', 'tlssled', 'twofi', 'urlcrazy', 'wireshark', 'wol-e', 'xplico']

# post-install scripts (what to do after cloning)
postInstall = {}
postInstall["nmap"] = ["./configure", "make", "make install"]
postInstall["nikto"] = ["echo \"#!/bin/sh\ncd $(pwd)/program; ./nikto.pl\" > nikto.sh", "chmod u+x nikto.sh"]

# how to run the cloned git (the script already guesses if there's an executable, this is for custom stuff)
runCmds = {}

# checks if a program is installed by running it in a subprocess and checking for error
def isInstalled(program):
    try:
        # pipe output to /dev/null for silence
        null = open("/dev/null", "w")
        subprocess.Popen(program, stdout=null, stderr=null)
        null.close()
        return True

    except OSError:
        return False

# if git is not installed, exit 1
def isGitInstalled():
    if not isInstalled("git"):
        print("git is required for this script to work. Please install it manually, e.g.:")
        print("   $ sudo apt-get install git")
        print("        or")
        print("   $ sudo dnf install git")
        print(" etc.")
        print("Exiting, status 1.")
        sys.exit(1)

# calls git clone, and wait for exit
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

# main function that checks if we need to clone a package, if so, run the post-install scripts
def installIfNeeded(package):
    dirName = PACKAGE_FOLDER+package

    if isInstalled(package):
        print(package, "seems already installed. Skipping")
        return

    print("Testing if", package, "exists locally...")
    if not os.path.isdir(dirName) :
        url = REMOTE_URL.replace("{PACKAGE}", package)
        print("Not found, gonna clone in", dirName)
        gitClone(url, dirName)

        if package in postInstall:
            print("Found post-install script(s)")
            for s in postInstall[package]:
                os.system("cd " + dirName + " && " + s)

# main function that tries to run a program (possibly cloning it before)
def run(package):

    #if package is already installed on the system via package manager, just call it
    if isInstalled(package):
        print(package, "seems already installed system-wide, calling it")
        os.system(package)

    #or, maybe clone the git, and run it
    else:
        installIfNeeded(package)

        # if we know how to run it, call the command
        if package in runCmds:
            print("Running", package)
            os.system(runCmds[package])

        #if we don't, try to guess
        else:
            baseName = PACKAGE_FOLDER+package+"/"+package

            if os.path.isfile(baseName+".sh"):
                print("Found an executable:", baseName+".sh", "running it... (Ctrl-C to exit)")
                os.system(baseName+".sh")
            elif os.path.isfile(baseName+".py"):
                print("Found an executable:", baseName+".py", "running it... (Ctrl-C to exit)")
                os.system(baseName+".py")
            elif os.path.isfile(baseName+".pl"):
                print("Found an executable:", baseName+".pl", "running it... (Ctrl-C to exit)")
                os.system(baseName+".pl")
            #finally, we give up
            else:
                print("Please run the program in", PACKAGE_FOLDER, package)

def printKaliMenu():
    print ('''
1) Information Gathering            8) Exploitation Tools
2) Vulnerability Analysis           9) Forensics Tools
3) Wireless Attacks                 10) Stress Testing
4) Web Applications                 11) Password Attacks
5) Sniffing & Spoofing              12) Reverse Engineering
6) Maintaining Access               13) Hardware Hacking
7) Reporting Tools                  14) Extra
''')

# check for prerequisites
isGitInstalled()

printKaliMenu()

run("hashid")