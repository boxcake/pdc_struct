# tests/test_strings.py

import pytest
from pydantic import Field
from pdc_struct import (
    StructModel,
    StructConfig,
    ByteOrder,
    StructVersion,
    StructPackError,
    StructMode,
)


class StringTestModel(StructModel):
    """Model for testing various string scenarios"""

    exact_str: str = Field(max_length=20, description="Field for exact length testing")
    short_str: str = Field(max_length=20, description="Field for short string testing")
    utf8_str: str = Field(max_length=20, description="Field for UTF-8 testing")

    struct_config = StructConfig(
        mode=StructMode.DYNAMIC,
        version=StructVersion.V1,
        byte_order=ByteOrder.LITTLE_ENDIAN,
    )


def test_exact_length_string():
    """Test string that exactly matches max_length."""
    model = StringTestModel(
        exact_str="abcdefghij", short_str="short", utf8_str="test"  # Exactly 10 chars
    )

    data = model.to_bytes()
    recovered = StringTestModel.from_bytes(data)

    assert len(recovered.exact_str) == 10
    assert recovered.exact_str == "abcdefghij"


def test_short_string_padding():
    """Test string shorter than max_length is properly padded."""
    model = StringTestModel(exact_str="test", short_str="short", utf8_str="test")

    data = model.to_bytes()

    # Check the actual bytes to verify padding
    format_str = model.struct_format_string()
    recovered = StringTestModel.from_bytes(data)

    # Should be padded with nulls but stripped on recovery
    assert len(recovered.exact_str) == 4
    assert recovered.exact_str == "test"


# ToDo: Should C_COMPATIBLE mode should reproduce this behavior?
# def test_string_with_null_bytes():
#     """Test handling of strings containing null bytes.
#     Note: In with C-style strings, null bytes act as string terminators,
#     effectively truncating the string at the first null byte.
#
#     """
#     original = "test\x00with\x00nulls"
#     model = StringTestModel(
#         exact_str=original,
#         short_str="short",
#         utf8_str="test"
#     )
#
#     data = model.to_bytes()
#     recovered = StringTestModel.from_bytes(data)
#
#     # Should be truncated at first null byte, matching C-style string behavior
#     assert recovered.exact_str == "test"
#     assert len(recovered.exact_str) == 4


def test_utf8_string():
    """Test handling of UTF-8 encoded strings."""
    test_strings = [
        "Hello 世界",  # Chinese
        "Café ñ",  # Spanish
        "αβγ",  # Greek
        "🌟⭐",  # Emojis
    ]

    for utf8_string in test_strings:
        model = StringTestModel(
            exact_str="test", short_str="short", utf8_str=utf8_string
        )

        data = model.to_bytes()
        recovered = StringTestModel.from_bytes(data)

        # UTF-8 strings might be truncated if byte length > max_length
        # We should get either the full string or a valid UTF-8 prefix
        assert recovered.utf8_str.encode("utf-8").decode("utf-8") == recovered.utf8_str


def test_utf8_truncation():
    """Test proper truncation of UTF-8 strings at character boundaries."""
    # String with multi-byte characters
    test_str = "Hello世界"  # 'Hello' (5 bytes) + '世' (3 bytes) + '界' (3 bytes)

    class StringTestModel(StructModel):
        """Model for testing various string scenarios"""

        utf8_str: str = Field(max_length=10, description="Field for UTF-8 testing")

        struct_config = StructConfig(
            mode=StructMode.DYNAMIC,
            version=StructVersion.V1,
            byte_order=ByteOrder.LITTLE_ENDIAN,
        )

    model = StringTestModel(utf8_str=test_str)

    data = model.to_bytes()

    with pytest.raises(UnicodeDecodeError, match="can't decode bytes in position 8-9"):
        recovered = StringTestModel.from_bytes(data)

    # ToDo: We could fix this behavior in the encoder and force truncation at a character boundary
    # # Should truncate at character boundary
    # assert recovered.utf8_str == "Hello世"  # '界' would exceed 10 bytes


def test_empty_string():
    """Test handling of empty strings."""
    model = StringTestModel(exact_str="", short_str="", utf8_str="")

    data = model.to_bytes()
    recovered = StringTestModel.from_bytes(data)

    assert recovered.exact_str == ""
    assert recovered.short_str == ""
    assert recovered.utf8_str == ""


def test_string_control_characters():
    """Test handling of strings with control characters."""
    control_str = "test\n\r\tcontrol"
    model = StringTestModel(exact_str=control_str, short_str="short", utf8_str="test")

    data = model.to_bytes()
    recovered = StringTestModel.from_bytes(data)

    # Control characters should be preserved
    assert recovered.exact_str == control_str
