# Copyright 2023 Wonder Dynamics

# This source code is licensed under the GNU GPLv3
# found in the LICENSE file in the root directory of this source tree.

"""Module handling export to disk operations with scene data."""

import os
import json
import importlib

import maya.cmds as cmds
import maya.mel as mel

from wd_validator import static, utilities

importlib.reload(static)
importlib.reload(utilities)

# Code should be Python27 compatible
# pylint: disable=consider-using-f-string
# pylint: disable=unspecified-encoding


def remove_xgen_palettes(undo=False):
    """ Unresolved path in xgen palettes will crash the scene when
    file command is called with the -list flag. This function will remove all
    of them and then undo the change if the flag is set correctly.
    Args:
        undo (bool, optional): Undo the previous step. Defaults to False.
    """
    if not cmds.undoInfo( state=True, q=True):
        cmds.undoInfo( state=True, infinity=True )

    if not undo:
        all_palettes = cmds.ls(type='xgmPalette')
        cmds.delete(all_palettes)

    else:
        cmds.undo()


def create_export_dir(scene_data):
    """Builds the export directory, stores it into the scene_data object and
    ensures the export directory exists.
    Args:
        scene_data (CollectExportData): the object holding the scene data.
    """

    # Workaround for some os where cmds.file(q=1, sn=1) returns an empty string.
    # Using list=True and keeping the first path since this is the scene name.

    remove_xgen_palettes() # If some xgen palettes have unresolved paths cmds.file will crash the scene...
    scene_path = cmds.file(query=True, l=True)[0]
    scene_root_dir = os.path.dirname(scene_path)

    pack_dir = os.path.join(scene_root_dir, '01_wonder_studio_character_data').replace('\\', '/')

    if not os.path.isdir(pack_dir):
        os.mkdir(pack_dir)

    scene_data.export_dir = pack_dir
    remove_xgen_palettes(undo=True)


def remove_fbx_attribute(scene_data):
    """ Loops trought all joints in the scene and removes filmboxTypeID attribute if found.
    Args:
        scene_data (CollectExportData): the object holding the scene data.
    """
    all_joints = cmds.ls(scene_data.rig_selection, type='joint', long=True)
    all_joints += cmds.listRelatives(scene_data.rig_selection, type='joint', ad=True, fullPath=True)

    for jnt in all_joints:
        if cmds.attributeQuery('filmboxTypeID', exists=True, node=jnt):
            cmds.deleteAttr(jnt + '.filmboxTypeID')


def fix_blendshapes(scene_data):
    """ Fix blendshapes so they don't break the geometry during export
    Args:
        scene_data (CollectExportData): the object holding the scene data.
    """
    face = scene_data.face_geo

    if face:
        # Find blendshapes
        blendshapes = cmds.ls(cmds.listHistory(face), type='blendShape')

        if blendshapes:
            if len(blendshapes) > 1:
                cmds.warning('More than one blendshape found on {}'.format(face))

            # Fix inputs in all blendshapes
            for blendshape in blendshapes:
                mesh_list = cmds.listConnections(blendshape + '.inputTarget')

                for mesh in mesh_list or []:
                    src_conn = mesh + '.inMesh'

                    # history connected to in mesh (should be either 1 if there are history
                    # or 0 if there are no history connected)
                    conns_in_mesh = cmds.listConnections(mesh + '.inMesh', p=1)
                    for conn in conns_in_mesh or []:
                        cmds.disconnectAttr(conn, src_conn)


def export_meshes(scene_data):
    """Export the skinned Model and its skeleton to a file in FBX format.
    Args:
        scene_data (CollectExportData): the object holding the scene data.
    Notes:
        scene_data object needs to have the export_dir defined for this method
            to be successful.
    """
    # Remove filmboxTypeID attribute from joints
    remove_fbx_attribute(scene_data)
    # Fix blendshapes so they don't break the mesh during export
    fix_blendshapes(scene_data)
    # Select objects
    cmds.select(clear=True)
    cmds.select(scene_data.geo_group)
    cmds.select(scene_data.rig_selection, add=True)
    cmds.select(scene_data.blendshapes, add=True)

    # Create export path
    export_path = os.path.join(scene_data.export_dir, 'character.fbx').replace('\\', '/')

    # Load FBX plugin and export
    cmds.loadPlugin('fbxmaya')

    mel.eval('FBXResetExport')
    mel.eval('FBXExportFileVersion -v FBX202000')
    mel.eval('FBXExportInAscii -v false')
    mel.eval('FBXExport -f \"{}\" -s'.format(export_path))

    print('\nData exported to: ' + export_path + '\n')


def remove_fbx_suffix(material):
    """ Remove a fbx namming conflict suffix from the mateirla name.
    Args:
        material (str): Name of the material.
    Returns:
        str: Name of the material with removed fbx suffix.
    """
    return material.split('_ncl1')[0]


