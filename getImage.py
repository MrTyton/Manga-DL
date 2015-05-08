import urllib2, urllib
import os
from time import sleep, time
import random
import zipfile
import os
import shutil
from os import listdir
from os.path import isfile, join
from optparse import OptionParser
import rearchive
import repackage
from StringIO import StringIO
import gzip
import socket


dumb = False
checkdir = ""

def download(url, dir, mode):
    global dumb
    global checkdir
    print "Crawling through %s" % url
    req = urllib2.Request(url, headers={"Accept-Encoding": "utf-8, gzip", "Accept-Charset": "utf-8", "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"})
    try:
        response = urllib2.urlopen(req)
    except:
        return url
    if response.getcode() == 200:
        try:
            page = response.read()
        except:
            return url
    else:
        response.close()        
        return main(url)
    if "comic_page" not in page:
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO( page )
            f = gzip.GzipFile(fileobj=buf)
            page = f.read()
            if "comic_page" not in page:
                print "Retrying"
                response.close()
                return url
            
        #encoding = response.headers['content-type'].split('charset=')[-1]
        #print response.headers
        #page = unicode(page, encoding, "ignore")
    response.close()
    startparse = page[page.index("comic_page"):]
    startparse = startparse[startparse.index('src="')+5:]
    image = startparse[:startparse.index('"')]
    
    image_base_url = image[:image.rfind("/img")+4]
    file_number = image.split("/")[-1][3:-4]
    
    startparse = page[page.index('page_select'):]
    startparse = startparse[:startparse.index('</select>')]
    numpages = startparse.count("<option")
    print "There are %d pages in this chapter" % numpages
    startparse = page[page.index('selected="selected"'):]
    directory = "%s/%s" % (dir, startparse[startparse.index('>')+1:startparse.index("<")].replace("/", ""))
    directory = directory.replace(":","").replace("<", "").replace(">", "").replace('"', "").replace("?", "").replace("*","").replace("|", "")
    #while directory[-1] == "." or directory[-1] == " ": directory = directory[:-1]
    directory = directory.strip(" \t.\n\r")
    ensure_dir(directory)
    print "Saving to %s" % directory
    checkdir = directory
    filenames = []
    
    if mode == True:
        starttime = time()
        for i in range(1, numpages+1):
            
            image_number = "%06d" % i #can rewrite this as a generator function
                        
            image = "%s%s.png" % (image_base_url, image_number)
            if os.path.isfile("%s/img%s.png" % (directory, image_number)):
                filenames.append("%s/img%s.png" % (directory, image_number))
                print "Skipping img%s.png because we've already downloaded it" % image_number
                continue
            if os.path.isfile("%s/img%s.jpg" % (directory, image_number)):
                filenames.append("%s/img%s.jpg" % (directory, image_number))
                print "Skipping img%s.jpg because we've already downloaded it" % image_number
                continue
            print "\rDownloading: %s" % image.split("/")[-1],
            try:
                u = urllib2.urlopen(image)
                #print u.info()
                file_name = "img%s.png" % (image_number)
            except:
                try:
                    image = "%s%s.jpg" % (image_base_url, image_number)
                    u = urllib2.urlopen(image)
                   # print u.info()
                    file_name = "img%s.jpg" % (image_number)
                except:
                    try:
                        image = "%s%s.jpeg" % (image_base_url, image_number)
                        u = urllib2.urlopen(image)
                       # print u.info()
                        file_name = "img%s.jpg" % (image_number)
                    except urllib2.HTTPError as e:
                        print "\nRetrying due to: ", e
                        dumb = True
                        return url
                    except Exception as e:
                        print "\nRetrying due to: ", e
                        if i > 4: dumb = False
                        else: dumb = True
                        #dumb = True
                        return url#[:url.rfind("/")] + "/%d" % i
            with open("%s/%s" % (directory, file_name), 'wb') as f:
                
            #meta = u.info()
            #file_size = int(meta.getheaders("Content-Length")[0]) / 1024
            #print "Downloading: %s at %s KiloBytes" % (file_name, file_size)
                try:
                    f.write(u.read())
                except:
                    u.close()
                    f.close()
                    os.remove("%s/%s" % (directory, file_name))
                    return url
                filenames.append("%s/%s" % (directory, file_name))
                u.close()
        print "\rCompleted Downloading after %02f seconds, now Archiving" % (time() - starttime)
    else:
        startparse = page[page.index("comic_page"):]
        startparse = startparse[startparse.index('src="')+5:]
        image = startparse[:startparse.index('"')]
        number = url.split("/")[-1]
        if not number.isdigit(): number = "1"
        number = "img%06d" % int(number)
        file_name = "%s.%s" % (number, image.split('.')[-1])
        if os.path.isfile("%s/%s" % (directory, file_name)):
            print "Skipping %s because we've already downloaded it" % file_name
            if page.count('<a href="http://bato.to/comic') == 5:
                return None
            startparse = page[page[:page.index("comic_page")].rfind('<a href="http://bato.to/read')+9:]
            nextpage = startparse[:startparse.index('"')]
            return nextpage
        try:
            u = urllib2.urlopen(image)
        except:
            print "SOMETHING BROKE"
            return url
        with open("%s/%s" % (directory, file_name), 'wb') as f:
            filenames.append("%s/%s" % (directory, file_name))
            meta = u.info()
            file_size = int(meta.getheaders("Content-Length")[0]) / 1024
            print "Downloading: %s at %s KiloBytes" % (file_name, file_size)
            try:
                f.write(u.read())
            except:
                u.close()
                return url
            u.close()   
        if page.count('<a href="http://bato.to/comic') == 5:
            return None
        startparse = page[page[:page.index("comic_page")].rfind('<a href="http://bato.to/read')+9:]
        nextpage = startparse[:startparse.index('"')]
        return nextpage
    if os.path.isfile("%s.zip" % directory):
        newfile = zipfile.ZipFile("%s-2.zip" % directory, "w")
    else:
        newfile = zipfile.ZipFile("%s.zip" % directory, "w")
    for x in filenames:
        os.rename(x, x.split("/")[-1])
        newfile.write(x.split("/")[-1])
        os.remove(x.split("/")[-1])
    shutil.rmtree(directory)
    newfile.close()
    print "Archiving complete, saved to %s.zip" % directory    
    startparse = page[page.index("chapter_select"):]
    startparse = startparse[:startparse.index('selected="selected"')]
    if startparse.count("option") == 1: return None
    startparse = startparse[:startparse.rfind("<option")]
    nexturl = startparse[startparse.rfind('value="')+7:]
    nexturl = nexturl[:nexturl.index('"')]
    return nexturl


