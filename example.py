"""
Example usage of pdc_struct module demonstrating various features.
"""

from typing import Optional, Union
from pydantic import Field
from pdc_struct import (
    StructConfig,
    StructMode,
    StructModel,
    ByteOrder,
    StructVersion,
)

class DynamicModel(StructModel):
    """Test model in DYNAMIC mode"""
    int_field: int = Field(description="Integer field")
    float_field: float = Field(description="Float field")
    string_field: str = Field(
        max_length=10,
        # struct_length=10,
        description="String field"
    )
    bool_field: bool = Field(description="Boolean field")

    struct_config = StructConfig(
        mode=StructMode.DYNAMIC,
        version=StructVersion.V1,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )

