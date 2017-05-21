#!/usr/bin/env python3

import os
import os.path
import sys
import subprocess
import requests
import signal

# global constants
REMOTE_URL='git://git.kali.org/packages/{PACKAGE}.git'
PACKAGE_FOLDER='dist/'

# package definitions
packages = {}
packages['info_gathering'] = ['acccheck', 'ace-voip', 'amap', 'automater', 'bing-ip2hosts', 'braa', 'casefile', 'cdpsnarf', 'cisco-torch', 'cookie-cadger', 'copy-router-config', 'dmitry', 'dnmap', 'dnsenum', 'dnsmap', 'dnsrecon', 'dnstracer', 'dnswalk', 'dotdotpwn', 'enum4linux', 'enumiax', 'exploitdb', 'fierce', 'firewalk', 'fragroute', 'fragrouter', 'ghost-phisher', 'golismero', 'goofile', 'hping3', 'intrace', 'ismtp', 'lbd', 'maltego-teeth', 'masscan', 'metagoofil', 'miranda', 'nmap', 'ntop', 'p0f', 'parsero', 'recon-ng', 'set', 'smtp-user-enum', 'snmpcheck', 'sslcaudit', 'sslsplit', 'sslstrip', 'sslyze', 'thc-ipv6', 'theharvester', 'tlssled', 'twofi', 'urlcrazy', 'wireshark', 'wol-e', 'xplico']
packages['vuln_analysis'] = ['bbqsql', 'bed', 'cisco-auditing-tool', 'cisco-global-exploiter', 'cisco-ocs', 'cisco-torch', 'commix', 'copy-router-config', 'dbpwaudit', 'doona', 'greenbone-security-assistant', 'gsd', 'hexorbase', 'inguma', 'jsql', 'lynis', 'nmap', 'ohrwurm', 'openvas-administrator', 'openvas-cli', 'openvas-manager', 'openvas-scanner', 'oscanner', 'powerfuzzer', 'sfuzz', 'sidguesser', 'siparmyknife', 'sqlmap', 'sqlninja', 'sqlsus', 'thc-ipv6', 'tnscmd10g', 'unix-privesc-check', 'yersinia']
packages['wifi'] = ['aircrack-ng', 'asleap', 'bluelog', 'bluemaho', 'bluepot', 'blueranger', 'bluesnarfer', 'bully', 'cowpatty', 'crackle', 'eapmd5pass', 'fern-wifi-cracker', 'ghost-phisher', 'giskismet', 'gr-scan', 'kalibrate-rtl', 'killerbee', 'kismet', 'mdk3', 'mfcuk', 'mfoc', 'mfterm', 'multimon-ng', 'pixiewps', 'reaver', 'redfang', 'rtlsdr-scanner', 'spooftooph', 'wifi-honey', 'wifitap', 'wifite']
packages['web'] = ['apache-users', 'arachni', 'bbqsql', 'blindelephant', 'burpsuite', 'commix', 'cutycapt', 'davtest', 'deblaze', 'dirb', 'dirbuster', 'fimap', 'funkload', 'grabber', 'jboss-autopwn', 'joomscan', 'jsql', 'maltego-teeth', 'padbuster', 'paros', 'parsero', 'plecost', 'powerfuzzer', 'proxystrike', 'recon-ng', 'skipfish', 'sqlmap', 'sqlninja', 'sqlsus', 'ua-tester', 'uniscan', 'vega', 'w3af', 'webscarab', 'webshag', 'webslayer', 'websploit', 'wfuzz', 'wpscan', 'xsser', 'zaproxy']
packages['sniffing_spoofing'] = ['burpsuite', 'dnschef', 'fiked', 'hamster-sidejack', 'hexinject', 'iaxflood', 'inviteflood', 'ismtp', 'isr-evilgrade', 'mitmproxy', 'ohrwurm', 'protos-sip', 'rebind', 'responder', 'rtpbreak', 'rtpinsertsound', 'rtpmixsound', 'sctpscan', 'siparmyknife', 'sipp', 'sipvicious', 'sniffjoke', 'sslsplit', 'sslstrip', 'thc-ipv6', 'voiphopper', 'webscarab', 'wifi-honey', 'wireshark', 'xspy', 'yersinia', 'zaproxy']
packages['keep_access'] = ['cryptcat', 'cymothoa', 'httptunnel', 'intersect', 'nishang', 'powersploit', 'ridenum', 'u3-pwn', 'webshells', 'weevely', 'dbd', 'dns2tcp', 'http-tunnel ', 'polenum', 'pwnat', 'sbd']
packages['reporting'] = ['casefile', 'cutycapt', 'dos2unix', 'dradis', 'keepnote ', 'magictree', 'metagoofil', 'nipper-ng', 'pipal']
packages['exploitation'] = ['armitage', 'backdoor-factory', 'beef', 'cisco-auditing-tool', 'cisco-global-exploiter', 'cisco-ocs', 'cisco-torch', 'commix', 'crackle', 'jboss-autopwn', 'linux-exploit-suggester', 'maltego-teeth', 'set', 'shellnoob', 'sqlmap', 'thc-ipv6', 'yersinia']
packages['forensics'] = ['binwalk', 'bulk-extractor', 'capstone', 'chntpw', 'cuckoo', 'dc3dd', 'ddrescue', 'dff', 'distorm3', 'dumpzilla', 'extundelete', 'foremost', 'galleta', 'guymager', 'iphone-backup-analyzer', 'p0f', 'pdf-parser', 'pdfid', 'pdgmail', 'peepdf', 'regripper', 'volatility', 'xplico']
packages['stress_test'] = ['dhcpig', 'funkload', 'iaxflood', 'inundator', 'inviteflood ', 'ipv6-toolkit', 'mdk3', 'reaver', 'rtpflood', 'slowhttptest', 't50', 'termineter', 'thc-ipv6', 'thc-ssl-dos']
packages['passwords'] = ['acccheck', 'burpsuite', 'cewl', 'chntpw', 'cisco-auditing-tool', 'cmospwd', 'creddump', 'crunch', 'dbpwaudit', 'findmyhash', 'gpp-decrypt', 'hash-identifier', 'hexorbase', 'john the ripper', 'johnny', 'keimpx', 'maltego-teeth', 'maskprocessor', 'multiforcer', 'ncrack', 'oclgausscrack', 'pack', 'patator', 'phrasendrescher', 'polenum', 'rainbowcrack', 'rcracki-mt', 'rsmangler', 'sqldict', 'statsprocessor', 'hydra', 'thc-pptp-bruter', 'truecrack', 'webscarab', 'wordlists', 'zaproxy']
packages['reverse_engineering'] = ['apktool', 'dex2jar', 'distorm3', 'edb-debugger', 'jad ', 'javasnoop', 'jd-gui', 'ollydbg', 'smali', 'valgrind', 'yara']
packages['hardware'] = ['android-sdk', 'apktool', 'arduino', 'dex2jar', 'sakis3g ', 'smali']
packages['extras'] = ['squid3', 'wifresti']
# adds a redirect for numeric input
packages['0'] = packages['info_gathering']
packages['1'] = packages['vuln_analysis']
packages['2'] = packages['wifi']
packages['3'] = packages['web']
packages['4'] = packages['sniffing_spoofing']
packages['5'] = packages['keep_access']
packages['6'] = packages['reporting']
packages['7'] = packages['exploitation']
packages['8'] = packages['forensics']
packages['9'] = packages['stress_test']
packages['10'] = packages['info_gathering']
packages['11'] = packages['info_gathering']
packages['12'] = packages['info_gathering']
packages['13'] = packages['info_gathering']
packages['14'] = packages['info_gathering']

