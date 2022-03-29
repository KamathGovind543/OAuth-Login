import uuid
import requests
from flask import Flask, render_template, session, request, redirect, url_for
from flask_session import Session  # https://pythonhosted.org/Flask-Session
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
import msal
import sqlalchemy
import app_config
import json
import logging


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = ''

# DATABASE CONNECTION URI
db=SQLAlchemy(app)
app.config.from_object(app_config)
oauth = OAuth(app)
Session(app)



#Logging object
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)#logging Level

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')#Logging Formatter

file_handler = logging.FileHandler('test.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone/#proxy-setups
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


#Creating a Database Model with its attributes
class Profile(db.Model):
    id = db.Column("id", db.Integer(),primary_key = True)
    name = db.Column(db.String(20))  
    email = db.Column(db.String(50)) 
    scope = db.Column(db.String(20))
    response  = db.Column(db.String(255)  , nullable = True)


google = oauth.register(
    name = "google",
    client_id = app_config.Google_client_id,
    client_secret = app_config.Google_client_secret,
    access_token_url = "https://accounts.google.com/o/oauth2/token",
    access_tokens_params = None,
    authorize_url = "https://accounts.google.com/o/oauth2/auth",
    authorize_params = None,
    api_base_url = "https://www.googleapis.com/oauth2/v1/userinfo",
    client_kwargs = {'scope' : 'openid profile email'},
)

#Localhost:5000 This is a First route its going to open in the Webpage


#Here in mainpage we have 2 buttons one for Google Login and One for Microsoft Login.
@app.route("/")    
def Loginpage():
    return render_template('mainpage.html')

#/getdetails route is executed when the authentication is done properly from the microsoft backend
@app.route("/getDetails")
def index():
    if not session.get("user"):
        logger.debug('Not in session Logging First')
        return redirect(url_for("login"))
   
    try:
        user=session["user"]
        name = user['name']  
        email = user['preferred_username']  
        scope = "OutLook"
        response = json.dumps(user)

        #Accessing the Attributes(information) of the user and storing in the Database if he is a first time logging in.
        user_info = Profile()
        user_info.name = name
        user_info.email = email
        user_info.scope = scope
        user_info.response = response

        em = user['preferred_username'] # Take the  email 
        print('email : ' + str(em)) 
        exist = Profile.query.filter(Profile.email == em).first() #check if the email already exist in the table
        if(exist):                                                             # if exist if block is going to execute
            print("Email Exist")
            return render_template('index.html', user=session["user"], version=msal.__version__)

        else:   # If the email does not exist it will add in the table and else block will execute
            db.session.add(user_info)
            db.session.commit()
            return render_template('index.html', user=session["user"], version=msal.__version__)
    except Exception as e:
        logger.error("No user in the session")
        print(str(e))
        return { "status"  : "Failure"}

@app.route("/login")
def login():
    
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
    return render_template("login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__)

@app.route(app_config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            logger.error('Token not Accuried Properply')
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
        logger.debug("Aunthentication of microsoft is working Properly")
    except ValueError:  # Usually caused by CSRF
        logger.error('Usually caused by CSRF')      
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("Loginpage", _external=True))

@app.route("/graphcall")
def graphcall():
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    graph_data = requests.get(  # Use token to call downstream service
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        ).json()
    return render_template('display.html', result=graph_data)

# To get the user data in the form of json
@app.route('/userprofile')  
def userprofile():
    if not session.get("user"):
        return redirect(url_for("Loginpage"))
    return render_template('userprofile.html',user=json.dumps(session["user"]),version=msal.__version__)

def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)

def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("authorized", _external=True))

def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result

app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)  # Used in template


#Google Registration.

#get_details is executed when the Google Authentication is done properly from the Google Backend
@app.route("/get_details")
def get_details():
    
    email = dict(session).get('email',None)
   
    return f"Hello your Email-id is {email}!"

@app.route('/googlelogin')
def google_login():
    google = oauth.create_client('google')
    redirect_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

#Authorization Code for Google 
@app.route('/authorize')
def google_authorize():
    try:
        google = oauth.create_client('google')
        token = google.authorize_access_token()
        resp = google.get('userinfo')
        user_info = resp.json()
        # do something with the token and profile
        session['email'] = user_info['email'] # Storing the User Data in the Session Variable
        session['id'] = user_info['id']
        name = user_info['name']
        email = user_info['email']
        scope = "Google"
        response = json.dumps(user_info)

        #Accessing the Attributes(information) of the user and storing in the Database if he is a first time logging in.
        profile_info = Profile() 
        profile_info.email = email
        profile_info.name = name
        profile_info.scope = scope
        profile_info.response = response

        
        em = user_info['email']
        exists = Profile.query.filter(Profile.email == em).first()
        if(exists): # If Email exists in the Database print the userinfo  if not else condition is execu
            return redirect('/get_details')
        else:    
            db.session.add(profile_info)
            db.session.commit()

        return redirect('/get_details')    
    except Exception as e:
        logger.error("Google Authorization Error")
        print(str(e))
        return { "status"  : "Failure"}
    
# Deleting the session storage with /logout api
@app.route('/googlelogout')
def googlelogout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect(url_for('Loginpage'))

if __name__ == "__main__":
    app.run(debug=True)

