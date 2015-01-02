#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from bottle import route


# Functions & classes =========================================================
@route("/sources/xex")
def test2(something, something_else):
    """
    Another docstring
    """
    pass
