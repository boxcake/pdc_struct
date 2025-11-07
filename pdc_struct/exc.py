# exc.py
"""Exceptions for pdc_struct"""


class StructPackError(Exception):
    """Raised when there is an error packing data into bytes"""

    pass


class StructUnpackError(Exception):
    """Raised when there is an error unpacking bytes into a model"""

    pass
