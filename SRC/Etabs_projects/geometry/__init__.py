# -*- coding: utf-8 -*-
"""
几何模块
包含结构几何创建的所有功能
"""

from .geometry_manager import create_structural_geometry
from .common import StructuralElementPlan, generate_grid_coordinates
from .mesh_utils import create_meshed_element, create_meshed_slab


# 主要接口函数
def create_geometry(sap_model):
    """
    创建结构几何的主接口

    Parameters:
        sap_model: ETABS SapModel对象

    Returns:
        tuple: (wall_names, cb_names, story_heights)
    """
    return create_structural_geometry(sap_model)


__all__ = [
    'create_geometry',
    'create_structural_geometry',
    'StructuralElementPlan',
    'generate_grid_coordinates',
    'create_meshed_element',
    'create_meshed_slab'
]