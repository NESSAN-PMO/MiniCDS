# -*- coding: utf-8 -*-
"""Allow minicds to be executable through `python -m minicds`."""
from __future__ import absolute_import

from .cdsserver import main


if __name__ == "__main__":  # pragma: no cover
    main(prog_name="minicds")
