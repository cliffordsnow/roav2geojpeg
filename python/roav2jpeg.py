from os.path import  expanduser
from pathlib import Path
from datetime import datetime
from datetime import timedelta
import datetime as dt
from time import mktime
import time
import csv
import sys
import os
import pyproj
from lib.ffprobe import FFProbe
import argparse
import ConfigParser
##import lib.exif_write


def get_gps_info(info_file):
    with open(info_file) as csvfile:
        gps = csv.reader(csvfile, delimiter=',')
        rownum = 0
        for row in gps:
            if(rownum == 0):
                lat1 = row[1]
                lon1 = row[2]
                rt = time.strptime(row[0],ROAV_TIME_FORMAT)
                start= rt
            else:
                end = time.strptime(row[0],ROAV_TIME_FORMAT)

            rownum = rownum + 1


    csvfile.close()
    return start,end

def get_gps_dur(s,e):
    return (timestamp(e) - timestamp(s))

def get_seconds(t):
    return t.total_seconds()


def get_video_duration(video_file):
    """Get video duration in seconds"""
    return float(FFProbe(video_file).video[0].duration)

def get_video_start_time(video_file):
    """Get video start time in seconds"""
    try:
        time_string = FFProbe(video_file).video[0].creation_time
        try:
            creation_time = time.strptime(time_string, TIME_FORMAT)
        except:
            return None
    except:
        return None
    return creation_time


def distance(lt,ln,lt2,ln2):
    geod = pyproj.Geod(ellps='WGS84')
    angle1, angle2, distance = geod.inv(ln2,lt2,ln,lt)
    return distance

def timestamp(t):
    return datetime.fromtimestamp(mktime(t))

def get_args():
    parser = argparse.ArgumentParser(description="Extract and geotag images from Roav Dashcam C1 Pro")
    parser.add_argument('-i','--input', required=True, help='mp4 video file to process')
#    parser.add_argument('-o','--outpath',required=True, help='path to store geotagged images')
    parser.add_argument('--tmp', required=False, default='/tmp',help='temporary path to store jpeg images')
    parser.add_argument('--sample-rate', default=1,help='Interval in seconds for video sample. default is 1 second')
    parser.add_argument('--time_offset', 
                        help='Time offset between video and gpx file in seconds (e.g. "3" means that video is ahead of GPX time by 3 seconds; negative offset is also possible)', 
                        default=0, type=float)
    parser.add_argument('--home-lat', help='Home Latitude in decimal degrees.', type=float)
    parser.add_argument('--home-lon', help='Home Longitude in decimal degrees.', type=float)
    parser.add_argument('--crop', help="crop dashcam jpeg")
    args = parser.parse_args()

    return args

def basename(video_file):
    basename, extension = os.path.splitext(video_file)
    return basename

if __name__ == '__main__':
#    Getting defaults out of the way. 

    ZERO_PADDING = 3
    TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.000000Z"
    ROAV_TIME_FORMAT = "%Y%m%d_%H:%M:%S.000"
    HOME = expanduser("~")
    video_crop = ''
    home_tmp = '/tmp'
    sample_interval = 1
    crop = None
    v = 'ffmpeg -i {} -loglevel quiet -ss {} -vf "fps=1/{} '
    

    config = ConfigParser.ConfigParser(allow_no_value=True)
    config.read(HOME+'/.config/roav/config')

    if config.has_option('HOME','lat'):
        home_lat = config.get('HOME','lat')
    if config.has_option('HOME','lon'):
        home_lon =  config.get('HOME','lon')
    if config.has_option('HOME','buffer'):
        home_buffer = int(config.get('HOME','buffer'))

    args = get_args()
    video_file = args.input
    info_file = basename(video_file) + '.info'

    if args.sample_rate:
        s_rate = args.sample_rate
    elif config.has_option('video','sample_rate'):
        s_rate = config.get('video','sample_rate')
    if args.crop:
        crop = args.crop
    elif config.has_option('video','crop'):
        crop = config.get('video','crop')

    if crop:
        v += ",crop=" + crop

    


    if args.tmp:
        home_tmp = args.tmp
    elif config.has_option('HOME','tmp'):
        home_tmp =  config.get('HOME','tmp')

    if not os.path.exists(home_tmp):
        os.mkdir(home_tmp)

    tmp = home_tmp + '/' + basename(video_file)
    if not os.path.isdir(tmp):
        os.mkdir(tmp)
    
    v +=  '" {}/{}%0{}d.jpeg'


#    Print out some interesting information about the video and gps files

    gps_info = get_gps_info(info_file)
    st = get_video_start_time(video_file)
    gps_time = timestamp(gps_info[0])
    gps_dur = get_seconds(get_gps_dur(gps_info[0] ,gps_info[1]))
    video_dur = get_video_duration(video_file)
    video_start = timestamp(st) - dt.timedelta(seconds=int(round(video_dur,0)))
    start_delay = timestamp(gps_info[0]) - video_start
    print "Video and GPS stats"
    # comparing video to gps information
    print "video start: ", timestamp(st) - dt.timedelta(seconds=int(round(video_dur,0)))
    print "gps start:   ", gps_time
    print "video end:   ", timestamp(st)
    print "gps end:     ", timestamp(gps_info[1])
    print "video duration: ", get_video_duration(video_file)
    print "gps duration:   ", gps_dur
    
    print "Processing video to individual jpeg frames"
    s = v.format(video_file,start_delay, s_rate, tmp, basename(video_file), ZERO_PADDING)
#   print s
    os.system(s)
    print "Processing Complete"
    print "Start geotagging images"
    
    # add exif data to images.
    
    with open(info_file,'r') as gps_info:
        gps = csv.reader(gps_info, delimiter=',')
        rownum = 1
        for row in gps:
            rt = timestamp(time.strptime(row[0],ROAV_TIME_FORMAT))
            lat1 = row[1]
            lon1 = row[2]
            ele = row[5]
            heading = row[7]
            jpeg = '{}/{}{:03d}.jpeg'.format(tmp,basename(video_file),rownum)
            exif_cmd = '/usr/bin/exiftool -quiet -overwrite_original \
                    -exif:CreateDate="{}" -exif:GPSLatitudeRef="N" -exif:GPSLatitude={} \
                    -exif:GPSLongitudeRef="W" -exif:GPSLongitude={} \
                    -exif:GPSAltitudeRef="Above Sea Level" -exif:GPSAltitude={} \
                    -exif:GPSDestBearing={} '.format(rt,lat1,lon1,ele, heading)
            exif_cmd += jpeg
            if(rownum == 1):
                if distance(lat1, lon1, home_lat, home_lon) > home_buffer:
                    os.system(exif_cmd)
                else:
                    os.system.remove(jpeg)
            else:
                if distance(lat1, lon1, home_lat, home_lon) > home_buffer and distance(lat, lon, lat1, lon1) > 0:
                    os.system(exif_cmd)
                else:
                    os.system.remove(jpeg)
            lat = lat1
            lon = lon1
            rownum += 1

    print "geotagging complete"

                


'''
    This section geotags the images from the video capture with
    the gps info from the info_file

    with open(info_file, 'r') as csvfile:
        gps = csv.reader(csvfile, delimiter=',')
        rownum = 0
'''
