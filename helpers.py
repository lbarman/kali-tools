# test all packages names against the reference URL, shows broken links / packages
def testAllURLs():
    allPackages = []
    for cat in data.packages:
        allPackages += data.packages[cat]
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
        if p not in data.specialGitURL:
            fullPath = "packages/"+p+".git"
            if p not in source:
                print("Error", p, "@", fullPath, "not found.")


# fetches the links to get the full description of the pacakge
def fetchPackageLinks():
    d = requests.get("http://tools.kali.org/tools-listing")
    rawHtml = d.text
    soup = BeautifulSoup(rawHtml, 'html.parser')
    links = {}
    for link in soup.find_all('a'):
        if "<a href=\"http://tools.kali.org/" in str(link) :
            package = link.string.lower().replace(" ", "-")
            links[package] = link.get('href')

    #for l in sorted(links.keys()):
    #    print("links['"+l+"'] = \""+links[l]+"\"")

    return links

def fetchPackageDescription(links):
    for p in sorted(data.desc.keys()):
        if data.desc[p] == "":
            if p in links:
                #print("Getting doc for", p)
                d = requests.get(links[p])

                out = ""
                if d.status_code == 200 :
                    rawHtml = d.text
                    soup = BeautifulSoup(rawHtml, 'html.parser')
                    for s in soup.find_all('section'):
                        if "Package Description" in str(s):
                            for par in s.find_all('p'):
                                if not "Homepage" in par.text:
                                    t = par.text.strip()
                                    if not t.endswith("."):
                                        t += "."
                                    out += t + " "
                    print("desc['"+p+"'] = \""+out.replace("\"", "\\\"")+"\"")