from os.path import abspath, dirname, join, normpath

import setuptools

setuptools.setup(
    # Basic package information:
    name='pelican_zopfli',
    version='1.0.1',
    py_modules=('pelican_zopfli',),

    # Packaging options:
    include_package_data=True,

    # Package dependencies:
    install_requires=['zopflipy>=1.1', 'pelican>=4.0', 'joblib>=0.13.2'],

    # Metadata for PyPI:
    author='Arvid Norlander',
    author_email='VorpalBlade@users.noreply.github.com',
    license='AGPL-3.0',
    url='https://github.com/VorpalBlade/pelican_zopfli',
    keywords='pelican blog static compress zopfli',
    description=('An static resource compression plugin for Pelican, the '
                 'static site generator.'),
    long_description=open(normpath(join(dirname(abspath(__file__)),
                                        'README.md'))).read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Framework :: Pelican :: Plugins",
    ],
)
