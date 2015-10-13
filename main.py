from flask import Flask, send_from_directory, request
from werkzeug import secure_filename
import os
import random
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)

class Config(object):
    DOMAIN = "http://127.0.0.1:5000/"
    DEBUG = True
    TESTING = False
    UPLOAD_FOLDER = "uploaded"

app = Flask(__name__)
app.config.from_object(Config)
files = {}
upload_ips = {}

def random_uid():
    letters = "ABCDEFGHJKMNPQRSTUVWXYZabcdefghjklmnpqestuvwxyz9234567"
    uid = ""
    for i in range(5):
        uid += letters[random.randint(0, len(letters) - 1)]
    return ''.join(uid)

def create_resource(uid, filename):
    ip = request.remote_addr
    global upload_ips

    if upload_ips["since"] < datetime.now().date():
        upload_ips = { "since": datetime.now().date() }

    if ip in upload_ips and upload_ips[ip] >= 3:
        err = "IP has already uploaded a file 3 times"
        logging.info(err)
        raise Exception(err)
    else:
        upload_ips[ip] = upload_ips.get(ip, 0) + 1
    valid_until = datetime.now() + timedelta(minutes=1)
    files[uid] =  { "filename" : filename, "valid_until" : valid_until, "recieved": False }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        f = request.files['file']
        sfilename = secure_filename(f.filename)
        filename = os.path.join(app.config['UPLOAD_FOLDER'], sfilename)
        f.save(filename)

        uid = random_uid()

        try:
            create_resource(uid, filename)
        except Exception, e:
            return str(e)

        logging.info("Create file mapping: %s => %s" % (uid, files[uid]))

        return "\nDownload file: %s -- you can only download it once, and within the next hour.\n" % (app.config["DOMAIN"] + uid)
    else:
        return 'Use cURL to POST your file to this location..'

@app.route('/<uid>/')
def get_file(uid):
    if uid not in files:
        return "That file doesnt exist."
    if not files[uid]["recieved"]:
        files[uid]["recieved"] = True
        filename = files[uid]["filename"]
        return send_from_directory('.', filename, as_attachment=True)
    else:
        return "You can only download a file once. Sorry!"

if __name__ == '__main__':
    if not os.path.isdir(app.config['UPLOAD_FOLDER']):
        os.mkdir(app.config['UPLOAD_FOLDER'])

    upload_ips["since"] = datetime.now().date()
    app.run()
