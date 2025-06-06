# -*- coding: utf-8 -*-
"""
材料模块
包含混凝土材料定义和各种截面属性
"""

from .concrete import (
    define_concrete_material,
    define_wall_sections,
    define_slab_sections,
    define_beam_sections,
    define_all_materials_and_sections
)
from .modifiers import apply_all_modifiers


# 主要接口函数
def define_materials(sap_model):
    """
    定义所有材料和截面的主接口

    Parameters:
        sap_model: ETABS SapModel对象
    """
    define_all_materials_and_sections(sap_model)
    apply_all_modifiers(sap_model)


__all__ = [
    'define_materials',
    'define_concrete_material',
    'define_wall_sections',
    'define_slab_sections',
    'define_beam_sections',
    'define_all_materials_and_sections',
    'apply_all_modifiers'
]