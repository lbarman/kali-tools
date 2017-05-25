#!/usr/bin/env python3

import os
import os.path
import sys
import subprocess
import requests
import signal
from bs4 import BeautifulSoup, SoupStrainer
import re

# global constants
REMOTE_URL='git://git.kali.org/packages/{PACKAGE}.git'
PACKAGE_FOLDER='dist/'
DESCRIPTION_EXTRACT_MAX_LENGTH = 100


# ##################################################################
#                  DATA & AUXILIARY FUNCTIONS
# ##################################################################

import data
import helpers

# ##################################################################
#                       HELPER FUNCTIONS
# ##################################################################

# Helper that handles Ctrl-D
def readInput(str):
    print(str)
    line = sys.stdin.readline()
    if line:
        line = line.replace("\r", "").replace("\n", "")
        return line
    else: # user pressed C-D, i.e. stdin has been
        print("Quitting.")
        sys.exit(1)

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

# checks if a program is installed system-wide by running it in a subprocess and checking for error
def isInstalledWithSystemPM(program):
    try:
        # pipe output to /dev/null for silence
        null = open("/dev/null", "w")
        res = subprocess.Popen(["which", program], stdout=subprocess.PIPE, stderr=null)
        null.close()
        o = res.stdout.read()
        if o == "":
            return False
        return True

    except OSError:
        return False

# checks if a program is "installed" locally (in dist/)
def isInstalledWithGitLocally(package):
    dirName = PACKAGE_FOLDER+package
    return os.path.isdir(dirName)

# if git is not installed, exit 1
def isGitInstalled():
    if not isInstalledWithSystemPM("git"):
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

    if isInstalledWithSystemPM(package):
        print(package, "seems already installed. Skipping")
        return

    print("Testing if", package, "exists locally...")
    if not isInstalledWithGitLocally(package) :
        url = REMOTE_URL.replace("{PACKAGE}", package)
        print("Not found, gonna clone in", dirName)
        gitClone(url, dirName)

        if package in data.postInstall:
            print("Found post-install script(s)")
            for s in data.postInstall[package]:
                os.system("cd " + dirName + " && " + s)

# main function that tries to run a program (possibly cloning it before)
def run(package):

    #if package is already installed on the system via package manager, just call it
    if isInstalledWithSystemPM(package):
        print(package, "seems already installed system-wide, calling it")
        os.system(package)

    #or, maybe clone the git, and run it
    else:
        installIfNeeded(package)

        # if we know how to run it, call the command
        if package in data.runCmds:
            print("Running", package)
            os.system(data.runCmds[package])

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


# ##################################################################
#                         MAIN LOGIC
# ##################################################################

def printHeader():
    print (''' _  _    __    __    ____     ____  _____  _____  __    ___ 
( )/ )  /__\  (  )  (_  _)___(_  _)(  _  )(  _  )(  )  / __)
 )  (  /(__)\  )(__  _)(_(___) )(   )(_)(  )(_)(  )(__ \__ 
(_)\_)(__)(__)(____)(____)    (__) (_____)(_____)(____)(___/''')

def printTableHeader(longestPackageName):
    print(" N°|  Name"+ ' ' * (longestPackageName - 4)+" | Installed | Description")
    print('---|'+'-' * (longestPackageName+3) + '|-----------|' + '-' * (DESCRIPTION_EXTRACT_MAX_LENGTH+1))


