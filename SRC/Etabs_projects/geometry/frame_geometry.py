# -*- coding: utf-8 -*-
"""
框架几何创建模块
负责创建框架结构的柱和梁（线单元）
"""

from typing import List, Dict, Tuple
from config import (
    NUM_STORIES, TYPICAL_STORY_HEIGHT, BOTTOM_STORY_HEIGHT,
    FRAME_COLUMN_SECTION_NAME, FRAME_BEAM_SECTION_NAME, SECONDARY_BEAM_SECTION_NAME,
    COLUMN_GRID_PATTERN, BEAM_LAYOUT, MAIN_BEAM_DIRECTION, SECONDARY_BEAM_SPACING,
    ENABLE_FRAME_COLUMNS, ENABLE_FRAME_BEAMS, NUM_GRID_LINES_X, NUM_GRID_LINES_Y,
    SLAB_SECTION_NAME, SLAB_MESH_X, SLAB_MESH_Y
)
from geometry.common import generate_grid_coordinates
from utils import add_frame_by_coord_custom, check_ret

# 可选导入次梁方向参数
try:
    from config import SECONDARY_BEAM_DIRECTION
except ImportError:
    SECONDARY_BEAM_DIRECTION = "Y"  # 默认Y方向


def create_frame_columns(sap_model, story_heights: Dict[int, float]) -> List[str]:
    """
    创建框架柱

    Parameters:
        sap_model: ETABS SapModel对象
        story_heights: 楼层高度字典

    Returns:
        list: 创建的柱名称列表
    """
    if not ENABLE_FRAME_COLUMNS:
        print("⏭️ 跳过框架柱创建（未启用）")
        return []

    print(f"\n🏗️ 开始创建框架柱...")
    print(f"   布置模式: {COLUMN_GRID_PATTERN}")

    frame_obj = sap_model.FrameObj
    grid_x, grid_y = generate_grid_coordinates()
    column_names = []

    # 根据布置模式确定柱子位置
    column_positions = []

    if COLUMN_GRID_PATTERN == "ALL_INTERSECTIONS":
        # 所有网格交点
        for i, x in enumerate(grid_x):
            for j, y in enumerate(grid_y):
                column_positions.append((i, j, x, y))

    elif COLUMN_GRID_PATTERN == "PERIMETER_ONLY":
        # 仅周边
        for i, x in enumerate(grid_x):
            for j, y in enumerate(grid_y):
                if i == 0 or i == len(grid_x) - 1 or j == 0 or j == len(grid_y) - 1:
                    column_positions.append((i, j, x, y))

    elif COLUMN_GRID_PATTERN == "CORNER_ONLY":
        # 仅角点
        corner_indices = [(0, 0), (0, len(grid_y) - 1), (len(grid_x) - 1, 0), (len(grid_x) - 1, len(grid_y) - 1)]
        for i, j in corner_indices:
            column_positions.append((i, j, grid_x[i], grid_y[j]))
    else:
        # 默认所有交点
        for i, x in enumerate(grid_x):
            for j, y in enumerate(grid_y):
                column_positions.append((i, j, x, y))

    print(f"   柱子数量: {len(column_positions)} 个/层")

    # 计算累积高度
    cum_z = 0.0

    for story_num in range(1, NUM_STORIES + 1):
        story_height = story_heights.get(story_num, TYPICAL_STORY_HEIGHT)
        z_bottom = cum_z
        z_top = cum_z + story_height
        cum_z = z_top

        print(f"  第 {story_num} 层柱子 (标高: {z_bottom:.1f}m - {z_top:.1f}m):")

        for i, j, x, y in column_positions:
            # 柱子名称
            col_name = f"COL_X{i}_Y{j}_S{story_num}"

            # 创建柱子（底部到顶部）
            ret_code, actual_name = add_frame_by_coord_custom(
                frame_obj, x, y, z_bottom, x, y, z_top,
                FRAME_COLUMN_SECTION_NAME, col_name, "Global"
            )

            check_ret(ret_code, f"AddFrameByCoord({col_name})")
            column_names.append(actual_name)

        print(f"    完成创建 {len(column_positions)} 根柱子")

    print(f"✅ 框架柱创建完成，共 {len(column_names)} 根")
    return column_names


