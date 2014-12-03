#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import json
import os.path
from string import Template

import bottle
from bottle import route, run, static_file, request, response
import inspect

from components.napoleon2html import napoleon_to_html


# Variables ===================================================================
def read_template(template_name):
    template_path = os.path.join(
        os.path.dirname(__file__),
        "static/templates/",
        template_name
    )
    with open(template_path) as f:
        return f.read()


# load all necessary templates
INDEX_TEMPLATE = read_template("index.html")
TABLE_TEMPLATE = read_template("table.html")
ROW_TEMPLATE   = read_template("row.html")
DESCR_TEMPLATE = read_template("descr.html")


# Classes =====================================================================
class PathID(object):
    def __init__(self, http_type, path):
        self.http_type = http_type
        self.path = path


class PathInfo(object):
    def __init__(self, http_type, args, docstring, mdocstring, module_name):
        self.http_type = http_type
        self.args = args
        self.docstring = self.sanitize(docstring)
        self.mdocstring = self.sanitize(mdocstring)
        self.module_name = module_name

    def sanitize(self, s):
        if s:
            return s.replace("<", "&lt;").replace(">", "&gt;")


# Functions ===================================================================
def list_routes():  # TODO: rename
    """
    Get dict
    """
    return dict(map(  # create dict from rules
        lambda r: (
            PathID(r.method, r.rule.split("<")[0]),
            PathInfo(
                http_type=r.method,
                args=r.get_callback_args(),
                docstring=inspect.getdoc(r.get_undecorated_callback()) or "",
                mdocstring=inspect.getdoc(
                    inspect.getmodule(r.get_undecorated_callback())
                ),
                module_name=r.get_undecorated_callback().__module__
            )
        ),
        bottle.default_app().routes
    ))




















@route('/')
def root():
    """Handle requests to root of the project."""
    content = group_routes(list_routes())

    accept = request.headers.get("Accept", "")
    if "json" in request.content_type.lower() or "json" in accept.lower():
        response.content_type = "application/json; charset=utf-8"
        return json.dumps(
            to_json(content),
            indent=4,
            separators=(',', ': ')
        )

    return to_html(content)


@route("/static/<fn>")
def get_static(fn):
    return static_file(fn, root='static/')


# TODO: remove
def main():
    run(
        server="paste",
        host="127.0.0.1",
        port=8888,
        debug=True,
        reloader=True,
        # ssl_pem="static/host.pem"
    )


@route("/something")
def test(something, something_else):
    """
    Here is docstring and so on.
    """
    pass

@route("/something/else")
def test2(something, something_else):
    """
    Another docstring
    """
    pass


# Main program ================================================================
if __name__ == '__main__':
    main()
