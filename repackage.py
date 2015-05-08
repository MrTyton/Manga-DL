from os import listdir
from os.path import isfile, join
import zipfile
import os
import shutil
from . import rename
from itertools import groupby
import natsort

def repackage(folder):
    data = [ f for f in listdir(folder) if isfile(join(folder,f)) ]
    groups = {}
    keyfunc = lambda x : x.split(" ")[0]
    data = sorted(data, key=keyfunc)
    for k, g in groupby(data, keyfunc):
        groups[k] = natsort.natsorted(list(g), key = lambda x : x.replace("Vol.", "Vol ").replace("Ch.", "Ch ").replace(".zip", " .zip"))
    for key in groups:
        files = groups[key]
        print key, files
        insertion_files = []
        for file in files:
            zippy = zipfile.ZipFile("%s/%s" % (folder, file), "r")
            os.mkdir("./%s" % file)
            zippy.extractall("./%s" % file)
            insertion_files.append(["./%s/%s" % (file, f) for f in listdir("./%s" % file) if isfile(join("./%s" % file, f))])
            zippy.close()
        insertion_files = [x for y in insertion_files for x in y]
        newZip = zipfile.ZipFile("./%s/%s %s.zip" % (folder, folder, key.replace("Vol.", "Volume ").replace("Ch.", "Chapter ").replace("v2", "").replace(".zip", "")), "w")
        for file in insertion_files:
            newZip.write(file)
        newZip.close()
        for file in files:
            shutil.rmtree("./%s" % file)
            os.remove("./%s/%s" % (folder, file))
    rename.main(folder)