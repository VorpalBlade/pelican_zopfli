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

"""
pelican_zopfli
--------------

A plugin to create .gz cache files for optimization.
"""

import logging
import os
from typing import Any, Mapping

import zopfli
from joblib import Parallel, delayed, parallel_backend
from pelican import signals, Pelican

logger = logging.getLogger(__name__)

# A list of file types to exclude from possible compression
EXCLUDE_TYPES = {
    # Compressed types
    '.bz2',
    '.gz',

    # Audio types
    '.aac',
    '.flac',
    '.mp3',
    '.wma',

    # Image types
    '.gif',
    '.jpg',
    '.jpeg',
    '.png',

    # Video types
    '.avi',
    '.mov',
    '.mp4',
    '.webm',

    # Internally-compressed fonts. gzip can often shave ~50 more bytes off,
    # but it's not worth it.
    '.woff',
    '.woff2',
}

# Determines level of compression
ZOPFLI_ITERATIONS = 15


def create_gzip_cache(pelican: Pelican):
    """Create a gzip cache file for every file that a webserver would
    reasonably want to cache (e.g., text type files).

    :param pelican: The Pelican instance
    """
    to_process = []
    for dirpath, _, filenames in os.walk(pelican.settings['OUTPUT_PATH']):
        for name in filenames:
            if should_compress(name):
                to_process.append(os.path.join(dirpath, name))

    overwrite = should_overwrite(pelican.settings)

    with parallel_backend('threading'):
        Parallel()(delayed(create_gzip_file)(e, overwrite) for e in to_process)


def should_compress(filename: str):
    """Check if the filename is a type of file that should be compressed.

    :param filename: A file name to check against
    """
    for extension in EXCLUDE_TYPES:
        if filename.endswith(extension):
            return False

    return True


def should_overwrite(settings: Mapping[str, Any]):
    """Check if the gzipped files should overwrite the originals.

    :param settings: The pelican instance settings
    """
    return settings.get('PELICAN_ZOPFLI_OVERWRITE',
                        settings.get('GZIP_CACHE_OVERWRITE', False))


def create_gzip_file(filepath: str, overwrite: bool):
    """Create a gzipped file in the same directory with a filepath.gz name.

    :param filepath: A file to compress
    :param overwrite: Whether the original file should be overwritten
    """
    compressed_path = filepath + '.gz'

    with open(filepath, 'rb') as uncompressed:
        gzip_compress_obj = zopfli.ZopfliCompressor(zopfli.ZOPFLI_FORMAT_GZIP,
                                                    iterations=ZOPFLI_ITERATIONS)

        uncompressed_data = uncompressed.read()
        gzipped_data = gzip_compress_obj.compress(uncompressed_data)
        gzipped_data += gzip_compress_obj.flush()

        if len(gzipped_data) >= len(uncompressed_data):
            logger.debug('No improvement: %s' % filepath)
            return

        with open(compressed_path, 'wb') as compressed:
            logger.debug('Compressing: %s' % filepath)
            try:
                compressed.write(gzipped_data)
            except Exception as ex:
                logger.critical('Gzip compression failed: %s' % ex)

        if overwrite:
            logger.debug('Overwriting: %s with %s' % (filepath, compressed_path))
            os.remove(filepath)
            os.rename(compressed_path, filepath)


def register():
    signals.finalized.connect(create_gzip_cache)
