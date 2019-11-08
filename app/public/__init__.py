# -*- coding: utf-8 -*-
"""The public module, including the homepage and user auth."""
from flask import Blueprint, session

main = Blueprint('main', __name__)

# from . import views, errors

# @main.before_request
# def func():
#     session.modified = True
