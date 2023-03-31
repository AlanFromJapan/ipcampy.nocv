# Big thanks to the below link which had all the core code needed
# https://stackoverflow.com/questions/49978705/access-ip-camera-in-python-opencv#49979186

import config
from flask import Flask, request, send_file, render_template, abort, redirect, make_response
from datetime import datetime, timedelta
import sys
import time

from io import BytesIO

import av

############################ FLASK VARS #################################
app = Flask(__name__, static_url_path='')

cap = None

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'ico'])



############################ Web requests ###############################

@app.route('/')
def homepage():
    #not logged in? go away
    if None == request.cookies.get('username'):
        return redirect("login")
    return render_template("main01.html", pagename="Home", cameras=config.myconfig["cameras"].values())

    
@app.route('/<nickname>/capture.jpg')
def captureImage(nickname):

    #not logged in? go away
    if None == request.cookies.get('username'):
        abort(500)  
        return

    if not nickname in config.myconfig["cameras"]:
        print(f"Error: unknown camera '{nickname}'")
        abort(500)  
        return

    cam = config.myconfig["cameras"][nickname]

    tstart = time.time()

    camurl = f"rtsp://{cam.ip}:{cam.port}{cam.suffix}"

    try:
        io_buf = BytesIO()

        # shamelessly taken from RTSPBrute software source (thanks for sharing <3)
        # https://gitlab.com/woolf/RTSPbrute/-/blob/master/rtspbrute/modules/attack.py
        with av.open(
            camurl,
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

        tend=time.time()
        if config.myconfig["detailedLogs"]:
            print(f"DBG: acquisition of {nickname} in {(tend - tstart):0.2f}s" )

        #return the in memory image
        return send_file(io_buf, mimetype='image/jpeg')
    except Exception as ex:
        print(f"ERROR getting data for {nickname} : {ex}")
        abort(501)


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