# utils.py
"""Utility functions for pdc_struct"""

from typing import Tuple, Type
from .types import is_optional_type
from .exc import StructUnpackError


def create_field_bitmap(model: 'StructModel') -> Tuple[bytes, list]:
    """Create a bitmap of present optional fields in a model instance.

    Generates a bitmap indicating which optional fields are present in the model,
    along with a list of field names that should be included in the struct.

    Args:
        model: The StructModel instance to analyze.

    Returns:
        A tuple containing:
            - bytes: The bitmap as bytes, with first byte indicating bitmap length
            - list: Names of fields to include in the struct

    Example:
        For a model with optional fields 'a' and 'b', where only 'a' is present:
        >>> bitmap, fields = create_field_bitmap(model)
        >>> bitmap.hex()
        '0180'  # 1 byte length, followed by bitmap with first bit set
    """
    optional_fields = [
        (name, field)
        for name, field in model.model_fields.items()
        if is_optional_type(field.annotation)
    ]

    if not optional_fields:
        return bytes([0]), list(model.model_fields.keys())

    # Calculate number of bytes needed for bitmap
    num_fields = len(optional_fields)
    num_bytes = (num_fields + 7) // 8  # Round up to nearest byte

    # Create bitmap
    bitmap = bytearray(num_bytes + 1)  # +1 for length byte
    bitmap[0] = num_bytes  # First byte is length

    # Track which fields are present
    present_fields = [name for name, field in model.model_fields.items()
                     if not is_optional_type(field.annotation)]

    # Set bits for present optional fields
    for i, (name, field) in enumerate(optional_fields):
        byte_index = 1 + (i // 8)
        bit_index = i % 8
        value = getattr(model, name, None)
        if value is not None:
            bitmap[byte_index] |= (1 << bit_index)
            present_fields.append(name)

    return bytes(bitmap), present_fields


def parse_field_bitmap(data: bytes, model_cls: Type['StructModel']) -> Tuple[bytes, list]:
    """Parse field bitmap from start of data.

    Args:
        data: The packed struct data starting with the bitmap.
        model_cls: The StructModel class to use for field information.

    Returns:
        A tuple containing:
            - bytes: The remaining data after the bitmap
            - list: Names of fields present in the packed data

    Raises:
        StructUnpackError: If the data is too short or bitmap is invalid.
    """
    if not data:
        raise StructUnpackError("No data for field bitmap")

    bitmap_length = data[0]

    # Special case: if first byte is 0 and no fields have values
    if bitmap_length == 0:
        # Check if all fields are optional and the model was empty
        if all(is_optional_type(field.annotation) for field in model_cls.model_fields.values()):
            return data[1:], []
        # Otherwise, include all fields
        return data[1:], list(model_cls.model_fields.keys())

    if len(data) < bitmap_length + 1:
        raise StructUnpackError("Data too short for field bitmap")

    bitmap = data[1:bitmap_length + 1]
    remaining_data = data[bitmap_length + 1:]

    # Get all required fields
    present_fields = [name for name, field in model_cls.model_fields.items()
                      if not is_optional_type(field.annotation)]

    # Add present optional fields based on bitmap
    optional_fields = [
        (name, field)
        for name, field in model_cls.model_fields.items()
        if is_optional_type(field.annotation)
    ]

    for i, (name, field) in enumerate(optional_fields):
        byte_index = i // 8
        bit_index = i % 8
        if byte_index < len(bitmap) and bitmap[byte_index] & (1 << bit_index):
            present_fields.append(name)

    return remaining_data, present_fields
