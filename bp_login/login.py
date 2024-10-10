from flask import Blueprint, render_template, current_app, session, redirect, request, make_response
from datetime import datetime, timedelta

from config import myconfig

'''
Add the below code to your main page to enable login page:

from bp_login.login import login_bp

##########################################################################################
#Login page
app.register_blueprint(login_bp)

#that's it! Now you have a login page that will be shown before any page, except the login page itself.
'''

login_bp = Blueprint('login_bp', __name__, template_folder='templates')


@login_bp.route("/login", methods=['POST', 'GET'])
def do_login():
    #if no access control, then no need to check
    if not myconfig.get("Access control", False):
        return redirect("home")

    #Get shows the page, POST checks the login
    if request.method == "GET":
        return render_template("login01.html", pagename="login", isprod=True, message="")
    else:
        l = request.form["login"].lower()
        pwd = request.form["pwd"]
        
        if l == myconfig["Login"].lower() and pwd == myconfig["Password"]:
            #Login is correct
            resp = make_response( redirect("home") )
            
            resp.set_cookie ('username', l, expires=datetime.now() + timedelta(days=30))
                
            return resp
        else:
            #incorrect login
            return render_template("login01.html", pagename="login", isprod=True, message="Login incorrect")


#This is a decorator that will be called before *any* request on the *app* (Different from before_request that is called only for the blueprint)
@login_bp.before_app_request
def check_login():
    #if no access control, then no need to check
    if not myconfig.get("Access control", False):
        return
    
    #if login page, no need to check
    if request.path == "/login":
        return

    #if no cookie, then redirect to login
    if 'username' not in request.cookies or request.cookies.get('username') != myconfig["Login"]:
        return redirect("/login")


@login_bp.route('/logout')
def logout():
    resp = make_response( redirect("home") )
    resp.delete_cookie('username')
    #resp.set_cookie ('username', '', expires=0)
    return resp