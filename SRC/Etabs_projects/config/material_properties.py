# -*- coding: utf-8 -*-
"""
ETABS 材料属性配置 - 扩展支持框架结构
定义所有材料和截面的属性参数，包括梁柱截面
"""

# ==== 材料名称定义 ====
CONCRETE_MATERIAL_NAME = "C30/37"
STEEL_MATERIAL_NAME = "Q345"  # 新增钢材

# ==== 截面名称定义 ====
# 剪力墙截面
WALL_SECTION_NAME = "Wall-200"
COUPLING_BEAM_SECTION_NAME = "CB-200"
SLAB_SECTION_NAME = "Slab-150"

# 框架截面（新增）
FRAME_COLUMN_SECTION_NAME = "COL600X600"
FRAME_BEAM_SECTION_NAME = "BEAM200X600"
SECONDARY_BEAM_SECTION_NAME = "BEAM200X400"

# ==== 混凝土材料属性 ====
CONCRETE_PROPERTIES = {
    'E_MODULUS': 30000000,  # 弹性模量 (kN/m²)
    'POISSON': 0.2,  # 泊松比
    'THERMAL_EXP': 1.0e-5,  # 热膨胀系数 (/°C)
    'UNIT_WEIGHT': 26.0,  # 容重 (kN/m³)
    'FC': 30,  # 抗压强度标准值 (MPa)
    'FT': 2.01,  # 抗拉强度标准值 (MPa)
}

# ==== 钢材属性（新增）====
STEEL_PROPERTIES = {
    'E_MODULUS': 206000000,  # 弹性模量 (kN/m²)
    'POISSON': 0.3,  # 泊松比
    'THERMAL_EXP': 1.2e-5,  # 热膨胀系数 (/°C)
    'UNIT_WEIGHT': 78.5,  # 容重 (kN/m³)
    'FY': 345,  # 屈服强度 (MPa)
    'FU': 470,  # 抗拉强度 (MPa)
}

# ==== 截面属性参数 ====
SECTION_PROPERTIES = {
    # 剪力墙相关
    'WALL': {
        'thickness': 0.2,
        'material': CONCRETE_MATERIAL_NAME,
        'shell_type': 'ShellThin',
        'wall_type': 'Specified'
    },

    'COUPLING_BEAM': {
        'thickness': 0.2,
        'material': CONCRETE_MATERIAL_NAME,
        'shell_type': 'ShellThin',
        'wall_type': 'Specified'
    },

    'SLAB': {
        'thickness': 0.15,
        'material': CONCRETE_MATERIAL_NAME,
        'shell_type': 'Membrane',
        'slab_type': 'Slab'
    },

    # 框架相关（新增）
    'FRAME_COLUMN': {
        'width': 0.6,    # 截面宽度
        'depth': 0.6,    # 截面高度
        'material': CONCRETE_MATERIAL_NAME,
        'section_type': 'Rectangle'
    },

    'FRAME_BEAM': {
        'width': 0.2,    # 截面宽度
        'depth': 0.6,    # 截面高度
        'material': CONCRETE_MATERIAL_NAME,
        'section_type': 'Rectangle'
    },

    'SECONDARY_BEAM': {
        'width': 0.2,    # 截面宽度
        'depth': 0.4,    # 截面高度
        'material': CONCRETE_MATERIAL_NAME,
        'section_type': 'Rectangle'
    }
}

# ==== 膜单元修正系数 ====
MEMBRANE_MODIFIERS = [
    1.0,  # f11 (膜刚度X方向) - 保持
    1.0,  # f22 (膜刚度Y方向) - 保持
    1.0,  # f12 (膜剪切刚度) - 保持
    0.0,  # f13 (横向剪切刚度XZ) - 设为0
    0.0,  # f23 (横向剪切刚度YZ) - 设为0
    0.0,  # f33 (弯曲刚度Z方向) - 设为0
    1.0,  # m11 (质量X方向) - 保持
    1.0,  # m22 (质量Y方向) - 保持
    1.0,  # m12 (质量XY耦合) - 保持
    1.0,  # m13 (质量XZ耦合) - 保持
    1.0,  # m23 (质量YZ耦合) - 保持
    1.0,  # m33 (质量Z方向) - 保持
    1.0   # weight (重量) - 保持
]

# ==== 楼面约束定义 ====
DIAPHRAGM_TYPES = {
    'RIGID': {
        'name': 'RIGID',
        'is_semi_rigid': False,
        'description': '刚性楼面'
    },
    'SEMI_RIGID': {
        'name': 'SRD',
        'is_semi_rigid': True,
        'description': '半刚性楼面'
    }
}

# ==== 框架结构参数（新增）====
FRAME_PARAMETERS = {
    'COLUMN_SPACING_X': 6.0,  # X方向柱距
    'COLUMN_SPACING_Y': 6.0,  # Y方向柱距
    'BEAM_CLEAR_COVER': 0.025,  # 梁保护层厚度
    'COLUMN_CLEAR_COVER': 0.025,  # 柱保护层厚度
    'BEAM_TOP_OFFSET': 0.0,  # 梁顶偏移
    'BEAM_BOTTOM_OFFSET': 0.0,  # 梁底偏移
}