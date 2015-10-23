""" Depending on settings makes common and special sources available
"""
USECDAQ = False
from sources import FileSource
from sources import SourceFactory
if USECDAQ:
    from CdaqSource import CdaqSource
