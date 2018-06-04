import subprocess as sp
import os
import platform

def video2jpeg(cmd_string):

    if(platform.system() == 'Linux'):
        FFMPEG_BIN = '/usr/bin/ffmpeg'
    elif(platform.system() == 'Darwin'):
        FFMPEG_BIN = '/Applications/??'
    else:
        FFMPEG_BIN = 'ffmpeg.exe'

    command =  'FFMPEG_BIN -ss 2 -i video -r 1 -vf crop=1525:1045:175:0 /tmp/video%d.jpeg' 

    print command

    return

