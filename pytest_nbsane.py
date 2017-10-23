# -*- coding: utf-8 -*-

import pytest
import re
import os
import io
import sys

def pytest_addoption(parser):
    group = parser.getgroup('nbsane')
    group.addoption(
        '--nbsane-run',
        action="store_true",
        help="help!")

    group.addoption(
        '--nbsane-lint',
        action="store_true",
        help="help!")

    group.addoption(
        '--store-html',
        action="store",
        dest='store_html',
        default='',
        help="help!")

    group.addoption(
        '--foo',
        action='store',
        dest='dest_foo',
        default='2017',
        help='Set the value for the fixture "bar".'
    )

    parser.addini('HELLO', 'Dummy pytest.ini setting')


@pytest.fixture
def bar(request):
    return request.config.option.dest_foo


import nbformat
import nbconvert
from nbconvert.preprocessors import ExecutePreprocessor


class RunNb(pytest.Item):
    def runtest(self):
        with io.open(self.name,encoding='utf8') as nb:
            notebook = nbformat.read(nb, as_version=4)

            # TODO: config options, and also:
            # TODO: which kernel? run in pytest's or use new one (option)
            kwargs = dict(timeout=600,
                          allow_errors=False,
                          # or sys.version_info[1] ?
                          kernel_name='python')
            ep = ExecutePreprocessor(**kwargs)
            ep.preprocess(notebook,{})

            # TODO: clean up this option handling
            if self.parent.parent.config.option.store_html != '':
                he = nbconvert.HTMLExporter()
                # could maybe use this for chance of testing the html? but not the aim of this project
                #he.template_file = 'basic'
                html, resources = he.from_notebook_node(notebook)
                # TODO: quick hack, and not cross platform
                with io.open(os.path.join(self.parent.parent.config.option.store_html,os.path.basename(self.name)+'.html'),'w') as f:
                    f.write(html)


def _insert_get_ipython(nb):
    # so pyflakes doesn't get confused about magics, and also doesn't
    # complain about this if magics not present.
    if len(nb['cells']) > 0:
        get_ipython_cell = nb['cells'][0].copy()
        get_ipython_cell.source = 'from IPython import get_ipython\nget_ipython()'
        nb['cells'].insert(0,get_ipython_cell)


import pyflakes.api as flakes
class LintNb(pytest.Item):
    def runtest(self):
        with io.open(self.name,encoding='utf8') as nbfile:
            nb = nbformat.read(nbfile, as_version=4)
            _insert_get_ipython(nb)
            py, resources = nbconvert.PythonExporter().from_notebook_node(nb)
            if sys.version_info[0]==2:
                # notebooks will start with "coding: utf-8", but py already unicode
                py = py.encode('utf8')
            if flakes.check(py,self.name) != 0:
                raise AssertionError


class IPyNbFile(pytest.File):
    def __init__(self, fspath, parent=None, config=None, session=None, dowhat=RunNb):
        self._dowhat = dowhat
        super(IPyNbFile,self).__init__(fspath, parent=parent, config=None, session=None)

    def collect(self):
        yield self._dowhat(str(self.fspath), self)

def pytest_collect_file(path, parent):
    opt = parent.config.option
    # TODO: Make this pattern standard/configurable.
    # match .ipynb except .nbval.ipynb
    if re.match("^((?!\.nbval).)*\.ipynb$",path.strpath,re.IGNORECASE):
        if opt.nbsane_run or opt.nbsane_lint:
            # TODO express via the options system if you ever figure it out
            assert opt.nbsane_run ^ opt.nbsane_lint
            if opt.nbsane_run:
                dowhat = RunNb
            elif opt.nbsane_lint:
                dowhat = LintNb
            return IPyNbFile(path, parent, dowhat=dowhat)
