#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
"""
Hist module level docstring.
"""
from bottle import route


# Functions & classes =========================================================
@route("/sources/hist")
def hist(something, something_else):
    """
    Here is hist docstring and so on.
    """
    pass


@route("/sources/hist/xe")
def hist_xe(something, something_else):
    """
    Here is hist/xe docstring and so on.
    """
    pass
