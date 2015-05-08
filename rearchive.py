import os
from os import listdir
from os.path import isfile, join
import zipfile
import shutil

def rearchive(worker):
    worker = "./%s" % worker
    dirs = [x[0] for x in os.walk(worker) if x[0] != "." and x[0] != worker]
    print dirs
    print "Starting\n"
    for i,directory in enumerate(dirs):
        print "\rWorking on %d out of %d..." % (i+1, len(dirs))
        #print directory
        files = [ f for f in listdir(directory) if isfile(join(directory,f)) ]
        #print files
        newzip = zipfile.ZipFile("%s.zip" % directory, "w")
        for i,current in enumerate(files):
            os.rename("%s/%s" % (directory, current), "%06d.%s" % (i+1, current[-3:]))
            current = "%06d.%s" % (i+1, current[-3:])
            newzip.write(current)
            os.remove(current)
        newzip.close()
        shutil.rmtree(directory)