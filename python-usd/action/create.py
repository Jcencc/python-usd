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


class SelectModel(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        import maya.cmds as cmds
        selected = cmds.ls(sl=True)
        if not selected:
            cmds.warning("请先选中模型")
            return Status.FAILURE
        blackboard.set('geo_selected', selected)
        return Status.SUCCESS


class GetGeometryInfo(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        if not blackboard.get('geo_selected'):
            return Status.FAILURE
        blackboard.set('GeoList', [])
        import maya.cmds as cmds
        from pxr import Sdf, Gf
        # 确保是多边形网格
        for obj in blackboard.get('geo_selected'):
            print(obj)
            # 获取形状节点（如果是变换节点）
            if cmds.objectType(obj, isType='transform'):
                shapes = cmds.listRelatives(obj, shapes=True, type='mesh')
                if shapes:
                    for mesh in shapes:
                        if not cmds.objectType(mesh, isType='mesh'):
                            cmds.warning(f"{mesh}不是多边形网格")
                            return Status.FAILURE

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
                        blackboard.get('GeoList').append({
                            'points': points,
                            'face_vertex_counts': face_vertex_counts,
                            'face_vertex_indices': face_vertex_indices,
                            'normals': normals,
                            'uvs': uvs,
                            'name': mesh
                        })
            else:
                if not cmds.objectType(obj, isType='mesh'):
                    cmds.warning(f"{obj}不是多边形网格")
                    return Status.FAILURE

                # 提取顶点位置
                points = cmds.xform(f"{obj}.vtx[*]", query=True, translation=True, worldSpace=True)
                points = [Gf.Vec3f(points[i], points[i + 1], points[i + 2]) for i in range(0, len(points), 3)]

                # 提取面信息
                face_count = cmds.polyEvaluate(obj, face=True)
                face_vertex_counts = []
                face_vertex_indices = []

                for face in range(face_count):
                    # 获取每个面的顶点索引
                    vtx_indices = cmds.polyInfo(f"{obj}.f[{face}]", faceToVertex=True)[0]
                    vtx_indices = list(map(int, vtx_indices.split()[-1:][0].split(',')))
                    face_vertex_counts.append(len(vtx_indices))
                    face_vertex_indices.extend(vtx_indices)

                # 提取法线
                normals = []
                # 获取顶点数量来确定法线数量
                vertex_count = cmds.polyEvaluate(obj, vertex=True)

                try:
                    # 尝试获取第一个顶点的法线来判断是否存在法线数据
                    first_normal = cmds.polyNormalPerVertex(f"{obj}.vtx[0]", query=True, xyz=True)
                    if first_normal:
                        # 逐顶点提取法线
                        for i in range(vertex_count):
                            normal = cmds.polyNormalPerVertex(f"{obj}.vtx[{i}]", query=True, xyz=True)
                            if normal:  # 确保成功获取法线
                                normals.append(Gf.Vec3f(normal[0], normal[1], normal[2]))
                except:
                    # 如果获取法线失败，视为没有法线数据
                    cmds.warning(f"{obj}没有可用的顶点法线数据")

                # 提取UV
                uvs = []
                try:
                    # 检查是否存在UV集
                    uv_sets = cmds.polyUVSet(obj, query=True, allUVSets=True)
                    if uv_sets and len(uv_sets) > 0:
                        uv_count = cmds.polyEvaluate(obj, uv=True)
                        for i in range(uv_count):
                            uv = cmds.polyEditUV(f"{obj}.map[{i}]", query=True, u=True, v=True)
                            uvs.append(Gf.Vec2f(uv[0], uv[1]))
                except:
                    cmds.warning(f"{obj}没有可用的UV数据")
                blackboard.get('GeoList').append({
                    'points': points,
                    'face_vertex_counts': face_vertex_counts,
                    'face_vertex_indices': face_vertex_indices,
                    'normals': normals,
                    'uvs': uvs,
                    'name': obj
                })
                # return {
                #     'points': points,
                #     'face_vertex_counts': face_vertex_counts,
                #     'face_vertex_indices': face_vertex_indices,
                #     'normals': normals,
                #     'uvs': uvs,
                #     'name': obj
                # }


class WriteRootPrim(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        if not blackboard.get('GeoList') or not blackboard.get('ROOT'):
            return Status.FAILURE
        from pxr import UsdGeom, Sdf
        for geo in blackboard.get('GeoList'):
            # 创建网格
            root_prim = blackboard.get('ROOT')
            stage = blackboard.get('stage')
            mesh = UsdGeom.Mesh.Define(stage, f"{root_prim.GetPath()}/{geo['name']}")

            # 设置点
            mesh.CreatePointsAttr(geo['points'])

            # 设置面拓扑
            mesh.CreateFaceVertexCountsAttr(geo['face_vertex_counts'])
            mesh.CreateFaceVertexIndicesAttr(geo['face_vertex_indices'])

            # 设置法线 - 修复部分
            if geo['normals']:
                # 创建法线属性
                normals_attr = mesh.CreateNormalsAttr(geo['normals'])

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
            if geo['uvs']:
                # 创建UV集
                uv_set = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar(
                    "st",
                    Sdf.ValueTypeNames.Float2Array,
                    UsdGeom.Tokens.varying
                )
                uv_set.Set(geo['uvs'])

                # 创建UV绑定
                mesh.CreatePrimvar("uvSet", Sdf.ValueTypeNames.Token).Set("st")

        return Status.SUCCESS


class CreateUsd(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        if not blackboard.get('usd_path'):
            return Status.FAILURE
        from pxr import Usd
        stage = Usd.Stage.CreateInMemory()
        blackboard.set('stage', stage)
        return Status.SUCCESS


class SetMateData(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        if not blackboard.get('stage'):
            return Status.FAILURE
        stage = blackboard.get('stage')
        metadata = blackboard.get('set_usd_metadata', {})
        for key, value in metadata.items():
            stage.SetMetadata(key, value)

        return Status.SUCCESS


class SetRootPrim(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        if not blackboard.get('stage'):
            return Status.FAILURE
        stage = blackboard.get('stage')
        root_prim = stage.DefinePrim("/Root", "Xform")
        stage.SetDefaultPrim(root_prim)
        blackboard.set('ROOT', root_prim)
        return Status.SUCCESS


class SaveUsd(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        if not blackboard.get('stage'):
            return Status.FAILURE
        stage = blackboard.get('stage')
        stage.Export(blackboard.get('usd_path'))
        return Status.SUCCESS


class OpenUsd(Action):
    def execute(self, blackboard: Blackboard) -> Status:
        if not blackboard.get('usd_path'):
            return Status.FAILURE
        import os

        os.startfile(blackboard.get('usd_path', ''))

