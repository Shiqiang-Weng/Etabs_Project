# -*- coding: utf-8 -*-
"""
数据一：剪力墙结构配置
基于原有配置，专门用于剪力墙结构系统
"""

import os

# ==== 配置标识 ====
CONFIG_NAME = "SHEAR_WALL"
CONFIG_DESCRIPTION = "33层联肢剪力墙结构"

# ==== ETABS 程序路径配置 ====
USE_NET_CORE = True
PROGRAM_PATH = r"C:\Program Files\Computers and Structures\ETABS 22\ETABS.exe"
ETABS_DLL_PATH = r"C:\Program Files\Computers and Structures\ETABS 22\ETABSv1.dll"
SCRIPT_DIRECTORY = r"C:\Users\Shiqi\Desktop\etabs_script_output_v5"

# ==== 模型文件配置 ====
MODEL_NAME = "ShearWall_Model_33Story_v5_1_26.edb"
MODEL_PATH = os.path.join(SCRIPT_DIRECTORY, MODEL_NAME)

# ==== ETABS 连接配置 ====
ATTACH_TO_INSTANCE = False
SPECIFY_PATH = False
REMOTE = False
REMOTE_COMPUTER = "YourRemoteComputerName"

# ==== 结构组件启用控制 ====
ENABLE_SHEAR_WALLS = True      # 启用剪力墙
ENABLE_COUPLING_BEAMS = True   # 启用连梁
ENABLE_SLABS = True           # 启用楼板
ENABLE_FRAME_COLUMNS = False  # 不创建框架柱
ENABLE_FRAME_BEAMS = False    # 不创建框架梁

# ==== 结构几何参数 ====
NUM_GRID_LINES_X, NUM_GRID_LINES_Y = 5, 3
SPACING_X, SPACING_Y = 6.0, 6.0
NUM_STORIES = 33
TYPICAL_STORY_HEIGHT, BOTTOM_STORY_HEIGHT = 3.0, 3.0

# ==== 网格划分参数 ====
# 剪力墙网格划分参数 - 2x2网格
SHEAR_WALL_MESH_H = 2  # 剪力墙水平方向网格数量
SHEAR_WALL_MESH_V = 2  # 剪力墙竖直方向网格数量

# 连梁网格划分参数 - 4x4网格
COUPLING_BEAM_MESH_H = 4  # 连梁水平方向网格数量
COUPLING_BEAM_MESH_V = 4  # 连梁竖直方向网格数量

# 楼板网格划分参数 - 4x4网格
SLAB_MESH_X = 4  # 楼板X方向网格数量
SLAB_MESH_Y = 4  # 楼板Y方向网格数量

# ==== 构件尺寸参数 ====
WALL_THICKNESS = 0.2
COUPLING_BEAM_HEIGHT = 0.6
SLAB_THICKNESS = 0.15

# ==== 材料名称定义 ====
CONCRETE_MATERIAL_NAME = "C30/37"

# ==== 截面名称定义 ====
WALL_SECTION_NAME = "Wall-200"
COUPLING_BEAM_SECTION_NAME = "CB-200"
SLAB_SECTION_NAME = "Slab-150"

# ==== 混凝土材料属性 ====
CONCRETE_PROPERTIES = {
    'E_MODULUS': 30000000,  # 弹性模量 (kN/m²)
    'POISSON': 0.2,  # 泊松比
    'THERMAL_EXP': 1.0e-5,  # 热膨胀系数 (/°C)
    'UNIT_WEIGHT': 26.0,  # 容重 (kN/m³)
    'FC': 30,  # 抗压强度标准值 (MPa)
    'FT': 2.01,  # 抗拉强度标准值 (MPa)
}

# ==== 截面属性参数 ====
SECTION_PROPERTIES = {
    'WALL': {
        'thickness': 0.2,
        'material': CONCRETE_MATERIAL_NAME,
        'shell_type': 'ShellThin',  # 薄壳
        'wall_type': 'Specified'  # 指定厚度
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
        'shell_type': 'Membrane',  # 膜单元
        'slab_type': 'Slab'
    }
}

# ==== 膜单元修正系数 ====
# 用于楼板膜单元设置，面外刚度设为0
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

# ==== 地震参数设置 ====
# 地震设防烈度：7 度（0.1 g）
RS_DESIGN_INTENSITY = 7
# 最大地震影响系数 αmax：0.0800
RS_BASE_ACCEL_G = 0.08
# 地震分组：第三组
RS_SEISMIC_GROUP = 3
# 场地类别：III 类
RS_SITE_CLASS = "III"
# 场地特征周期 Tg：0.65 s
RS_CHARACTERISTIC_PERIOD = 0.65

# ==== 反应谱参数 ====
RS_FUNCTION_NAME = (
    f"UserRSFunc_GB50011_G{RS_SEISMIC_GROUP}_{RS_SITE_CLASS}_{RS_DESIGN_INTENSITY}deg"
)
MODAL_CASE_NAME = "MODAL_RS"
RS_DAMPING_RATIO = 0.05
GRAVITY_ACCEL = 9.80665
GENERATE_RS_COMBOS = True

# ==== 荷载参数 ====
DEFAULT_DEAD_SUPER_SLAB = 1.5  # 楼板恒荷载 kPa
DEFAULT_LIVE_LOAD_SLAB = 2.0   # 楼板活荷载 kPa
DEFAULT_FINISH_LOAD_KPA = 0.01  # 面层荷载 kPa

# ==== 分析设置 ====
ANALYSIS_WAIT_TIME = 5  # 分析前等待时间（秒）
DELETE_OLD_RESULTS = True  # 是否删除旧分析结果

# ==== Story-Drift 提取相关 ====
# 要提取哪些工况／组合的层间位移角
STORY_DRIFT_CASES = ["RS-X", "RS-Y"]          # 随自己模型调整
# 规范或项目控制限值（‰）
DRIFT_LIMIT_PERMIL = 1.0                      # 1‰ = 1/1000

# ==== 剪力墙特殊参数 ====
SHEAR_WALL_LAYOUT = {
    'WALL_SEGMENT_RATIO': 1/3,  # 墙-梁-墙的分段比例
    'ENABLE_EDGE_WALLS': True,   # 是否创建边缘墙体
    'WALL_OPENING_RATIO': 0.3,   # 洞口率（连梁长度/总长度）
}

# ==== 输出控制 ====
OUTPUT_CONTROL = {
    'PRINT_DETAILED_INFO': True,    # 是否打印详细信息
    'PRINT_WALL_INFO': True,        # 是否打印墙体信息
    'PRINT_COUPLING_BEAM_INFO': True, # 是否打印连梁信息
}

print(f"✅ 已加载剪力墙结构配置: {CONFIG_DESCRIPTION}")
print(f"   模型: {MODEL_NAME}")
print(f"   网格: 墙体{SHEAR_WALL_MESH_H}×{SHEAR_WALL_MESH_V}, 连梁{COUPLING_BEAM_MESH_H}×{COUPLING_BEAM_MESH_V}, 楼板{SLAB_MESH_X}×{SLAB_MESH_Y}")