def ensure_dir(f):
    if not os.path.exists(f):
        os.makedirs(f)

def main(urls, dirs):
    global dumb
    global checkdir
    smart = True
    #baddies = open("bad.txt", "a")
    ans = []
    for first_url, DIR in zip(urls, dirs):
        URL = first_url
        oldir = checkdir
        count = 0
        while(True):
            old = URL
            URL = download(URL, DIR, smart)
            #print oldir, checkdir
            if URL is None: break
            count += 1
            if dumb and count == 3:
                smart = False
                if URL[-2] == "/2" or URL[-2] == "/3": URL = URL[:-2]
            if count == 5 and URL == old:
                if not smart:
                    baddies = open("bad.txt", "a")
                    baddies.write("%s\n" % URL)
                    baddies.close()
                    ans.append((URL, DIR))
                    break
                try:
                    temp = int(URL[-1])
                    if temp == 2:
                        URL = URL[:-1] + "3"
                        count = 0
                    else:
                        baddies = open("bad.txt", "a")
                        baddies.write("%s\n" % URL)
                        baddies.close()
                        ans.append((URL[:-2], DIR)) if URL[:-2] == "/3" else ans.append((URL, DIR))
                        break
                except:
                    if URL[-1] == "/":
                        URL = URL + "2"
                    else:
                        URL = URL + "/2"
                    sleep(60)
                    count = 0
                #break
            elif URL != old:
                count = 0
                if oldir != checkdir:
                    oldir = checkdir
                    smart = True
                    dumb = False
            #sleeptime = random.random() * 10 % 1# + 5
            #print "Waiting for %f seconds..." % sleeptime
            #sleep(sleeptime)
            print "----------\n"
        smart = True
        dumb = False
    return ans
    

def runner(urls, locations):
    starttime = time()
    socket.setdefaulttimeout(15)
    things = [(x, y) for x, y in zip(urls, locations)]
    for url, loc in things:
        print "Adding %s to the queue, to be saved in %s" % (url, loc)
    while things != []:
        things = main([x[0] for x in things], [x[1] for x in things])
        baddies = open("bad.txt", "a")
        baddies.write("\n--------------\n\n")
        baddies.close()
        if things != []:
             print "Sleeping for 300 seconds"
             sleep(300)
    [rearchive.rearchive(loc) for loc in locations]
    [repackage.repackage(loc) for loc in locations]
    print "Total running time: %.02f minutes" % ((time() - starttime) / 60.)
         
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-u", "--url", dest="urls", action="append", default=[])
    parser.add_option("-l", "--location", dest="locations", action="append", default=[])
    options, args = parser.parse_args()
    runner(options.urls, options.locations)