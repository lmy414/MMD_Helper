bl_info = {
    "name": "MMD Helper",
    "author": "Mirror",
    "version": (0, 1),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > MMD Tools",
    "description": "MMD模型优化工具集，包含物理层级清理和材质合并功能",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

# 导入各功能模块
from . import remove_physics
from . import merge_materials
from . import panel

# 全局注册列表
classes = []


def register():
    # 注册所有模块
    remove_physics.register_remove_physics()
    merge_materials.register_merge_materials()
    panel.register_panel()

    # 添加到全局注册列表
    global classes
    classes.extend([
        remove_physics.OBJECT_OT_remove_joints_rigidbodies,
        merge_materials.MATERIAL_OT_merge_by_diffuse,
        panel.MMD_TOOLS_PT_Panel
    ])


def unregister():
    # 注销所有模块
    remove_physics.unregister_remove_physics()
    merge_materials.unregister_merge_materials()
    panel.unregister_panel()

    # 从全局注册列表注销
    global classes
    for cls in classes:
        bpy.utils.unregister_class(cls)
    classes.clear()


# 直接运行时的注册
if __name__ == "__main__":
    register()
