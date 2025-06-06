# -*- coding: utf-8 -*-
"""
网格划分工具
包含各种构件的网格划分功能
"""

from typing import List, Tuple
from utils import add_area_by_coord_custom, check_ret
from geometry.common import calculate_element_dimensions, print_element_creation_info, validate_coordinates


def create_mesh_grid(x_min: float, x_max: float, y_min: float, y_max: float,
                     z_min: float, z_max: float, mesh_h: int, mesh_v: int,
                     orientation: str) -> List[Tuple[List[float], List[float], List[float]]]:
    """
    创建网格坐标

    Parameters:
        x_min, x_max: X方向范围
        y_min, y_max: Y方向范围
        z_min, z_max: Z方向范围
        mesh_h: 水平方向网格数
        mesh_v: 竖直方向网格数
        orientation: 方向（'X'或'Y'）

    Returns:
        list: 网格单元坐标列表
    """
    mesh_elements = []

    if orientation == 'X':
        # X方向构件（水平构件）
        width = x_max - x_min
        height = z_max - z_min
        dx = width / mesh_h
        dz = height / mesh_v
        y_coord = y_min  # Y坐标保持不变

        for i in range(mesh_h):
            for j in range(mesh_v):
                x0 = x_min + i * dx
                x1 = x_min + (i + 1) * dx
                z0 = z_min + j * dz
                z1 = z_min + (j + 1) * dz

                mesh_x = [x0, x1, x1, x0]
                mesh_y = [y_coord] * 4
                mesh_z = [z0, z0, z1, z1]

                mesh_elements.append((mesh_x, mesh_y, mesh_z))

    else:  # Y方向构件（竖直构件）
        width = y_max - y_min
        height = z_max - z_min
        dy = width / mesh_h
        dz = height / mesh_v
        x_coord = x_min  # X坐标保持不变

        for i in range(mesh_h):
            for j in range(mesh_v):
                y0 = y_min + i * dy
                y1 = y_min + (i + 1) * dy
                z0 = z_min + j * dz
                z1 = z_min + (j + 1) * dz

                mesh_x = [x_coord] * 4
                mesh_y = [y0, y1, y1, y0]
                mesh_z = [z0, z0, z1, z1]

                mesh_elements.append((mesh_x, mesh_y, mesh_z))

    return mesh_elements


def create_slab_mesh_grid(x_min: float, x_max: float, y_min: float, y_max: float,
                          z_coord: float, mesh_x: int, mesh_y: int) -> List[
    Tuple[List[float], List[float], List[float]]]:
    """
    创建楼板网格坐标

    Parameters:
        x_min, x_max: X方向范围
        y_min, y_max: Y方向范围
        z_coord: Z坐标（楼板高度）
        mesh_x: X方向网格数
        mesh_y: Y方向网格数

    Returns:
        list: 楼板网格单元坐标列表
    """
    mesh_elements = []

    width_x = x_max - x_min
    width_y = y_max - y_min
    dx = width_x / mesh_x
    dy = width_y / mesh_y

    for i in range(mesh_x):
        for j in range(mesh_y):
            x0 = x_min + i * dx
            x1 = x_min + (i + 1) * dx
            y0 = y_min + j * dy
            y1 = y_min + (j + 1) * dy

            mesh_x_coords = [x0, x1, x1, x0]
            mesh_y_coords = [y0, y0, y1, y1]
            mesh_z_coords = [z_coord] * 4

            mesh_elements.append((mesh_x_coords, mesh_y_coords, mesh_z_coords))

    return mesh_elements


