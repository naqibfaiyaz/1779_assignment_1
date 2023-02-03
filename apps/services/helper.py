# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import apps, base64, logging
import os, string, random
from werkzeug.utils import secure_filename

def upload_file(file):
    apps.logger.info(file)
    assetRoot = apps.config.DebugConfig.ASSETS_ROOT if (os.getenv('DEBUG', 'False') == 'True') else apps.config.ProductionConfig.ASSETS_ROOT
    path = os.path.join(assetRoot + "/public/" + ''.join(random.choice(string.ascii_lowercase) for i in range(32)) + secure_filename(file.filename))
    apps.logger.info(path)
    file.save(apps.__name__ + path)
    return path

def getBase64(path):
    # logging.info(path)
    with open(apps.__name__ + path, "rb") as img:
        encoded_string = "data:image/jpeg;base64," + base64.b64encode(img.read()).decode()
    
    return encoded_string