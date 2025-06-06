# -*- coding: utf-8 -*-
"""
ETABS 自动化配置设置 - 扩展支持框架结构
包含所有项目级别的配置参数
"""

import os

# ==== ETABS 程序路径配置 ====
USE_NET_CORE = True
PROGRAM_PATH = r"C:\Program Files\Computers and Structures\ETABS 22\ETABS.exe"
ETABS_DLL_PATH = r"C:\Program Files\Computers and Structures\ETABS 22\ETABSv1.dll"
SCRIPT_DIRECTORY = r"C:\Users\Shiqi\Desktop\etabs_script_output_v5"

# ==== 模型文件配置 ====
MODEL_NAME = "Mixed_Structure_Model_v6.edb"  # 混合结构模型
MODEL_PATH = os.path.join(SCRIPT_DIRECTORY, MODEL_NAME)

# ==== ETABS 连接配置 ====
ATTACH_TO_INSTANCE = False
SPECIFY_PATH = False
REMOTE = False
REMOTE_COMPUTER = "YourRemoteComputerName"

# ==== 结构类型选择（新增）====
STRUCTURE_TYPE = "MIXED"  # 可选: "SHEAR_WALL", "FRAME", "MIXED"

# SHEAR_WALL: 纯剪力墙结构
# FRAME: 纯框架结构
# MIXED: 混合结构（剪力墙+框架）

ENABLE_SHEAR_WALLS = True  # 是否创建剪力墙
ENABLE_FRAME_COLUMNS = True  # 是否创建框架柱
ENABLE_FRAME_BEAMS = True  # 是否创建框架梁
ENABLE_SLABS = True  # 是否创建楼板

# ==== 结构几何参数 ====
NUM_GRID_LINES_X, NUM_GRID_LINES_Y = 5, 3
SPACING_X, SPACING_Y = 6.0, 6.0
NUM_STORIES = 33
TYPICAL_STORY_HEIGHT, BOTTOM_STORY_HEIGHT = 3.0, 3.0

# ==== 网格划分参数 ====
# 剪力墙网格划分参数 - 2x2网格
SHEAR_WALL_MESH_H = 2
SHEAR_WALL_MESH_V = 2

# 连梁网格划分参数 - 4x4网格
COUPLING_BEAM_MESH_H = 4
COUPLING_BEAM_MESH_V = 4

# 楼板网格划分参数 - 4x4网格
SLAB_MESH_X = 4
SLAB_MESH_Y = 4

# ==== 构件尺寸参数 ====
WALL_THICKNESS = 0.2
COUPLING_BEAM_HEIGHT = 0.6
SLAB_THICKNESS = 0.15

# 框架构件尺寸（新增）
COLUMN_WIDTH = 0.6
COLUMN_DEPTH = 0.6
FRAME_BEAM_WIDTH = 0.2
FRAME_BEAM_DEPTH = 0.6
SECONDARY_BEAM_WIDTH = 0.2
SECONDARY_BEAM_DEPTH = 0.4

# ==== 框架布置参数（新增）====
# 柱子布置
COLUMN_GRID_PATTERN = "ALL_INTERSECTIONS"  # 可选: "ALL_INTERSECTIONS", "PERIMETER_ONLY", "CUSTOM"

# 梁的布置
BEAM_LAYOUT = {
    'MAIN_BEAMS': True,      # 主梁（沿网格线）
    'SECONDARY_BEAMS': True,  # 次梁（楼板内部）
    'EDGE_BEAMS': True,      # 边梁
}

# 梁的布置细节
MAIN_BEAM_DIRECTION = "BOTH"  # 可选: "X_ONLY", "Y_ONLY", "BOTH"
SECONDARY_BEAM_SPACING = 2.0  # 次梁间距

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
DEFAULT_DEAD_SUPER_SLAB = 1.5  # 楼板恒荷载 kPa
DEFAULT_LIVE_LOAD_SLAB = 2.0   # 楼板活荷载 kPa
DEFAULT_FINISH_LOAD_KPA = 0.01  # 面层荷载 kPa

# 框架荷载参数（新增）
BEAM_DEAD_LOAD = 10.0  # 梁上恒荷载 kN/m（除自重外）
BEAM_LIVE_LOAD = 5.0   # 梁上活荷载 kN/m
COLUMN_AXIAL_LOAD = 0.0  # 柱顶轴向荷载 kN（通常由楼板传递）

# ==== 分析设置 ====
ANALYSIS_WAIT_TIME = 5
DELETE_OLD_RESULTS = True

# ==== Story-Drift 提取相关 ====
STORY_DRIFT_CASES = ["RS-X", "RS-Y"]
DRIFT_LIMIT_PERMIL = 1.0  # 1‰

# ==== 施工和设计参数（新增）====
CONSTRUCTION_PARAMS = {
    'CONCRETE_GRADE': 'C30',
    'STEEL_GRADE': 'HRB400',
    'ENVIRONMENT_CATEGORY': 'I',  # 环境类别
    'FIRE_RESISTANCE_RATING': 2.0,  # 耐火等级（小时）
}

# ==== 模型验证参数（新增）====
MODEL_CHECK_PARAMS = {
    'MIN_COLUMN_SPACING': 3.0,  # 最小柱距
    'MAX_COLUMN_SPACING': 12.0,  # 最大柱距
    'MIN_BEAM_SPAN': 2.0,       # 最小梁跨
    'MAX_BEAM_SPAN': 15.0,      # 最大梁跨
    'MAX_STORY_HEIGHT': 6.0,    # 最大层高
}

# ==== 输出控制（新增）====
OUTPUT_CONTROL = {
    'PRINT_DETAILED_INFO': True,    # 是否打印详细信息
    'EXPORT_GEOMETRY_DATA': False,  # 是否导出几何数据
    'GENERATE_DRAWINGS': False,     # 是否生成图纸
    'CREATE_REPORTS': True,         # 是否创建报告
}