def create_meshed_element(area_api, x_list: List[float], y_list: List[float],
                          z_list: List[float], section: str, base_user_name: str,
                          pier_or_spandrel_label: str, mesh_h: int, mesh_v: int,
                          element_type: str, is_coupling_beam: bool = False) -> List[str]:
    """
    创建网格化构件

    Parameters:
        area_api: ETABS面对象API
        x_list, y_list, z_list: 坐标列表
        section: 截面名称
        base_user_name: 基础用户名
        pier_or_spandrel_label: 墙肢或连梁标签
        mesh_h, mesh_v: 水平和竖直方向网格数
        element_type: 构件类型
        is_coupling_beam: 是否为连梁

    Returns:
        list: 创建的构件名称列表
    """
    # 验证输入坐标
    if not validate_coordinates(x_list, y_list, z_list):
        print(f"警告: 坐标无效，跳过构件 {base_user_name}")
        return []

    created_names = []
    dimensions = calculate_element_dimensions(x_list, y_list)

    # 确定构件方向和尺寸
    if dimensions['is_x_direction']:
        orientation = 'X'
        width = dimensions['width_x']
        height = abs(max(z_list) - min(z_list))
        x_min, x_max = dimensions['x_min'], dimensions['x_max']
        y_min = y_list[0]
        z_min, z_max = min(z_list), max(z_list)

        mesh_config = f"{mesh_h}×{mesh_v}网格划分"
        print_element_creation_info(element_type, "水平", width, height, mesh_config)

        # 生成网格
        mesh_elements = create_mesh_grid(x_min, x_max, y_min, y_min,
                                         z_min, z_max, mesh_h, mesh_v, 'X')
    else:
        orientation = 'Y'
        width = dimensions['width_y']
        height = abs(max(z_list) - min(z_list))
        y_min, y_max = dimensions['y_min'], dimensions['y_max']
        x_min = x_list[0]
        z_min, z_max = min(z_list), max(z_list)

        mesh_config = f"{mesh_h}×{mesh_v}网格划分"
        print_element_creation_info(element_type, "竖直", width, height, mesh_config)

        # 生成网格
        mesh_elements = create_mesh_grid(x_min, x_min, y_min, y_max,
                                         z_min, z_max, mesh_h, mesh_v, 'Y')

    # 创建网格单元
    for idx, (mesh_x, mesh_y, mesh_z) in enumerate(mesh_elements):
        i = idx // mesh_v + 1
        j = idx % mesh_v + 1
        mesh_name = f"{base_user_name}_H{i}_V{j}"

        ret_code, etabs_name = add_area_by_coord_custom(
            area_api, 4, mesh_x, mesh_y, mesh_z, section, mesh_name
        )
        check_ret(ret_code, f"AddByCoord({mesh_name})")

        name_final = etabs_name or mesh_name
        created_names.append(name_final)

        # 分配Pier或Spandrel标签
        if pier_or_spandrel_label:
            if is_coupling_beam:
                check_ret(area_api.SetSpandrel(name_final, pier_or_spandrel_label),
                          f"SetSpandrel({name_final})")
            else:
                check_ret(area_api.SetPier(name_final, pier_or_spandrel_label),
                          f"SetPier({name_final})")

    print(f"      完成创建 {len(created_names)} 个{element_type}网格单元")
    return created_names


def create_meshed_slab(area_api, x_list: List[float], y_list: List[float],
                       z_list: List[float], section: str, base_user_name: str,
                       mesh_x: int, mesh_y: int) -> List[str]:
    """
    创建网格化楼板

    Parameters:
        area_api: ETABS面对象API
        x_list, y_list, z_list: 坐标列表
        section: 截面名称
        base_user_name: 基础用户名
        mesh_x, mesh_y: X和Y方向网格数

    Returns:
        list: 创建的楼板名称列表
    """
    if not validate_coordinates(x_list, y_list, z_list):
        print(f"警告: 楼板坐标无效，跳过构件 {base_user_name}")
        return []

    created_names = []
    dimensions = calculate_element_dimensions(x_list, y_list)

    width_x = dimensions['width_x']
    width_y = dimensions['width_y']
    z_coord = z_list[0]

    print(f"    创建楼板: {width_x:.1f}m × {width_y:.1f}m，{mesh_x}×{mesh_y}网格划分")

    # 生成楼板网格
    mesh_elements = create_slab_mesh_grid(
        dimensions['x_min'], dimensions['x_max'],
        dimensions['y_min'], dimensions['y_max'],
        z_coord, mesh_x, mesh_y
    )

    # 创建网格单元
    for idx, (mesh_x_coords, mesh_y_coords, mesh_z_coords) in enumerate(mesh_elements):
        i = idx // mesh_y + 1
        j = idx % mesh_y + 1
        mesh_name = f"{base_user_name}_X{i}_Y{j}"

        ret_code, etabs_name = add_area_by_coord_custom(
            area_api, 4, mesh_x_coords, mesh_y_coords, mesh_z_coords, section, mesh_name
        )
        check_ret(ret_code, f"AddByCoord({mesh_name})")

        name_final = etabs_name or mesh_name
        created_names.append(name_final)

        # 为楼板网格单元分配半刚性楼面约束
        check_ret(
            area_api.SetDiaphragm(name_final, "SRD"),
            f"SetDiaphragm({name_final}, SRD)"
        )

    print(f"      完成创建 {len(created_names)} 个楼板网格单元")
    return created_names