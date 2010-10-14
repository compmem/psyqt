

from distutils.core import setup, Extension
from distutils.sysconfig import get_config_var
import os
import sys

setup(name='psyqt', 
      version='0.0.1',
      package_dir={"psyqt":"psyqt"},
      packages=['psyqt'],
      author=['Per B. Sederberg'],
      maintainer=['Per B. Sederberg'],
      maintainer_email=['psederberg@gmail.com'],
      url=['http://github.com/psederberg/psyqt'])