def create_frame_beams(sap_model, story_heights: Dict[int, float]) -> List[str]:
    """
    创建框架梁

    Parameters:
        sap_model: ETABS SapModel对象
        story_heights: 楼层高度字典

    Returns:
        list: 创建的梁名称列表
    """
    if not ENABLE_FRAME_BEAMS:
        print("⏭️ 跳过框架梁创建（未启用）")
        return []

    print(f"\n🏗️ 开始创建框架梁...")
    print(f"   主梁方向: {MAIN_BEAM_DIRECTION}")
    print(f"   次梁设置: 间距{SECONDARY_BEAM_SPACING}m, 方向{SECONDARY_BEAM_DIRECTION}")

    frame_obj = sap_model.FrameObj
    grid_x, grid_y = generate_grid_coordinates()
    beam_names = []

    # 计算累积高度
    cum_z = 0.0

    for story_num in range(1, NUM_STORIES + 1):
        story_height = story_heights.get(story_num, TYPICAL_STORY_HEIGHT)
        z_level = cum_z + story_height  # 梁在楼层顶部
        cum_z += story_height

        print(f"  第 {story_num} 层梁 (标高: {z_level:.1f}m):")
        story_beam_count = 0

        # 创建X方向主梁
        if BEAM_LAYOUT.get('MAIN_BEAMS_X', False) and MAIN_BEAM_DIRECTION in ["X_ONLY", "BOTH"]:
            for j, y in enumerate(grid_y):
                for i in range(NUM_GRID_LINES_X - 1):
                    x1, x2 = grid_x[i], grid_x[i + 1]
                    beam_name = f"BEAM_X{i}_{i + 1}_Y{j}_S{story_num}"

                    ret_code, actual_name = add_frame_by_coord_custom(
                        frame_obj, x1, y, z_level, x2, y, z_level,
                        FRAME_BEAM_SECTION_NAME, beam_name, "Global"
                    )

                    check_ret(ret_code, f"AddFrameByCoord({beam_name})")
                    beam_names.append(actual_name)
                    story_beam_count += 1

        # 创建Y方向主梁
        if BEAM_LAYOUT.get('MAIN_BEAMS_Y', False) and MAIN_BEAM_DIRECTION in ["Y_ONLY", "BOTH"]:
            for i, x in enumerate(grid_x):
                for j in range(NUM_GRID_LINES_Y - 1):
                    y1, y2 = grid_y[j], grid_y[j + 1]
                    beam_name = f"BEAM_X{i}_Y{j}_{j + 1}_S{story_num}"

                    ret_code, actual_name = add_frame_by_coord_custom(
                        frame_obj, x, y1, z_level, x, y2, z_level,
                        FRAME_BEAM_SECTION_NAME, beam_name, "Global"
                    )

                    check_ret(ret_code, f"AddFrameByCoord({beam_name})")
                    beam_names.append(actual_name)
                    story_beam_count += 1

        # 创建次梁
        if BEAM_LAYOUT.get('SECONDARY_BEAMS', False):
            secondary_beams = _create_secondary_beams(
                frame_obj, grid_x, grid_y, z_level, story_num
            )
            beam_names.extend(secondary_beams)
            story_beam_count += len(secondary_beams)

        print(f"    完成创建 {story_beam_count} 根梁")

    print(f"✅ 框架梁创建完成，共 {len(beam_names)} 根")
    return beam_names


