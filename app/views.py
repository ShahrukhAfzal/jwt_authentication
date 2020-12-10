import os
import uuid

from app import app

from flask import (request, render_template,
    jsonify, make_response, redirect, url_for)
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)

#location where all images will be uploaded
UPLOAD_TO = os.path.dirname(os.path.realpath(__file__)) + '/media'
TEST_USERNAME = 'test'
TEST_PASSWORD = '123456'

app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_SECRET_KEY'] = str(uuid.uuid4())

jwt = JWTManager(app)

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

DEFAULT_THROTTLE_LIMITS = ["5 per minute"]
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=DEFAULT_THROTTLE_LIMITS
)


@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == "POST":
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        if (username != TEST_USERNAME or password != TEST_PASSWORD):
            return render_template("index.html", error='Wrong credentials')

        # Create the tokens we will be sending back to the user
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)

        resp = make_response(redirect(url_for('upload_image')))
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp

    return render_template("index.html")

@app.route('/logout', methods=['POST'])
def logout():
    resp = make_response(redirect(url_for('login')))
    unset_jwt_cookies(resp)
    return resp


@app.route("/upload-image", methods=["GET", "POST"])
@jwt_required
def upload_image():
    if request.method == "POST":
        if request.files:
            image = request.files["image"]
            image.save(os.path.join(UPLOAD_TO, image.filename))
            context = {
                'filename': image.filename,
                'location' : UPLOAD_TO
            }
            return render_template('upload_success.html', context=context)

    return render_template("upload_image.html")

