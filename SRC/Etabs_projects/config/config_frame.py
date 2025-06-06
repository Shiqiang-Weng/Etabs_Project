# -*- coding: utf-8 -*-
"""
数据二：框架结构配置
专门用于钢筋混凝土框架结构系统
"""

import os

# ==== 配置标识 ====
CONFIG_NAME = "FRAME"
CONFIG_DESCRIPTION = "10层钢筋混凝土框架结构"

# ==== ETABS 程序路径配置 ====
USE_NET_CORE = True
PROGRAM_PATH = r"C:\Program Files\Computers and Structures\ETABS 22\ETABS.exe"
ETABS_DLL_PATH = r"C:\Program Files\Computers and Structures\ETABS 22\ETABSv1.dll"
SCRIPT_DIRECTORY = r"C:\Users\Shiqi\Desktop\etabs_script_output_v5"

# ==== 模型文件配置 ====
MODEL_NAME = "Frame_Model_10Story_v6.edb"
MODEL_PATH = os.path.join(SCRIPT_DIRECTORY, MODEL_NAME)

# ==== ETABS 连接配置 ====
ATTACH_TO_INSTANCE = False
SPECIFY_PATH = False
REMOTE = False
REMOTE_COMPUTER = "YourRemoteComputerName"

# ==== 结构组件启用控制 ====
ENABLE_SHEAR_WALLS = False     # 不创建剪力墙
ENABLE_COUPLING_BEAMS = False  # 不创建连梁
ENABLE_SLABS = True           # 启用楼板
ENABLE_FRAME_COLUMNS = True   # 启用框架柱
ENABLE_FRAME_BEAMS = True     # 启用框架梁

# ==== 结构几何参数 ====
NUM_GRID_LINES_X, NUM_GRID_LINES_Y = 5, 3
SPACING_X, SPACING_Y = 6.0, 6.0
NUM_STORIES = 10
TYPICAL_STORY_HEIGHT, BOTTOM_STORY_HEIGHT = 3.0, 3.0

# ==== 楼板网格划分参数 ====
SLAB_MESH_X = 4  # 楼板X方向网格数量
SLAB_MESH_Y = 4  # 楼板Y方向网格数量

# ==== 框架构件尺寸参数 ====
COLUMN_WIDTH = 0.6      # 柱截面宽度
COLUMN_DEPTH = 0.6      # 柱截面高度
FRAME_BEAM_WIDTH = 0.25  # 主梁截面宽度
FRAME_BEAM_DEPTH = 0.6   # 主梁截面高度
SECONDARY_BEAM_WIDTH = 0.25  # 次梁截面宽度
SECONDARY_BEAM_DEPTH = 0.4   # 次梁截面高度
SLAB_THICKNESS = 0.12    # 楼板厚度（框架结构可以更薄）

# ==== 材料名称定义 ====
CONCRETE_MATERIAL_NAME = "C30/37"
STEEL_MATERIAL_NAME = "Q345"  # 钢材（预留，当前未使用）

# ==== 截面名称定义 ====
FRAME_COLUMN_SECTION_NAME = "COL600X600"
FRAME_BEAM_SECTION_NAME = "BEAM250X600"
SECONDARY_BEAM_SECTION_NAME = "BEAM250X400"
SLAB_SECTION_NAME = "Slab-120"

# ==== 混凝土材料属性 ====
CONCRETE_PROPERTIES = {
    'E_MODULUS': 30000000,  # 弹性模量 (kN/m²)
    'POISSON': 0.2,  # 泊松比
    'THERMAL_EXP': 1.0e-5,  # 热膨胀系数 (/°C)
    'UNIT_WEIGHT': 26.0,  # 容重 (kN/m³)
    'FC': 30,  # 抗压强度标准值 (MPa)
    'FT': 2.01,  # 抗拉强度标准值 (MPa)
}

# ==== 钢材属性（预留）====
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
    'FRAME_COLUMN': {
        'width': COLUMN_WIDTH,
        'depth': COLUMN_DEPTH,
        'material': CONCRETE_MATERIAL_NAME,
        'section_type': 'Rectangle'
    },

    'FRAME_BEAM': {
        'width': FRAME_BEAM_WIDTH,
        'depth': FRAME_BEAM_DEPTH,
        'material': CONCRETE_MATERIAL_NAME,
        'section_type': 'Rectangle'
    },

    'SECONDARY_BEAM': {
        'width': SECONDARY_BEAM_WIDTH,
        'depth': SECONDARY_BEAM_DEPTH,
        'material': CONCRETE_MATERIAL_NAME,
        'section_type': 'Rectangle'
    },

    'SLAB': {
        'thickness': SLAB_THICKNESS,
        'material': CONCRETE_MATERIAL_NAME,
        'shell_type': 'ShellThin',  # 框架结构楼板用薄板
        'slab_type': 'Slab'
    }
}

# ==== 框架布置参数 ====
# 柱子布置模式
COLUMN_GRID_PATTERN = "ALL_INTERSECTIONS"  # 所有网格交点都布置柱子
# 其他选项: "PERIMETER_ONLY"（仅周边）, "CORNER_ONLY"（仅角点）

# 梁的布置
BEAM_LAYOUT = {
    'MAIN_BEAMS_X': True,        # X方向主梁
    'MAIN_BEAMS_Y': True,        # Y方向主梁
    'SECONDARY_BEAMS': True,     # 次梁
    'EDGE_BEAMS': True,          # 边梁
}

