from swagger_generator.template import *
from swagger_generator.insert import *
from swagger_generator import util
from swagger_generator import swagger_info
from swagger_generator.template_arg import TemplateArg
from swagger_generator.data_type import DataType


import sys

if sys.version_info < (3, 7):
    raise Exception("Must be using at least Python 3.7")

__version__ = "1.0.5"