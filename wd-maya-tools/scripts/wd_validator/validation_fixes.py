# Copyright 2023 Wonder Dynamics

# This source code is licensed under the GNU GPLv3
# found in the LICENSE file in the root directory of this source tree.

"""Module that hold function for fixing failed validations."""

import datetime
import os
import importlib

from maya import cmds, mel

from wd_validator import utilities

importlib.reload(utilities)

# code needs to run in python 2.7
# pylint: disable=consider-using-f-string


def all_group_fix(scene_data):
    """Creates the all group hierarchy.

    Args:
        scene_data (CollectExportData): the object holding the scene data.
    """

    print('This should fix the group missing or misnamed mismatching or transformed')
    # create empty group
    group = cmds.group(em=True)

    # parent body and geo
    cmds.parent(scene_data.geo_group, group)
    cmds.parent(scene_data.rig_group, group)

    # make sure there is not other all in the root
    name = 'all'
    target = '|{}'.format(name)
    if cmds.objExists(target):
        new_name = name + datetime.datetime.now().strftime('%y%m%d%H%M%S%f')
        cmds.rename(target, new_name)

    # rename as all
    cmds.rename(group, target)


def joint_name_fix(scene_data):
    """Fixes names on joints so they are USD compatible.

    Args:
        scene_data (CollectExportData): the object holding the scene data.
    """
    if scene_data.validation_data.get('rig_check') != 'fix':
        return

    def _fix_joint_name(joint):
        # fix by removing all namespaces. In this way, the bone auto assign can still work.
        new_name = joint.rsplit(':', 1)[-1]
        # we still need to check for weird characters
        new_name = utilities.to_valid_usd_name(new_name)
        cmds.rename(joint, new_name)

    joints = cmds.listRelatives(scene_data.rig_selection, ad=1, pa=1, type='joint') or []
    joints += [scene_data.rig_selection]
    for joint in joints:
        _fix_joint_name(joint)


def remove_animation_on_rig_fix(scene_data):
    """Disconnect animation curves from rig.

    Args:
        scene_data (CollectExportData): the object holding the scene data.
    """
    if scene_data.validation_data.get('rig_check') != 'warning_fix':
        return

    rig_selection =  scene_data.rig_selection
    if not cmds.objExists(rig_selection):
        print('>>> WARNING! Could not find rig selection {}'.format(rig_selection))
        return

    animation_curves_found = utilities.get_animation_curves_connected_to_group(rig_selection)
    utilities.disconnect_curves(animation_curves_found)


def remove_animation_on_geo_fix(scene_data):
    """Disconnect animation curves from rig.

    Args:
        scene_data (CollectExportData): the object holding the scene data.
    """
    geo_group = scene_data.geo_group or []

    # keeping existing group
    valid_geo_groups = [grp for grp in geo_group if grp and cmds.objExists(grp)]

    if not valid_geo_groups:
        print('>>> WARNING! Could not find the GEO group!')
        return

    animation_curves_found = utilities.get_animation_curves_connected_to_group(*valid_geo_groups)
    utilities.disconnect_curves(animation_curves_found)


def reference_data_fix():
    """Imports all reference content in this maya scene."""
    all_references = cmds.file(query=True, reference=True)

    if all_references:
        for ref in all_references:
            cmds.file(ref, importReference=True)

        reference_data_fix()

    # utilities.remove_namespaces()


def fix_empty_file_nodes(scene_data):
    """Deletes from current scene all texture nodes that do no have a texture assigned and that
    are described in the scene data object.
    Args:
        scene_data (CollectExportData): the object with the scene data alreadu initialized.
    """
    for file_node, texture_path in scene_data.file_nodes.items():
        if not texture_path:
            cmds.delete(file_node)


def save_scene(overwrite=True):
    """Saves the maya scene by overwriting it.
    Args:
        overwrite (bool, optional): whether or not to overwrite, or save
            it with an _export suffix. Optional, defaults to overwirte
    """
    if overwrite:
        cmds.file(save=True)

    else:
        # Workaround for some os where cmds.file(q=1, sn=1) returns an empty string.
        # Using list=True and keeping the first path since this is the scene name.
        scene_full_path = cmds.file(query=True, l=True)[0]

        # Save the scene with _export suffix
        root_path, scene_name = os.path.split(scene_full_path)
        root_name, extension = os.path.splitext(scene_name)

        suffix = '_export'
        export_scene_name = root_name + suffix + extension
        export_name = os.path.join(root_path, export_scene_name)

        cmds.file(rename=export_name)
        cmds.file(save=True)


def remove_pre_skin_history(scene_data):
    """ Remove non deforming history on a mesh.
    Args:
        scene_data (CollectExportData): the object with the scene data alreadu initialized.
    """
    message = 'Not supported history nodes detected!\nYou can apply a bypass fix for them.'
    message += '\nThis might remove blendshapes if they are not in correct deformation order!'
    message += '\nIf you decide to apply a fix, please check if there are any unwanted side effects afterwards.'
    answer = cmds.confirmDialog(title='Warning', message=message, button=['Apply Bypass Fix','Abort'], defaultButton='Apply Bypass Fix', cancelButton='Abort', dismissString='Abort')

    if answer == 'Apply Bypass Fix':
        for mesh in scene_data.meshes_with_history:
            print('Bypassing history nodes on mesh \"{}\"'.format(mesh.split('|')[-1]))
            history = cmds.listHistory(mesh)

            # Find the skin cluster node
            for node in history:
                if cmds.nodeType(node) == 'skinCluster':
                    skin_cluster = node
                    break
            else:
                skin_cluster = None

            # Connect the skin cluster node to the shape
            if skin_cluster:
                cmds.connectAttr(skin_cluster + '.outputGeometry[0]', mesh + '.inMesh', force=True)

    else:
        print('Aborting mesh history fix.')


