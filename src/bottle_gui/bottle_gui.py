#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import json
import inspect
import os.path
from string import Template

import bottle
from bottle import route, static_file, request, response

from napoleon2html import napoleon_to_html


# Variables ===================================================================
TEMPLATE_PATH = "static/templates/"  #: Path to the template directory.


def read_template(template_name):
    """
    Read content of the template file.

    Args:
        template_name (str): Name of the file.

    Returns:
        str: Content of `template_name` from :attr:`TEMPLATE_PATH` directory.
    """
    template_path = os.path.join(
        os.path.dirname(__file__),
        TEMPLATE_PATH,
        template_name
    )

    with open(template_path) as f:
        return f.read()


# load all necessary templates
INDEX_TEMPLATE = read_template("index.html")  #: static/templates/index.html
TABLE_TEMPLATE = read_template("table.html")  #: static/templates/table.html
ROW_TEMPLATE   = read_template("row.html")  #: static/templates/row.html
DESCR_TEMPLATE = read_template("descr.html")  #: static/templates/descr.html
BLACKLIST = ["/", "/bottle_gui_static/"]


# Classes =====================================================================
class RouteInfo(object):
    """
    Container for informations about `route`.

    Attributes:
        method (fn reference): Reference to undecorated function.
        path (str): Path to the function in bottle.
        args (list): Args of the function.
        docstring (str): Docstring for the function.
        mdocstring (str): Docstring for the module where the function is.
        module_name (str): Name of the module where the function is.
    """
    def __init__(self, method, path, args, docstring, mdocstring, module_name):
        """
        Attributes
            method (fn reference): see Attributes section for details.
            path (str): see Attributes section for details.
            args (list): see Attributes section for details.
            docstring (str): see Attributes section for details.
            mdocstring (str): see Attributes section for details.
            module_name (str): see Attributes section for details.
        """
        self.method = method
        self.path = path
        self.args = args
        self.docstring = self._sanitize(docstring)
        self.mdocstring = self._sanitize(mdocstring)
        self.module_name = module_name

    def _sanitize(self, s):
        """
        Replace ``<`` and ``>`` with corresponding HTML entities.

        Args:
            s (str): Input string.

        Returns:
            str: String with entities, or `s` ``if not s``.
        """
        if s:
            return s.replace("<", "&lt;").replace(">", "&gt;")

        return s

    def to_html(self):
        """
        Convert informations about this route to HTML.

        Note:
            :attr:`DESCR_TEMPLATE` and :attr:`ROW_TEMPLATE` is used.

        Returns:
            str: HTML representation of the `route`.
        """
        descr = ""

        # process docstring
        if self.docstring:
            docstring = self.docstring.strip() or ""

            descr = Template(DESCR_TEMPLATE).substitute(
                method_description=napoleon_to_html(docstring)
            )

        # wrap arguments to the html
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

    def to_dict(self):
        """
        Return dictionary representation of the class. This method is used for
        JSON output.

        Returns:
            dict: Dictionary following keys: ``method``, ``path``, ``args``, \
                  ``docstring``, ``mdocstring``, ``module_name``.
        """
        return {
            "method": self.method,
            "path": self.path,
            "args": self.args,
            "docstring": self.docstring,
            "mdocstring": self.mdocstring,
            "module_name": self.module_name,
        }

    def __str__(self):  # TODO: remove
        return self.method + " " + self.path


class RouteGroup(object):
    """
    This object is used to group :class:`RouteInfo` objects.

    Args:
        routes (list, default []): List with :class:`RouteInfo` objects.
    """
    def __init__(self, routes=[]):
        self.routes = routes

    def get_path(self):  # TODO: shortest path
        """
        Return `path` for this group.

        Returns:
            str: Path.
        """
        if len(self.routes) == 1:
            return self.routes[0].path

        # get longest path
        route_paths = map(lambda x: x.path, self.routes)
        longest_path = max(route_paths)

        if longest_path.endswith("/"):
            return longest_path

        return os.path.dirname(longest_path)

    def get_docstring(self):
        """
        Return 'module' docstring.

        Returns:
            str: Module docstring, if defined, or blank string.
        """
        if self.routes:
            return self.routes[0].mdocstring or ""

        return ""

    def to_html(self):
        """
        Convert group and all contained paths to HTML.

        Note:
            :attr:`TABLE_TEMPLATE` is used.

        Returns:
            str: HTML.
        """
        return Template(TABLE_TEMPLATE).substitute(
            name=self.get_path(),
            description=self.get_docstring(),
            rows="\n".join(
                map(
                    lambda x: x.to_html(),
                    sorted(self.routes, key=lambda x: x.path)
                )
            )
        )

    def to_dict(self):
        """
        Convert group to dict. This method is used for JSON output.

        Returns:
            dict: {path: [routes]}

        See Also:
            :meth:`RouteInfo.to_dict`
        """
        return {
            self.get_path(): map(lambda x: x.to_dict(), self.routes)
        }

    def __str__(self):  # TODO: remove
        return "group: " + " ".join(map(lambda x: str(x), self.routes)) + "\n"


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


def to_html(grouped_routes):
    """
    Convert list of :class:`RouteGroup` objects in `group_routes` to HTML.

    Args:
        grouped_routes (list): Llist of :class:`RouteGroup` objects.

    Returns:
        str: HTML page with routes.
    """
    return Template(INDEX_TEMPLATE).substitute(
        tables="\n".join(
            map(
                lambda x: x.to_html(),
                sorted(grouped_routes, key=lambda x: x.get_path())
            )
        )
    )


def to_json(grouped_routes):
    """
    Convert list of :class:`RouteGroup` objects in `grouped_routes` to JSON.

    Args:
        grouped_routes (list): Llist of :class:`RouteGroup` objects.

    Returns:
        str: JSON representation of `grouped_routes`.
    """
    routes = map(
        lambda x: x.to_dict(),
        grouped_routes
    )

    return json.dumps(
        routes,
        indent=4,
        separators=(',', ': ')
    )


def gui(path="/"):
    """
    Run `bootle-gui` at given `path`.

    Args:
        path (str, default "/"): Bottle path on which the application will be
             available.

    Returns:
        fn reference: Function, which provides the `bottle-gui` functionality,\
                      mapped to bottle `path`.
    """
    @route(path)
    def root():
        """
        Handle requests to root of the project.
        """
        grouped_routes = group_routes(
            filter(lambda x: x.path not in BLACKLIST, list_routes())
        )

        accept = request.headers.get("Accept", "")
        if "json" in request.content_type.lower() or "json" in accept.lower():
            response.content_type = "application/json; charset=utf-8"
            return to_json(grouped_routes)

        return to_html(grouped_routes)

    return root


@route("/bottle_gui_static/<fn>")
def get_static(fn):
    """
    Serve static files.
    """
    return static_file(
        fn,
        root=os.path.join(os.path.dirname(__file__), 'static/')
    )