def printPackageLine(id, p, longestPackageName, highlightTerm):
    #pad for 0-9
    num = str(id)+") "
    if id < 10 :
        num = " "+num

    #compute "installed" field
    isInstalledStr = "            "
    if isInstalledWithSystemPM(p):
        isInstalledStr = " YES, system"
    elif isInstalledWithGitLocally(p):
        isInstalledStr = " YES, git   "

    #compute description field
    description = ""
    if p in data.desc:
        description = data.desc[p]
        if len(description) > DESCRIPTION_EXTRACT_MAX_LENGTH:
            description = description[0:DESCRIPTION_EXTRACT_MAX_LENGTH-3]+"..."
        description = " " + description

    #pad the name to the longest name
    spaces = ' ' * (longestPackageName - len(p))
    
    #if given, highlight the term
    if highlightTerm is not None:
        regex = re.compile(re.escape(highlightTerm), re.IGNORECASE)
        p = regex.sub("\033[31m"+highlightTerm+"\033[m", p)
        description = regex.sub("\033[31m"+highlightTerm+"\033[m", description)

        if "[31m" not in p and "[31m" not in description:
            description = description.replace("...", "\033[31m...\033[m")


    print(num, p, spaces, isInstalledStr, description)

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
    while not action.isdigit() or int(action)<1 or int(action)>14 or not str(action) in data.packages:
        action = readInput("Category: ")
    printKaliSubMenu(str(action))

# prints a collection of packages
def printPackageCollection(package, highlightTerm):

    #compute a map to find the package given the number
    m = {}

    longestStr = len(max(package, key=len))
    print("")
    i = 1
    printTableHeader(longestStr)
    for p in package:
        m[i] = p
        printPackageLine(i, p, longestStr, highlightTerm)
        i += 1
    print("")
    no = ""
    while not no.isdigit() or int(no)<1 or int(no)>=i:
        no = readInput("Package No: ")

    selectedPackage = m[int(no)]
    printSelectedPackage(selectedPackage, highlightTerm)

# prints one of Kali's categories
def printKaliSubMenu(id):
    ps = data.packages[id]
    printPackageCollection(ps, None)

# prints the selected package, test if installed, and asks wheter to run it
def printSelectedPackage(p, highlightTerm):
    print("-" * DESCRIPTION_EXTRACT_MAX_LENGTH)
    print("| Package\033[1m", p, "\033[0m") #just to put in bold
    print("-" * DESCRIPTION_EXTRACT_MAX_LENGTH)
    if p in data.desc and data.desc[p] != "":
        print("| Description:")
        d = data.desc[p]
        if highlightTerm is not None:
            regex = re.compile(re.escape(highlightTerm), re.IGNORECASE)
            d = regex.sub("\033[31m"+highlightTerm+"\033[m", d)
        #print with line wrap
        ds = d.split("\n")
        for part in ds:
            while len(part) > DESCRIPTION_EXTRACT_MAX_LENGTH:
                end = part[0:DESCRIPTION_EXTRACT_MAX_LENGTH].rfind(' ')
                print("| "+part[0:end])
                part=part[end+1:]
            print("| "+part)
    else:
        print("| (no description yet)")
            
    print("-" * DESCRIPTION_EXTRACT_MAX_LENGTH)

    if isInstalledWithSystemPM(p) or isInstalledWithGitLocally(p):
        print("This package is already installed (and will not be downloaded).")
    else:
        print("This package is \033[31mnot\033[m installed, and will be downloaded if you try to run it.")

    ans = ""
    while ans != "y" and ans != "n" :
        ans = readInput('Would you like to download/run it ? [Y/n] ').lower()

    if ans == "y":
        print("")
        run(p)
    else:
        printKaliMenu()

def search(term):
    print("")
    print("Searching for", term)

    matches = []
    for cat in data.packages:
        if not cat.isdigit():
            for p in data.packages[cat]:
                if term.lower() in p.lower() or (p in data.desc and term.lower() in data.desc[p].lower()):
                    matches.append(p)

    if len(matches) == 0:
        print("No packages matching.")
    else:
        matches = list(set(matches)) #make results uniques
        printPackageCollection(matches, term)

# ##################################################################
#                         ENTRY POINT
# ##################################################################


# entry point
handleInterrupts()
isGitInstalled()

printHeader()
# if no args given, print interactive menu, otherwise, directly search
if len(sys.argv) == 1:
    print("")
    print("PROTIP: use "+sys.argv[0]+" TERM to directly search for TERM")
    printKaliMenu()
else:
    search(sys.argv[1])


# use this to test if all packages are still hosted correctly
# helpers.testAllURLs()
#l = helpers.fetchPackageLinks()
#helpers.fetchPackageDescription(l)