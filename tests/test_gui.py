#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
# This work is licensed under a Creative Commons 3.0 Unported License
# (http://creativecommons.org/licenses/by/3.0/).
#
# Imports ====================================================================
import sys
import time
import random
from multiprocessing import Process

import pytest
import requests
from bottle import run

import services

sys.path.append('../')
from bottle_gui2 import bottle_gui


# Variables ==================================================================
ADDR = "127.0.0.1"
# PORT = 8000
PORT = random.randint(10000, 65525)
URL = 'http://%s:%s%s' % (ADDR, PORT, "/")
SERV = None


# Functions & classes ========================================================
def run_server():
    bg = bottle_gui()
    run(
        host=ADDR,
        port=PORT,
        # server="paste",
        # debug=True,
        # reloader=True,
        # ssl_pem="static/host.pem"
    )


# Setup/Teardown ==============================================================
def setup_module(module):
    """
    Run server as subprocess.

    This is something like module constructor.
    """
    global SERV
    SERV = Process(target=run_server)
    SERV.start()
    time.sleep(1)


def teardown_module(module):
    """
    Shut down server subprocess.

    This is something like module destructor.
    """
    SERV.terminate()

    # test that server was really closed
    with pytest.raises(requests.exceptions.ConnectionError):
        requests.get(URL)


# Tests =======================================================================
def test_html_output():
    res = requests.get(URL)
    assert "<title>API index</title>" in res.text

    assert "Xex module docstring." in res.text
    assert "/sources/xex" in res.text
    assert "Another docstring" in res.text

    assert "Hist module level docstring." in res.text
    assert "/sources/hist" in res.text
    assert "/sources/hist/xe" in res.text
    assert "Here is hist docstring and so on." in res.text
    assert "Here is hist/xe docstring and so on." in res.text


def test_json_output():
    pass
