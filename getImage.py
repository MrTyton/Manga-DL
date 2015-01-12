import urllib2
import os
from time import sleep
import random

def download(url, dir):
    print url
    req = urllib2.Request(url, headers={"Accept-Encoding": "utf-8", "Accept-Charset": "utf-8", "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"})
    response = urllib2.urlopen(req)
    if response.getcode() == 200:
        page = response.read()
    else:
        response.close()        
        return main(url)
    if "comic_page" not in page:
        encoding = response.headers['content-type'].split('charset=')[-1]
        print encoding
        page = unicode(page, encoding, "ignore")
        if "comic_page" not in page:
            print "Sleeping"
            response.close()
            return url
    response.close()
    startparse = page[page.index("comic_page"):]
    startparse = startparse[startparse.index('src="')+5:]
    image = startparse[:startparse.index('"')]
    #print image
    file_name = image.split('/')[-1]
    u = urllib2.urlopen(image)
    startparse = page[page.index('selected="selected"'):]
    directory = "%s/%s" % (dir, startparse[startparse.index('>')+1:startparse.index("<")])
    directory = directory.replace(":","").replace("<", "").replace(">", "").replace('"', "").replace("?", "").replace("*","").replace("|", "")
    while directory[-1] == ".": directory = directory[:-1]
    ensure_dir(directory)
    #print directory
    f = open("%s/%s" % (directory, file_name), 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0]) / 1024
    print "Downloading: %s at %s KiloBytes" % (file_name, file_size)
    f.write(u.read())   
    f.close()
    nextchapter = '<a href="http://bato.to/read' in page
    if page.count('<a href="http://bato.to/comic') == 5:
        return None
    startparse = page[page[:page.index("comic_page")].rfind('<a href="http://bato.to/read')+9:]
    nextpage = startparse[:startparse.index('"')]
    return nextpage



def ensure_dir(f):
    if not os.path.exists(f):
        os.makedirs(f)

def main():
    urls = ["http://bato.to/read/_/297036/rising-x-rydeen_ch27_by_village-idiot/2", "http://bato.to/read/_/187537/dr-duo_v1_ch1_by_fried-squid-scans", "http://bato.to/read/_/269565/karakai-jouzu-no-takagi-san_v1_ch1_by_ciel-scans", "http://bato.to/read/_/168435/kyou-no-yuiko-san_v1_ch1_by_mal-scanlations", "http://bato.to/read/_/196619/dousei-recipe_v1_ch0.1_by_scx-scans"]
    dirs = ["Rising x Rydeen", "Dr. Duo", "Teasing Master Takagi-san", "Today's Yuiko-San", "Dousei Recipe"]
    #URL = raw_input("Start URL: ")
    #DIR = raw_input("Directory: ")
    baddies = open("bad.txt", "w")
    for first_url, DIR in zip(urls, dirs):
        URL = first_url
        count = 0
        while(True):
            old = URL
            URL = download(URL, DIR)
            if URL is None: break
            count += 1
            if count == 20 and URL == old:
                baddies.write("%s\n" % URL)
                break
            elif URL != old:
                count = 0
            sleep(random.random() * 10)
    baddies.close()
main()
#("http://bato.to/read/_/123901/nijiiro-days_v1_ch1_by_chibi-manga", "Nijiiro Days")