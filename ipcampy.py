# Big thanks to the below link which had all the core code needed
# https://stackoverflow.com/questions/49978705/access-ip-camera-in-python-opencv#49979186

import logging
import config
from flask import Flask, request, send_file, render_template, abort, redirect, flash, Response
from datetime import datetime, timedelta
import sys, os
import time
import re

from werkzeug.utils import secure_filename
import PIL

import camCapture

from bp_login.login import login_bp

############################ BEFORE ANYTHING ELSE #################################
#logging to file AND console
logging.basicConfig(filename=config.myconfig["logfile"], level=config.myconfig.get("log level", logging.INFO), format=config.myconfig.get("log format", '%(asctime)s - %(levelname)s - %(message)s'))

console = logging.StreamHandler()
console.setLevel(config.myconfig.get("log level", logging.INFO))
formatter = logging.Formatter(config.myconfig.get("log format", '%(asctime)s - %(levelname)s - %(message)s'))
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

logging.info("Starting app..")

############################ CONSTANTS #################################
TIMELAPSE_IMG_PER_SEC = 3.0
REGEX_STILLS_NAME = """([^_]+)_(?P<date>[^_]+)_(?P<time>[^_]+)\.jpg$"""

############################ FLASK VARS & GLOBALS #################################
app = Flask(__name__, static_url_path='')
#needed for flash(), you need session, so you need to encrypt stuffs
app.secret_key = config.myconfig["secret_key"]

reStills = re.compile(REGEX_STILLS_NAME, re.IGNORECASE)


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'ico'])



##########################################################################################
################################## Web requests ##########################################
##########################################################################################

##########################################################################################
#Login page
app.register_blueprint(login_bp)

##########################################################################################
#Default home page with list of cameras and low res capture
@app.route('/')
@app.route('/home')
def homepage():
    return render_template("main01.html", pagename="Home", cameras=config.myconfig["cameras"], conf=config.myconfig)


##########################################################################################
#Zooms to ONE camera (show in high res)
@app.route('/zoom/<nickname>')
def zoomPage(nickname):

    if nickname not in [x.nickname for x in config.myconfig["cameras"]]:
        flash(f"Error: unknown camera '{nickname}'")
        return redirect("/")

    cam = [x for x in config.myconfig["cameras"] if x.nickname == nickname][0]

    return render_template("zoom01.html", pagename=f"Zoom on [{cam.nickname}]", cam=cam, conf=config.myconfig)

    

##########################################################################################
#Callback to generate a capture on the fly
@app.route('/<nickname>/capture.jpg')
def captureImage(nickname):


    if nickname not in [x.nickname for x in config.myconfig["cameras"]]:
        app.logger.error(f"Unknown camera '{nickname}'")
        abort(500)  
        return

    cam = [x for x in config.myconfig["cameras"] if x.nickname == nickname][0]

    highRes = True if "highRes" in request.args and request.args["highRes"] == "true" else False

    io_buf, _ = camCapture.captureStill(cam, highRes=highRes)

    if io_buf == None:
        #something wrong happened
        abort(501)
    else:
        #put back at start (in case it wasn't already)
        io_buf.seek(0)

        #return the in memory image
        return send_file(io_buf, mimetype='image/jpeg')        


##########################################################################################
#Callback to save an image on the disk
@app.route('/save/<nickname>')
def saveImage(nickname):


    if nickname not in [x.nickname for x in config.myconfig["cameras"]]:
        app.logger.error(f"Unknown camera '{nickname}'")
        abort(500)  
        return

    cam = [x for x in config.myconfig["cameras"] if x.nickname == nickname][0]

    highRes = True

    io_buf, _ = camCapture.captureStill(cam, highRes=highRes)

    if io_buf == None:
        flash(f"Error save shot of '{nickname}'")
        return redirect("/")
    else:
        #put back at start (in case it wasn't already)
        io_buf.seek(0)
        img = PIL.Image.open(io_buf)
        #make sure it is saved in the subfolder of current file
        dir_path = os.path.dirname(os.path.realpath(__file__))
        thumbnail = os.path.join(dir_path, "static", "stills", secure_filename(nickname).lower() + f"_{datetime.now():%Y%m%d_%H%M%S}.jpg")
        img.save(thumbnail, format="jpeg", quality=90)
        flash(f"Saved shot for '{nickname}' successful.", "success")
        return redirect("/")


        
##########################################################################################
#TIMELAPSE: pseudo video Motion JPEG style

#returns the list of stills present for that camera. Assumes name was sanitized.
def stillsListForCamera(nickname:str):
    #list of stills for that camera
    path= os.path.join("static", "stills")
    l = [l for l in os.listdir(path) if 
         os.path.isfile(os.path.join(path, l)) 
         and l.lower().endswith('.jpg') 
         and l.lower().startswith(nickname.lower()) 
         ]
    
    #sorted ignorecase
    l = sorted(l, key=lambda x: str(x).lower())
    return l

#returns the next still taken for that camera 
def getNextStill (nickname:str):
    #just to be safe (CompTIA Security+)
    nickname = secure_filename(nickname)

    #list of stills for that camera
    l = stillsListForCamera(nickname)

    if len(l) == 0:
        abort(404)


    path= os.path.join("static", "stills")
    for f in l:
        frame = open(os.path.join(path,f), 'rb').read()
        #here is where the framerate is enforced
        time.sleep(1.0/TIMELAPSE_IMG_PER_SEC)
        #notice the yield
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        

