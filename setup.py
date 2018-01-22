"""
Setup module for the display_xml python package
"""
import setuptools
from setupbase import (
    ensure_python, find_packages
    )

setup_dict = dict(
    name='display_xml',
    description='Prettier XML in IPython/Jupyter display contexts.',
    packages=find_packages(),
    author          = 'M Pacer',
    author_email    = 'mpacer@berkeley.edu',
    url             = 'https://github.com/mpacer/display_xml',
    license         = 'BSD',
    platforms       = "Linux, Mac OS X, Windows",
    keywords        = ['Jupyter', 'JupyterLab', 'XML'],
    python_requires = '>=3.6',
    classifiers     = [
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'Pygments>=2.2.0',
        'ipython>=6.2.1',
        'lxml>=4.1.1'
    ]
)

try:
    ensure_python(setup_dict["python_requires"].split(','))
except ValueError as e:
    raise  ValueError("{:s}, to use {} you must use python {} ".format(
                          e,
                          setup_dict["name"],
                          setup_dict["python_requires"])
                     )

from display_xml import __version__

setuptools.setup(
    version=__version__,
    **setup_dict
)