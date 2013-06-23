#encoding=utf-8
import distutils.version,logging,re,subprocess,os,shutil,hashlib,time,zipfile,os
from os.path import isdir, isfile, join, dirname, realpath

#生成文件的 MD5
def GetFileMd5(filename):
    if not os.path.isfile(filename):
        return
    myhash = hashlib.md5()
    f = file(filename,'rb')
    while True:
        b = f.read(8096)
        if not b :
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()

def RunProc(args):
    proc = subprocess.Popen(args, stdin = subprocess.PIPE, 
                              stdout = subprocess.PIPE, 
                              stderr = subprocess.PIPE, 
                              shell = True)

    unused_stderrdata = proc.communicate()
    proc.wait()
    return unused_stderrdata

def ClearSvn(dir):
        ds = [join(dir, i) for i in os.listdir(dir) if isdir(join(dir, i))]
        fs = [join(dir, i) for i in os.listdir(dir) if isfile(join(dir, i))]
        for d in ds:
                ClearSvn(d)
                if '\.svn' in d:
                        #print d
                        os.rmdir(d)
        for f in fs:
                if '\.svn' in f:
                        #print f
                        os.chmod(f, 33206)
                        os.remove(f)



def ClearFiles(dir):
    for root,dirs,files in os.walk(dir):
        for f in files:
            os.remove(root + '/' + f)

    for d in os.listdir(dir):
        shutil.rmtree(dir + '/' + d)

def CopyFolderOs(sFolder,tFolder):
    sourcePath = sFolder
    destPath = tFolder
    for root, dirs, files in os.walk(sourcePath):

        #figure out where we're going
        dest = destPath + root.replace(sourcePath, '')

        #if we're in a directory that doesn't exist in the destination folder
        #then create a new folder
        if not os.path.isdir(dest):
            os.mkdir(dest)
            #print 'Directory created at: ' + dest

        #loop through all files in the directory
        for f in files:

            #compute current (old) & new file locations
            oldLoc = root + '\\' + f
            newLoc = dest + '\\' + f

            if not os.path.isfile(newLoc):
                try:
                    shutil.copy2(oldLoc, newLoc)
                    print 'File ' + f + ' copied.'
                except IOError:
                    print 'file "' + f + '" already exists'

def MakeZip(filename):   
    z = zipfile.ZipFile(filename + ".zip","w")
    for dirpath,dirs,files in os.walk(filename):
        if(dirpath == filename):
            for fname in files:
                z.write(dirpath + "/" + fname,fname)
        else:
            for fname in files:
                if os.name == "nt":
                    z.write(dirpath + "/" + fname,dirpath[dirpath.find("\\") + 1:len(dirpath)] + "/" + fname)
                else:
                    z.write(dirpath + "/" + fname,dirpath[dirpath.find("/") + 1:len(dirpath)] + "/" + fname) 
                
    z.close()


if __name__ == "__main__":
    CopyFolderOs("../compressed","../online")
    CopyFolderOs("../compressed/qitan/jobs/","../compressed/qitan/testtest/jobs")
    shutil.copyfile("../compressed/qitan/common.js", "../compressed/qitan/testtest/common.js")
      


    



    



