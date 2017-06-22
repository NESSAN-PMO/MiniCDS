# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
This is an Astropy affiliated package.
"""

# Affiliated packages may add whatever they like to this file, but
# should keep this content at the top.
# ----------------------------------------------------------------------------
from ._astropy_init import *
# ----------------------------------------------------------------------------

if not _ASTROPY_SETUP_:
    # For egg_info test builds to pass, put package imports here.

    pass

from astropy import config as _config
class Conf( _config.ConfigNamespace ):

    host = _config.ConfigItem(
            '0.0.0.0',
            'Listening this address.' )
    server_port = _config.ConfigItem(
            9000,
            'Listening this port.' )
    loglevel = _config.ConfigItem(
            "DEBUG",
            "Log level of astropy logging system." )
    ucac4_path = _config.ConfigItem(
            "/data/catalog/ucac4/u4b"
            'UCAC4 data file location' )

conf = Conf()
