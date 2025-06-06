# -*- coding: utf-8 -*-
"""
构件修正系数设置模块
用于设置楼板膜单元修正系数等
"""

from utils import check_ret, arr, get_etabs_modules
from config import MEMBRANE_MODIFIERS


def apply_slab_membrane_modifiers(sap_model):
    """
    为楼板设置膜单元修正系数，将面外刚度设为0

    工程意义：
    - 膜单元只传递面内力（Nx, Ny, Nxy）
    - 面外刚度（弯曲、扭转）设为0，不传递弯矩
    - 更符合实际工程中楼板的受力特点

    Parameters:
        sap_model: ETABS SapModel对象
    """
    ETABSv1, System, COMException = get_etabs_modules()

    if not sap_model:
        print("❌ 错误: SapModel 未初始化，无法设置楼板膜单元修正")
        return

    area_obj = sap_model.AreaObj

    # 确保模型未锁定
    try:
        sap_model.SetModelIsLocked(False)
    except:
        pass

    # 获取所有楼板名称
    num_val = System.Int32(0)
    names_val = System.Array.CreateInstance(System.String, 0)
    ret_tuple = area_obj.GetNameList(num_val, names_val)
    check_ret(ret_tuple[0], "AreaObj.GetNameList")

    all_names = list(ret_tuple[2]) if ret_tuple[1] > 0 and ret_tuple[2] is not None else []
    slab_names = [n for n in all_names if n.startswith("SLAB_")]

    if not slab_names:
        print("💡 提示: 模型中未找到楼板对象")
        return

    print(f"\n--- 楼板膜单元修正设置 ---")
    print(f"找到 {len(slab_names)} 个楼板网格单元")
    print(f"设置面外刚度为0，保持面内刚度不变")

    # 准备修正系数数组
    modifiers_membrane = arr(MEMBRANE_MODIFIERS)

    successful_count = 0
    failed_count = 0
    failed_names = []

    print(f"正在应用膜单元修正系数...")

    for slab_name in slab_names:
        try:
            ret_tuple = area_obj.SetModifiers(slab_name, modifiers_membrane)
            ret_code = ret_tuple[0] if isinstance(ret_tuple, tuple) else ret_tuple

            if ret_code in (0, 1):
                successful_count += 1
            else:
                failed_count += 1
                failed_names.append(slab_name)
                print(f"  ⚠️ 警告: 楼板 '{slab_name}' 设置失败，返回码: {ret_code}")

        except Exception as e:
            failed_count += 1
            failed_names.append(slab_name)
            print(f"  ❌ 错误: 楼板 '{slab_name}' 设置异常: {e}")

    # 强制刷新模型视图
    try:
        sap_model.View.RefreshView(0, False)
        print("  模型视图已刷新")
    except Exception as e:
        print(f"  刷新视图失败: {e}")

    # 输出结果统计
    print(f"\n楼板膜单元修正完成:")
    print(f"  ✅ 成功处理: {successful_count} 个楼板网格单元")
    print(f"  ❌ 处理失败: {failed_count} 个楼板网格单元")
    print(f"  📊 面内刚度: f11 = f22 = f12 = 1.0 (保持)")
    print(f"  📊 面外刚度: f13 = f23 = f33 = 0.0 (清零)")
    print(f"  🔧 工程意义: 楼板仅传递面内力，不传递弯矩")

    if failed_names:
        print(f"  失败的楼板 (前5个): {failed_names[:5]}")

    print("--- 楼板膜单元修正完毕 ---")

    # 验证建议
    if successful_count > 0:
        print(f"\n✅ 验证建议:")
        print(f"1. 在ETABS中选择任一楼板对象")
        print(f"2. 查看 '对象数据' > '属性修正' 面板")
        print(f"3. 确认面外刚度修正 F13、F23、F33 = 0.0")
        print(f"4. 确认面内刚度修正 F11、F22、F12 = 1.0")
        print(f"5. 这样设置使楼板表现为纯膜单元")


def apply_all_modifiers(sap_model):
    """
    应用所有构件修正系数

    Parameters:
        sap_model: ETABS SapModel对象
    """
    print("\n🔧 开始应用构件修正系数...")

    apply_slab_membrane_modifiers(sap_model)

    print("✅ 所有构件修正系数应用完成")