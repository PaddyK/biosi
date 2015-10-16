import os
import sys

path = os.path.dirname(os.path.realpath(__file__))
path = os.path.abspath(os.path.join(path, os.path.pardir))
# Path to model and other packages
sys.path.insert(0, path)
# Path to submodules
sys.path.insert(0, os.path.join(path, 'nanomsg'))
