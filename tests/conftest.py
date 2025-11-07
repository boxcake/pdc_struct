"""tests/conftest.py PyTest test fixtures"""


import pytest
from typing import Optional
from pydantic import Field
from pdc_struct import StructModel, StructConfig, ByteOrder, StructVersion
from pdc_struct.enums import StructMode


class DynamicModel(StructModel):
    """Test model in DYNAMIC mode"""

    int_field: int = Field(description="Integer field")
    float_field: float = Field(description="Float field")
    string_field: str = Field(
        max_length=10, struct_length=10, description="String field"
    )
    bool_field: bool = Field(description="Boolean field")

    struct_config = StructConfig(
        mode=StructMode.DYNAMIC,
        version=StructVersion.V1,
        byte_order=ByteOrder.LITTLE_ENDIAN,
    )


class CCompatibleModel(StructModel):
    """Test model in C_COMPATIBLE mode"""

    int_field: int = Field(description="Integer field")
    float_field: float = Field(description="Float field")
    string_field: str = Field(
        max_length=10, struct_length=10, description="String field"
    )
    bool_field: bool = Field(description="Boolean field")

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        version=StructVersion.V1,
        byte_order=ByteOrder.LITTLE_ENDIAN,
    )


@pytest.fixture
def dynamic_model():
    """Fixture for dynamic model"""
    return DynamicModel(
        int_field=42, float_field=3.14159, string_field="test data", bool_field=True
    )


@pytest.fixture
def c_compatible_model():
    """Fixture for c_compatible model"""
    return CCompatibleModel(
        int_field=42, float_field=3.14159, string_field="test data", bool_field=True
    )


# Basic Models - Dynamic Mode
class AllTypesDynamicModel(StructModel):
    """Test model containing all basic field types - Dynamic Mode"""

    int_field: int = Field(description="Integer field")
    float_field: float = Field(description="Float field")
    string_field: str = Field(
        max_length=10, struct_length=10, description="String field"
    )
    bool_field: bool = Field(description="Boolean field")

    struct_config = StructConfig(
        mode=StructMode.DYNAMIC,
        version=StructVersion.V1,
        byte_order=ByteOrder.LITTLE_ENDIAN,
    )


# Basic Models - C Compatible Mode
class AllTypesCCompatibleModel(StructModel):
    """Test model containing all basic field types - C Compatible Mode"""

    int_field: int = Field(description="Integer field")
    float_field: float = Field(description="Float field")
    string_field: str = Field(
        max_length=10, struct_length=10, description="String field"
    )
    bool_field: bool = Field(description="Boolean field")

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        version=StructVersion.V1,
        byte_order=ByteOrder.LITTLE_ENDIAN,
    )


# Optional Fields Model - Dynamic Mode Only
class OptionalFieldsModel(StructModel):
    """Test model containing optional fields (Dynamic Mode only)"""

    required_int: int = Field(description="Required integer field")
    required_string: str = Field(max_length=15, description="Required string field")
    optional_float: Optional[float] = Field(None, description="Optional float field")
    optional_string: Optional[str] = Field(
        None, max_length=20, description="Optional string field"
    )
    optional_bool: Optional[bool] = Field(None, description="Optional boolean field")

    struct_config = StructConfig(
        mode=StructMode.DYNAMIC,
        version=StructVersion.V1,
        byte_order=ByteOrder.LITTLE_ENDIAN,
    )


# Optional Fields Model - Dynamic Mode Only
class AllOptionalFieldsModel(StructModel):
    """Test model containing only optional fields (Dynamic Mode only)"""

    optional_float: Optional[float] = Field(None, description="Optional float field")
    optional_string: Optional[str] = Field(
        None, max_length=20, description="Optional string field"
    )
    optional_bool: Optional[bool] = Field(None, description="Optional boolean field")

    struct_config = StructConfig(
        mode=StructMode.DYNAMIC,
        version=StructVersion.V1,
        byte_order=ByteOrder.LITTLE_ENDIAN,
    )


