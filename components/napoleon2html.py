#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from docutils.core import publish_parts
from sphinxcontrib.napoleon import Config, GoogleDocstring


# Functions & objects =========================================================
def napoleon_to_sphinx(docstring, **config_params):
    """
    Convert napoleon docstring to plain sphinx string.

    Args:
        docstring (str): Docstring in napoleon format.
        **config_params (dict): Whatever napoleon doc configuration you want.

    Returns:
        str: Sphinx string.
    """
    if "napoleon_use_param" not in config_params:
        config_params["napoleon_use_param"] = False

    if "napoleon_use_rtype" not in config_params:
        config_params["napoleon_use_rtype"] = False

    config = Config(**config_params)

    return str(GoogleDocstring(docstring, config))


def napoleon_to_html(docstring, **config_params):
    """
    Convert `docstring` in napoleon docstring format to HTML.

    Args:
        docstring (str): Docstring in napoleon format.
        **config_params (dict): Whatever napoleon doc configuration you want.

    Returns:
        str: HTML string.
    """
    sphinxstring = napoleon_to_sphinx(docstring, **config_params)

    document = publish_parts(sphinxstring, writer_name='html')

    return document['body']
