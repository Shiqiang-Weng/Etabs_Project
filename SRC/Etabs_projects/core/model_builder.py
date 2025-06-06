# -*- coding: utf-8 -*-
"""
ETABS 模型构建器
负责协调整个模型的创建过程
"""

import os
import time
from typing import Optional, List, Dict, Any

from config import MODEL_PATH, SCRIPT_DIRECTORY
from core.api_connector import ETABSConnector
from core.exceptions import ETABSModelError
from utils import get_etabs_modules, check_ret


class ETABSModelBuilder:
    """ETABS模型构建器类"""

    def __init__(self):
        self.connector = ETABSConnector()
        self.sap_model: Optional[Any] = None
        self._ETABSv1, self._System, self._COMException = get_etabs_modules()

        # 存储创建的构件名称
        self.wall_names: List[str] = []
        self.coupling_beam_names: List[str] = []
        self.slab_names: List[str] = []
        self.story_heights: Dict[int, float] = {}

    def build_model(self) -> bool:
        """
        构建完整的ETABS模型

        Returns:
            bool: 构建成功返回True
        """
        try:
            # 1. 连接ETABS
            if not self.connector.connect():
                raise ETABSModelError("无法连接到ETABS")

            # 2. 初始化模型
            if not self.connector.initialize_model():
                raise ETABSModelError("无法初始化ETABS模型")

            self.sap_model = self.connector.get_sap_model()
            if not self.sap_model:
                raise ETABSModelError("无法获取SapModel对象")

            print("✅ ETABS模型构建器初始化完成")
            return True

        except Exception as e:
            print(f"❌ 模型构建失败: {e}")
            return False

    def add_materials_and_sections(self, materials_module) -> bool:
        """
        添加材料和截面定义

        Parameters:
            materials_module: 材料模块

        Returns:
            bool: 添加成功返回True
        """
        try:
            if not self.sap_model:
                raise ETABSModelError("SapModel未初始化")

            materials_module.define_materials(self.sap_model)
            print("✅ 材料和截面定义完成")
            return True

        except Exception as e:
            print(f"❌ 材料和截面定义失败: {e}")
            return False

    def add_geometry(self, geometry_module) -> bool:
        """
        添加几何结构

        Parameters:
            geometry_module: 几何模块

        Returns:
            bool: 添加成功返回True
        """
        try:
            if not self.sap_model:
                raise ETABSModelError("SapModel未初始化")

            wall_names, cb_names, story_heights = geometry_module.create_structural_geometry(self.sap_model)

            self.wall_names = wall_names
            self.coupling_beam_names = cb_names
            self.story_heights = story_heights

            print("✅ 结构几何创建完成")
            print(f"   - 剪力墙单元: {len(wall_names)} 个")
            print(f"   - 连梁单元: {len(cb_names)} 个")
            print(f"   - 楼层数: {len(story_heights)} 层")

            return True

        except Exception as e:
            print(f"❌ 几何结构创建失败: {e}")
            return False

    def add_loads(self, loads_module) -> bool:
        """
        添加荷载定义

        Parameters:
            loads_module: 荷载模块

        Returns:
            bool: 添加成功返回True
        """
        try:
            if not self.sap_model:
                raise ETABSModelError("SapModel未初始化")

            loads_module.define_all_loads(
                self.sap_model,
                self.wall_names,
                self.coupling_beam_names
            )

            print("✅ 荷载定义完成")
            return True

        except Exception as e:
            print(f"❌ 荷载定义失败: {e}")
            return False

    def run_analysis(self, analysis_module) -> bool:
        """
        运行结构分析

        Parameters:
            analysis_module: 分析模块

        Returns:
            bool: 分析成功返回True
        """
        try:
            if not self.sap_model:
                raise ETABSModelError("SapModel未初始化")

            # 保存模型
            self.save_model()

            # 运行分析
            analysis_module.run_analysis(self.sap_model, MODEL_PATH)

            print("✅ 结构分析完成")
            return True

        except Exception as e:
            print(f"❌ 结构分析失败: {e}")
            return False

    def extract_results(self, results_module) -> bool:
        """
        提取分析结果

        Parameters:
            results_module: 结果模块

        Returns:
            bool: 提取成功返回True
        """
        try:
            if not self.sap_model:
                raise ETABSModelError("SapModel未初始化")

            results_module.extract_all_results(self.sap_model)

            print("✅ 结果提取完成")
            return True

        except Exception as e:
            print(f"❌ 结果提取失败: {e}")
            return False

    def save_model(self) -> bool:
        """
        保存模型文件

        Returns:
            bool: 保存成功返回True
        """
        try:
            if not self.sap_model:
                raise ETABSModelError("SapModel未初始化")

            # 确保输出目录存在
            os.makedirs(SCRIPT_DIRECTORY, exist_ok=True)

            # 刷新视图
            check_ret(
                self._ETABSv1.cView(self.sap_model.View).RefreshView(0, False),
                "RefreshView",
                ok_codes=(0, 1)
            )

            # 保存模型
            ret_save = self._ETABSv1.cFile(self.sap_model.File).Save(MODEL_PATH)
            if ret_save != 0:
                raise ETABSModelError(f"保存模型失败: 返回码 {ret_save}")

            print(f"✅ 模型已保存到: {MODEL_PATH}")
            return True

        except Exception as e:
            print(f"❌ 模型保存失败: {e}")
            return False

    def close(self) -> None:
        """关闭模型构建器"""
        if self.connector:
            self.connector.close()
        print("🔒 模型构建器已关闭")

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            dict: 模型信息字典
        """
        return {
            'wall_count': len(self.wall_names),
            'coupling_beam_count': len(self.coupling_beam_names),
            'slab_count': len(self.slab_names),
            'story_count': len(self.story_heights),
            'story_heights': self.story_heights,
            'model_path': MODEL_PATH
        }