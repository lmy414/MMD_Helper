import bpy
from collections import defaultdict


class MATERIAL_OT_merge_by_diffuse(bpy.types.Operator):
    """合并使用相同漫反射贴图的材质"""
    bl_idname = "material.merge_by_diffuse"
    bl_label = "合并相同贴图的材质"
    bl_options = {'REGISTER', 'UNDO'}

    # 高级选项
    merge_threshold: bpy.props.IntProperty(
        name="合并阈值",
        description="当相同贴图的材质数量达到此值时才进行合并",
        default=2,
        min=2,
        max=100
    )

    purge_unused: bpy.props.BoolProperty(
        name="清理未使用资源",
        description="合并后自动清理未使用的材质和纹理",
        default=True
    )

    def get_diffuse_texture(self, material):
        """获取材质的漫反射贴图"""
        if not material or not material.use_nodes:
            return None

        for node in material.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                base_color = node.inputs.get('Base Color')
                if base_color and base_color.links:
                    texture_node = base_color.links[0].from_node
                    if texture_node.type == 'TEX_IMAGE' and texture_node.image:
                        return texture_node.image
        return None

    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type in {'MESH', 'CURVE'}]

        if not selected_objects:
            self.report({'WARNING'}, "未选中任何有效对象")
            return {'CANCELLED'}

        texture_to_materials = defaultdict(list)
        processed_materials = set()

        # 收集材质信息
        for obj in selected_objects:
            for slot in obj.material_slots:
                material = slot.material
                if not material or material in processed_materials:
                    continue

                texture = self.get_diffuse_texture(material)
                texture_to_materials[texture].append(material)
                processed_materials.add(material)

        merge_count = 0
        materials_merged = 0

        # 执行合并操作
        for texture, materials in texture_to_materials.items():
            if len(materials) < self.merge_threshold:
                continue

            master_material = materials[0]
            materials_to_merge = materials[1:]

            for obj in selected_objects:
                for slot in obj.material_slots:
                    if slot.material in materials_to_merge:
                        slot.material = master_material
                        merge_count += 1

            materials_merged += len(materials_to_merge)

        # 清理未使用资源
        if self.purge_unused and merge_count > 0:
            bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

        # 显示结果
        result_message = f"合并完成! 减少了 {merge_count} 个材质引用"
        if materials_merged > 0:
            result_message += f", 合并了 {materials_merged} 个材质"

        self.report({'INFO'}, result_message)

        # 在3D视图顶部显示通知
        context.area.header_text_set(f"材质优化: 合并了{materials_merged}个材质")
        bpy.app.timers.register(
            lambda: context.area.header_text_set(None),
            first_interval=5
        )

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "merge_threshold")
        layout.prop(self, "purge_unused")

        # 显示当前场景材质统计
        row = layout.row()
        row.label(text=f"场景材质总数: {len(bpy.data.materials)}")

        # 显示选中对象的材质信息
        if context.selected_objects:
            selected_materials = set()
            for obj in context.selected_objects:
                if hasattr(obj, 'material_slots'):
                    for slot in obj.material_slots:
                        if slot.material:
                            selected_materials.add(slot.material)

            row = layout.row()
            row.label(text=f"选中对象材质数: {len(selected_materials)}")


# 注册函数
def register_merge_materials():
    bpy.utils.register_class(MATERIAL_OT_merge_by_diffuse)

    # 添加到物体右键菜单
    bpy.types.VIEW3D_MT_object_context_menu.append(
        lambda self, context: self.layout.operator(MATERIAL_OT_merge_by_diffuse.bl_idname))


# 注销函数
def unregister_merge_materials():
    bpy.utils.unregister_class(MATERIAL_OT_merge_by_diffuse)

    # 从菜单中移除
    bpy.types.VIEW3D_MT_object_context_menu.remove(
        lambda self, context: self.layout.operator(MATERIAL_OT_merge_by_diffuse.bl_idname))
