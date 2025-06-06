# -*- coding: utf-8 -*-
"""
质量源定义模块
"""

from utils import check_ret, arr, get_etabs_modules


def define_mass_source_simple(sap_model):
    """
    简化版质量源定义 - 跳过偶然偏心设置

    Parameters:
        sap_model: ETABS SapModel对象
    """
    ETABSv1, System, COMException = get_etabs_modules()

    if not sap_model:
        print("❌ 错误: SapModel 未初始化, 无法定义质量源")
        return

    print("\n⚖️ 定义质量源（简化版，跳过偶然偏心）...")

    # 质量源参数设置
    load_pattern_names = ["DEAD", "LIVE"]
    scale_factors = [1.0, 0.5]

    # 将Python列表转换为.NET数组
    load_pattern_names_api = arr(load_pattern_names, System.String)
    scale_factors_api = arr(scale_factors, System.Double)

    print(f"  荷载模式: {load_pattern_names}")
    print(f"  系数: {scale_factors}")

    try:
        pm = sap_model.PropMaterial

        # 使用PropMaterial.SetMassSource_1设置基本质量源
        ret = pm.SetMassSource_1(
            False,  # includeElementsMass: 不包含元素自重
            False,  # includeAdditionalMass: 包含附加质量
            True,  # includeLoads: 包含指定荷载
            len(load_pattern_names),  # 荷载模式数量
            load_pattern_names_api,  # 荷载模式名称数组
            scale_factors_api  # 荷载系数数组
        )

        check_ret(ret, f"PropMaterial.SetMassSource_1", (0, 1))
        print("✅ 质量源设置成功")

        # 输出最终状态
        print(f"\n--- 质量源定义完成 ---")
        print(f"DEAD荷载质量系数: 1.0, LIVE荷载质量系数: 0.5")
        print(f"偶然偏心: 未设置（按用户要求跳过）")
        print("--- 质量源定义完毕 ---")

    except Exception as e:
        print(f"❌ 质量源设置失败: {e}")
        print("💡 建议: 请手动在ETABS界面中设置质量源")
        print("路径: Define > Mass Source")
        print(f"      荷载模式: DEAD(1.0), LIVE(0.5)")
        return


def define_diaphragms(sap_model):
    """
    定义楼面约束
    - RIGID : 刚性
    - SRD   : 半刚性

    Parameters:
        sap_model: ETABS SapModel对象
    """
    ETABSv1, System, COMException = get_etabs_modules()

    if not sap_model:
        print("❌ 错误: SapModel 未初始化")
        return

    diaphragm_api = sap_model.Diaphragm

    # 读取已存在的楼面名称
    name_rigid = "RIGID"
    name_semi = "SRD"

    num_val = System.Int32(0)
    names_val = System.Array[System.String](0)

    ret_tuple = diaphragm_api.GetNameList(num_val, names_val)
    check_ret(ret_tuple[0], "Diaphragm.GetNameList")

    existing = list(ret_tuple[2]) if ret_tuple[1] > 0 and ret_tuple[2] is not None else []

    # 刚性楼面
    if name_rigid not in existing:
        check_ret(
            diaphragm_api.SetDiaphragm(name_rigid, False),  # isSemiRigid = False
            f"SetDiaphragm({name_rigid})"
        )

    # 半刚性楼面
    if name_semi not in existing:
        check_ret(
            diaphragm_api.SetDiaphragm(name_semi, True),  # isSemiRigid = True
            f"SetDiaphragm({name_semi})"
        )

    print("✅ 楼面约束定义完毕：RIGID(刚性)、SRD(半刚性)")


def define_all_mass_sources(sap_model):
    """
    定义所有质量源相关设置

    Parameters:
        sap_model: ETABS SapModel对象
    """
    print("\n🏗️ 开始定义质量源和楼面约束...")

    define_diaphragms(sap_model)
    define_mass_source_simple(sap_model)

    print("✅ 质量源和楼面约束定义完成")