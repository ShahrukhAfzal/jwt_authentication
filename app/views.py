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
from flask_cors import CORS, cross_origin

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

DEFAULT_THROTTLE_LIMITS = ["50 per minute"]
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

def create_media_folder():
    if not os.path.exists(UPLOAD_TO):
        os.makedirs(UPLOAD_TO)


import time

@app.route('/time')
def get_current_time():
    return {'time': time.time()}

from PIL import Image
import io



@app.route("/upload-image", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":
        if request.files:
            image = request.files["file"]
            create_media_folder()
            image.save(os.path.join(UPLOAD_TO, image.filename))
            context = {
                'filename': image.filename,
                'location' : UPLOAD_TO
            }
            print(context)
            return jsonify(context)

    elif request.method == 'GET':
        import base64
        import io

        image = os.path.join(UPLOAD_TO, 'img.png')

        img = Image.open(image, mode='r')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        my_encoded_img = base64.encodebytes(img_byte_arr.getvalue()).decode('ascii')

        # import io
        # from PIL import Image
        # with io.BytesIO() as output:
        #     from PIL import Image
        #     with Image.open(image) as img:
        #         img.convert('RGB').save(output, 'BMP')
        #     data = output.getvalue()[14:]
        print(my_encoded_img)
        return jsonify(my_encoded_img)





@app.route("/check-throttle-limit", methods=["GET"])
def check_throttle_limit():
    return {'throttle_limit': DEFAULT_THROTTLE_LIMITS[0]}


CORS(app, expose_headers='Authorization')
