# -*- coding: utf-8 -*-
"""
配置模块 - 支持多种结构类型
包含项目的所有配置参数
"""

# ==== 结构类型选择 ====
# 修改这里来切换不同的结构类型配置
STRUCTURE_TYPE = "FRAME"  # 可选: "SHEAR_WALL", "FRAME"

# 根据结构类型导入对应配置
if STRUCTURE_TYPE == "SHEAR_WALL":
    try:
        # 导入剪力墙配置（数据一）
        from .config_shear_wall import *

        print(f"📋 使用配置: 剪力墙结构 ({CONFIG_DESCRIPTION})")
    except ImportError as e:
        print(f"❌ 无法导入剪力墙配置: {e}")
        print("使用默认设置...")
        from .settings import *
        from .material_properties import *

elif STRUCTURE_TYPE == "FRAME":
    try:
        # 导入框架配置（数据二）
        from .config_frame import *

        print(f"📋 使用配置: 框架结构 ({CONFIG_DESCRIPTION})")
    except ImportError as e:
        print(f"❌ 无法导入框架配置: {e}")
        print("使用默认设置...")
        from .settings import *
        from .material_properties import *

else:
    print(f"❌ 不支持的结构类型: {STRUCTURE_TYPE}")
    print("使用默认设置...")
    from .settings import *
    from .material_properties import *

# 为向后兼容性，确保所有必要的变量都存在
try:
    # 检查基本变量是否存在
    required_vars = [
        'NUM_STORIES', 'TYPICAL_STORY_HEIGHT', 'BOTTOM_STORY_HEIGHT',
        'NUM_GRID_LINES_X', 'NUM_GRID_LINES_Y', 'SPACING_X', 'SPACING_Y',
        'CONCRETE_MATERIAL_NAME', 'MODEL_PATH'
    ]

    missing_vars = []
    for var in required_vars:
        if var not in globals():
            missing_vars.append(var)

    if missing_vars:
        print(f"⚠️ 警告: 缺少必要的配置变量: {missing_vars}")

except Exception as e:
    print(f"⚠️ 配置检查时出错: {e}")

# 打印当前配置摘要
print(f"   结构类型: {STRUCTURE_TYPE}")
if 'ENABLE_SHEAR_WALLS' in globals():
    print(f"   剪力墙: {'✅' if ENABLE_SHEAR_WALLS else '❌'}")
if 'ENABLE_FRAME_COLUMNS' in globals():
    print(f"   框架柱: {'✅' if ENABLE_FRAME_COLUMNS else '❌'}")
if 'ENABLE_FRAME_BEAMS' in globals():
    print(f"   框架梁: {'✅' if ENABLE_FRAME_BEAMS else '❌'}")
if 'ENABLE_SLABS' in globals():
    print(f"   楼板: {'✅' if ENABLE_SLABS else '❌'}")

# 导出所有配置变量
__all__ = [
    # 基本配置
    'STRUCTURE_TYPE', 'CONFIG_NAME', 'CONFIG_DESCRIPTION',
    'USE_NET_CORE', 'PROGRAM_PATH', 'ETABS_DLL_PATH', 'SCRIPT_DIRECTORY',
    'MODEL_NAME', 'MODEL_PATH', 'ATTACH_TO_INSTANCE', 'SPECIFY_PATH', 'REMOTE',

    # 几何参数
    'NUM_GRID_LINES_X', 'NUM_GRID_LINES_Y', 'SPACING_X', 'SPACING_Y',
    'NUM_STORIES', 'TYPICAL_STORY_HEIGHT', 'BOTTOM_STORY_HEIGHT',

    # 构件启用控制
    'ENABLE_SHEAR_WALLS', 'ENABLE_FRAME_COLUMNS', 'ENABLE_FRAME_BEAMS', 'ENABLE_SLABS',

    # 地震参数
    'RS_DESIGN_INTENSITY', 'RS_BASE_ACCEL_G', 'RS_SEISMIC_GROUP',
    'RS_SITE_CLASS', 'RS_CHARACTERISTIC_PERIOD', 'RS_FUNCTION_NAME',
    'MODAL_CASE_NAME', 'RS_DAMPING_RATIO', 'GRAVITY_ACCEL',

    # 荷载参数
    'DEFAULT_DEAD_SUPER_SLAB', 'DEFAULT_LIVE_LOAD_SLAB', 'DEFAULT_FINISH_LOAD_KPA',

    # 材料属性
    'CONCRETE_MATERIAL_NAME', 'CONCRETE_PROPERTIES',

    # 分析设置
    'ANALYSIS_WAIT_TIME', 'DELETE_OLD_RESULTS',

    # 结果提取
    'STORY_DRIFT_CASES', 'DRIFT_LIMIT_PERMIL',
]

# 根据结构类型添加特定的导出变量
if STRUCTURE_TYPE == "SHEAR_WALL":
    __all__.extend([
        'SHEAR_WALL_MESH_H', 'SHEAR_WALL_MESH_V',
        'COUPLING_BEAM_MESH_H', 'COUPLING_BEAM_MESH_V',
        'SLAB_MESH_X', 'SLAB_MESH_Y',
        'WALL_SECTION_NAME', 'COUPLING_BEAM_SECTION_NAME', 'SLAB_SECTION_NAME',
        'SECTION_PROPERTIES', 'MEMBRANE_MODIFIERS', 'DIAPHRAGM_TYPES',
        'WALL_THICKNESS', 'COUPLING_BEAM_HEIGHT',
    ])
elif STRUCTURE_TYPE == "FRAME":
    __all__.extend([
        'FRAME_COLUMN_SECTION_NAME', 'FRAME_BEAM_SECTION_NAME', 'SECONDARY_BEAM_SECTION_NAME',
        'SLAB_SECTION_NAME', 'SECTION_PROPERTIES', 'DIAPHRAGM_TYPES',
        'COLUMN_GRID_PATTERN', 'BEAM_LAYOUT', 'MAIN_BEAM_DIRECTION',
        'SECONDARY_BEAM_SPACING', 'SECONDARY_BEAM_DIRECTION',
        'COLUMN_WIDTH', 'COLUMN_DEPTH', 'FRAME_BEAM_WIDTH', 'FRAME_BEAM_DEPTH',
        'SLAB_MESH_X', 'SLAB_MESH_Y',
    ])