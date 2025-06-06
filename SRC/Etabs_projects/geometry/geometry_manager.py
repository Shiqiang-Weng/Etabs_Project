# -*- coding: utf-8 -*-
"""
几何管理器 - 支持剪力墙和框架结构
负责协调所有几何构件的创建
"""

from typing import List, Dict, Tuple
from config import (
    NUM_STORIES, TYPICAL_STORY_HEIGHT, BOTTOM_STORY_HEIGHT,
    ENABLE_SHEAR_WALLS, ENABLE_FRAME_COLUMNS, ENABLE_FRAME_BEAMS, ENABLE_SLABS,
    CONFIG_NAME
)


def create_structural_geometry(sap_model) -> Tuple[List[str], List[str], Dict[int, float]]:
    """
    创建结构几何体 - 自适应不同结构类型

    Parameters:
        sap_model: ETABS SapModel对象

    Returns:
        tuple: (wall_names, cb_names, story_heights) - 为保持向后兼容性
    """
    print(f"\n🏗️ 开始创建结构几何体...")
    print(f"   结构类型: {CONFIG_NAME}")
    print(f"   楼层数: {NUM_STORIES}")

    # 初始化返回变量
    wall_names = []
    cb_names = []
    story_heights = {}

    # 计算楼层高度（所有结构类型都需要）
    for s_num in range(1, NUM_STORIES + 1):
        story_heights[s_num] = TYPICAL_STORY_HEIGHT if s_num > 1 else BOTTOM_STORY_HEIGHT

    # 根据配置创建不同类型的结构
    if ENABLE_SHEAR_WALLS:
        # 剪力墙结构
        from geometry.shear_wall_geometry import create_shear_wall_structural_geometry
        wall_names, cb_names, story_heights = create_shear_wall_structural_geometry(sap_model)

    elif ENABLE_FRAME_COLUMNS or ENABLE_FRAME_BEAMS:
        # 框架结构
        from geometry.frame_geometry import create_frame_structural_geometry
        column_names, beam_names, slab_names, story_heights = create_frame_structural_geometry(sap_model)

        # 为保持向后兼容性，将框架构件映射到原有变量名
        wall_names = column_names  # 柱子替代墙体
        cb_names = beam_names  # 梁替代连梁

    else:
        print("⚠️ 警告: 未启用任何主要结构构件")

    # 创建楼板（如果启用）
    if ENABLE_SLABS:
        if ENABLE_SHEAR_WALLS:
            # 剪力墙结构的楼板已在上面创建
            pass
        elif ENABLE_FRAME_COLUMNS or ENABLE_FRAME_BEAMS:
            # 框架结构的楼板已在上面创建
            pass
        else:
            # 仅楼板结构
            _create_standalone_slabs(sap_model, story_heights)

    print(f"\n✅ 结构几何创建完成:")
    if ENABLE_SHEAR_WALLS:
        print(f"   - 剪力墙网格单元: {len(wall_names)} 个")
        print(f"   - 连梁网格单元: {len(cb_names)} 个")
    elif ENABLE_FRAME_COLUMNS or ENABLE_FRAME_BEAMS:
        print(f"   - 框架柱: {len(wall_names)} 根")
        print(f"   - 框架梁: {len(cb_names)} 根")

    return wall_names, cb_names, story_heights


def _create_standalone_slabs(sap_model, story_heights: Dict[int, float]):
    """
    创建独立楼板（当仅启用楼板时）

    Parameters:
        sap_model: ETABS SapModel对象
        story_heights: 楼层高度字典
    """
    print("\n🏢 创建独立楼板...")

    from config import SLAB_MESH_X, SLAB_MESH_Y, SLAB_SECTION_NAME, NUM_GRID_LINES_X, NUM_GRID_LINES_Y
    from geometry.common import generate_grid_coordinates
    from geometry.mesh_utils import create_meshed_slab

    grid_x, grid_y = generate_grid_coordinates()
    area_obj = sap_model.AreaObj

    cum_z = 0.0
    slab_count = 0

    for i_s in range(NUM_STORIES):
        s_num = i_s + 1
        s_h = story_heights.get(s_num, TYPICAL_STORY_HEIGHT)
        cum_z += s_h
        z_sl = cum_z

        for ix_sl in range(NUM_GRID_LINES_X - 1):
            for iy_sl in range(NUM_GRID_LINES_Y - 1):
                x0, y0 = grid_x[ix_sl], grid_y[iy_sl]
                x1, y1 = grid_x[ix_sl + 1], grid_y[iy_sl + 1]

                sl_x = [x0, x1, x1, x0]
                sl_y = [y0, y0, y1, y1]
                sl_z = [z_sl] * 4
                sl_name = f"SLAB_X{ix_sl}_Y{iy_sl}_S{s_num}"

                created_slab_names = create_meshed_slab(
                    area_obj, sl_x, sl_y, sl_z,
                    SLAB_SECTION_NAME, sl_name,
                    SLAB_MESH_X, SLAB_MESH_Y
                )

                slab_count += len(created_slab_names)

    print(f"✅ 独立楼板创建完成，共 {slab_count} 个网格单元")


# 保持向后兼容性的函数别名
def generate_planar_layout():
    """保持向后兼容性的函数别名"""
    if ENABLE_SHEAR_WALLS:
        from geometry.shear_wall_geometry import generate_shear_wall_planar_layout
        return generate_shear_wall_planar_layout()
    else:
        return []


def create_slabs(sap_model, story_heights: Dict[int, float]):
    """保持向后兼容性的函数别名"""
    if ENABLE_SLABS:
        _create_standalone_slabs(sap_model, story_heights)