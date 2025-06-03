import bpy


class OBJECT_OT_remove_joints_rigidbodies(bpy.types.Operator):
    """移除joints和rigidbodies层级"""
    bl_idname = "object.remove_joints_rigidbodies"
    bl_label = "移除物理层级"
    bl_options = {'REGISTER', 'UNDO'}

    remove_joints: bpy.props.BoolProperty(
        name="移除Joints",
        description="移除所有名为'joints'的层级",
        default=True
    )

    remove_rigidbodies: bpy.props.BoolProperty(
        name="移除Rigidbodies",
        description="移除所有名为'rigidbodies'的层级",
        default=True
    )

    remove_empty_collections: bpy.props.BoolProperty(
        name="清理空集合",
        description="移除所有空的集合",
        default=True
    )

    def execute(self, context):
        # 确保选中了对象
        if not context.selected_objects:
            self.report({'WARNING'}, "请先选中根物体")
            return {'CANCELLED'}

        # 获取根物体
        root_object = context.active_object

        # 统计变量
        joints_removed = 0
        rigidbodies_removed = 0
        collections_cleaned = 0

        # 移除joints层级
        if self.remove_joints:
            # 查找名为'joints'的子物体
            joints_object = next((child for child in root_object.children if child.name.lower() == "joints"), None)

            if joints_object:
                # 移除所有后代物体
                for obj in joints_object.children_recursive:
                    bpy.data.objects.remove(obj, do_unlink=True)
                    joints_removed += 1

                # 移除joints物体本身
                bpy.data.objects.remove(joints_object, do_unlink=True)
                joints_removed += 1

        # 移除rigidbodies层级
        if self.remove_rigidbodies:
            # 查找名为'rigidbodies'的子物体
            rigidbodies_object = next((child for child in root_object.children if child.name.lower() == "rigidbodies"),
                                      None)

            if rigidbodies_object:
                # 移除所有后代物体
                for obj in rigidbodies_object.children_recursive:
                    bpy.data.objects.remove(obj, do_unlink=True)
                    rigidbodies_removed += 1

                # 移除rigidbodies物体本身
                bpy.data.objects.remove(rigidbodies_object, do_unlink=True)
                rigidbodies_removed += 1

        # 清理空集合
        if self.remove_empty_collections:
            # 查找所有空集合
            empty_collections = [coll for coll in bpy.data.collections if not coll.objects]

            for coll in empty_collections:
                # 确保集合名称包含"joints"或"rigidbodies"
                if "joints" in coll.name.lower() or "rigidbodies" in coll.name.lower():
                    bpy.data.collections.remove(coll)
                    collections_cleaned += 1

        # 更新场景
        context.view_layer.update()

        # 显示结果通知
        total_removed = joints_removed + rigidbodies_removed
        result_msg = f"物理层级清理完成! 共移除{total_removed}个物体"
        if collections_cleaned > 0:
            result_msg += f", 清理{collections_cleaned}个空集合"

        self.report({'INFO'}, result_msg)

        # 在3D视图顶部显示通知
        context.area.header_text_set(result_msg)
        bpy.app.timers.register(
            lambda: context.area.header_text_set(None),
            first_interval=5
        )

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "remove_joints")
        layout.prop(self, "remove_rigidbodies")
        layout.separator()
        layout.prop(self, "remove_empty_collections")


# 注册函数
def register_remove_physics():
    bpy.utils.register_class(OBJECT_OT_remove_joints_rigidbodies)

    # 添加到物体右键菜单
    bpy.types.VIEW3D_MT_object_context_menu.append(
        lambda self, context: self.layout.operator(OBJECT_OT_remove_joints_rigidbodies.bl_idname))


# 注销函数
def unregister_remove_physics():
    bpy.utils.unregister_class(OBJECT_OT_remove_joints_rigidbodies)

    # 从菜单中移除
    bpy.types.VIEW3D_MT_object_context_menu.remove(
        lambda self, context: self.layout.operator(OBJECT_OT_remove_joints_rigidbodies.bl_idname))
