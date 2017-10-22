# -*- coding: utf-8 -*-

import os
import re

def test_bar_fixture(testdir):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    testdir.makepyfile("""
        def test_sth(bar):
            assert bar == "europython2015"
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--foo=europython2015',
        '-v'
    )

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_sth PASSED',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'nbsane:',
        '*--foo=DEST_FOO*Set the value for the fixture "bar".',
    ])


def test_hello_ini_setting(testdir):
    testdir.makeini("""
        [pytest]
        HELLO = world
    """)

    testdir.makepyfile("""
        import pytest

        @pytest.fixture
        def hello(request):
            return request.config.getini('HELLO')

        def test_hello_world(hello):
            assert hello == 'world'
    """)

    result = testdir.runpytest('-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_hello_world PASSED',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0

_nb = """
{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "%(the_source)s"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python",
   "pygments_lexer": "ipython3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
"""

def test_definitely_ran_paranoid(testdir):
    testdir.makefile('.ipynb', testing123=_nb%{'the_source':"open('x','w').write('y')"})
    result = testdir.runpytest('--nbsane-run','-v')
    assert result.ret == 0
    assert open('x','r').read() == 'y'

def test_rungood(testdir):
    testdir.makefile('.ipynb', testing123=_nb%{'the_source':"1/1"})
    result = testdir.runpytest('--nbsane-run','-v')
    assert result.ret == 0

def test_runbad(testdir):
    testdir.makefile('.ipynb', testing123=_nb%{'the_source':"1/0"})
    result = testdir.runpytest('--nbsane-run','-v')
    assert result.ret == 1

def test_rungood_html(testdir):
    testdir.makefile('.ipynb', testing123=_nb%{'the_source':"42"})

    result = testdir.runpytest(
        '--nbsane-run',
        '--store-html=%s'%testdir.tmpdir.strpath,
        '-v')
    assert result.ret == 0

    # test that html has happened
    answer = None
    with open(os.path.join(testdir.tmpdir.strpath,'testing123.ipynb.html')) as f:
        for line in f:
            if re.search("<pre>42</pre>", line):
                answer = 42
    assert answer == 42

def test_lintgood(testdir):
    testdir.makefile('.ipynb', testing123=_nb%{'the_source':"1/1"})
    result = testdir.runpytest('--nbsane-lint','-v')
    assert result.ret == 0

def test_lintbad(testdir):
    testdir.makefile('.ipynb', testing123=_nb%{'the_source':"these undefined names are definitely undefined"})
    result = testdir.runpytest('--nbsane-lint','-v')
    assert result.ret == 1
