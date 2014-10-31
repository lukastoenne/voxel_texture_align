### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "Voxel Texture Align",
    "author": "Lukas Toenne",
    "version": (0, 1, 0),
    "blender": (2, 7, 2),
    "location": "Texture Properties",
    "description": "Align a voxel texture transformation to the domain object",
    "warning": "",
    "category": "Development"}

import bpy
from bpy.types import Operator, Panel
from mathutils import *


"""
def get_texture(context):
    slot = context.texture_slot
    return slot, texture
        return context.texture_slot
    except:
        pass

    try:
        ma = context.material
        return ma.active_texture
    except:
        pass

    try:
        ma = context.material_slot.material
        return ma.active_texture
    except:
        pass

    raise Exception("Could not find texture in context")
"""

# XXX this gives exceptions, no idea why !!!
"""
def voxel_tex_poll(context):
    slot = context.texture_slot
    tex = slot.texture
    if tex.type != 'VOXEL_DATA':
        return False

    vd = tex.voxel_data
    if vd.file_format not in {'SMOKE', 'HAIR'}:
        return False

    return True
"""


def get_domain_transform(ob, md):
    if md.type == 'SMOKE':
        m = Matrix.Identity(4)
        min_loc = Vector((min(bb[0] for bb in ob.bound_box),
                          min(bb[1] for bb in ob.bound_box),
                          min(bb[2] for bb in ob.bound_box)))
        max_loc = Vector((max(bb[0] for bb in ob.bound_box),
                          max(bb[1] for bb in ob.bound_box),
                          max(bb[2] for bb in ob.bound_box)))
        loc = min_loc
        scale = (max_loc - min_loc)

        for i in range(3):
            m[i][i] = scale[i]
            m[i][3] = loc[i]

        return m
    else:
        return Matrix.Identity(4)


inv_texspace = Matrix.Identity(4)
for i in range(3):
    inv_texspace[i][i] = 0.5
    inv_texspace[i][3] = 0.5

# returns necessary offset and scale for texture slot
# to compensate for domain transform
def get_texture_inverse_transform(ob, md):
    mat = get_domain_transform(ob, md) * inv_texspace

    loc, rot, scale = mat.decompose()

    safe_div = lambda x : 1.0 / x if x != 0.0 else 0.0

    inv_scale = Vector((safe_div(scale[0]), safe_div(scale[1]), safe_div(scale[2])))
    inv_loc = -loc
    return inv_loc, inv_scale


def get_modifier_type(ob, type):
    for md in ob.modifiers:
        if md.type == type:
            return md
    return None


class VoxelTextureAlignOperator(Operator):
    """Align a voxel texture transformation to the domain object"""
    bl_idname = "texture.voxel_align"
    bl_label = "Voxel Align"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        slot = context.texture_slot
        tex = slot.texture
        vd = tex.voxel_data

        ob = vd.domain_object
        if vd.file_format == 'SMOKE':
            md = get_modifier_type(ob, 'SMOKE')
        elif vd.file_format == 'HAIR':
            md = get_modifier_type(ob, 'HAIR')
        else:
            return {'CANCELLED'}

        slot.mapping = 'FLAT'
        slot.mapping_x = 'X'
        slot.mapping_y = 'Y'
        slot.mapping_z = 'Z'
        slot.texture_coords = 'OBJECT'
        slot.object = ob

        offset, scale = get_texture_inverse_transform(ob, md)
        slot.offset[:] = offset[:]
        slot.scale = scale[:]

        return {'FINISHED'}



class VoxelTextureAlignPanel(Panel):
    """Align a voxel texture transformation to the domain object"""
    bl_label = "Voxel Align"
    bl_idname = "TEXTURE_PT_voxel_align"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"

#    @classmethod
#    def poll(cls, context):
#        return voxel_tex_poll(context)

    def draw(self, context):
        slot = context.texture_slot
        tex = slot.texture
        vd = tex.voxel_data
        layout = self.layout

        layout.operator_context = 'EXEC_REGION_WIN'
        layout.operator("texture.voxel_align")

 
def register():
    bpy.utils.register_class(VoxelTextureAlignOperator)
    bpy.utils.register_class(VoxelTextureAlignPanel)

def unregister():
    bpy.utils.unregister_class(VoxelTextureAlignOperator)
    bpy.utils.unregister_class(VoxelTextureAlignPanel)

if __name__ == "__main__":
    register()