def _create_secondary_beams(frame_obj, grid_x: List[float], grid_y: List[float],
                            z_level: float, story_num: int) -> List[str]:
    """
    创建次梁

    Parameters:
        frame_obj: ETABS框架对象API
        grid_x: X方向网格坐标
        grid_y: Y方向网格坐标
        z_level: 标高
        story_num: 楼层号

    Returns:
        list: 创建的次梁名称列表
    """
    secondary_beam_names = []

    # 在每个网格区域内创建次梁
    for i in range(NUM_GRID_LINES_X - 1):
        for j in range(NUM_GRID_LINES_Y - 1):
            x1, x2 = grid_x[i], grid_x[i + 1]
            y1, y2 = grid_y[j], grid_y[j + 1]

            # 计算次梁数量和位置
            if SECONDARY_BEAM_DIRECTION == "Y":
                # Y方向次梁（跨越X方向）
                span_length = x2 - x1
                num_secondary = max(1, int(span_length / SECONDARY_BEAM_SPACING))

                if num_secondary > 1:
                    dy = span_length / num_secondary
                    for k in range(1, num_secondary):
                        x_sec = x1 + k * dy
                        sec_beam_name = f"SEC_BEAM_X{i}_{i + 1}_Y{j}_{j + 1}_K{k}_S{story_num}"

                        ret_code, actual_name = add_frame_by_coord_custom(
                            frame_obj, x_sec, y1, z_level, x_sec, y2, z_level,
                            SECONDARY_BEAM_SECTION_NAME, sec_beam_name, "Global"
                        )

                        check_ret(ret_code, f"AddFrameByCoord({sec_beam_name})")
                        secondary_beam_names.append(actual_name)

            elif SECONDARY_BEAM_DIRECTION == "X":
                # X方向次梁（跨越Y方向）
                span_length = y2 - y1
                num_secondary = max(1, int(span_length / SECONDARY_BEAM_SPACING))

                if num_secondary > 1:
                    dx = span_length / num_secondary
                    for k in range(1, num_secondary):
                        y_sec = y1 + k * dx
                        sec_beam_name = f"SEC_BEAM_X{i}_{i + 1}_Y{j}_{j + 1}_K{k}_S{story_num}"

                        ret_code, actual_name = add_frame_by_coord_custom(
                            frame_obj, x1, y_sec, z_level, x2, y_sec, z_level,
                            SECONDARY_BEAM_SECTION_NAME, sec_beam_name, "Global"
                        )

                        check_ret(ret_code, f"AddFrameByCoord({sec_beam_name})")
                        secondary_beam_names.append(actual_name)

    if secondary_beam_names:
        print(f"    完成创建 {len(secondary_beam_names)} 根次梁")

    return secondary_beam_names


def create_frame_slabs(sap_model, story_heights: Dict[int, float]) -> List[str]:
    """
    创建框架结构的楼板

    Parameters:
        sap_model: ETABS SapModel对象
        story_heights: 楼层高度字典

    Returns:
        list: 创建的楼板名称列表
    """
    from geometry.mesh_utils import create_meshed_slab

    print(f"\n🏢 开始创建框架楼板...")

    grid_x, grid_y = generate_grid_coordinates()
    area_obj = sap_model.AreaObj
    slab_names = []

    cum_z_slabs = 0.0

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

                slab_names.extend(created_slab_names)

    print(f"✅ 框架楼板创建完成，共 {len(slab_names)} 个网格单元")
    return slab_names


def create_frame_structural_geometry(sap_model) -> Tuple[List[str], List[str], List[str], Dict[int, float]]:
    """
    创建框架结构几何体 - 主要接口函数

    Parameters:
        sap_model: ETABS SapModel对象

    Returns:
        tuple: (column_names, beam_names, slab_names, story_heights)
    """
    print(f"\n🏗️ 开始创建 {NUM_STORIES} 层框架结构...")
    print(f"   网格: {NUM_GRID_LINES_X}×{NUM_GRID_LINES_Y}")
    print(f"   柱截面: {FRAME_COLUMN_SECTION_NAME}")
    print(f"   主梁截面: {FRAME_BEAM_SECTION_NAME}")
    print(f"   次梁截面: {SECONDARY_BEAM_SECTION_NAME}")

    # 计算楼层高度
    story_heights = {}
    for s_num in range(1, NUM_STORIES + 1):
        story_heights[s_num] = TYPICAL_STORY_HEIGHT if s_num > 1 else BOTTOM_STORY_HEIGHT

    # 创建柱子
    column_names = create_frame_columns(sap_model, story_heights)

    # 创建梁
    beam_names = create_frame_beams(sap_model, story_heights)

    # 创建楼板
    slab_names = create_frame_slabs(sap_model, story_heights)

    # 打印摘要
    print(f"\n✅ 框架结构几何创建完成:")
    print(f"   - 框架柱: {len(column_names)} 根")
    print(f"   - 框架梁: {len(beam_names)} 根")
    print(f"   - 楼板单元: {len(slab_names)} 个")
    print(f"   - 楼层数: {len(story_heights)} 层")

    return column_names, beam_names, slab_names, story_heights


