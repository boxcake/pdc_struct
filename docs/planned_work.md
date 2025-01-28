Plan for Moving Field Configuration to StructConfig
Background
Currently, PDC Struct uses Pydantic Field parameters (via json_schema_extra and metadata) to configure struct-specific field attributes. This approach is deprecated in Pydantic 2 and will be unavailable in Pydantic 3. We need to move these configurations to the StructConfig class.

Current Usage Example
python

Copy
class Point(StructModel):
    # Currently using Field parameters
    string_field: str = Field(
        max_length=10,
        struct_length=10,
        description="String field"
    )
    
    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )
Proposed New Structure
python

Copy
class Point(StructModel):
    # Field only uses standard Pydantic parameters
    string_field: str = Field(description="String field")
    
    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN,
        field_config={
            'string_field': {
                'struct_length': 10,
                'max_length': 10
            }
        }
    )
Required Changes
1. Update StructConfig Class
python

Copy
class StructConfig:
    def __init__(
        self,
        mode: StructMode = StructMode.C_COMPATIBLE,
        version: StructVersion = StructVersion.V1,
        byte_order: ByteOrder = ByteOrder.LITTLE_ENDIAN,
        propagate_byte_order: bool = True,
        field_config: dict = None
    ):
        self.mode = mode
        self.version = version
        self.byte_order = byte_order
        self.propagate_byte_order = propagate_byte_order
        self.field_config = field_config or {}
2. Modify TypeHandler Base Class
Need to update how type handlers access field configuration:

python

Copy
class TypeHandler(ABC, metaclass=TypeHandlerMeta):
    @classmethod
    def _get_field_config(cls, field_name: str, model_cls: Type['StructModel']) -> dict:
        """Get struct-specific configuration for a field."""
        if model_cls.struct_config.field_config:
            return model_cls.struct_config.field_config.get(field_name, {})
        return {}

    @classmethod
    def _get_field_length_generic(cls, field_name: str, model_cls: Type['StructModel']) -> Optional[int]:
        """Get struct length from field configuration."""
        config = cls._get_field_config(field_name, model_cls)
        return config.get('struct_length')
3. Update String Handler
Example of updating a specific type handler:

python

Copy
class StringHandler(TypeHandler):
    @classmethod
    def get_struct_format(cls, field_name: str, model_cls: Type['StructModel']) -> str:
        struct_length = cls._get_field_length_generic(field_name, model_cls)
        if struct_length is None:
            raise ValueError(f"Field '{field_name}' requires struct_length in field_config")
        return f'{struct_length}s'

    @classmethod
    def validate_field(cls, field_name: str, model_cls: Type['StructModel']) -> None:
        config = cls._get_field_config(field_name, model_cls)
        if cls.needs_length() and 'struct_length' not in config:
            raise ValueError(f"Field '{field_name}' requires struct_length in field_config")
4. Update StructModel Class
Modify how field validation and configuration is handled:

python

Copy
class StructModel(BaseModel):
    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        super().__pydantic_init_subclass__(**kwargs)
        
        # Validate struct_config field configurations
        if not hasattr(cls, 'struct_config'):
            raise ValueError("StructModel requires struct_config")
        
        cls._field_handlers = {}
        for field_name, field in cls.model_fields.items():
            handler = TypeHandlerMeta.get_handler(field.annotation)
            cls._field_handlers[field_name] = handler
            
            # Validate field configuration
            try:
                handler.validate_field(field_name, cls)
            except ValueError as e:
                raise ValueError(f"Field '{field_name}': {e}")
5. Update Test Cases
All test cases need to be updated to use the new configuration style:

python

Copy
def test_string_handling():
    class StringModel(StructModel):
        text: str = Field(description="Test string")
        
        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE,
            field_config={
                'text': {
                    'struct_length': 10,
                    'max_length': 10
                }
            }
        )
Implementation Steps
Create new StructConfig class with field_config support
Update TypeHandler base class with new config access methods
Update all type handlers to use new configuration access
Modify StructModel to validate new style configurations
Update all test cases to use new configuration style
Add migration guide to documentation
Update README and examples
Backward Compatibility
Consider adding a deprecation warning when old-style field configuration is detected, to help users migrate to the new style.

Documentation Updates
Update README with new configuration style
Add migration guide
Update all examples
Document all available field configuration options
Would you like me to expand on any part of this plan or provide additional examples?

 Copy
