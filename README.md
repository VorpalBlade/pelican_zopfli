# Zopfli Gzip cache

This is a variant of [gzip_cache] but using [zopfli] for better compression.

Certain web servers (e.g., Nginx) can use a static cache of gzip-compressed
files to prevent the server from compressing files during an HTTP call. Since
compression occurs at another time, these compressed files can be compressed
at a higher compression level for increased optimization.

Since zopfli is slow, this plugin uses joblib to compress files in parallel.

The ``pelican-zopfli`` plugin compresses all common text type files into a
``.gz`` file within the same directory as the original file.

## Installation

The easiest option is to install via pip from PyPI:

```
pip install pelican-zopfli
```

It is also possible to simply clone the git repository and put it in a directory
listed in ``PLUGIN_PATHS`` in your ``pelicanconf.py``:

```
git clone https://github.com/VorpalBlade/pelican_zopfli.git
```

In both cases you will then have to enable the plugin by putting
``pelican_zopfli`` into ``PLUGINS`` in your pelican configuration. It is
a good idea to only do this in your ``publishconf.py`` since this plugin is
quite slow.

## Settings

* `PELICAN_ZOPFLI_OVERWRITE`
  If True, the original files will be replaced by the gzip-compressed files. 
  This is useful for static hosting services (e.g S3). Defaults to False.
  
 [gzip_cache]: <https://github.com/getpelican/pelican-plugins/tree/master/gzip_cache>
 [zopfli]: <https://github.com/google/zopfli>
 