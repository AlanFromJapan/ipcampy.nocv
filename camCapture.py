import config
from datetime import datetime, timedelta
import sys
import time
import os
import traceback

from io import BytesIO, StringIO
from sharedObjects import IpCamera

import av
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

#fonts
font_label = ImageFont.truetype(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), config.myconfig["path 2 fonts"]), '8bitOperatorPlusSC-Regular.ttf'), 16)

##############################################################################3
# Capture 1 still frame from the camera and decorates
# 
def captureStill (cam: IpCamera):
    tstart = time.time()

    try:
        io_buf = BytesIO()

        # shamelessly taken from RTSPBrute software source (thanks for sharing <3)
        # https://gitlab.com/woolf/RTSPbrute/-/blob/master/rtspbrute/modules/attack.py
        with av.open(
            cam.url(),
            options={
                "rtsp_transport": "tcp",
                "rtsp_flags": "prefer_tcp",
                "stimeout": "3000000",
            },
            timeout=60.0,
        ) as container:
            stream = container.streams.video[0]
            stream.thread_type = "AUTO"
            for frame in container.decode(video=0):
                frame.to_image().save(io_buf, format="jpeg")
                break
        
        #put back at start in case
        io_buf.seek(0)

        if config.myconfig["detailedLogs"]:
            print(f"DBG: acquisition of {cam.nickname} in {(time.time() - tstart):0.2f}s" )

        #add time
        img = Image.open(io_buf)
        draw = ImageDraw.Draw(img)

        #if label not disabled for that cam
        if cam.overlay_label != "":
            label = cam.overlay_label.format(datetime.now(), cam.nickname, cam.ip, cam.port)
            w,h = draw.textsize(label, font_label)
            x,y= 1, img.height            
            draw.rectangle((x, y, x + w, y - h), fill=(192, 192, 192), outline=(255, 255, 255))
            draw.text((x,y - h), text=label, fill=(30,30,30), font=font_label)

        #put back at start (needed here!)
        io_buf.seek(0)
        img.save(io_buf, format="jpeg", quality=90)


        #put back at start (needed here!)
        io_buf.seek(0)

        #return the in memory image
        return io_buf, (time.time() - tstart)
    except Exception as ex:
        print(f"ERROR getting data for {cam.nickname} : {ex}")
        traceback.print_exc(limit=5, file=sys.stdout)

        return None, (time.time() - tstart)
