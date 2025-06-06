# -*- coding: utf-8 -*-
"""
ETABS API 连接器
负责与ETABS程序的连接和通信
"""

import time
import sys
from typing import Optional, Any

from config import (
    ATTACH_TO_INSTANCE, REMOTE, REMOTE_COMPUTER, SPECIFY_PATH,
    PROGRAM_PATH, NUM_STORIES, TYPICAL_STORY_HEIGHT, BOTTOM_STORY_HEIGHT,
    NUM_GRID_LINES_X, NUM_GRID_LINES_Y, SPACING_X, SPACING_Y
)
from utils import get_etabs_modules, check_ret


class ETABSConnector:
    """ETABS API连接器类"""

    def __init__(self):
        self.my_etabs: Optional[Any] = None
        self.sap_model: Optional[Any] = None
        self._ETABSv1 = None
        self._System = None
        self._COMException = None

        # 获取已加载的模块
        self._ETABSv1, self._System, self._COMException = get_etabs_modules()

        if not all([self._ETABSv1, self._System, self._COMException]):
            raise RuntimeError("ETABS API模块未正确加载，请先调用load_dotnet_etabs_api()")

    def connect(self) -> bool:
        """
        连接到ETABS实例

        Returns:
            bool: 连接成功返回True
        """
        print("\nETABS 连接与模型初始化...")

        helper = self._ETABSv1.cHelper(self._ETABSv1.Helper())

        if ATTACH_TO_INSTANCE:
            return self._attach_to_existing_instance(helper)
        else:
            return self._create_new_instance(helper)

    def _attach_to_existing_instance(self, helper) -> bool:
        """附加到已存在的ETABS实例"""
        print("正在尝试附加到已运行的ETABS 实例...")

        try:
            getter = helper.GetObjectHost if REMOTE else helper.GetObject
            self.my_etabs = getter(REMOTE_COMPUTER if REMOTE else "CSI.ETABS.API.ETABSObject")
            print("已成功附加到 ETABS 实例。")
            return True

        except self._COMException as e:
            error_msg = f"致命错误: 附加到 ETABS 实例失败。COMException: {e}\n请确保 ETABS 正在运行。"
            print(error_msg)
            return False

        except Exception as e:
            error_msg = f"致命错误: 附加到 ETABS 实例时发生未知错误: {e}"
            print(error_msg)
            return False

    def _create_new_instance(self, helper) -> bool:
        """创建新的ETABS实例"""
        print("正在启动新的 ETABS 实例...")

        try:
            creator = helper.CreateObjectHost if REMOTE and SPECIFY_PATH else \
                helper.CreateObject if SPECIFY_PATH else \
                    helper.CreateObjectProgIDHost if REMOTE else \
                        helper.CreateObjectProgID

            path_or_progid = PROGRAM_PATH if SPECIFY_PATH else "CSI.ETABS.API.ETABSObject"
            self.my_etabs = creator(REMOTE_COMPUTER if REMOTE else path_or_progid)

        except self._COMException as e:
            error_msg = f"致命错误: 启动 ETABS实例失败。COMException: {e}\n请检查 PROGRAM_PATH 或 ProgID。"
            print(error_msg)
            return False

        except Exception as e:
            error_msg = f"致命错误: 启动 ETABS 实例时发生未知错误: {e}"
            print(error_msg)
            return False

        # 启动应用程序
        check_ret(self.my_etabs.ApplicationStart(), "my_etabs.ApplicationStart")
        print("ETABS 应用程序已启动。")
        return True

    def initialize_model(self) -> bool:
        """
        初始化模型

        Returns:
            bool: 初始化成功返回True
        """
        if not self.my_etabs:
            print("错误: ETABS实例未连接")
            return False

        print("等待 ETABS 用户界面初始化 (大约5秒)...")
        time.sleep(5)

        self.sap_model = self.my_etabs.SapModel
        if self.sap_model is None:
            print("致命错误: my_etabs.SapModel 返回为 None。")
            return False

        try:
            self.sap_model.SetModelIsLocked(False)
            print("已尝试设置模型为未锁定状态。")
        except Exception as e_lock:
            print(f"警告: 设置模型未锁定状态失败: {e_lock}")

        # 初始化新模型
        check_ret(
            self.sap_model.InitializeNewModel(self._ETABSv1.eUnits.kN_m_C),
            "sap_model.InitializeNewModel"
        )
        print(f"新模型已成功初始化, 单位设置为: kN, m, °C ")

        # 创建网格模型
        file_obj = self._ETABSv1.cFile(self.sap_model.File)
        check_ret(
            file_obj.NewGridOnly(
                NUM_STORIES, TYPICAL_STORY_HEIGHT, BOTTOM_STORY_HEIGHT,
                NUM_GRID_LINES_X, NUM_GRID_LINES_Y, SPACING_X, SPACING_Y
            ),
            "file_obj.NewGridOnly"
        )
        print(f"空白网格模型已创建 ({NUM_STORIES}层, X向轴线: {NUM_GRID_LINES_X}, Y向轴线: {NUM_GRID_LINES_Y})。")

        return True

    def close(self) -> None:
        """关闭ETABS连接"""
        if not ATTACH_TO_INSTANCE and self.my_etabs is not None:
            try:
                self.my_etabs.ApplicationExit(False)
                print("ETABS 应用程序已关闭。")
            except Exception as e:
                print(f"关闭 ETABS 失败: {e}")

    def get_sap_model(self):
        """获取SapModel对象"""
        return self.sap_model

    def get_etabs_instance(self):
        """获取ETABS实例"""
        return self.my_etabs