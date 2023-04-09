# Big thanks to the below link which had all the core code needed
# https://stackoverflow.com/questions/49978705/access-ip-camera-in-python-opencv#49979186

import config
from flask import Flask, request, send_file, render_template, abort, redirect, make_response, flash
from datetime import datetime, timedelta
import sys
import time

from io import BytesIO, StringIO
from sharedObjects import IpCamera

import camCapture

############################ FLASK VARS #################################
app = Flask(__name__, static_url_path='')

cap = None

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
    return render_template("main01.html", pagename="Home", cameras=config.myconfig["cameras"])


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

    return render_template("zoom01.html", pagename=f"Zoom on [{cam.nickname}]", cam=cam)

    

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
        if cap != None:
            print("Release OpenCV ...")
            cap.release()