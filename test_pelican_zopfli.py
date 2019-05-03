# pelican_zopfli - A plugin to create .gz cache files for optimization.
# Copyright (c) 2012 Matt Layman
# Copyright (C) 2019 Arvid Norlander
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Core plugins unit tests"""

import os
import tempfile
import time
import unittest
from contextlib import contextmanager
from hashlib import md5
from shutil import rmtree
from tempfile import mkdtemp

import pelican_zopfli


@contextmanager
def temporary_folder():
    """creates a temporary folder, return it and delete it afterwards.

    This allows to do something like this in tests:

        >>> with temporary_folder() as d:
            # do whatever you want
    """
    tempdir = mkdtemp()
    try:
        yield tempdir
    finally:
        rmtree(tempdir)


class TestPelicanZopfli(unittest.TestCase):
    def test_should_compress(self):
        # Some filetypes should compress and others shouldn't.
        self.assertTrue(pelican_zopfli.should_compress('foo.html'))
        self.assertTrue(pelican_zopfli.should_compress('bar.css'))
        self.assertTrue(pelican_zopfli.should_compress('baz.js'))
        self.assertTrue(pelican_zopfli.should_compress('foo.txt'))

        self.assertFalse(pelican_zopfli.should_compress('foo.gz'))
        self.assertFalse(pelican_zopfli.should_compress('bar.png'))
        self.assertFalse(pelican_zopfli.should_compress('baz.mp3'))
        self.assertFalse(pelican_zopfli.should_compress('foo.mov'))

    def test_should_overwrite(self):
        # Default to false if pelican_zopfli_OVERWRITE is not set
        settings = {}
        self.assertFalse(pelican_zopfli.should_overwrite(settings))
        settings = {'PELICAN_ZOPFLI_OVERWRITE': False}
        self.assertFalse(pelican_zopfli.should_overwrite(settings))
        settings = {'PELICAN_ZOPFLI_OVERWRITE': True}
        self.assertTrue(pelican_zopfli.should_overwrite(settings))

    def test_creates_gzip_file(self):
        # A file matching the input filename with a .gz extension is created.

        # The plugin walks over the output content after the finalized signal
        # so it is safe to assume that the file exists (otherwise walk would
        # not report it). Therefore, create a dummy file to use.
        with temporary_folder() as tempdir:
            html_fd, a_html_filename = tempfile.mkstemp(suffix='.html',
                                                        dir=tempdir)
            with os.fdopen(html_fd, mode='w') as tmp_f:
                tmp_f.write("Some compressible test data " + '0' * 32)
            pelican_zopfli.create_gzip_file(a_html_filename, False)
            self.assertTrue(os.path.exists(a_html_filename + '.gz'))

    def test_skips_gzip_file_when_uncompressible(self):
        # A file matching the input filename with a .gz extension is created.

        # The plugin walks over the output content after the finalized signal
        # so it is safe to assume that the file exists (otherwise walk would
        # not report it). Therefore, create a dummy file to use.
        with temporary_folder() as tempdir:
            html_fd, a_html_filename = tempfile.mkstemp(suffix='.html',
                                                        dir=tempdir)
            # Write some uncompressible data
            with os.fdopen(html_fd, mode='w') as tmp_f:
                tmp_f.write("X")
            pelican_zopfli.create_gzip_file(a_html_filename, False)
            self.assertFalse(os.path.exists(a_html_filename + '.gz'))

    def test_creates_same_gzip_file(self):
        # Should create the same gzip file from the same contents.

        # gzip will create a slightly different file because it includes
        # a timestamp in the compressed file by default. This can cause
        # problems for some caching strategies.
        with temporary_folder() as tempdir:
            html_fd, a_html_filename = tempfile.mkstemp(suffix='.html',
                                                        dir=tempdir)
            with os.fdopen(html_fd, mode='w') as tmp_f:
                tmp_f.write("Some compressible test data " + '0' * 32)
            a_gz_filename = a_html_filename + '.gz'
            pelican_zopfli.create_gzip_file(a_html_filename, False)
            gzip_hash = get_md5(a_gz_filename)
            time.sleep(1)
            pelican_zopfli.create_gzip_file(a_html_filename, False)
            self.assertEqual(gzip_hash, get_md5(a_gz_filename))

    def test_overwrites_gzip_file(self):
        # A file matching the input filename with a .gz extension is not created.

        # The plugin walks over the output content after the finalized signal
        # so it is safe to assume that the file exists (otherwise walk would
        # not report it). Therefore, create a dummy file to use.
        with temporary_folder() as tempdir:
            _, a_html_filename = tempfile.mkstemp(suffix='.html', dir=tempdir)
            pelican_zopfli.create_gzip_file(a_html_filename, True)
            self.assertFalse(os.path.exists(a_html_filename + '.gz'))


def get_md5(filepath):
    with open(filepath, 'rb') as fh:
        return md5(fh.read()).hexdigest()
