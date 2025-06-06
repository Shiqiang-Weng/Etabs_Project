# -*- coding: utf-8 -*-
"""
混凝土材料定义模块 - 扩展支持框架结构
"""

from utils import check_ret, get_etabs_modules
from config import (
    CONCRETE_MATERIAL_NAME, CONCRETE_PROPERTIES,
    WALL_SECTION_NAME, COUPLING_BEAM_SECTION_NAME,
    SLAB_SECTION_NAME, FRAME_COLUMN_SECTION_NAME,
    FRAME_BEAM_SECTION_NAME, SECONDARY_BEAM_SECTION_NAME,
    SECTION_PROPERTIES, ENABLE_FRAME_COLUMNS, ENABLE_FRAME_BEAMS,
    ENABLE_SHEAR_WALLS
)

# 可选导入钢材参数（如果存在）
try:
    from config import STEEL_MATERIAL_NAME, STEEL_PROPERTIES

    STEEL_AVAILABLE = True
except ImportError:
    STEEL_MATERIAL_NAME = "Q345"  # 默认值
    STEEL_PROPERTIES = {
        'E_MODULUS': 206000000,
        'POISSON': 0.3,
        'THERMAL_EXP': 1.2e-5,
        'UNIT_WEIGHT': 78.5,
        'FY': 345,
        'FU': 470,
    }
    STEEL_AVAILABLE = False


def define_concrete_material(sap_model):
    """
    定义混凝土材料

    Parameters:
        sap_model: ETABS SapModel对象
    """
    ETABSv1, System, COMException = get_etabs_modules()

    if not all([ETABSv1, System, sap_model]):
        raise ValueError("ETABS模块或SapModel未正确初始化")

    pm = sap_model.PropMaterial

    # 定义混凝土材料
    check_ret(
        pm.SetMaterial(CONCRETE_MATERIAL_NAME, ETABSv1.eMatType.Concrete),
        f"SetMaterial({CONCRETE_MATERIAL_NAME})",
        (0, 1)
    )

    # 设置各向同性材料属性
    check_ret(
        pm.SetMPIsotropic(
            CONCRETE_MATERIAL_NAME,
            CONCRETE_PROPERTIES['E_MODULUS'],
            CONCRETE_PROPERTIES['POISSON'],
            CONCRETE_PROPERTIES['THERMAL_EXP']
        ),
        f"SetMPIsotropic({CONCRETE_MATERIAL_NAME})"
    )

    # 设置重量和质量
    check_ret(
        pm.SetWeightAndMass(
            CONCRETE_MATERIAL_NAME,
            1,
            CONCRETE_PROPERTIES['UNIT_WEIGHT']
        ),
        f"SetWeightAndMass({CONCRETE_MATERIAL_NAME})"
    )

    print(f"✅ 混凝土材料 '{CONCRETE_MATERIAL_NAME}' 定义完成")


def define_steel_material(sap_model):
    """
    定义钢材料（如果需要）

    Parameters:
        sap_model: ETABS SapModel对象
    """
    ETABSv1, System, COMException = get_etabs_modules()

    if not all([ETABSv1, System, sap_model]):
        raise ValueError("ETABS模块或SapModel未正确初始化")

    pm = sap_model.PropMaterial

    # 定义钢材料
    check_ret(
        pm.SetMaterial(STEEL_MATERIAL_NAME, ETABSv1.eMatType.Steel),
        f"SetMaterial({STEEL_MATERIAL_NAME})",
        (0, 1)
    )

    # 设置各向同性材料属性
    check_ret(
        pm.SetMPIsotropic(
            STEEL_MATERIAL_NAME,
            STEEL_PROPERTIES['E_MODULUS'],
            STEEL_PROPERTIES['POISSON'],
            STEEL_PROPERTIES['THERMAL_EXP']
        ),
        f"SetMPIsotropic({STEEL_MATERIAL_NAME})"
    )

    # 设置重量和质量
    check_ret(
        pm.SetWeightAndMass(
            STEEL_MATERIAL_NAME,
            1,
            STEEL_PROPERTIES['UNIT_WEIGHT']
        ),
        f"SetWeightAndMass({STEEL_MATERIAL_NAME})"
    )

    print(f"✅ 钢材料 '{STEEL_MATERIAL_NAME}' 定义完成")


