#!/usr/bin/env python

import unittest
import os
import sys
import tempfile
import shutil
import subprocess

class Common(object):
    """
    Variables and methods for common use in different tests.
    """
    PDF2HTMLEX_PATH = "/usr/local/bin/pdf2htmlEX" # defined in CMakeLists.txt
    if not os.path.isfile(PDF2HTMLEX_PATH) or not os.access(PDF2HTMLEX_PATH, os.X_OK):
        print >> sys.stderr, "Cannot locate pdf2htmlEX executable, expected at ", PDF2HTMLEX_PATH,
        ". Make sure source was built before running this test."
        exit(1)

    SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TEST_DIR = os.path.join(SRC_DIR, 'test')
    DATA_DIR = os.path.join(SRC_DIR, 'share')

    GENERATING_MODE = bool(os.environ.get('P2H_TEST_GEN'))

    # temporary directories defined in CMakeLists.txt:
    TMPDIR = "/tmp/pdf2htmlEX/tmp"
    PNGDIR = "/tmp/pdf2htmlEX/png"
    DATDIR = "/tmp/pdf2htmlEX/dat"
    OUTDIR = "/tmp/pdf2htmlEX/out"

    def setUp(self):
        # filter manifest
        with open(os.path.join(self.DATA_DIR, 'manifest')) as inf:
            with open(os.path.join(self.DATDIR, 'manifest'), 'w') as outf:
                ignore = False
                for line in inf:
                    if ignore:
                        if line.startswith('#TEST_IGNORE_END'):
                            ignore = False
                    elif line.startswith('#TEST_IGNORE_BEGIN'):
                        ignore = True
                    else:
                        outf.write(line)

        # copy files
        shutil.copy(os.path.join(self.DATA_DIR, 'base.min.css'),
                os.path.join(self.DATDIR, 'base.min.css'))
        shutil.copy(os.path.join(self.TEST_DIR, 'fancy.min.css'),
                os.path.join(self.DATDIR, 'fancy.min.css'))

    def run_pdf2htmlEX(self, args):
        """
        Execute the pdf2htmlEX with the specified arguments.

        :type args: list of values
        :param args: list of arguments to pass to executable.
        :return: an object of relevant info
        """

        shutil.rmtree(self.TMPDIR, ignore_errors=False, onerror=None)
        os.mkdir(self.TMPDIR)

        args = [Common.PDF2HTMLEX_PATH,
               '--data-dir', self.DATDIR,
               '--dest-dir', self.TMPDIR
              ] + args

        with open(os.devnull, 'w') as fnull:
            return_code = subprocess.call(list(map(str, args)), stderr=fnull)

        self.assertEquals(return_code, 0, 'cannot execute pdf2htmlEX')

        files = os.listdir(self.TMPDIR)
        for file in files:
            shutil.copy(os.path.join(self.TMPDIR,file), self.OUTDIR)

        return {
            'return_code' : return_code,
            'output_files' : files
        }