def validate_frame_geometry():
    """
    验证框架几何参数的合理性

    Returns:
        bool: 验证通过返回True
    """
    try:
        from config import SPACING_X, SPACING_Y, FRAME_BEAM_DEPTH

        issues = []

        # 检查柱距
        MIN_COLUMN_SPACING = 3.0
        MAX_COLUMN_SPACING = 12.0

        if SPACING_X < MIN_COLUMN_SPACING:
            issues.append(f"X方向柱距 {SPACING_X}m 小于最小值 {MIN_COLUMN_SPACING}m")
        if SPACING_X > MAX_COLUMN_SPACING:
            issues.append(f"X方向柱距 {SPACING_X}m 大于最大值 {MAX_COLUMN_SPACING}m")

        if SPACING_Y < MIN_COLUMN_SPACING:
            issues.append(f"Y方向柱距 {SPACING_Y}m 小于最小值 {MIN_COLUMN_SPACING}m")
        if SPACING_Y > MAX_COLUMN_SPACING:
            issues.append(f"Y方向柱距 {SPACING_Y}m 大于最大值 {MAX_COLUMN_SPACING}m")

        # 检查跨高比
        max_span = max(SPACING_X, SPACING_Y)
        span_to_depth = max_span / FRAME_BEAM_DEPTH
        if span_to_depth > 25:
            issues.append(f"梁跨高比 {span_to_depth:.1f} 大于限值 25")

        if issues:
            print("⚠️ 框架几何验证发现问题:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ 框架几何验证通过")
            return True

    except ImportError as e:
        print(f"⚠️ 框架几何验证失败: {e}")
        return True  # 容错处理


def get_frame_statistics():
    """
    获取框架统计信息

    Returns:
        dict: 框架统计信息
    """
    stats = {}

    try:
        grid_x, grid_y = generate_grid_coordinates()

        # 柱数量
        if COLUMN_GRID_PATTERN == "ALL_INTERSECTIONS":
            columns_per_level = len(grid_x) * len(grid_y)
        elif COLUMN_GRID_PATTERN == "PERIMETER_ONLY":
            columns_per_level = 2 * (len(grid_x) + len(grid_y) - 2)
        elif COLUMN_GRID_PATTERN == "CORNER_ONLY":
            columns_per_level = 4
        else:
            columns_per_level = len(grid_x) * len(grid_y)

        stats['columns_per_level'] = columns_per_level
        stats['total_columns'] = columns_per_level * NUM_STORIES

        # 梁数量估算
        beams_per_level = 0
        if MAIN_BEAM_DIRECTION in ["X_ONLY", "BOTH"]:
            beams_per_level += (NUM_GRID_LINES_X - 1) * NUM_GRID_LINES_Y
        if MAIN_BEAM_DIRECTION in ["Y_ONLY", "BOTH"]:
            beams_per_level += NUM_GRID_LINES_X * (NUM_GRID_LINES_Y - 1)

        stats['beams_per_level'] = beams_per_level
        stats['total_beams'] = beams_per_level * NUM_STORIES

        # 楼板数量
        slab_panels = (NUM_GRID_LINES_X - 1) * (NUM_GRID_LINES_Y - 1) * NUM_STORIES
        slab_elements = slab_panels * SLAB_MESH_X * SLAB_MESH_Y
        stats['slab_elements'] = slab_elements

        stats['total_elements'] = stats['total_columns'] + stats['total_beams'] + stats['slab_elements']

    except Exception as e:
        print(f"⚠️ 统计信息计算失败: {e}")
        stats = {'total_elements': 0}

    return stats


def print_frame_geometry_summary():
    """
    打印框架几何摘要
    """
    try:
        stats = get_frame_statistics()

        print(f"\n📊 框架几何摘要:")
        print(f"   柱子: {stats.get('total_columns', 0)} 根")
        print(f"   梁: {stats.get('total_beams', 0)} 根")
        print(f"   楼板单元: {stats.get('slab_elements', 0)} 个")
        print(f"   总单元数: {stats.get('total_elements', 0)} 个")

        # 布置模式
        print(f"   柱布置: {COLUMN_GRID_PATTERN}")
        print(f"   主梁方向: {MAIN_BEAM_DIRECTION}")
        print(f"   次梁间距: {SECONDARY_BEAM_SPACING}m")

    except Exception as e:
        print(f"⚠️ 框架几何摘要打印失败: {e}")