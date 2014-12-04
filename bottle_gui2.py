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
# class PathID(object):
#     def __init__(self, method, path):
#         self.method = method
#         self.path = path


class PathInfo(object):
    def __init__(self, method, path, args, docstring, mdocstring, module_name):
        self.method = method
        self.path = path
        self.args = args
        self.docstring = self.sanitize(docstring)
        self.mdocstring = self.sanitize(mdocstring)
        self.module_name = module_name

    def sanitize(self, s):
        if s:
            return s.replace("<", "&lt;").replace(">", "&gt;")

    def __str__(self):  # TODO: remove
        return self.method + " " + self.path


class PathGroup(object):
    def __init__(self, routes=[]):
        self.routes = routes

    def add_route(self, route):
        self.routes.append(route)

    def __str__(self):  # TODO: remove
        return "group: " + " ".join(map(lambda x: str(x), self.routes)) + "\n"


# Functions ===================================================================
def list_routes():  # TODO: rename
    """
    Get dict
    """
    return map(
        lambda r: PathInfo(
            method=r.method,
            path=r.rule.split("<")[0],
            args=r.get_callback_args(),
            docstring=inspect.getdoc(r.get_undecorated_callback()) or "",
            mdocstring=inspect.getdoc(
                inspect.getmodule(r.get_undecorated_callback())
            ),
            module_name=r.get_undecorated_callback().__module__
        ),
        bottle.default_app().routes
    )


def group_routes(ungrouped_routes):
    groups = []

    # go from longest routes to shorter
    routes = sorted(
        ungrouped_routes,
        key=lambda x: len(x.path),
        reverse=True
    )

    # group and remove / routes - they would break grouping algorithm later
    root_paths = filter(lambda x: x.path == "/", routes)
    if root_paths:
        groups.append(
            PathGroup(root_paths)
        )

        # remove / routes if present
        map(lambda x: routes.pop(), root_paths)

    processed = set()
    for route in routes:
        # skip already processed routes
        if route in processed:
            continue

        # find all routes, which starts with `route`
        same_group = filter(
            lambda x: x.path.startswith(route.path),
            routes
        )

        # skip routes without groups for later processing
        if len(same_group) <= 1:  # always at least one route
            continue

        groups.append(
            PathGroup(same_group)
        )
        processed.update(same_group)

    # don't forget to uprocessed routes
    for route in set(routes) - processed:
        groups.append(
            PathGroup([route])
        )

    return groups








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


@route("/sources/hist")
def test(something, something_else):
    """
    Here is docstring and so on.
    """
    pass

@route("/sources/hist/xe")
def test(something, something_else):
    """
    Here is docstring and so on.
    """
    pass

@route("/sources/xex")
def test2(something, something_else):
    """
    Another docstring
    """
    pass


# Main program ================================================================
if __name__ == '__main__':
    # main()
    print "routes"
    print map(lambda x: str(x), list_routes())
    print
    print "grouped"
    print "".join(map(lambda x: str(x), group_routes(list_routes())))
