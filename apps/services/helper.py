# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import apps, base64, requests
import os, string, random, glob
from flask import json
from werkzeug.utils import secure_filename

def getBase64(path):
    print(path)
    img_url = "https://1779cloudcomputing.s3.amazonaws.com/" + path
    print(img_url)
    encoded_string = "data:image/jpeg;base64," + base64.b64encode(requests.get(img_url).content).decode()
    
    return encoded_string