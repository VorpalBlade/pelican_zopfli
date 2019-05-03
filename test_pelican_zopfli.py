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
from hashlib import sha512

import pelican_zopfli


def test_should_compress():
    # Some file types should compress and others shouldn't.
    assert pelican_zopfli.should_compress('foo.html')
    assert pelican_zopfli.should_compress('bar.css')
    assert pelican_zopfli.should_compress('baz.js')
    assert pelican_zopfli.should_compress('foo.txt')

    assert not pelican_zopfli.should_compress('foo.gz')
    assert not pelican_zopfli.should_compress('bar.png')
    assert not pelican_zopfli.should_compress('baz.mp3')
    assert not pelican_zopfli.should_compress('foo.mov')


def test_should_overwrite():
    # Default to false if pelican_zopfli_OVERWRITE is not set
    settings = {}
    assert not pelican_zopfli.should_overwrite(settings)
    settings = {'PELICAN_ZOPFLI_OVERWRITE': False}
    assert not pelican_zopfli.should_overwrite(settings)
    settings = {'PELICAN_ZOPFLI_OVERWRITE': True}
    assert pelican_zopfli.should_overwrite(settings)


def test_creates_gzip_file(tmpdir):
    # A file matching the input filename with a .gz extension is created.

    # The plugin walks over the output content after the finalized signal
    # so it is safe to assume that the file exists (otherwise walk would
    # not report it). Therefore, create a dummy file to use.
    html_fd, a_html_filename = tempfile.mkstemp(suffix='.html', dir=str(tmpdir))
    with os.fdopen(html_fd, mode='w') as tmp_f:
        tmp_f.write("Some compressible test data " + '0' * 32)
    pelican_zopfli.create_gzip_file(a_html_filename, False)
    assert os.path.exists(a_html_filename + '.gz')


def test_skips_gzip_file_when_uncompressible(tmpdir):
    # A file matching the input filename with a .gz extension is created.

    # The plugin walks over the output content after the finalized signal
    # so it is safe to assume that the file exists (otherwise walk would
    # not report it). Therefore, create a dummy file to use.
    html_fd, a_html_filename = tempfile.mkstemp(suffix='.html', dir=str(tmpdir))
    # Write some uncompressible data
    with os.fdopen(html_fd, mode='w') as tmp_f:
        tmp_f.write("X")
    pelican_zopfli.create_gzip_file(a_html_filename, False)
    assert not os.path.exists(a_html_filename + '.gz')


def test_creates_same_gzip_file(tmpdir):
    # Should create the same gzip file from the same contents.

    # gzip will create a slightly different file because it includes
    # a timestamp in the compressed file by default. This can cause
    # problems for some caching strategies.
    html_fd, a_html_filename = tempfile.mkstemp(suffix='.html', dir=str(tmpdir))
    with os.fdopen(html_fd, mode='w') as tmp_f:
        tmp_f.write("Some compressible test data " + '0' * 32)
    a_gz_filename = a_html_filename + '.gz'
    pelican_zopfli.create_gzip_file(a_html_filename, False)
    gzip_hash = get_hash(a_gz_filename)
    time.sleep(1)
    pelican_zopfli.create_gzip_file(a_html_filename, False)
    assert gzip_hash == get_hash(a_gz_filename)


def test_overwrites_gzip_file(tmpdir):
    # A file matching the input filename with a .gz extension is not created.

    # The plugin walks over the output content after the finalized signal
    # so it is safe to assume that the file exists (otherwise walk would
    # not report it). Therefore, create a dummy file to use.
    _, a_html_filename = tempfile.mkstemp(suffix='.html', dir=str(tmpdir))
    pelican_zopfli.create_gzip_file(a_html_filename, True)
    assert not os.path.exists(a_html_filename + '.gz')


def get_hash(filepath):
    with open(filepath, 'rb') as fh:
        return sha512(fh.read()).hexdigest()
