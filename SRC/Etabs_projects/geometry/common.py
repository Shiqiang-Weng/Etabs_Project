# -*- coding: utf-8 -*-
"""
几何模块通用工具
包含结构几何创建的通用函数和类
"""

from typing import List, Dict, Any
from config import SPACING_X, SPACING_Y, NUM_GRID_LINES_X, NUM_GRID_LINES_Y


class StructuralElementPlan:
    """结构构件平面定义类"""

    def __init__(self, x_coords: List[float], y_coords: List[float],
                 section_name: str, base_name_template: str,
                 is_coupling_beam: bool, element_type_prefix: str):
        """
        初始化结构构件平面定义

        Parameters:
            x_coords: X坐标列表
            y_coords: Y坐标列表
            section_name: 截面名称
            base_name_template: 基础名称模板
            is_coupling_beam: 是否为连梁
            element_type_prefix: 构件类型前缀（P=墙肢, S=连梁）
        """
        self.x_coords = list(x_coords)
        self.y_coords = list(y_coords)
        self.section_name = section_name
        self.base_name_template = base_name_template
        self.is_coupling_beam = is_coupling_beam
        self.element_type_prefix = element_type_prefix

    def get_story_instance_details(self, story_number: int) -> Dict[str, Any]:
        """
        获取指定楼层的构件详细信息

        Parameters:
            story_number: 楼层号

        Returns:
            dict: 构件详细信息
        """
        return {
            "xy_coords_planar": (self.x_coords, self.y_coords),
            "area_object_name": f"{self.base_name_template}_S{story_number}",
            "section_name": self.section_name,
            "is_coupling_beam": self.is_coupling_beam,
            "pier_spandrel_definition_name": f"{self.element_type_prefix}_{self.base_name_template}"
        }


def generate_grid_coordinates() -> tuple:
    """
    生成网格坐标

    Returns:
        tuple: (grid_x, grid_y) 网格坐标列表
    """
    grid_x = [i * SPACING_X for i in range(NUM_GRID_LINES_X)]
    grid_y = [i * SPACING_Y for i in range(NUM_GRID_LINES_Y)]
    return grid_x, grid_y


def calculate_element_dimensions(x_coords: List[float], y_coords: List[float]) -> Dict[str, float]:
    """
    计算构件尺寸

    Parameters:
        x_coords: X坐标列表
        y_coords: Y坐标列表

    Returns:
        dict: 包含width, height等尺寸信息
    """
    width_x = abs(max(x_coords) - min(x_coords)) if len(set(x_coords)) > 1 else 0
    width_y = abs(max(y_coords) - min(y_coords)) if len(set(y_coords)) > 1 else 0

    return {
        'width_x': width_x,
        'width_y': width_y,
        'x_min': min(x_coords),
        'x_max': max(x_coords),
        'y_min': min(y_coords),
        'y_max': max(y_coords),
        'is_x_direction': width_x > width_y,  # 判断主要方向
        'orientation': 'X方向' if width_x > width_y else 'Y方向'
    }


def create_pier_spandrel_labels(sap_model, layout_defs: List[StructuralElementPlan]) -> tuple:
    """
    创建墙肢和连梁标签

    Parameters:
        sap_model: ETABS SapModel对象
        layout_defs: 布局定义列表

    Returns:
        tuple: (defined_piers, defined_spandrels) 已定义的标签集合
    """
    from utils import check_ret

    pier_obj = sap_model.PierLabel
    spandrel_obj = sap_model.SpandrelLabel

    defined_piers = set()
    defined_spandrels = set()

    for el_def in layout_defs:
        label = f"{el_def.element_type_prefix}_{el_def.base_name_template}"

        if el_def.is_coupling_beam and label not in defined_spandrels:
            check_ret(spandrel_obj.SetSpandrel(label, False), f"SetSpandrel({label})", (0, 1))
            defined_spandrels.add(label)

        elif (not el_def.is_coupling_beam) and label not in defined_piers:
            check_ret(pier_obj.SetPier(label), f"SetPier({label})", (0, 1))
            defined_piers.add(label)

    print(f"已创建 {len(defined_piers)} 个墙肢标签和 {len(defined_spandrels)} 个连梁标签")

    return defined_piers, defined_spandrels


def print_element_creation_info(element_type: str, orientation: str,
                                width: float, height: float, mesh_config: str):
    """
    打印构件创建信息

    Parameters:
        element_type: 构件类型
        orientation: 方向
        width: 宽度
        height: 高度
        mesh_config: 网格配置
    """
    print(f"    创建{orientation}{element_type}: {width:.1f}m × {height:.1f}m，{mesh_config}")


def validate_coordinates(x_coords: List[float], y_coords: List[float],
                         z_coords: List[float]) -> bool:
    """
    验证坐标有效性

    Parameters:
        x_coords: X坐标列表
        y_coords: Y坐标列表
        z_coords: Z坐标列表

    Returns:
        bool: 坐标有效返回True
    """
    if not (len(x_coords) == len(y_coords) == len(z_coords)):
        return False

    if len(x_coords) < 3:  # 至少需要3个点构成面
        return False

    # 检查是否所有坐标都是有效数值
    try:
        for coords in [x_coords, y_coords, z_coords]:
            for coord in coords:
                float(coord)
    except (ValueError, TypeError):
        return False

    return True