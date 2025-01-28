""" pdc_struct core classes """
from .struct_config import StructConfig
from .struct_model import StructModel
from .bit_field import BitFieldModel, Bit

# Moved this here to avoid a circular import
from .structmodel_handler import StructModelHandler