# String Models
class StringDynamicModel(StructModel):
    """Test model with different string configurations - Dynamic Mode"""

    exact_str: str = Field(max_length=10, description="String exactly at max length")
    short_str: str = Field(max_length=20, description="String shorter than max length")
    utf8_str: str = Field(max_length=30, description="String with UTF-8 characters")

    struct_config = StructConfig(
        mode=StructMode.DYNAMIC,
        version=StructVersion.V1,
        byte_order=ByteOrder.LITTLE_ENDIAN,
    )


class StringCCompatibleModel(StructModel):
    """Test model with different string configurations - C Compatible Mode"""

    exact_str: str = Field(max_length=10, description="String exactly at max length")
    short_str: str = Field(max_length=20, description="String shorter than max length")
    utf8_str: str = Field(max_length=30, description="String with UTF-8 characters")

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        version=StructVersion.V1,
        byte_order=ByteOrder.LITTLE_ENDIAN,
    )


# Endianness Models
class BigEndianDynamicModel(StructModel):
    """Test model using big-endian byte order - Dynamic Mode"""

    int_field: int = Field(description="Integer field")
    float_field: float = Field(description="Float field")
    string_field: str = Field(max_length=10, description="String field")

    struct_config = StructConfig(
        mode=StructMode.DYNAMIC,
        version=StructVersion.V1,
        byte_order=ByteOrder.BIG_ENDIAN,
    )


class BigEndianCCompatibleModel(StructModel):
    """Test model using big-endian byte order - C Compatible Mode"""

    int_field: int = Field(description="Integer field")
    float_field: float = Field(description="Float field")
    string_field: str = Field(max_length=10, description="String field")

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        version=StructVersion.V1,
        byte_order=ByteOrder.BIG_ENDIAN,
    )


# Fixtures
@pytest.fixture
def all_types_dynamic_model():
    """Fixture providing an instance of AllTypesDynamicModel with test data"""
    return AllTypesDynamicModel(
        int_field=42, float_field=3.14159, string_field="test data", bool_field=True
    )


@pytest.fixture
def all_types_c_compatible_model():
    """Fixture providing an instance of AllTypesCCompatibleModel with test data"""
    return AllTypesCCompatibleModel(
        int_field=42, float_field=3.14159, string_field="test data", bool_field=True
    )


@pytest.fixture
def optional_fields_model():
    """Fixture providing an instance of OptionalFieldsModel with some fields set"""
    return OptionalFieldsModel(
        required_int=42,
        required_string="required",
        optional_float=3.14159,
        optional_string="optional",
        # optional_bool intentionally left unset
    )


@pytest.fixture
def optional_fields_model_all_unset():
    """Fixture providing an instance of OptionalFieldsModel with no fields set"""
    return AllOptionalFieldsModel()


@pytest.fixture
def string_dynamic_model():
    """Fixture providing an instance of StringDynamicModel with test strings"""
    return StringDynamicModel(
        exact_str="exactlen10",  # Exactly 10 chars
        short_str="short",  # Less than 20 chars
        utf8_str="Hello 世界",  # UTF-8 characters
    )


@pytest.fixture
def string_c_compatible_model():
    """Fixture providing an instance of StringCCompatibleModel with test strings"""
    return StringCCompatibleModel(
        exact_str="exactlen10",  # Exactly 10 chars
        short_str="short",  # Less than 20 chars
        utf8_str="Hello 世界",  # UTF-8 characters
    )


@pytest.fixture
def big_endian_dynamic_model():
    """Fixture providing an instance of BigEndianDynamicModel with test data"""
    return BigEndianDynamicModel(
        int_field=42, float_field=3.14159, string_field="big endian"
    )


@pytest.fixture
def big_endian_c_compatible_model():
    """Fixture providing an instance of BigEndianCCompatibleModel with test data"""
    return BigEndianCCompatibleModel(
        int_field=42, float_field=3.14159, string_field="big endian"
    )