# 梁的布置细节
MAIN_BEAM_DIRECTION = "BOTH"  # 主梁方向: "X_ONLY", "Y_ONLY", "BOTH"
SECONDARY_BEAM_SPACING = 3.0  # 次梁间距（米）
SECONDARY_BEAM_DIRECTION = "Y"  # 次梁方向: "X", "Y"

# ==== 框架特殊参数 ====
FRAME_PARAMETERS = {
    'COLUMN_BOTTOM_FIXED': True,    # 柱底固定
    'BEAM_END_RELEASES': False,     # 梁端释放
    'CONSIDER_P_DELTA': True,       # 考虑P-Δ效应
    'RIGID_ZONE_FACTOR': 0.5,       # 刚域系数
}

# ==== 楼板设置 ====
SLAB_PROPERTIES = {
    'DIAPHRAGM_TYPE': 'RIGID',      # 楼面约束类型: 'RIGID' 或 'SEMI_RIGID'
    'MESH_TYPE': 'SHELL_THIN',      # 网格类型
    'EDGE_CONSTRAINTS': True,       # 边缘约束
}

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
RS_DESIGN_INTENSITY = 7
RS_BASE_ACCEL_G = 0.08
RS_SEISMIC_GROUP = 3
RS_SITE_CLASS = "III"
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
DEFAULT_DEAD_SUPER_SLAB = 2.0   # 楼板恒荷载 kPa (框架结构通常更大)
DEFAULT_LIVE_LOAD_SLAB = 2.0    # 楼板活荷载 kPa
DEFAULT_FINISH_LOAD_KPA = 0.5   # 面层荷载 kPa

# ==== 框架构件荷载 ====
BEAM_DEAD_LOAD = 10.0   # 梁上恒荷载 kN/m（墙体、设备等）
BEAM_LIVE_LOAD = 5.0    # 梁上活荷载 kN/m
COLUMN_AXIAL_LOAD = 50.0  # 修改这里：从 0.0 改为 50.0，给柱子添加轴向荷载 kN

# 如果找不到上面的定义，请在文件中添加：
if 'COLUMN_AXIAL_LOAD' not in locals():
    COLUMN_AXIAL_LOAD = 50.0  # 柱顶轴向荷载 kN

# ==== 分析设置 ====
ANALYSIS_WAIT_TIME = 5
DELETE_OLD_RESULTS = True

# ==== Story-Drift 提取相关 ====
STORY_DRIFT_CASES = ["RS-X", "RS-Y"]
DRIFT_LIMIT_PERMIL = 1.0  # 框架结构位移角限值通常较大

# ==== 设计参数 ====
DESIGN_PARAMETERS = {
    'CONCRETE_GRADE': 'C30',
    'STEEL_GRADE': 'HRB400',
    'COVER_THICKNESS': 0.025,   # 保护层厚度
    'MIN_COLUMN_SIZE': 0.4,     # 最小柱截面
    'MAX_COLUMN_SIZE': 1.2,     # 最大柱截面
    'MIN_BEAM_HEIGHT': 0.3,     # 最小梁高
    'MAX_BEAM_HEIGHT': 1.0,     # 最大梁高
}

# ==== 构造要求 ====
CONSTRUCTION_REQUIREMENTS = {
    'MIN_COLUMN_SPACING': 3.0,    # 最小柱距
    'MAX_COLUMN_SPACING': 9.0,    # 最大柱距
    'MAX_BEAM_SPAN': 12.0,        # 最大梁跨
    'MIN_BEAM_SPAN': 2.5,         # 最小梁跨
    'SPAN_TO_DEPTH_RATIO': 15,    # 跨高比限值
}

# ==== 输出控制 ====
OUTPUT_CONTROL = {
    'PRINT_DETAILED_INFO': True,     # 是否打印详细信息
    'PRINT_COLUMN_INFO': True,       # 是否打印柱信息
    'PRINT_BEAM_INFO': True,         # 是否打印梁信息
    'PRINT_CONNECTION_INFO': False,   # 是否打印节点信息
}

# ==== 网格划分参数（仅为兼容性保留）====
SHEAR_WALL_MESH_H = 0  # 不适用
SHEAR_WALL_MESH_V = 0  # 不适用
COUPLING_BEAM_MESH_H = 0  # 不适用
COUPLING_BEAM_MESH_V = 0  # 不适用

# ==== 不适用的参数（为兼容性设置为空或默认值）====
WALL_SECTION_NAME = ""
COUPLING_BEAM_SECTION_NAME = ""
MEMBRANE_MODIFIERS = []
WALL_THICKNESS = 0.0
COUPLING_BEAM_HEIGHT = 0.0

print(f"✅ 已加载框架结构配置: {CONFIG_DESCRIPTION}")
print(f"   模型: {MODEL_NAME}")
print(f"   柱截面: {COLUMN_WIDTH}m×{COLUMN_DEPTH}m")
print(f"   主梁截面: {FRAME_BEAM_WIDTH}m×{FRAME_BEAM_DEPTH}m")
print(f"   次梁截面: {SECONDARY_BEAM_WIDTH}m×{SECONDARY_BEAM_DEPTH}m")
print(f"   楼板厚度: {SLAB_THICKNESS}m")
print(f"   楼板网格: {SLAB_MESH_X}×{SLAB_MESH_Y}")