"""Test BitFieldModel functionality."""


from pdc_struct import (
    BitFieldModel,
    StructConfig,
    Bit,
)


def test_bitfield_inheritance():
    """Test inheriting from multiple BitFieldModel classes."""

    class BaseField1(BitFieldModel):
        flag_a: bool = Bit(0)
        flag_b: bool = Bit(1)
        struct_config = StructConfig(bit_width=8)

    class BaseField2(BitFieldModel):
        flag_c: bool = Bit(2)
        flag_d: bool = Bit(3)
        struct_config = StructConfig(bit_width=8)

    class CombinedField(BaseField1, BaseField2):
        pass  # Should inherit all bit definitions

    # Create instance and verify bit positions are maintained
    combined = CombinedField(flag_a=True, flag_b=False, flag_c=True, flag_d=False)

    # Expected packed value: 0b0101 (bits 0 and 2 set)
    expected = 5
    assert combined.packed_value == expected

    # Test individual flag access
    assert combined.flag_a is True
    assert combined.flag_b is False
    assert combined.flag_c is True
    assert combined.flag_d is False

    # Test initialization from packed value
    from_packed = CombinedField(packed_value=5)
    assert from_packed.flag_a is True
    assert from_packed.flag_b is False
    assert from_packed.flag_c is True
    assert from_packed.flag_d is False
