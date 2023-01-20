# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.services.memcache import blueprint
from flask import render_template, request, json, Response
from flask_login import login_required
from apps import memcache


@blueprint.route('/index')
# @login_required
def index():

    return render_template('home/index.html', segment='index')

