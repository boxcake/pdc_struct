from pdc_struct import (
    StructModel,
    StructConfig,
    StructMode,
    ByteOrder,
    BitFieldModel,
    Bit
)


class InvalidWidth(BitFieldModel):
    x: bool = Bit(0)
    struct_config = StructConfig(bit_width=12)  # Invalid width