@app.route("/still/<nickname>")
def timelapseImage(nickname:str):
    #https://blog.miguelgrinberg.com/post/video-streaming-with-flask

    r = Response(getNextStill(nickname=nickname),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    #doesn't look very efficient but in case ...
    r.headers.set("X-Framerate", str(int(TIMELAPSE_IMG_PER_SEC)))
    return r


@app.route('/timelapse/<nickname>')
def timelapsePage(nickname):
    
    cam = [x for x in config.myconfig["cameras"] if x.nickname == nickname][0]

    return render_template("timelapse.html", cam=cam)


##########################################################################################
#FILMSTRIP navigate through the pictures

#Expects timeTag in format "xx:yy"
def getStillAtTime(nickname:str, timeTag:str, deltaMin:int = 0):
    #list of stills for that camera
    l = stillsListForCamera(nickname)

    if len(l) == 0:
        return None, timeTag
    
    d = datetime.strptime(timeTag, "%H:%M")
    d = d + timedelta(minutes=deltaMin)
    t = d.strftime("%H%M")

    for fname in l:
        m = reStills.search(fname)
        if not m:
            #no match ?? Shouldn't happen
            continue
        if m.group("time").startswith(t):
            #found it!
            return fname, d.strftime("%H:%M")
    
    #if we're here, we asked for an image which doesn't exist
    return None, timeTag
            

#The Filmstrip page for a given camera
@app.route('/strip/<nickname>', methods=['GET','POST'])
def stripPage(nickname):
    if nickname == None or nickname == "None":
        #apparently this happens .. didn't figure why but nothing good will come of it
        abort(401)

    #just to be safe (CompTIA Security+)
    app.logger.info(f"Strip of '{nickname}' (secured to '{secure_filename(nickname)}') ")
    nickname = secure_filename(nickname)

    cam = [x for x in config.myconfig["cameras"] if x.nickname == nickname][0]

    imgURL = None
    currentTime = ""

    #POST BACK POST BACK POST BACK
    if request.method == 'POST':
        #Read current time if present
        if request.form["currentTime"] != "":
            currentTime = request.form["currentTime"]
        
        delta = 0

        if request.form["action"] == "goto" and request.form["time"] != "" :
            # GOTO TIME
            flash(f"Goto time {request.form['time']}")

            f, t = getStillAtTime(nickname=nickname, timeTag=request.form["time"])

            if f:
                imgURL = "/stills/" + f
                currentTime = t
            else:
                flash(f"Couldn't find still for {nickname} at {request.form['time']} (with delta {delta} min)", "error")
        elif request.form["action"].startswith("minus"):
            #GO BACK IN TIME
            delta = -int(request.form["action"].replace("minus-", ""))
            f, t = getStillAtTime(nickname=nickname, timeTag=currentTime, deltaMin=delta)

            if f:
                imgURL = "/stills/" + f
                currentTime = t
            else:
                flash(f"Couldn't find still for {nickname} at {currentTime} (with delta {delta} min)", "error")
        elif request.form["action"].startswith("plus"):
            #GO FORWARD IN TIME
            delta = int(request.form["action"].replace("plus-", ""))
            f, t = getStillAtTime(nickname=nickname, timeTag=currentTime, deltaMin=delta)

            if f:
                imgURL = "/stills/" + f
                currentTime = t
            else:
                flash(f"Couldn't find still for {nickname} at {currentTime} (with delta {delta} min)", "error")
        else:
            flash("Unknown or TODO implement", "error")            
    else:
        #Get so first view
        flash(f"Show latest still for '{nickname}'")

        #list of stills for that camera
        l = stillsListForCamera(nickname)

        if len(l) > 0 :
            imgURL = "/stills/" + l[-1]
            m = reStills.search(l[-1])
            if not m:
                flash("ERROR latest image doesn't follow expected filename pattern", "error")
                app.logger.error(f"Strip latest filename was '{l[-1]}'")
            else:
                currentTime = m.group("time")[:2] + ":" + m.group("time")[2:4]
                app.logger.debug(f"Latest timetag is {currentTime} from file {l[-1]}")

        else:
            flash(f"No still available for camera '{nickname}'", "error")

    return render_template("filmstrip.html", cam=cam, imgURL=imgURL, currentTime=currentTime)



########################################################################################
## Main entry point
#
if __name__ == '__main__':
    print ("""
USAGE:
    python3 ipcampy.py [path_to_cert.pem path_to_key.pem]

If you don't provide the *.pem files it will start as an HTTP app. You need to pass both .pem files to run as HTTPS.
    """)
    try:
        #start web interface
        app.debug = not config.myconfig["isProd"]
        
        #run as HTTPS?
        if len(sys.argv) == 3:
            #go HTTPS
            app.logger.info("Start as HTTPS")
            app.run(host='0.0.0.0', port=int(config.myconfig["app_port"]), threaded=True, ssl_context=(sys.argv[1], sys.argv[2]))
        else:
            #not secured HTTP
            app.logger.info("Start as HTTP unsecured")
            app.run(host='0.0.0.0', port=int(config.myconfig["app_port"]), threaded=True)

    except Exception as e:
        app.logger.error(f"{e}")
        app.logger.error("Exiting ...")
        sys.exit(1)