def export_textures(scene_data):
    """Copies textures defiend in material defined in scene data by name and creates
    the description data for the materials that are stored in the scene data
    metadata_json key.
    Args:
        scene_data (CollectExportData): the scene data object initialized with materials.
    """
    materials_list = []

    for material in scene_data.materials:
        mat_dict = {}

        material_type = cmds.nodeType(material)

        if material_type in ['aiStandardSurface', 'standardSurface']:
            type_ = 'surface'

        else:
            type_ = 'flat'

        mat_dict['material_name'] = remove_fbx_suffix(material)
        mat_dict['material_type'] = type_
        mat_dict['mesh_names'] = utilities.get_material_meshes(material)
        mat_dict['render_engine'] = 'arnold'

        for attr, key_names in static.material_attributes[material_type].items():
            attr_value, attr_textures = utilities.get_attribute_value(material, attr)

            if attr == 'normalCamera':
                mat_dict['bump_type'] = attr_value[0]
                mat_dict['bump_flip'] = attr_value[2]

                if attr_textures:
                    tex_name = utilities.make_extension_lowercase(os.path.split(attr_textures[0])[-1])
                    mat_dict[key_names[1]] = tex_name
                    utilities.copy_textures(attr_textures, scene_data.export_dir)

                else:
                    mat_dict[key_names[1]] = None

                mat_dict['bumpWeight_value'] = attr_value[1]

            else:
                mat_dict[key_names[0]] = attr_value

                if attr_textures:
                    tex_name = utilities.make_extension_lowercase(os.path.split(attr_textures[0])[-1])
                    mat_dict[key_names[1]] = tex_name
                    utilities.copy_textures(attr_textures, scene_data.export_dir)

                else:
                    mat_dict[key_names[1]] = None

        materials_list.append(mat_dict)

    scene_data.metadata_json['materials'] = materials_list


def export_groom(scene_data):
    """Exports all interactive grooms present in current scene. It also adds the groom material data
    the the scene data json metadata variable.
    Args:
        scene_data (CollectExportData): the scene data object initialized with materials.
    Notes:
        Needs export dir to be defined in scene data and the folder to be already created.
    """
    print('\n>>> Exporting xGen groom...\n')

    ig_spline_bases = cmds.ls(type='xgmSplineBase') or None
    all_interactive_grooms = []
    all_materials = {}

    i = 1

    for spline_base in ig_spline_bases:
        scalp_geo = cmds.listConnections(spline_base + '.boundMesh')[0]

        if scalp_geo:
            interactive_groom_shape = utilities.get_spline_description(spline_base)
            interactive_groom = cmds.listRelatives(interactive_groom_shape, parent=True)[0]
            interactive_groom_sg = cmds.listConnections(
                '{}.instObjGroups'.format(interactive_groom_shape), type='shadingEngine'
            )[0]
            material = cmds.listConnections('{}.surfaceShader'.format(interactive_groom_sg))[0]

            new_name = '{mesh}_groom{id}_sd'.format(id=str(i), mesh=scalp_geo)

            if material not in all_materials:
                all_materials[material] = [new_name]
            else:
                all_materials[material].append(new_name)

            cmds.rename(interactive_groom, new_name)
            all_interactive_grooms.append(new_name)

            i += 1

    for mat, groom_list in all_materials.items():
        base_color = cmds.getAttr('%s.baseColor' % mat)
        melanin = cmds.getAttr('%s.melanin' % mat)
        melanin_redness = cmds.getAttr('%s.melaninRedness' % mat)
        melanin_randomize = cmds.getAttr('%s.melaninRandomize' % mat)
        roughness = cmds.getAttr('%s.roughness' % mat)
        ior = cmds.getAttr('%s.ior' % mat)

        hair_mat = {}
        hair_mat['material_name'] = mat
        hair_mat['material_type'] = 'hair'
        hair_mat['groom_names'] = [groom.split('|')[-1] for groom in groom_list]
        hair_mat['render_engine'] = 'arnold'

        hair_mat['diffuse_value'] = tuple(base_color[0])
        hair_mat['diffuse_texture'] = None
        hair_mat['melanin_value'] = melanin
        hair_mat['melanin_texture'] = None
        hair_mat['melaninRedness_value'] = melanin_redness
        hair_mat['melaninRedness_texture'] = None
        hair_mat['melaninRandomize_value'] = melanin_randomize
        hair_mat['melaninRandomize_texture'] = None
        hair_mat['roughness_value'] = roughness
        hair_mat['roughness_texture'] = None
        hair_mat['ior_value'] = ior
        hair_mat['ior_texture'] = None

    if all_interactive_grooms:
        # Export groom
        export_path = os.path.join(scene_data.export_dir, 'groom.abc').replace('\\', '/')
        current_frame = cmds.currentTime(query=True)

        job = f'-f "{export_path}" -fr {current_frame} {current_frame} -step 1 -wfw'

        for groom in all_interactive_grooms:
            job += ' -obj {}'.format(groom)

        cmds.xgmSplineCache(export=True, j=job)
        scene_data.metadata_json['materials'].append(hair_mat)

        print('>>> All xGen grooms exported.')

    else:
        cmds.warning('>>> No interactive grooms for export.')


def export_metadata(scene_data):
    """Dumps the json metadata in scene data object to a file on disk.
    Args:
        scene_data (CollectExportData): the scene data object initialized with scene content.
    """
    metadata_path = os.path.join(scene_data.export_dir, 'metadata.json').replace('\\', '/')

    output_dict = scene_data.metadata_json
    output_dict['body']['armature_name'] = scene_data.rig_group.split('|')[-1]
    output_dict['body']['bone_names'] = utilities.read_data('rig_mapping')

    eyes_data = utilities.get_eyes_data()

    if scene_data.face_geo:
        output_dict['face']['mesh_name'] = scene_data.face_geo.split('|')[-1]

        for blendshape in scene_data.face_blendshapes:
            output_dict['face']['blendshape_names'][blendshape] = blendshape

        if eyes_data:
            output_dict['eyes_rig'] = eyes_data
        else:
            output_dict['eyes_rig'] = []

    with open(metadata_path, 'w') as outfile:
        json.dump(output_dict, outfile, indent=4)


def export(xgen_export, scene_data):
    """Does the full export of geometry, textures, grooms and json metadata. Also creates
    the export directory.
    Args:
        xgen_export (bool): whether or not to export hair grooms.
        scene_data (CollectExportData): the scene data object initialized with scene content.
    """
    create_export_dir(scene_data)
    export_meshes(scene_data)
    export_textures(scene_data)

    if xgen_export:
        export_groom(scene_data)

    export_metadata(scene_data)
