# Copyright 2023 Wonder Dynamics

# This source code is licensed under the GNU GPLv3
# found in the LICENSE file in the root directory of this source tree.

"""Module that hold function for fixing failed validations."""

import os
import importlib

from maya import cmds, mel

from wd_validator import utilities

importlib.reload(utilities)


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


