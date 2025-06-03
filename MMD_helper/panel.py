import bpy


class MMD_TOOLS_PT_Panel(bpy.types.Panel):
    """MMD工具集"""
    bl_label = "MMD工具集"
    bl_idname = "MMD_TOOLS_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MMD工具'  # 右侧面板名称
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout

        # 物理层级清理
        box = layout.box()
        box.label(text="物理层级清理", icon='PHYSICS')
        box.operator("object.remove_joints_rigidbodies", text="移除物理层级")

        # 材质工具
        layout.separator()
        box = layout.box()
        box.label(text="材质优化工具", icon='MATERIAL')

        # 材质合并功能
        box.operator("material.merge_by_diffuse", text="合并相同贴图的材质")

        # 材质统计信息
        row = box.row()
        row.label(text=f"场景材质总数: {len(bpy.data.materials)}")

        # 显示选中对象的材质信息
        if context.selected_objects:
            selected_materials = set()
            material_users = 0

            for obj in context.selected_objects:
                if hasattr(obj, 'material_slots'):
                    material_users += len(obj.material_slots)
                    for slot in obj.material_slots:
                        if slot.material:
                            selected_materials.add(slot.material)

            row = box.row()
            row.label(text=f"选中对象材质: {len(selected_materials)}")

            row = box.row()
            row.label(text=f"材质槽总数: {material_users}")


# 注册函数
def register_panel():
    bpy.utils.register_class(MMD_TOOLS_PT_Panel)


# 注销函数
def unregister_panel():
    bpy.utils.unregister_class(MMD_TOOLS_PT_Panel)
