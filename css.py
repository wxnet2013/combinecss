#!/usr/bin/env python
#coding:utf-8

import os,re,time,random,subprocess,codecs,sys,shutil
sys.path.append("bin")
import util

def jslog(msg):
  LogFile = open("log.txt","a")
  LogFile.write(str("\r\n" + msg))
  LogFile.close()

def getCode(p):
    try:
        f = file(p,"r")
        code = f.read();
        f.close()
        #utf8编码文件可能存在bom信息，需要剔除否则会导致样式文件失效
        if code[:3] == codecs.BOM_UTF8:
            return code[3:]
        else:
            return code
    except IOError, (errno, strerror):
        return "file not found"
        

def isPath(p):
    return p[0:3] == "../"

def getPath(p):
    if isPath(p):
        return p[3:]

def isCSS(p):
    return p[-3:] == "css"

def isFile(p):
    return p.find("/") == -1

def ClearFiles(dir):
    for root,dirs,files in os.walk(dir):
        for f in files:
            os.remove(root + '/' + f)

    for d in os.listdir(dir):
        shutil.rmtree(dir + '/' + d)

def Compile(compiler_jar_path, source_paths):
  args = ['java', '-jar', compiler_jar_path]
  for a in source_paths:
      args.append(a)

  proc = subprocess.Popen(args, stdin = subprocess.PIPE, 
                                         stdout = subprocess.PIPE, 
                                         stderr = subprocess.PIPE, 
                                         shell = True)
  stdoutdata,unused_stderrdata = proc.communicate()
  jslog(source_paths[2] + "-------------------------------------------");
  jslog(unused_stderrdata)


re_import = re.compile(r'\s*@import\s*url\((?:\"|\')(?P<path>.*?)(?:\"|\')\)(?:\;)?',re.M)
re_relative_image = re.compile(r'\.\.\/\.\.\/images',re.M)

image_base = "http://www.qiyipic.com/common/fix"

TempCode = {}

#不包含import的文件以及包含import文件的代码key。
CodeList = []

def makelist(p):
    if not p[0:4] == "code":
        p = "code/" + p
    code = getCode(p)
    if code == "file not found":
        ok = raw_input(p + " 不存在")
        
    filelist = re_import.findall(code)
    if len(filelist) == 0:
        #print "empty"
        return CodeList.insert(0,p)
    else:
        #print filelist
        flag = str(random.random())
        TempCode[flag] = re_import.sub("",code)
        CodeList.insert(0,flag)
        filelist.reverse()
        for f in filelist:
            if isFile(f):
                f = "../" + os.path.split(p)[0] + "/" + f
            makelist(getPath(f))

CommonList = []
def combine(f):
    global CodeList,TempCode,CommonList
    if isCSS(f):
        #print "\n====================\ncss/" + f + "\n===================="
        print f + "------ok"
        makelist("code/assets/" + f)

        cssfile = open("combine/" + f,"w")

 
        #文件列表排重
        ListTemp  = []
        [ListTemp.append(i) for i in CodeList if not i in ListTemp]

        #print CodeList
        #print ListTemp
        codetemp = []
        if f == "global.css":
            CommonList = ListTemp;
        else:
            for item in ListTemp*1:
                if item in CommonList:
                    ListTemp.remove(item)
                    
        for css in ListTemp:
            if isCSS(css):
                codetemp.append(getCode(css))
                #cssfile.write(getCode(f))
                #print getCode(f)
            else:
                codetemp.append(TempCode[css])
                #cssfile.write(TempCode[f])
                #print TempCode[f]

        print codetemp
        cssfile.write(re_relative_image.sub(image_base,"\r\n".join(codetemp)))
        temp = []
        TempCode = {}
        CodeList = []
        cssfile.close()
        if os.name == "nt":
            #java -jar yuicompressor.jar -o commonmin.css common.css
            print "combine/"  + f.lower()
            Compile("bin/yuicompressor-2.4.7.jar",['-o','compressed/' + f.lower(), "combine/"  + f.lower()])
            #Compile("closure-stylesheets-20111230.jar",['--allow-unrecognized-properties','--output-file','compressed/qitan3/' + f.lower(), "combine/"  + f.lower()])
        else:
            os.popen("java -jar yuicompressor-2.4.7.jar" + " -o qitan3/" + f.lower() + " combine/"  + f.lower())
            #os.popen("java -jar closure-stylesheets-20111230.jar" + " --output-file qitan3/" + f.lower() + " combine/"  + f.lower())


##bootstrap
#清空目录
ClearFiles("combine")
ClearFiles("compressed")

if(os.path.exists("upload.zip")):
    os.remove("upload.zip")
if(not os.path.exists("compressed")):
    os.makedirs("compressed")
if(os.path.exists("log.txt")):
    os.remove("log.txt")

#unix平台直接更新svn
if not os.name == "nt":
    f = os.popen("svn update code")
    print f.read()


CssList = os.listdir("code/assets")
combine("global.css")
CssList.remove("global.css")
#合并CSS文件
for f in  CssList:
  combine(f)



if not os.name == "nt":
  for f in os.listdir("qitan3"):
    print "copy" + f
    shutil.copy("qitan3/"  + f, "compressed/qitan3/" + f)

util.MakeZip("compressed")
os.rename("compressed.zip","upload.zip")
 
print "\r\n----compress success----"


'''
isOnline = raw_input("need isOnline ?:")
if isOnline == "y":
  print "uploading..."
  if os.name == "nt":
    proc = subprocess.Popen(['node','upload.js'], stdin = subprocess.PIPE, 
                                         stdout = subprocess.PIPE, 
                                         stderr = subprocess.PIPE, 
                                         shell = True)
    proc.wait()
    stdoutdata,unused_stderrdata = proc.communicate()
    print "upload" + stdoutdata
  else:
     rst = os.popen("node upload.js")
     print rst.read()
  #print unused_stderrdata
'''
raw_input("")
        
