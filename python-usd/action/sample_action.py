# -*- coding: utf-8 -*-
# Jcen
import json
import time

from behavior_tree.core import (
    Inverter, Repeater, Succeeder, UntilFail, Action, Condition, Blackboard, Status
)
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'  # 只保留级别和消息，去掉日志器名称
)

class CheckProject(Condition):
    """检查当前项目配置的流程是否为目标流程"""

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.get('name'), blackboard=kwargs.get('blackboard'))
        for key, value in kwargs.items():
            setattr(self, key, value)

    def check(self, blackboard: Blackboard) -> bool:
        project_flows = blackboard.get("isProject", "")
        return project_flows == getattr(self, 'isProject', None) if getattr(self, 'isProject', None) else True


class CheckNeedExportMaterial(Condition):
    """检查是否需要导出材质"""

    def check(self, blackboard: Blackboard) -> bool:
        # 从黑板获取材质导出配置，默认需要导出
        return blackboard.get("export_material", True)


class GetData(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        logging.info('更新数据中.....')
        time.sleep(2)
        return Status.SUCCESS  # 语义正确：数据更新成功


class ClearFile(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        logging.info('清理文件中.....')
        time.sleep(2)
        return Status.SUCCESS  # 语义正确：数据更新成功


class SaveFile(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        logging.info('保存文件中.....')
        time.sleep(2)
        return Status.SUCCESS


class MayaAbcAllExport(Action):
    """Maya ABC全部输出（包含材质）"""

    def execute(self, blackboard: Blackboard) -> Status:
        current_project = blackboard.get("project")
        logging.info(f"项目 {current_project} 执行 输出材质")
        return Status.SUCCESS


class MayaAbcNoMaterialExport(Action):
    """Maya ABC不输出材质"""

    def execute(self, blackboard: Blackboard) -> Status:
        current_project = blackboard.get("project")
        logging.info(f"项目 {current_project} 执行 不输出材质")

        return Status.SUCCESS


class MayaUsdPipe(Action):
    """执行USD流程发布资产"""

    def execute(self, blackboard: Blackboard) -> Status:
        current_project = blackboard.get("project")
        logging.info(f"项目 {current_project} 执行 maya usd 流程发布资产")
        return Status.SUCCESS


class HouAbcPipe(Action):
    """执行ABC流程发布资产"""

    def execute(self, blackboard: Blackboard) -> Status:
        current_project = blackboard.get("project")
        logging.info(f"项目 {current_project} 执行 hou abc 流程发布资产")
        return Status.SUCCESS


class HouUsdPipe(Action):
    """执行USD流程发布资产"""

    def execute(self, blackboard: Blackboard) -> Status:
        current_project = blackboard.get("project")
        logging.info(f"项目 {current_project} 执行 hou usd 流程发布资产")
        return Status.SUCCESS


class ModelCheck(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        logging.info('执行动作： 模型检查')
        time.sleep(0.5)
        return Status.SUCCESS

class ModelExport(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        logging.info('执行动作： 模型导出')
        time.sleep(0.5)
        return Status.SUCCESS

class ShaderExport(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        logging.info('执行动作： 材质导出')
        time.sleep(0.5)
        return Status.SUCCESS

class OtherAction(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        logging.info('执行动作： 其他自定义动作')
        time.sleep(0.5)
        return Status.SUCCESS

class PublishServer(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        logging.info('执行动作： 发布资产到服务器')
        time.sleep(0.5)
        return Status.SUCCESS

class GetBlackboardData(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        logging.info('执行动作： 获取黑板数据')

        # 方式1：通过节点关联的tree获取黑板（已实现）
        logging.info("通过self.tree获取的黑板本地数据" + str(self.tree.blackboard.local_data))

        time.sleep(0.5)
        return Status.SUCCESS  # 注意：原代码缺少返回值，需补充


class CreateBouncingBallAnime(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        import maya.cmds as cmds
        import math
        # 设置帧率为24fps
        cmds.currentUnit(time='film')

        # 清除场景中可能存在的同名物体
        if cmds.objExists("ball"):
            cmds.delete("ball")

        # 创建小球
        ball = cmds.polySphere(r=1, name="ball")[0]

        # 创建参考平面
        if not cmds.objExists("reference_plane"):
            plane = cmds.polyPlane(w=20, h=20, name="reference_plane")[0]
            cmds.setAttr(plane + ".translateY", 0)  # 放置在0位置作为参考

        # 动画参数
        fps = 24  # 帧率
        duration_seconds = 5  # 动画持续5秒
        total_frames = duration_seconds * fps  # 总帧数
        float_range = 10  # 浮动范围（正负10个单位）
        speed = 2  # 浮动速度（周期数/秒）

        # 计算每帧的位置并设置关键帧
        for frame in range(total_frames + 1):
            # 计算时间（秒）
            time = frame / fps

            # 使用正弦函数计算Y轴位置，实现平滑浮动
            # 正弦函数范围是[-1, 1]，乘以浮动范围得到[-10, 10]
            y_position = math.sin(time * speed * math.pi) * float_range

            # 设置位置并添加关键帧
            cmds.setAttr(ball + ".translateY", y_position)
            cmds.setKeyframe(ball, attribute='translateY', time=frame)

        # 优化动画曲线使运动更平滑
        cmds.select(ball)
        cmds.filterCurve()

        logging.info(f"小球上下浮动动画创建完成！浮动范围: ±{float_range}单位，持续时间: {duration_seconds}秒")

        return Status.SUCCESS


class EnergyPulseAction(Action):
    """能量脉冲动画 - 实时缩放并变色"""

    def execute(self, blackboard: Blackboard) -> Status:
        import maya.cmds as cmds
        import math
        # 获取或创建目标物体
        target = blackboard.get("target")
        if not target or not cmds.objExists(target):
            target = cmds.polySphere(name="energy_orb")[0]
            blackboard.set("target", target)
            cmds.setAttr(f"{target}.overrideEnabled", 1)  # 启用颜色覆盖

        # 动画参数
        duration = 2.0  # 动画持续2秒
        start_time = time.time()
        initial_scale = cmds.getAttr(f"{target}.scale")[0][0]
        job_id = None  # 用于保存脚本任务ID

        # 实时更新函数
        def update():
            elapsed = time.time() - start_time
            if elapsed >= duration:
                # 动画结束，清理任务
                cmds.scriptJob(kill=job_id, force=True)
                # 恢复初始状态
                cmds.setAttr(f"{target}.scale", initial_scale, initial_scale, initial_scale)
                cmds.setAttr(f"{target}.overrideColorR", 1)
                cmds.setAttr(f"{target}.overrideColorG", 1)
                cmds.setAttr(f"{target}.overrideColorB", 1)
                return False  # 停止任务

            # 计算进度（0-1）
            progress = elapsed / duration

            # 脉冲缩放（正弦函数实现呼吸效果）
            scale_factor = 1 + math.sin(progress * math.pi * 6) * 0.5
            cmds.setAttr(f"{target}.scale",
                         initial_scale * scale_factor,
                         initial_scale * scale_factor,
                         initial_scale * scale_factor)

            # 颜色变化（从蓝到红）
            cmds.setAttr(f"{target}.overrideColorR", progress)
            cmds.setAttr(f"{target}.overrideColorB", 1 - progress)

            return True  # 继续执行

        # 创建每帧更新的脚本任务
        job_id = cmds.scriptJob(everyFrame=update, protected=True)
        blackboard.set(f"{self.__class__.__name__}_job_id", job_id)

        logging.info(f"启动能量脉冲动画: {target}")
        return Status.SUCCESS  # 表示动画正在运行


class TrajectoryAction(Action):
    """轨迹运动动画 - 实时沿路径移动"""

    def execute(self, blackboard: Blackboard) -> Status:
        import maya.cmds as cmds
        import math
        # 获取或创建目标物体
        target = blackboard.get("target")
        if not target or not cmds.objExists(target):
            target = cmds.polyCone(name="projectile")[0]
            blackboard.set("target", target)

        # 记录初始位置
        start_pos = cmds.xform(target, q=True, translation=True, worldSpace=True)
        start_time = time.time()
        duration = 3.0  # 持续3秒
        job_id = None

        # 实时更新函数
        def update():
            elapsed = time.time() - start_time
            if elapsed >= duration:
                cmds.scriptJob(kill=job_id, force=True)
                return False

            progress = elapsed / duration
            # 计算8字轨迹（双纽线数学公式）
            theta = progress * math.pi * 4
            radius = 10
            x = radius * math.sin(theta)
            z = radius * math.sin(theta) * math.cos(theta)
            y = start_pos[1] + math.sin(theta) * 3  # 上下浮动

            # 更新位置
            cmds.xform(target, translation=[
                start_pos[0] + x,
                start_pos[1] + y,
                start_pos[2] + z
            ], worldSpace=True)

            # 面向运动方向
            cmds.xform(target, rotation=[0, theta * 180 / math.pi, 0], worldSpace=True)

            return True

        # 创建实时更新任务
        job_id = cmds.scriptJob(everyFrame=update, protected=True)
        blackboard.set(f"{self.__class__.__name__}_job_id", job_id)

        logging.info(f"启动轨迹运动动画: {target}")
        return Status.SUCCESS


class QuantumJitterAction(Action):
    """量子抖动动画 - 实时随机位置抖动"""

    def execute(self, blackboard: Blackboard) -> Status:
        import maya.cmds as cmds
        import math
        # 获取或创建目标物体
        target = blackboard.get("target")
        if not target or not cmds.objExists(target):
            target = cmds.polyCube(name="quantum_cube")[0]
            blackboard.set("target", target)
            cmds.setAttr(f"{target}.overrideEnabled", 1)

        # 动画参数
        start_pos = cmds.xform(target, q=True, translation=True, worldSpace=True)
        start_time = time.time()
        duration = 2.5  # 持续2.5秒
        jitter_range = 3.0  # 抖动范围
        job_id = None

        # 实时更新函数
        def update():
            elapsed = time.time() - start_time
            if elapsed >= duration:
                cmds.scriptJob(kill=job_id, force=True)
                # 回到初始位置
                cmds.xform(target, translation=start_pos, worldSpace=True)
                cmds.setAttr(f"{target}.overrideOpacity", 1.0)
                return False

            progress = elapsed / duration
            # 随时间减小抖动范围
            current_range = jitter_range * (1 - progress)

            # 随机抖动位置
            x = start_pos[0] + (math.sin(elapsed * 10) * current_range * 0.5)
            y = start_pos[1] + (math.cos(elapsed * 8) * current_range * 0.5)
            z = start_pos[2] + (math.sin(elapsed * 12) * current_range * 0.5)

            cmds.xform(target, translation=[x, y, z], worldSpace=True)

            # 闪烁效果
            opacity = 0.7 + math.sin(elapsed * 20) * 0.3
            cmds.setAttr(f"{target}.overrideOpacity", opacity)

            return True

        # 创建实时更新任务
        job_id = cmds.scriptJob(everyFrame=update, protected=True)
        blackboard.set(f"{self.__class__.__name__}_job_id", job_id)

        logging.info(f"启动量子抖动动画: {target}")
        return Status.SUCCESS
