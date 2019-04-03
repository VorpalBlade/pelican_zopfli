# Zopfli Gzip cache

This is a variant of [gzip_cache] but using [zopfli] for better compression.

Since zopfli is slow, this also uses joblib to compress files in parallel.

You need to install zopflipy and joblib:

```
pip install zopflipy joblib
```

Certain web servers (e.g., Nginx) can use a static cache of gzip-compressed
files to prevent the server from compressing files during an HTTP call. Since
compression occurs at another time, these compressed files can be compressed
at a higher compression level for increased optimization.

The ``pelican-zopfli`` plugin compresses all common text type files into a ``.gz``
file within the same directory as the original file.

# Settings

* `GZIP_CACHE_OVERWRITE`
  If True, the original files will be replaced by the gzip-compressed files. 
  This is useful for static hosting services (e.g S3). Defaults to False.
  
 [gzip_cache]: <https://github.com/getpelican/pelican-plugins/tree/master/gzip_cache>
 [zopfli]: <https://github.com/google/zopfli>
 