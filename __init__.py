# SPDX-License-Identifier: GPL-2.0-or-later

bl_info = {
    "name": "Node Presets Extended",
    "description": "Useful and time-saving tools for node group workflow",
    "author": "Campbell Barton, Stephan Kellermayr",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "Node Editors > Add > Template",
    "description": "Add node groups directly to the node editors",
    "warning": "",
    "doc_url": "{BLENDER_MANUAL_URL}/addons/node/node_presets.html",
    "category": "Node",
}

import os
import bpy
from bpy.types import (
    Operator,
    Menu,
    AddonPreferences,
)

from bpy.props import (
    StringProperty,
)


# -----------------------------------------------------------------------------
# Node Adding Operator


def node_center(context):
    from mathutils import Vector
    loc = Vector((0.0, 0.0))
    node_selected = context.selected_nodes
    if node_selected:
        for node in node_selected:
            loc += node.location
        loc /= len(node_selected)
    return loc


def node_template_add(context, filepath, node_group, ungroup, report):
    """ Main function
    """

    space = context.space_data
    node_tree = space.node_tree
    node_active = context.active_node
    node_selected = context.selected_nodes

    if node_tree is None:
        report({'ERROR'}, "No node tree available")
        return

    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        assert(node_group in data_from.node_groups)
        data_to.node_groups = [node_group]
    node_group = data_to.node_groups[0]

    # add node!
    center = node_center(context)

    for node in node_tree.nodes:
        node.select = False

    node_type_string = {
        "ShaderNodeTree": "ShaderNodeGroup",
        "CompositorNodeTree": "CompositorNodeGroup",
        "TextureNodeTree": "TextureNodeGroup",
        "GeometryNodeTree": "GeometryNodeGroup",
    }[type(node_tree).__name__]

    node = node_tree.nodes.new(type=node_type_string)
    node.node_tree = node_group

    is_fail = (node.node_tree is None)
    if is_fail:
        report({'WARNING'}, "Incompatible node type")

    node.select = True
    node_tree.nodes.active = node
    node.location = center

    if is_fail:
        node_tree.nodes.remove(node)
    else:
        if ungroup:
            bpy.ops.node.group_ungroup()

    # node_group.user_clear()
    # bpy.data.node_groups.remove(node_group)


# -----------------------------------------------------------------------------
# Node Template Prefs

def node_search_path(context, ui_type):
    preferences = context.preferences
    addon_prefs = preferences.addons[__name__].preferences
    node_paths = {
        "GeometryNodeTree": addon_prefs.search_path_geometry,
        "ShaderNodeTree": addon_prefs.search_path_shader,
        "CompositorNodeTree": addon_prefs.search_path_compositing,
        "TextureNodeTree": addon_prefs.search_path_texture
    }
    return node_paths.get(ui_type)


class NodeTemplatePrefs(AddonPreferences):
    bl_idname = __name__

    search_path_geometry: StringProperty(
        name="Geometry nodes path",
        subtype='DIR_PATH',
    )
    search_path_shader: StringProperty(
        name="Shader nodes path",
        subtype='DIR_PATH',
    )
    search_path_compositing: StringProperty(
        name="Compositing nodes path",
        subtype='DIR_PATH',
    )
    search_path_texture: StringProperty(
        name="Texture nodes path",
        subtype='DIR_PATH',
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "search_path_geometry")
        layout.prop(self, "search_path_shader")
        layout.prop(self, "search_path_compositing")
        layout.prop(self, "search_path_texture")


class NODE_OT_template_add(Operator):
    """Add a node template"""
    bl_idname = "node.template_add"
    bl_label = "Add node group template"
    bl_description = "Add node group template"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(
        subtype='FILE_PATH',
    )
    group_name: StringProperty()

    @classmethod
    def poll(cls, context):
        return context.space_data.node_tree

    def execute(self, context):
        node_template_add(context, self.filepath, self.group_name, True, self.report)

        return {'FINISHED'}

    def invoke(self, context, event):
        node_template_add(context, self.filepath, self.group_name, event.shift, self.report)

        return {'FINISHED'}


# -----------------------------------------------------------------------------
# Node menu list

def node_template_cache(context, *, reload=False):
    dirpath = node_search_path(context, context.area.ui_type)

    if (context.area.ui_type == "GeometryNodeTree"):
        if node_template_cache._node_cache_geometry_path != dirpath:
            reload = True
        node_cache = node_template_cache._node_cache_geometry
    elif (context.area.ui_type == "ShaderNodeTree"):
        if node_template_cache._node_cache_shader_path != dirpath:
            reload = True
        node_cache = node_template_cache._node_cache_shader
    elif (context.area.ui_type == "CompositorNodeTree"):
        if node_template_cache._node_cache_compositing_path != dirpath:
            reload = True
        node_cache = node_template_cache._node_cache_compositing
    elif (context.area.ui_type == "TextureNodeTree"):
        if node_template_cache._node_cache_texture_path != dirpath:
            reload = True
        node_cache = node_template_cache._node_cache_texture

    if reload:
        node_cache = []
    if node_cache:
        return node_cache

    for fn in os.listdir(dirpath):
        if fn.endswith(".blend"):
            filepath = os.path.join(dirpath, fn)
            with bpy.data.libraries.load(filepath) as (data_from, data_to):
                for group_name in data_from.node_groups:
                    if not group_name.startswith("_"):
                        node_cache.append((group_name, filepath))

    node_cache = sorted(node_cache)

    if (context.area.ui_type == "GeometryNodeTree"):
        node_template_cache._node_cache_geometry = node_cache
        node_template_cache._node_cache_geometry_path = dirpath
    elif (context.area.ui_type == "ShaderNodeTree"):
        node_template_cache._node_cache_shader = node_cache
        node_template_cache._node_cache_shader_path = dirpath
    elif (context.area.ui_type == "CompositorNodeTree"):
        node_template_cache._node_cache_compositing = node_cache
        node_template_cache._node_cache_compositing_path = dirpath
    elif (context.area.ui_type == "TextureNodeTree"):
        node_template_cache._node_cache_texture = node_cache
        node_template_cache._node_cache_texture_path = dirpath

    return node_cache


node_template_cache._node_cache_geometry = []
node_template_cache._node_cache_geometry_path = ""
node_template_cache._node_cache_shader = []
node_template_cache._node_cache_shader_path = ""
node_template_cache._node_cache_compositing = []
node_template_cache._node_cache_compositing_path = ""
node_template_cache._node_cache_texture = []
node_template_cache._node_cache_texture_path = ""


class NODE_MT_template_add(Menu):
    bl_label = "Node Template"

    def draw(self, context):
        layout = self.layout

        dirpath = node_search_path(context, context.area.ui_type)
        if dirpath == "":
            layout.label(text="Set search dir in the addon-prefs")
            return

        try:
            node_items = node_template_cache(context)
        except Exception as ex:
            node_items = ()
            layout.label(text=repr(ex), icon='ERROR')

        for group_name, filepath in node_items:
            props = layout.operator(
                NODE_OT_template_add.bl_idname,
                text=group_name,
            )
            props.filepath = filepath
            props.group_name = group_name


def add_node_button(self, context):
    self.layout.menu(
        NODE_MT_template_add.__name__,
        text="Template",
        icon='PLUGIN',
    )


classes = (
    NODE_OT_template_add,
    NODE_MT_template_add,
    NodeTemplatePrefs
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.NODE_MT_add.append(add_node_button)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.NODE_MT_add.remove(add_node_button)


if __name__ == "__main__":
    register()