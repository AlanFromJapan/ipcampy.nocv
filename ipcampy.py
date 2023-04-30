# Big thanks to the below link which had all the core code needed
# https://stackoverflow.com/questions/49978705/access-ip-camera-in-python-opencv#49979186

import config
from flask import Flask, request, send_file, render_template, abort, redirect, make_response, flash, Response
from datetime import datetime, timedelta
import sys, os
import time
import re

from werkzeug.utils import secure_filename
from io import BytesIO, StringIO
from sharedObjects import IpCamera

import camCapture


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
#Default home page with list of cameras and low res capture
@app.route('/')
def homepage():
    #not logged in? go away
    if None == request.cookies.get('username'):
        return redirect("/login")
    return render_template("main01.html", pagename="Home", cameras=config.myconfig["cameras"], conf=config.myconfig)


##########################################################################################
#Zooms to ONE camera (show in high res)
@app.route('/zoom/<nickname>')
def zoomPage(nickname):
    #not logged in? go away
    if None == request.cookies.get('username'):
        return redirect("/login")

    if not nickname in [x.nickname for x in config.myconfig["cameras"]]:
        flash(f"Error: unknown camera '{nickname}'")
        return redirect("/")

    cam = [x for x in config.myconfig["cameras"] if x.nickname == nickname][0]

    return render_template("zoom01.html", pagename=f"Zoom on [{cam.nickname}]", cam=cam, conf=config.myconfig)

    

##########################################################################################
#Callback to generate a capture on the fly
@app.route('/<nickname>/capture.jpg')
def captureImage(nickname):

    #not logged in? go away
    if None == request.cookies.get('username'):
        abort(500)  
        return

    if not nickname in [x.nickname for x in config.myconfig["cameras"]]:
        print(f"Error: unknown camera '{nickname}'")
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
#TIMELAPSE: pseudo video Motion JPEG style

#returns the list of stills present for that camera. Assumes name was sanitized.
def stillsListForCamera(nickname:str):
    #list of stills for that camera
    path= os.path.join("static", "stills")
    l = [l for l in os.listdir(path) if 
         os.path.isfile(os.path.join(path, l)) 
         and l.lower()[-4:] == '.jpg' 
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
@app.route('/strip/<nickname>', methods=['GET','POST'])
def stripPage(nickname):
    #just to be safe (CompTIA Security+)
    print(f"Strip of '{nickname}' (secured to '{secure_filename(nickname)}') ")
    nickname = secure_filename(nickname)

    cam = [x for x in config.myconfig["cameras"] if x.nickname == nickname][0]

    imgURL = None
    currentTime = ""

    #POST BACK POST BACK POST BACK
    if request.method == 'POST':
        #Read current time if present
        if request.form["currentTime"] != "":
            currentTime = request.form["currentTime"]

        # Goto
        if request.form["action"] == "goto" and request.form["time"] != "" :
            flash(f"Goto time " + request.form["time"])

            #list of stills for that camera
            l = stillsListForCamera(nickname)

            if len(l) == 0:
                abort(404)
            t = request.form["time"].replace(":", "")
            f = None
            for fname in l:
                m = reStills.search(fname)
                if not m:
                    #no match ?? Shouldn't happen
                    continue
                if m.group("time").startswith(t):
                    #found it!
                    f = fname
                    break
            print(f"DBG Strip GOTO '{f}'")
            if f:
                imgURL = "/stills/" + f
                currentTime = t

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
                    print(f"ERR: Strip latest filename was '{l[-1]}'")
                else:
                    currentTime = m.group("time")[:2] + ":" + m.group("time")[2:4]
                    print(f"DBG: latest timetag is {currentTime} from file {l[-1]}")

            else:
                flash(f"No still available for camera '{nickname}'", "error")

    return render_template("filmstrip.html", cam=cam, imgURL=imgURL, currentTime=currentTime)


##########################################################################################
#Login page
@app.route('/login', methods=['POST', 'GET'])
def doLogin():

    if config.myconfig["detailedLogs"]:
        print(f"Login page shown by request of {request.remote_addr}")
        
    if request.method == "GET":
        return render_template("login01.html", pagename="login", message="")
    else:
        vLogin = request.form["login"]
        vPwd = request.form["pwd"]
        
        if vLogin == config.myconfig["app_login"] and vPwd == config.myconfig["app_password"]:
            #Login is correct
            if config.myconfig["detailedLogs"]:
                print(f"Login attempt SUCCESS of {request.remote_addr} !")

            resp = make_response( redirect("/") )
            
            resp.set_cookie ('username', vLogin, expires=datetime.now() + timedelta(days=30))
                
            return resp
        else:
            #incorrect login
            if config.myconfig["detailedLogs"]:
                print(f"Login attempt FAILED by {request.remote_addr} using '{vLogin}' : '{vPwd}'")

            return render_template("login01.html", pagename="login", message="Login incorrect")




########################################################################################
## Main entry point
#
if __name__ == '__main__':
    print ("""
USAGE:
    python3 ipcampy.py [path_to_cert.pem path_to_key.perm]

If you don't provide the *.pem files it will start as an HTTP app. You need to pass both .pem files to run as HTTPS.
    """)
    try:
        #start web interface
        app.debug = not config.myconfig["isProd"]
        
        #run as HTTPS?
        if len(sys.argv) == 3:
            #go HTTPS
            print("INFO: start as HTTPSSSSSSSSSSS")
            app.run(host='0.0.0.0', port=int(config.myconfig["app_port"]), threaded=True, ssl_context=(sys.argv[1], sys.argv[2]))
        else:
            #not secured HTTP
            print("INFO: start as HTTP unsecured")
            app.run(host='0.0.0.0', port=int(config.myconfig["app_port"]), threaded=True)

    finally:
        pass