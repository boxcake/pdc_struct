# PDC Struct Roadmap

This document outlines planned improvements and breaking changes for future versions of PDC Struct.

---

## High Priority

### 1. Migrate from Deprecated Field Usage (Pydantic v3 Compatibility)

**Status:** Required for Pydantic v3 compatibility
**Target Version:** 1.1.0
**Breaking Change:** Yes (API change)

#### Problem

The current implementation uses the deprecated Pydantic v1 pattern of passing arbitrary keyword arguments directly to `Field()`:

```python
sender_hw_addr: bytes = Field(struct_length=6, description="...")
string_field: str = Field(max_length=30, struct_length=10, description="...")
```

This pattern is **deprecated in Pydantic v2** and will be **removed in Pydantic v3**. According to Pydantic's migration guide:

> Using extra keyword arguments on Field is deprecated and will be removed. Use `json_schema_extra` instead. Deprecated in Pydantic V2.0 to be removed in V3.0.

#### Impact

This affects:
- **README.md examples** - Primary documentation showing deprecated pattern
- **tests/** - 15+ test files using `struct_length`, `max_length` as direct kwargs
- **docs/pydantic-feature-request.md** - Feature proposal examples
- **User code** - Any external users following current documentation

#### Proposed Solutions

##### Option A: Use `json_schema_extra` (Interim Solution)

Migrate to the current Pydantic v2 standard:

```python
sender_hw_addr: bytes = Field(
    json_schema_extra={"struct_length": 6},
    description="Sender hardware address (MAC)"
)
```

**Pros:**
- Compatible with current Pydantic v2
- Minimal code changes
- Clear separation of struct metadata from standard Field parameters

**Cons:**
- More verbose
- No type safety for struct-specific parameters
- Users must remember to use the dict syntax

##### Option B: Use `Annotated` with Custom Metadata (Recommended)

Leverage Pydantic v2's `Annotated` support for type-safe metadata:

```python
from typing import Annotated
from pdc_struct import StructLength

sender_hw_addr: Annotated[bytes, StructLength(6)] = Field(
    description="Sender hardware address (MAC)"
)

# For multiple struct attributes:
string_field: Annotated[str, StructLength(10), MaxLength(30)] = Field(
    description="String field"
)
```

**Implementation:**

```python
# pdc_struct/metadata.py
from pydantic import BaseMetadata

class StructLength(BaseMetadata):
    """Specify fixed byte length for struct serialization."""
    def __init__(self, length: int):
        self.length = length

class StructFormat(BaseMetadata):
    """Override default struct format character."""
    def __init__(self, format_char: str):
        self.format_char = format_char

class MaxLength(BaseMetadata):
    """Maximum length for strings (enforced during validation)."""
    def __init__(self, length: int):
        self.length = length
```

**Pros:**
- Type-safe metadata
- Cleaner syntax
- Follows modern Pydantic v2 best practices
- Better IDE support and autocomplete
- Clear separation between validation and serialization metadata
- Can stack multiple metadata annotations

**Cons:**
- Larger API change for users
- Requires Python 3.9+ for `Annotated` (already require 3.11+, so not an issue)
- More complex implementation

#### Migration Path

**Phase 1 (v1.1.0):**
1. Implement `Annotated` metadata classes
2. Update internal code to support both old and new APIs
3. Add deprecation warnings when using kwargs directly
4. Update all documentation and examples to new API
5. Provide migration guide

**Phase 2 (v1.2.0):**
1. Remove support for direct Field kwargs
2. Require `Annotated` syntax for struct metadata
3. Clean up internal compatibility code

#### Files Requiring Changes

**Core Implementation:**
- `pdc_struct/type_handler/meta.py` - Read metadata from Annotated
- `pdc_struct/models/bit_field.py` - Update Bit() helper
- All type handlers in `pdc_struct/type_handler/`

**Documentation:**
- `README.md` - Update all examples
- `docs/pydantic-feature-request.md` - Update proposal examples
- Create `MIGRATION.md` guide

**Tests:**
- `tests/test_basic.py`
- `tests/test_strings.py`
- `tests/test_bytes_endianness.py`
- All other test files using Field kwargs

---

## Medium Priority

### 2. C Struct Alignment / Padding Support

**Status:** Enhancement
**Target Version:** 1.2.0

#### Problem

C compilers align struct members to natural boundaries for CPU performance. A `uint32_t` is aligned to a 4-byte boundary, a `double` to 8 bytes, etc. This means C structs often contain invisible padding bytes:

```c
// Default C alignment - 12 bytes total, not 6!
struct Example {
    uint8_t  a;      // offset 0
    // 3 bytes padding
    uint32_t b;      // offset 4
    uint8_t  c;      // offset 8
    // 3 bytes padding (struct size rounds up to alignment)
};
```

Currently, pdc_struct produces tightly packed data with no padding, requiring C code to use `#pragma pack(1)` to interoperate.

#### Proposed Solution

Add an alignment mode to `StructConfig`:

```python
class StructConfig:
    mode: Mode = Mode.C_COMPATIBLE
    byte_order: ByteOrder = ByteOrder.NATIVE
    alignment: int = 1  # 1 = packed, 4 = 32-bit, 8 = 64-bit

class MyStruct(StructModel):
    struct_config = StructConfig(alignment=4)  # Match 32-bit C alignment

    a: UInt8
    b: UInt32  # Automatically padded to 4-byte boundary
    c: UInt8
    # Automatic end padding
```

#### Alignment Rules

For `alignment=N`, each field aligns to `min(sizeof(field), N)`:

| Type | Size | Alignment (N=4) | Alignment (N=8) |
|------|------|-----------------|-----------------|
| Int8/UInt8 | 1 | 1 | 1 |
| Int16/UInt16 | 2 | 2 | 2 |
| Int32/UInt32 | 4 | 4 | 4 |
| Int64/UInt64 | 8 | 4 | 8 |
| Float32 | 4 | 4 | 4 |
| Float64 | 8 | 4 | 8 |

#### Implementation Notes

- Add `alignment` parameter to `StructConfig`
- Calculate padding before each field based on current offset
- Add end padding so struct size is multiple of largest member alignment
- Provide `struct_padding()` helper for explicit padding fields
- Consider `Aligned[T, N]` annotation for per-field alignment override

### 3. Improve Annotated Type Support

**Status:** Enhancement
**Target Version:** 1.1.0

Currently, the codebase has some support for extracting types from `Annotated`, but it could be more comprehensive. With the migration to `Annotated` metadata, this becomes critical.

**Tasks:**
- Ensure all type handlers properly extract the base type from `Annotated`
- Support stacking multiple metadata annotations
- Add validation that ensures conflicting metadata raises clear errors

### 4. Enhanced BitField API

**Status:** Enhancement
**Target Version:** 1.2.0

The current `Bit()` function could be reimagined with `Annotated`:

```python
# Current
flags: int = Bit(width=8, default=0)

# Proposed
flags: Annotated[int, BitWidth(8)] = 0
```

### 5. Validator Integration

**Status:** Enhancement
**Target Version:** 1.2.0

Better integration with Pydantic's validators for struct-specific constraints:

```python
string_field: Annotated[str, StructLength(10)] = Field(
    description="Limited string",
    # Automatically validate max length during model validation
)
```

Add automatic validators based on struct metadata:
- String length validation matching `StructLength`
- Integer range validation for fixed-width types
- Byte length validation for bytes fields

---

## Low Priority

### 6. Performance Optimizations

**Status:** Nice to have
**Target Version:** 1.3.0

**Opportunities:**
- Cache struct format strings more aggressively
- Optimize field handler lookups
- Consider using `struct.Struct` objects for repeated pack/unpack operations
- Profile and optimize hot paths in serialization

### 7. Extended Type Support

**Status:** Enhancement
**Target Version:** 1.3.0

**Additional types to consider:**
- `Decimal` for fixed-point arithmetic
- `datetime` and `date` types
- Custom binary formats (e.g., compressed data)
- Nested lists/arrays with fixed sizes

### 8. Better Error Messages

**Status:** Enhancement
**Target Version:** 1.2.0

Improve error messages to include:
- Field name and type in pack/unpack errors
- Expected vs actual byte lengths
- Suggestions for common mistakes
- Clear indication of which field caused the error in nested structures

---

## Documentation Improvements

### 9. Comprehensive Examples

**Status:** Ongoing
**Target Version:** 1.1.0+

**Needed:**
- More real-world protocol examples (DNS, DHCP, etc.)
- C interop examples with actual C code
- IoT device communication tutorial
- Binary file format parsing guide
- Performance comparison vs alternatives

### 10. API Reference Documentation

**Status:** Completed
**Target Version:** 1.1.0

**Generate proper API docs:**
- Use Sphinx or MkDocs
- Document all public APIs
- Include type hints in documentation
- Add more docstring examples

---

## Testing Improvements

### 11. Increased Test Coverage

**Current Coverage:** ~85-90% (estimated)
**Target:** >95%

**Areas needing more coverage:**
- Error cases and edge conditions
- Nested struct error handling
- All combinations of byte orders
- Unusual field configurations
- Round-trip testing for all supported types

### 12. Property-Based Testing

**Status:** Enhancement
**Target Version:** 1.2.0

Use Hypothesis for property-based testing:
- Round-trip property: `from_bytes(x.to_bytes()) == x`
- Format string generation correctness
- Struct size calculations
- Random data serialization/deserialization

---

## Breaking Changes Summary

### v1.1.0 (Next Minor Release)

**Deprecations (with warnings):**
- Direct Field kwargs (`struct_length`, etc.) deprecated
- Old API still works but emits warnings

**New Features:**
- `Annotated` metadata classes
- Migration guide published

### v1.2.0

**Breaking Changes:**
- Remove support for direct Field kwargs
- Require `Annotated` for struct metadata
- May require minor API adjustments based on v1.1.0 feedback

---

## Timeline

- **v1.1.0** (Q1 2026): Pydantic v3 compatibility preparation
  - Add `Annotated` support
  - Deprecation warnings
  - Documentation updates

- **v1.2.0** (Q2 2026): Remove deprecated APIs
  - Breaking change: require new API
  - Enhanced features based on v1.1.0 feedback

- **v1.3.0** (Q3 2026+): Performance and features
  - Optimizations
  - Extended type support
  - Stability improvements

---

## Contributing

If you're interested in contributing to any of these initiatives, please:
1. Open an issue to discuss the approach
2. Reference this roadmap in your PR
3. Update this roadmap if plans change

## Feedback

Have thoughts on this roadmap? Please open an issue with the `roadmap` label to discuss priorities, timelines, or propose new items.
