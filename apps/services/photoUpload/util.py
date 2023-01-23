# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, request, json, Response
from flask_login import login_required
import apps, base64, logging
import os, random, string
from pathlib import Path



def upload_file(file):
    apps.logger.info(file)
    assetRoot = apps.config.DebugConfig.ASSETS_ROOT if (os.getenv('DEBUG', 'False') == 'True') else apps.config.ProductionConfig.ASSETS_ROOT
    basedir = apps.config.DebugConfig.basedir if (os.getenv('DEBUG', 'False') == 'True') else apps.config.ProductionConfig.basedir
    apps.logger.info(os.path.realpath(__file__))
    apps.logger.info(basedir)
    path = os.path.join(basedir + assetRoot + "/public", ''.join(random.choice(string.ascii_lowercase) for i in range(32)) + file.filename)
    apps.logger.info(path)
    file.save(path)
    return path

def getBase64(path):
    with open(path, "rb") as img:
        encoded_string = "data:image/jpeg;base64," + base64.b64encode(img.read()).decode()
    
    return encoded_string