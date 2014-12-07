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
class RouteInfo(object):
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

    def to_html(self):
        descr = ""
        if self.docstring:
            docstring = self.docstring.strip() or ""

            descr = Template(DESCR_TEMPLATE).substitute(
                method_description=napoleon_to_html(docstring)
            )

        args = self.args or ""
        if args:
            args_style = "&#8672; &lt;<span class='param'>"
            args = args_style + "</span>, <span class='param'>".join(args)
            args += "</span>&gt;"

        return Template(ROW_TEMPLATE).substitute(
            name=self.path,
            args=args,
            http_type=self.method,
            method_description=descr
        )


class RouteGroup(object):
    def __init__(self, routes=[]):
        self.routes = routes

    def add_route(self, route):
        self.routes.append(route)

    def __str__(self):  # TODO: remove
        return "group: " + " ".join(map(lambda x: str(x), self.routes)) + "\n"

    def get_path(self):
        if len(self.routes) == 1:
            return self.routes[0].path

        # get longest path
        route_paths = map(lambda x: x.path, self.routes)
        longest_path = max(route_paths)

        if longest_path.endswith("/"):
            return longest_path

        return os.path.dirname(longest_path)

    def get_docstring(self):
        if self.routes:
            return self.routes[0].mdocstring or ""

        return ""

    def to_html(self):
        return Template(TABLE_TEMPLATE).substitute(
            name=self.get_path(),
            description=self.get_docstring(),
            rows="\n".join(
                map(lambda x: x.to_html(), self.routes)
            )
        )


# Functions ===================================================================
def list_routes():
    """
    Get list of :class:`RouteInfo` objects from bottle introspection.

    Returns:
        list: :class:`RouteInfo` objects.
    """
    return map(
        lambda r: RouteInfo(
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
    """
    Group list of :class:`RouteInfo` objects in `ungrouped_routes` by their
    :attr:`RouteInfo.path` properties.

    Args:
        ungrouped_routes (list): List of :class:`RouteInfo` objects.

    Returns:
        list: :class:`RouteGroup` objects.
    """
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
            RouteGroup(root_paths)
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
        if len(same_group) <= 1:  # contains always actual route, so <= 1
            continue

        groups.append(RouteGroup(same_group))
        processed.update(same_group)

    # don't forget to uprocessed routes
    for route in set(routes) - processed:
        groups.append(
            RouteGroup([route])
        )

    return groups


def to_html(grouped_list):
    return Template(INDEX_TEMPLATE).substitute(
        tables="\n".join(
            map(lambda x: x.to_html(), grouped_list)
        )
    )





@route('/')
def root():
    """Handle requests to root of the project."""
    content = group_routes(list_routes())

    # accept = request.headers.get("Accept", "")
    # if "json" in request.content_type.lower() or "json" in accept.lower():
    #     response.content_type = "application/json; charset=utf-8"
    #     return json.dumps(
    #         to_json(content),
    #         indent=4,
    #         separators=(',', ': ')
    #     )

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
    main()
