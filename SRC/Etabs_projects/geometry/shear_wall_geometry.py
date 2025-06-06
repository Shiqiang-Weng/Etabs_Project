# -*- coding: utf-8 -*-
"""
剪力墙几何创建模块
负责创建剪力墙结构的墙体和连梁（面单元）
"""

from typing import List, Dict, Tuple
from config import (
    NUM_STORIES, TYPICAL_STORY_HEIGHT, BOTTOM_STORY_HEIGHT,
    WALL_SECTION_NAME, COUPLING_BEAM_SECTION_NAME, SLAB_SECTION_NAME,
    COUPLING_BEAM_HEIGHT, SHEAR_WALL_MESH_H, SHEAR_WALL_MESH_V,
    COUPLING_BEAM_MESH_H, COUPLING_BEAM_MESH_V, SLAB_MESH_X, SLAB_MESH_Y,
    NUM_GRID_LINES_X, NUM_GRID_LINES_Y, SPACING_X, SPACING_Y
)
from geometry.common import (
    StructuralElementPlan, generate_grid_coordinates,
    create_pier_spandrel_labels
)
from geometry.mesh_utils import create_meshed_element, create_meshed_slab
from utils import check_ret


def generate_shear_wall_planar_layout() -> List[StructuralElementPlan]:
    """
    生成剪力墙平面布局定义

    结构工程理念：
    - 采用1/3分段原理：墙-梁-墙，每段2米
    - 这种布置符合联肢剪力墙的经典构造做法
    - 连梁跨度2米，既能有效传递水平力，又便于施工

    Returns:
        list: 结构构件平面定义列表
    """
    elements = []
    grid_x, grid_y = generate_grid_coordinates()
    seg_f = 1 / 3.0  # 分段系数：墙-连梁-墙的1/3分段

    # 水平方向元素（沿Y轴网格线）
    for iy, y_c in enumerate(grid_y):
        for ix in range(NUM_GRID_LINES_X - 1):  # 在X轴网格线之间
            xs, xe = grid_x[ix], grid_x[ix + 1]

            # 左侧墙肢：从0到2米
            elements.append(StructuralElementPlan(
                [xs, xs + SPACING_X * seg_f, xs + SPACING_X * seg_f, xs],
                [y_c] * 4,
                WALL_SECTION_NAME, f"HWL_X{ix}_Y{iy}", False, "P"))

            # 中间连梁：从2米到4米
            elements.append(StructuralElementPlan(
                [xs + SPACING_X * seg_f, xs + SPACING_X * 2 * seg_f,
                 xs + SPACING_X * 2 * seg_f, xs + SPACING_X * seg_f],
                [y_c] * 4,
                COUPLING_BEAM_SECTION_NAME, f"HCB_X{ix}_Y{iy}", True, "S"))

            # 右侧墙肢：从4米到6米
            elements.append(StructuralElementPlan(
                [xs + SPACING_X * 2 * seg_f, xe, xe, xs + SPACING_X * 2 * seg_f],
                [y_c] * 4,
                WALL_SECTION_NAME, f"HWR_X{ix}_Y{iy}", False, "P"))

    # 竖直方向元素（沿X轴网格线）
    for ix, x_c in enumerate(grid_x):
        for iy in range(NUM_GRID_LINES_Y - 1):  # 在Y轴网格线之间
            ys, ye = grid_y[iy], grid_y[iy + 1]

            # 下部墙肢
            elements.append(StructuralElementPlan(
                [x_c] * 4,
                [ys, ys + SPACING_Y * seg_f, ys + SPACING_Y * seg_f, ys],
                WALL_SECTION_NAME, f"VWB_X{ix}_Y{iy}", False, "P"))

            # 中间连梁
            elements.append(StructuralElementPlan(
                [x_c] * 4,
                [ys + SPACING_Y * seg_f, ys + SPACING_Y * 2 * seg_f,
                 ys + SPACING_Y * 2 * seg_f, ys + SPACING_Y * seg_f],
                COUPLING_BEAM_SECTION_NAME, f"VCB_X{ix}_Y{iy}", True, "S"))

            # 上部墙肢
            elements.append(StructuralElementPlan(
                [x_c] * 4,
                [ys + SPACING_Y * 2 * seg_f, ye, ye, ys + SPACING_Y * 2 * seg_f],
                WALL_SECTION_NAME, f"VWT_X{ix}_Y{iy}", False, "P"))

    return elements