# special git folders
specialGitURL = {}
specialGitURL['wifresti'] = 'https://github.com/LionSec/wifresti.git'

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

# test all packages names against the reference URL, shows broken links / packages
def testAllURLs():
    allPackages = []
    for cat in packages:
        allPackages += packages[cat]
    allPackages = set(allPackages)
    allPackages = sorted(list(allPackages))

    #get the page referencing all packages
    source = ""
    try:
        print("Contacting web server...")
        req = requests.get("http://git.kali.org/gitweb/", timeout=30)
        print("Done.")
        source = req.text
    except:
        print("Could not read git repos")
        sys.exit(1)

    #for each package, check if in page
    for p in allPackages:
        if p not in specialGitURL:
            fullPath = "packages/"+p+".git"
            if p not in source:
                print("Error", p, "@", fullPath, "not found.")

def readInput(str): #handles Ctrl-D
    print(str)
    line = sys.stdin.readline()
    if line:
        line = line.replace("\r", "").replace("\n", "")
        return line
    else: # user pressed C-D, i.e. stdin has been
        print("Quitting.")
        sys.exit(1)

def printHeader():
    print (''' _  _    __    __    ____     ____  _____  _____  __    ___ 
( )/ )  /__\  (  )  (_  _)___(_  _)(  _  )(  _  )(  )  / __)
 )  (  /(__)\  )(__  _)(_(___) )(   )(_)(  )(_)(  )(__ \__ 
(_)\_)(__)(__)(____)(____)    (__) (_____)(_____)(____)(___/''')

def printKaliMenu():
    print('''
Please select a category:

1) Information Gathering            8) Exploitation Tools
2) Vulnerability Analysis           9) Forensics Tools
3) Wireless Attacks                 10) Stress Testing
4) Web Applications                 11) Password Attacks
5) Sniffing & Spoofing              12) Reverse Engineering
6) Maintaining Access               13) Hardware Hacking
7) Reporting Tools                  14) Extra
''')
    action = ""
    while not action.isdigit() or int(action)<1 or int(action)>14 or not str(action) in packages:
        action = readInput("Category: ")
    printKaliSubMenu(str(action))

def printKaliSubMenu(id):
    ps = packages[id]

    #compute a map to find the package given the number
    m = {}

    print("")
    i = 1
    for p in ps:
        m[i] = p
        print(str(i) + ") "+p)
        i += 1
    print("")
    no = ""
    while not no.isdigit() or int(no)<1 or int(no)>=i:
        no = readInput("Package No: ")

    selectedPackage = m[int(no)]
    printSelectedPackage(selectedPackage)

def printSelectedPackage(p):
    print("")
    print("Package\033[1m", p, "\033[0m") #just to put in bold

    dirName = PACKAGE_FOLDER+p
    if isInstalled(p) or os.path.isdir(dirName):
        print("This package is already installed.")
    else:
        print("This package is\033[1m not\033[0m installed, and will be downloaded if you try to run it.")

    ans = ""
    while ans != "y" and ans != "n" :
        ans = readInput('Would you like to run it ? [Y/n] ').lower()

    if ans == "y":
        print("")
        run(p)
    else:
        printKaliMenu()

#register the Ctrl-C and others to have a clean exit
def handleInterrupts():
    def signal_handler(signal, frame):
        print("Quitting.")
        sys.exit(1)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGABRT, signal_handler)
    signal.signal(signal.SIGFPE, signal_handler)
    signal.signal(signal.SIGILL, signal_handler)
    signal.signal(signal.SIGSEGV, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

handleInterrupts()
isGitInstalled()
printHeader()
printKaliMenu()

#testAllURLs()