def define_wall_sections(sap_model):
    """
    定义墙体截面

    Parameters:
        sap_model: ETABS SapModel对象
    """
    if not ENABLE_SHEAR_WALLS:
        print("⏭️ 跳过剪力墙截面定义（未启用剪力墙）")
        return

    ETABSv1, System, COMException = get_etabs_modules()
    pa = sap_model.PropArea

    # 剪力墙截面
    wall_props = SECTION_PROPERTIES['WALL']
    check_ret(
        pa.SetWall(
            WALL_SECTION_NAME,
            getattr(ETABSv1.eWallPropType, wall_props['wall_type']),
            getattr(ETABSv1.eShellType, wall_props['shell_type']),
            wall_props['material'],
            wall_props['thickness']
        ),
        f"SetWall({WALL_SECTION_NAME})",
        (0, 1)
    )

    # 连梁截面
    cb_props = SECTION_PROPERTIES['COUPLING_BEAM']
    check_ret(
        pa.SetWall(
            COUPLING_BEAM_SECTION_NAME,
            getattr(ETABSv1.eWallPropType, cb_props['wall_type']),
            getattr(ETABSv1.eShellType, cb_props['shell_type']),
            cb_props['material'],
            cb_props['thickness']
        ),
        f"SetWall({COUPLING_BEAM_SECTION_NAME})",
        (0, 1)
    )

    print(f"✅ 墙体截面定义完成")


def define_slab_sections(sap_model):
    """
    定义楼板截面

    Parameters:
        sap_model: ETABS SapModel对象
    """
    ETABSv1, System, COMException = get_etabs_modules()
    pa = sap_model.PropArea

    # 楼板截面
    slab_props = SECTION_PROPERTIES['SLAB']

    # 根据结构类型选择楼板类型
    try:
        from config import STRUCTURE_TYPE
        if STRUCTURE_TYPE == "FRAME":
            # 框架结构使用薄板
            shell_type = 'ShellThin'
        else:
            # 剪力墙结构使用膜单元
            shell_type = slab_props.get('shell_type', 'Membrane')
    except:
        shell_type = slab_props.get('shell_type', 'Membrane')

    check_ret(
        pa.SetSlab(
            SLAB_SECTION_NAME,
            getattr(ETABSv1.eSlabType, slab_props['slab_type']),
            getattr(ETABSv1.eShellType, shell_type),
            slab_props['material'],
            slab_props['thickness']
        ),
        f"SetSlab({SLAB_SECTION_NAME})",
        (0, 1)
    )

    print(f"✅ 楼板截面定义完成（{shell_type}）")


def define_frame_sections(sap_model):
    """
    定义框架截面（梁和柱）

    Parameters:
        sap_model: ETABS SapModel对象
    """
    pf = sap_model.PropFrame

    # 定义柱截面
    if ENABLE_FRAME_COLUMNS:
        column_props = SECTION_PROPERTIES['FRAME_COLUMN']
        check_ret(
            pf.SetRectangle(
                FRAME_COLUMN_SECTION_NAME,
                column_props['material'],
                column_props['depth'],
                column_props['width']
            ),
            f"SetRectangle({FRAME_COLUMN_SECTION_NAME})",
            (0, 1)
        )
        print(f"✅ 柱截面 '{FRAME_COLUMN_SECTION_NAME}' 定义完成 ({column_props['width']}m×{column_props['depth']}m)")

    # 定义主梁截面
    if ENABLE_FRAME_BEAMS:
        beam_props = SECTION_PROPERTIES['FRAME_BEAM']
        check_ret(
            pf.SetRectangle(
                FRAME_BEAM_SECTION_NAME,
                beam_props['material'],
                beam_props['depth'],
                beam_props['width']
            ),
            f"SetRectangle({FRAME_BEAM_SECTION_NAME})",
            (0, 1)
        )
        print(f"✅ 主梁截面 '{FRAME_BEAM_SECTION_NAME}' 定义完成 ({beam_props['width']}m×{beam_props['depth']}m)")

        # 定义次梁截面
        secondary_props = SECTION_PROPERTIES['SECONDARY_BEAM']
        check_ret(
            pf.SetRectangle(
                SECONDARY_BEAM_SECTION_NAME,
                secondary_props['material'],
                secondary_props['depth'],
                secondary_props['width']
            ),
            f"SetRectangle({SECONDARY_BEAM_SECTION_NAME})",
            (0, 1)
        )
        print(
            f"✅ 次梁截面 '{SECONDARY_BEAM_SECTION_NAME}' 定义完成 ({secondary_props['width']}m×{secondary_props['depth']}m)")


def define_beam_sections(sap_model):
    """
    定义梁截面（保持向后兼容）

    Parameters:
        sap_model: ETABS SapModel对象
    """
    # 这个函数现在由define_frame_sections代替
    define_frame_sections(sap_model)


