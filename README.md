# roav2geojpeg
# Anker Roav Dashcam C1 Pro

Convert dashcam mp4 videos to geotagged images for importing into Mapillary and OpenStreetCam.

### Current features:

* exclude images from user define distance from home location
* drop duplicate images using geotagged distance
* crop portion of video to remove extraneous portions of the video such as the vehicle's hood.

roav2geojpeg uses python libraries for ffmpeg and ffprobe

This software is in an alpha stage of development. It kind of works for me, but can throw errors.
Not all command line arguments are working. There are limited presets that can be set in a configure file.

Upload of images to either service has yet to be tested.

#### Future improvements (don't want to call them enhancements just yet)

* use python modules to grab frames from video
* use python pyexiv2 module to add exif geotags to jpegs
