#!/usr/bin/python
from PIL import Image
import os
import tempfile
from fnmatch import fnmatch
import subprocess
import sys

# create list of image paths from given directory
def makeImageList(dirname):
    l = filter(lambda x:fnmatch(x,'*.tga'), os.listdir(dirname))
    l.sort()
    return l

def unpackVideo(vidname, starttime = 0, length = 10, scale = None):
    outpath = tempfile.mkdtemp("_unpack")
    print("dir is {0}".format(outpath))
    vidname = os.path.abspath(vidname)
    print("vidpath is {0}".format(vidname))
    command = ["/usr/bin/mplayer", "-nosound", "-ss", str(starttime),
               "-endpos", str(length), vidname, 
               #"-vf", "rotate",
               #"-vf", "format=bgr24", 
               "-fps", "25",
               "-vo", "tga"]
    if scale:
        command = command + ["-vf", "scale={0}:{1}".format(scale[0],scale[1])]
    print command
    subprocess.call(command, cwd=outpath)
    return outpath

inpath = unpackVideo(sys.argv[1],0,200)
list = makeImageList(inpath)
outpath = tempfile.mkdtemp("_repack")

frameskew = 48
outcount = len(list)-frameskew

first = Image.open(os.path.join(inpath,'00000001.tga'))
size = first.size

print "Size is {0}".format(size)

for idx in range(outcount):
    fidx,lidx = idx,idx+frameskew
    im = Image.new("RGB",size)
    for i in range(frameskew):
        xstart = (i * size[0])/frameskew
        xend = ((i+1) * size[0])/frameskew
        frame = Image.open(os.path.join(inpath,list[idx+i]))
        im.paste(frame.crop((xstart,0,xend,size[1])),(xstart,0))
    im.save(os.path.join(outpath,"{0:08}.tga".format(idx+1)))

# build video
buildcmd = ["mencoder", "mf://*.tga", 
            "-mf", "w={0}:h={1}:fps=25:type=tga".format(size[0],size[1]),
            "-ovc", "lavc", "-lavcopts", "vcodec=mpeg4:mbd=2:trell",
            "-oac", "copy", "-o", os.path.abspath("output.avi")]
subprocess.call(buildcmd, cwd=outpath)

#clean up
cleancmd = ["rm", "-rf", outpath, inpath]
subprocess.call(cleancmd)
