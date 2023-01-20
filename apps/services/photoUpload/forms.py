# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import Email, DataRequired

# login and registration


class addPhotoForm(FlaskForm):
    key = StringField('Key',
                         id='key_photo_upload',
                         validators=[DataRequired()])
    value = StringField('Value',
                             id='value_photo_upload',
                             validators=[DataRequired()])