def create_shear_wall_structural_geometry(sap_model) -> Tuple[List[str], List[str], Dict[int, float]]:
    """
    创建剪力墙结构几何体

    Parameters:
        sap_model: ETABS SapModel对象

    Returns:
        tuple: (wall_names, cb_names, story_heights)
    """
    print(f"\n🏗️ 开始创建 {NUM_STORIES} 层剪力墙结构...")
    print("网格配置：")
    print(f"  - 剪力墙: {SHEAR_WALL_MESH_H}×{SHEAR_WALL_MESH_V} 网格")
    print(f"  - 连梁: {COUPLING_BEAM_MESH_H}×{COUPLING_BEAM_MESH_V} 网格")
    print(f"  - 楼板: {SLAB_MESH_X}×{SLAB_MESH_Y} 网格")

    # 获取ETABS API对象
    area_obj = sap_model.AreaObj

    # 初始化返回列表
    wall_names, cb_names, story_heights = [], [], {}

    # 生成平面布局定义
    layout_defs = generate_shear_wall_planar_layout()

    # 创建pier/spandrel标签
    create_pier_spandrel_labels(sap_model, layout_defs)

    # 逐层创建墙体和连梁
    cum_z = 0.0  # 累积高度追踪器

    for i_s in range(NUM_STORIES):
        s_num = i_s + 1  # 楼层编号（从1开始）
        s_h = TYPICAL_STORY_HEIGHT if i_s > 0 else BOTTOM_STORY_HEIGHT
        story_heights[s_num] = s_h

        # 计算不同构件的标高
        z_b = cum_z  # 层底标高
        z_t = cum_z + s_h  # 层顶标高
        z_cb_b = z_t - COUPLING_BEAM_HEIGHT  # 连梁底部标高
        z_cb_t = z_t  # 连梁顶部标高
        cum_z = z_t

        print(f"  创建第 {s_num} 层构件 (层高: {s_h:.1f}m):")

        # 统计计数
        story_wall_count = 0
        story_cb_count = 0

        # 对每个布局定义创建实际的3D构件
        for el_def in layout_defs:
            story_details = el_def.get_story_instance_details(s_num)
            planar_x, planar_y = story_details["xy_coords_planar"]
            area_name = story_details["area_object_name"]
            section_name = story_details["section_name"]
            is_cb = story_details["is_coupling_beam"]
            pier_spandrel_label = story_details["pier_spandrel_definition_name"]

            # 根据构件类型选择不同的Z坐标
            coords_3d_x = list(planar_x)
            coords_3d_y = list(planar_y)

            if is_cb:
                # 连梁：仅在层顶COUPLING_BEAM_HEIGHT范围内
                coords_3d_z = [z_cb_b, z_cb_b, z_cb_t, z_cb_t]

                created_names = create_meshed_element(
                    area_obj, coords_3d_x, coords_3d_y, coords_3d_z,
                    section_name, area_name, pier_spandrel_label,
                    COUPLING_BEAM_MESH_H, COUPLING_BEAM_MESH_V,
                    "连梁", is_coupling_beam=True
                )
                cb_names.extend(created_names)
                story_cb_count += len(created_names)
            else:
                # 剪力墙：跨越整个层高
                coords_3d_z = [z_b, z_b, z_t, z_t]

                created_names = create_meshed_element(
                    area_obj, coords_3d_x, coords_3d_y, coords_3d_z,
                    section_name, area_name, pier_spandrel_label,
                    SHEAR_WALL_MESH_H, SHEAR_WALL_MESH_V,
                    "剪力墙", is_coupling_beam=False
                )
                wall_names.extend(created_names)
                story_wall_count += len(created_names)

        print(f"    第 {s_num} 层完成: {story_wall_count} 个墙体网格, {story_cb_count} 个连梁网格")

    # 创建楼板
    print("\n🏢 开始创建剪力墙楼板...")
    create_shear_wall_slabs(sap_model, story_heights)

    print(f"\n✅ 剪力墙结构几何创建完成:")
    print(f"   - 剪力墙网格单元: {len(wall_names)} 个")
    print(f"   - 连梁网格单元: {len(cb_names)} 个")

    return wall_names, cb_names, story_heights


def create_shear_wall_slabs(sap_model, story_heights: Dict[int, float]):
    """
    创建剪力墙结构的楼板

    Parameters:
        sap_model: ETABS SapModel对象
        story_heights: 楼层高度字典
    """
    grid_x, grid_y = generate_grid_coordinates()
    area_obj = sap_model.AreaObj

    cum_z_slabs = 0.0
    slab_count = 0

    for i_s in range(NUM_STORIES):
        s_num = i_s + 1
        s_h = story_heights.get(s_num, TYPICAL_STORY_HEIGHT)
        cum_z_slabs += s_h
        z_sl = cum_z_slabs

        for ix_sl in range(NUM_GRID_LINES_X - 1):
            for iy_sl in range(NUM_GRID_LINES_Y - 1):
                x0, y0 = grid_x[ix_sl], grid_y[iy_sl]
                x1, y1 = grid_x[ix_sl + 1], grid_y[iy_sl + 1]

                sl_x = [x0, x1, x1, x0]
                sl_y = [y0, y0, y1, y1]
                sl_z = [z_sl] * 4
                sl_name = f"SLAB_X{ix_sl}_Y{iy_sl}_S{s_num}"

                # 使用楼板网格划分函数
                created_slab_names = create_meshed_slab(
                    area_obj, sl_x, sl_y, sl_z,
                    SLAB_SECTION_NAME, sl_name,
                    SLAB_MESH_X, SLAB_MESH_Y
                )

                slab_count += len(created_slab_names)

    print(f"✅ 剪力墙楼板创建完成，共 {slab_count} 个网格单元")