def validate_section_properties():
    """
    验证截面属性的合理性

    Returns:
        bool: 验证通过返回True
    """
    issues = []

    # 验证柱截面
    if ENABLE_FRAME_COLUMNS:
        col_props = SECTION_PROPERTIES['FRAME_COLUMN']
        if col_props['width'] < 0.3 or col_props['depth'] < 0.3:
            issues.append("柱截面尺寸过小（建议≥300mm）")
        if col_props['width'] > 1.5 or col_props['depth'] > 1.5:
            issues.append("柱截面尺寸过大（建议≤1500mm）")

    # 验证梁截面
    if ENABLE_FRAME_BEAMS:
        beam_props = SECTION_PROPERTIES['FRAME_BEAM']
        span_to_depth_ratio = 6.0 / beam_props['depth']  # 假设6m跨度
        if span_to_depth_ratio > 25:
            issues.append(f"主梁跨高比过大 ({span_to_depth_ratio:.1f})，建议增加梁高")
        if span_to_depth_ratio < 8:
            issues.append(f"主梁跨高比过小 ({span_to_depth_ratio:.1f})，可考虑减小梁高")

    # 验证剪力墙截面
    if ENABLE_SHEAR_WALLS:
        wall_props = SECTION_PROPERTIES.get('WALL', {})
        if 'thickness' in wall_props:
            thickness = wall_props['thickness']
            if thickness < 0.1:
                issues.append(f"剪力墙厚度过小 ({thickness * 1000:.0f}mm)，建议≥100mm")
            elif thickness > 0.6:
                issues.append(f"剪力墙厚度过大 ({thickness * 1000:.0f}mm)，建议≤600mm")

    if issues:
        print("⚠️ 截面属性验证发现问题:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ 截面属性验证通过")
        return True


def define_all_materials_and_sections(sap_model):
    """
    定义所有材料和截面

    Parameters:
        sap_model: ETABS SapModel对象
    """
    print("\n📐 开始定义材料和截面...")

    # 验证截面属性
    validate_section_properties()

    # 定义材料
    define_concrete_material(sap_model)
    # define_steel_material(sap_model)  # 如果需要钢结构，取消注释

    # 定义剪力墙截面
    if ENABLE_SHEAR_WALLS:
        define_wall_sections(sap_model)

    # 定义楼板截面
    define_slab_sections(sap_model)

    # 定义框架截面
    if ENABLE_FRAME_COLUMNS or ENABLE_FRAME_BEAMS:
        define_frame_sections(sap_model)

    print("✅ 所有材料和截面定义完成")

    # 打印结构类型摘要
    try:
        from config import STRUCTURE_TYPE
        print(f"\n📋 结构类型: {STRUCTURE_TYPE}")
        print(f"   剪力墙: {'✅' if ENABLE_SHEAR_WALLS else '❌'}")
        print(f"   框架柱: {'✅' if ENABLE_FRAME_COLUMNS else '❌'}")
        print(f"   框架梁: {'✅' if ENABLE_FRAME_BEAMS else '❌'}")
    except ImportError:
        print("⚠️ 无法获取结构类型信息")


def print_material_summary():
    """
    打印材料配置摘要
    """
    try:
        print(f"\n🧱 材料配置摘要:")
        print(f"   混凝土: {CONCRETE_MATERIAL_NAME}")
        print(f"   强度: C{CONCRETE_PROPERTIES.get('FC', 0):.0f}")
        print(f"   弹性模量: {CONCRETE_PROPERTIES.get('E_MODULUS', 0) / 1000000:.0f} GPa")
        print(f"   容重: {CONCRETE_PROPERTIES.get('UNIT_WEIGHT', 0)} kN/m³")

        if STEEL_AVAILABLE:
            print(f"   钢材: {STEEL_MATERIAL_NAME} (可用)")
        else:
            print(f"   钢材: 未配置")

    except Exception as e:
        print(f"⚠️ 材料摘要打印失败: {e}")


def get_section_count_estimate():
    """
    估算截面数量

    Returns:
        dict: 截面数量估算
    """
    section_count = {}

    if ENABLE_FRAME_COLUMNS:
        section_count['columns'] = 1  # 1种柱截面
    if ENABLE_FRAME_BEAMS:
        section_count['beams'] = 2  # 主梁+次梁
    if ENABLE_SHEAR_WALLS:
        section_count['walls'] = 2  # 墙+连梁

    section_count['slabs'] = 1  # 1种楼板
    section_count['total'] = sum(section_count.values())

    return section_count