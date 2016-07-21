"""Setup file for Pokemon Go Map
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

    setup(name='pokemongo-map',
          version='1.0.0',
          description='PokemonGo Map installer. This is an independent project from the Pokemon Go Map',
          long_description=long_description,
          url='https://github.com/Darkade/pokemongo-map-pip',
          author='Ivan Reyes',
          author_email='',
          license='MIT',
          classifiers=['Development Status :: 3 - Alpha',
                       'Intended Audience :: Other Audience',
                       'Topic :: Games/Entertainment',
                       'Topic :: Games/Entertainment :: Puzzle Games',
                       'Topic :: Games/Entertainment :: Role-Playing',
                       'License :: OSI Approved :: MIT License',
                       'Programming Language :: Python :: 2.7',
                       ],
          keywords='pokemon pokemongo map',
          package_dir={'': 'pokemongomap'},
          packages= ['pogom.pgoapi.protos'],
          install_requires=['ConfigArgParse==0.10.0',
                            'Flask>=0.11.1',
                            'Flask-Cors==2.1.2',
                            'Flask-Compress==1.3.0',
                            'Jinja2>=2.8',
                            'MarkupSafe>=0.23',
                            'Werkzeug>=0.11.10',
                            'argparse>=1.2.1',
                            'click>=6.6',
                            'itsdangerous>=0.24',
                            'peewee>=2.8.1',
                            'wsgiref>=0.1.2',
                            'geopy>=1.11.0',
                            'protobuf>=2.6.1',
                            'requests>=2.10.0',
                            's2sphere>=0.2.4',
                            'gpsoauth>=0.3.0',
                            'protobuf-to-dict>=0.1.0'],
          extras_require={'dev': [''],
                          'test': ['']},

          package_data={'pokemongomap': ['static/dist', 'templates']},

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
          entry_points={'console_scripts': ['pokemap=runserver:main']},
        )
