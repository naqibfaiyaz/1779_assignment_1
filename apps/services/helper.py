# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import apps, base64, requests
import os, string, random, glob
from werkzeug.utils import secure_filename
from apps.services.s3Manager.routes import s3_upload

def upload_file(file):
    filename = ''.join(random.choice(string.ascii_lowercase) for i in range(32)) + secure_filename(file.filename)
    apps.logger.info(filename)

    bucket_name='1779cloudcomputing'
    s3_upload(bucket_name, file, filename)
    
    print(bucket_name)

    return filename

def getBase64(path):
    print(path)
    img_url = "https://1779cloudcomputing.s3.amazonaws.com/" + path
    print(img_url)
    encoded_string = "data:image/jpeg;base64," + base64.b64encode(requests.get(img_url).content).decode()
    
    return encoded_string

def removeAllImages():
    assetRoot = apps.config.DebugConfig.ASSETS_ROOT if (os.getenv('DEBUG', 'False') == 'True') else apps.config.ProductionConfig.ASSETS_ROOT
    files = glob.glob(apps.__name__ + assetRoot + "/public/*")
    for f in files:
        apps.logging.info(f)
        os.remove(f)