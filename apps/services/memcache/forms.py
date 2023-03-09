# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import Length, InputRequired, Regexp

# login and registration


class ImageForm(FlaskForm):
    key = StringField('key',
                         id='key',
                         validators=[InputRequired(), Length(4, 64), Regexp('^[a-zA-Z0-9_]+$', message="Keys can contain alpha nemeric or '_' character only")])
    image_path = StringField('image_path',
                             id='image_path',
                             validators=[InputRequired()])
                             