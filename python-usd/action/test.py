# -*- coding: utf-8 -*-
# Jcen
from behavior_tree.core import (
    Action, Blackboard, Status, Inverter, Condition, Repeater, UntilFail
)
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

import maya.cmds as cmds
import os
from pxr import Usd, UsdGeom, Gf, Sdf


def extract_geometry_info(mesh):
    """提取单个网格的几何信息"""
    # 确保是多边形网格
    if not cmds.objectType(mesh, isType='mesh'):
        cmds.warning(f"{mesh}不是多边形网格")
        return None

    # 提取顶点位置
    points = cmds.xform(f"{mesh}.vtx[*]", query=True, translation=True, worldSpace=True)
    points = [Gf.Vec3f(points[i], points[i + 1], points[i + 2]) for i in range(0, len(points), 3)]

    # 提取面信息
    face_count = cmds.polyEvaluate(mesh, face=True)
    face_vertex_counts = []
    face_vertex_indices = []

    for face in range(face_count):
        # 获取每个面的顶点索引
        vtx_indices = cmds.polyInfo(f"{mesh}.f[{face}]", faceToVertex=True)[0]
        vtx_indices = list(map(int, vtx_indices.split()[-1:][0].split(',')))
        face_vertex_counts.append(len(vtx_indices))
        face_vertex_indices.extend(vtx_indices)

    # 提取法线
    normals = []
    # 获取顶点数量来确定法线数量
    vertex_count = cmds.polyEvaluate(mesh, vertex=True)

    try:
        # 尝试获取第一个顶点的法线来判断是否存在法线数据
        first_normal = cmds.polyNormalPerVertex(f"{mesh}.vtx[0]", query=True, xyz=True)
        if first_normal:
            # 逐顶点提取法线
            for i in range(vertex_count):
                normal = cmds.polyNormalPerVertex(f"{mesh}.vtx[{i}]", query=True, xyz=True)
                if normal:  # 确保成功获取法线
                    normals.append(Gf.Vec3f(normal[0], normal[1], normal[2]))
    except:
        # 如果获取法线失败，视为没有法线数据
        cmds.warning(f"{mesh}没有可用的顶点法线数据")

    # 提取UV
    uvs = []
    try:
        # 检查是否存在UV集
        uv_sets = cmds.polyUVSet(mesh, query=True, allUVSets=True)
        if uv_sets and len(uv_sets) > 0:
            uv_count = cmds.polyEvaluate(mesh, uv=True)
            for i in range(uv_count):
                uv = cmds.polyEditUV(f"{mesh}.map[{i}]", query=True, u=True, v=True)
                uvs.append(Gf.Vec2f(uv[0], uv[1]))
    except:
        cmds.warning(f"{mesh}没有可用的UV数据")

    return {
        'points': points,
        'face_vertex_counts': face_vertex_counts,
        'face_vertex_indices': face_vertex_indices,
        'normals': normals,
        'uvs': uvs,
        'name': mesh
    }


def write_geometry_to_usd(geo_info, file_path):
    """将几何信息写入USD文件"""
    # 创建USD舞台
    stage = Usd.Stage.CreateNew(file_path)

    # 创建一个Xform作为根
    root_xform = UsdGeom.Xform.Define(stage, "/Root")

    # 创建网格
    mesh = UsdGeom.Mesh.Define(stage, f"/Root/{geo_info['name']}")

    # 设置点
    mesh.CreatePointsAttr(geo_info['points'])

    # 设置面拓扑
    mesh.CreateFaceVertexCountsAttr(geo_info['face_vertex_counts'])
    mesh.CreateFaceVertexIndicesAttr(geo_info['face_vertex_indices'])

    # 设置法线 - 修复部分
    if geo_info['normals']:
        # 创建法线属性
        normals_attr = mesh.CreateNormalsAttr(geo_info['normals'])

        # 替代方法设置法线插值：使用SetNormalsInterpolation
        # 检查是否有此方法，有则使用
        if hasattr(mesh, 'SetNormalsInterpolation'):
            mesh.SetNormalsInterpolation(UsdGeom.Tokens.vertex)
        else:
            # 更通用的方法：直接设置属性
            interpolation_attr = mesh.GetNormalsInterpolationAttr()
            if not interpolation_attr.IsDefined():
                interpolation_attr = mesh.CreateNormalsInterpolationAttr()
            interpolation_attr.Set(UsdGeom.Tokens.vertex)

    # 设置UV
    if geo_info['uvs']:
        # 创建UV集
        uv_set = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar(
            "st",
            Sdf.ValueTypeNames.Float2Array,
            UsdGeom.Tokens.varying
        )
        uv_set.Set(geo_info['uvs'])

        # 创建UV绑定
        mesh.CreatePrimvar("uvSet", Sdf.ValueTypeNames.Token).Set("st")

    # 保存USD文件
    stage.Save()
    print(f"成功写入USD文件: {file_path}")
    return True


def export_geo_details_to_usd(file_path=None):
    """主函数：导出选中模型的详细几何信息到USD"""
    # 检查选择
    selected = cmds.ls(selection=True, long=True)
    if not selected:
        cmds.warning("请先选中模型")
        return False

    # 获取文件路径
    if not file_path:
        file_path = [r'C:\Users\17203\Desktop\github\python-usd\sample\sample.usda']
        if not file_path:
            return False
        file_path = file_path[0]

    # 确保目录存在
    dir_name = os.path.dirname(file_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    try:
        # 处理每个选中的物体
        for obj in selected:
            # 获取形状节点（如果是变换节点）
            if cmds.objectType(obj, isType='transform'):
                shapes = cmds.listRelatives(obj, shapes=True, type='mesh')
                if shapes:
                    for shape in shapes:
                        geo_info = extract_geometry_info(shape)
                        if geo_info:
                            write_geometry_to_usd(geo_info, file_path)
            else:
                geo_info = extract_geometry_info(obj)
                if geo_info:
                    write_geometry_to_usd(geo_info, file_path)

        return True

    except Exception as e:
        cmds.warning(f"导出失败: {str(e)}")
        return False


class Test(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        export_geo_details_to_usd()
        return Status.SUCCESS




