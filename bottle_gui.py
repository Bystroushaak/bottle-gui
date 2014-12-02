#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os.path
from string import Template

import bottle
from bottle import route, run, static_file, request
import inspect

from components.napoleon2html import napoleon_to_html

from plugins.sources import pretty_dump  # TODO: replace with bottle-rest


# Variables ===================================================================
def read_template(template_name):
    template_path = os.path.join([
        __file__,
        "static/templates/",
        template_name
    ])
    with open(template_path) as f:
        return f.read()


# load all necessary templates
INDEX_TEMPLATE = read_template("index.html")
TABLE_TEMPLATE = read_template("table.html")
ROW_TEMPLATE   = read_template("row.html")
DESCR_TEMPLATE = read_template("descr.html")


# Functions & Classes =========================================================
def list_routes():
    """
    Get list of routes defined in bottle.py.

    Each record contains informations about ``type`` (get/post/whatever),
    ``route`` ("/"), ``docstring`` for function, which will be called and
    ``mdocstring`` (module docstring). Information about parameters is added
    to the ``args`` property.

    Returns:
        dict: {
            "route": {
                "http_type": "",
                "docstring": "",
                "mdocstring": "",
                "args": []
            },
            ..
        }
    """
    def sanitize(s):
        if s:
            return s.replace("<", "&lt;").replace(">", "&gt;")

    return dict(map(
        lambda r: (
            (r.method, r.rule.split("<")[0]),
            {
                "http_type": r.method,
                "docstring": sanitize(
                    inspect.getdoc(r.get_undecorated_callback()) or ""
                ),
                "mdocstring": sanitize(inspect.getdoc(
                    inspect.getmodule(r.get_undecorated_callback())
                )),
                "args": r.get_callback_args()
            }
        ),
        bottle.default_app().routes
    ))


def group_routes(route_data):
    """
    Move routes to groups, remove mdocstrings from each route and put it only
    to the module group.

    Args:
        route_data (list): returned from list_routes()

    Returns:
        dict: {
            ("http_type", "path"): {
                "docstring": "Module docstring.",
                "routes": {
                    "/path/": {
                        "http_type": "GET/POST/PUT/..",
                        "docstring": "Method docstring.",
                        "args": [names, of, arguments]
                    },

                    "/path/more.html": {
                        ...
                    }
                }
            },
            ...
        }
    """
    def remove_key(d, key):
        if key in d:
            del d[key]

        return d

    # remove banned elements (internal routes for application)
    banned_paths = [("GET", "/"), ("GET", "/static/")]
    for path in banned_paths:
        if path in route_data:
            del route_data[path]

    # go from longest routes to shorter
    routes = sorted(route_data.keys(), key=lambda x: len(x), reverse=True)
    process_later = routes[:]

    grouped = {}
    for method, path in routes:
        # find all routes, which starts with `route`
        same_group = filter(
            lambda (x_method, x_path): x_path.startswith(path),
            routes
        )

        if len(same_group) <= 1:
            continue

        # join "route" and "route/" into one path
        if path.endswith("/") and (method, path[:-1]) in routes:
            continue

        # group all routes from `same_group` to one dictionary, remove module
        # docstring from subroutes and move it to the "package" level
        grouped[path] = {
            "docstring": route_data[(method, path)].get("mdocstring", ""),
            "routes": dict(map(
                lambda x: (x, remove_key(route_data[x], "mdocstring")),
                same_group
            ))
        }

        # single routes with no subroutes
        map(
            lambda x:
                process_later.remove(x) if x in process_later else "",
            same_group
        )

    # same thing as above, but for single routes without subroutes
    for route in process_later:
        grouped[route[1]] = {
            "docstring": route_data[route]["mdocstring"],
            "routes": {route: remove_key(route_data[route], "mdocstring")}
        }

    return grouped


def to_html(grouped_data):
    """
    Convert `grouped_data` to HTML, for human viewers (I've heard, that they
    don't prefer JSON for some strange reason).

    Args:
        grouped_data (dict): output from func:`group_data`.

    Returns:
        str: HTML made from templates (see INDEX_TEMPLATE, TABLE_TEMPLATE,
             ROW_TEMPLATE and DESCR_TEMPLATE) and data.
    """
    output = ""
    for route, data in sorted(grouped_data.iteritems()):
        rows = ""
        for function_route, group_data in sorted(data["routes"].iteritems()):
            descr = ""
            if group_data["docstring"]:
                docstring = group_data["docstring"].strip() or ""

                descr = Template(DESCR_TEMPLATE).substitute(
                    method_description=napoleon_to_html(docstring)
                )

            args = group_data["args"] if group_data["args"] else ""
            if args:
                args_style = "&#8672; &lt;<span class='param'>"
                args = args_style + "</span>, <span class='param'>".join(args)
                args += "</span>&gt;"

            rows += Template(ROW_TEMPLATE).substitute(
                name=function_route[1],
                args=args,
                http_type=group_data["http_type"],
                method_description=descr
            )

        output += Template(TABLE_TEMPLATE).substitute(
            name=route,
            description=data["docstring"] or "",
            rows=rows
        )

    return Template(INDEX_TEMPLATE).substitute(tables=output)


def to_json(grouped_data):
    """
    Convert data to json-friendly format.

    Args:
        grouped_data (dict): output from func:`group_data`.

    Example of the input::

        {
            '/sources/shaddack': {
                'routes': {
                    ('GET', '/sources/shaddack/_unittest'): {
                        'args': [],
                        'docstring': None,
                        'http_type': 'GET'
                    },
                    ('GET', '/sources/shaddack'): {
                        'args': [],
                        'docstring': "Returns:\n    list: of Shaddack's projects.\n\nSee /shaddack/_schema for description of datastructures.",
                        'http_type': 'GET'
                    },
                    ('GET', '/sources/shaddack/_schema'): {
                        'args': [],
                        'docstring': None,
                        'http_type': 'GET'
                    }
                },
                'docstring': "Shaddack API for retreiving links to Shaddack's projects published at his site\n(see BASE_URL)."
            },
        }

    Example of the output::

        {
            "/sources/shaddack": {
                "docstring": "Shaddack API for retreiving links to Shaddack's projects published at his site\n(see BASE_URL).",
                "GET": {
                    "/sources/shaddack/_schema": {
                        "args": [],
                        "docstring": null,
                        "http_type": "GET"
                    },
                    "/sources/shaddack": {
                        "args": [],
                        "docstring": "Returns:\n    list: of Shaddack's projects.\n\nSee /shaddack/_schema for description of datastructures.",
                        "http_type": "GET"
                    },
                    "/sources/shaddack/_unittest": {
                        "args": [],
                        "docstring": null,
                        "http_type": "GET"
                    }
                }
            },
        }

    Returns:
        dict: Dict with simple keys.
    """
    output = {}

    for route, data in sorted(grouped_data.iteritems()):
        output[route] = {}
        output[route]["docstring"] = data["docstring"]

        for sub_route, sub_data in sorted(data["routes"].iteritems()):
            if sub_route[0] not in output[route]:
                output[route][sub_route[0]] = {}

            output[route][sub_route[0]][sub_route[1]] = sub_data

    return output


@route('/')
def root():
    """Handle requests to root of the project."""
    content = group_routes(list_routes())

    accept = request.headers.get("Accept", "")
    if "json" in request.content_type.lower() or "json" in accept.lower():
        print content
        return pretty_dump(to_json(content))

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


# Main program ================================================================
if __name__ == '__main__':
    main()
