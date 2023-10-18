# Copyright 2023 Wonder Dynamics

# This source code is licensed under the GNU GPLv3
# found in the LICENSE file in the root directory of this source tree.

"""Module that groups different utitlies from data persistence, to validation, to querying maya properties
 to file management and data building.
 """

import json
import base64
import os
import re
import glob
import shutil

from wd_validator import static

import maya.cmds as cmds
import xgenm as xg


# Code should be Python27 compatible
# pylint: disable=consider-using-f-string


def write_data(key, dict_data):
    """Persists data by saving it encoded in the header section of the maya file.
    Args:
        key (str): the key to retrieve the data later.
        dict_data (dict): the data to persist.
    Notes:
        valid keys are eyes_mapping, rig_mapping, rig_status and face_mesh.
    """
    dict_string = json.dumps(dict_data)
    encoded_data = base64.b64encode(dict_string.encode('utf-8'))

    cmds.fileInfo(key, encoded_data)


def read_data(key):
    """Reads the data stored in the maya scene header for that key.
    Args:
        key (str): the key to the stored data.
    Returns:
        dict or None: The stored data as a python dictionary or None if
            keys was not found.
    """
    data = cmds.fileInfo(key, query=True)

    if data:
        data = json.loads(base64.b64decode(data[0]))
    else:
        data = None

    return data


def check_data(key):
    """Returns whether or not a key contains data in the maya scene.
    Args:
        key (str): the key to the stored data.
    Returns:
        bool: whether or not the key has data associated.
    """
    if cmds.fileInfo(key, query=True):
        return True

    else:
        return False


def remove_data(key):
    """Removes a key and its associated data from the scene.
    Args:
        key (str): the key to the stored data.
    """
    cmds.fileInfo(remove=key)


def reset_validation_data(scene_data):
    """Resets the status value of all validators to None.
    Args:
        scene_data (CollectExportData): the object holding the scene data.
    """
    default_validation_values = {}

    for key in static.validation_windows_data.keys():
        default_validation_values[key] = None

    scene_data.validation_data = default_validation_values


def abort_validation(scene_data):
    """Sets an 'aborted' status in all the validators that were not executed.
    Args:
        scene_data (CollectExportData): the object holding the scene data.
    """
    for key, val in scene_data.validation_data.items():
        if val is None:
            scene_data.gui_inst.update_status(val_type=key, status='aborted')

    message = ['>>> Validation ABORTED.', '  > Make sure to fix current errors before continuing with the validation.']
    scene_data.gui_inst.update_script_output(message=message)


def remove_namespaces():
    """Removes all namespaces found on scene by moving all their content to the root namespace.
    Notes:
        This method is currently not being used.
    """
    cmds.namespace(setNamespace=':')

    default_namespaces = ['UI', 'shared']
    all_namespaces = [
        x for x in cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True) if x not in default_namespaces
    ]

    if all_namespaces:
        all_namespaces.sort(key=len, reverse=True)

        for namespace in all_namespaces:
            if cmds.namespace(exists=namespace) is True:
                cmds.namespace(removeNamespace=namespace, mergeNamespaceWithRoot=True)


def get_texture_path(file_node):
    """Gets the list of paths on disk for textures in a specified node name.
    UDIM textures will be expanded to existing files matching the UDIM description.
    Args:
        file_node (str): The node name to inspect.
    Returns:
        list[str] or None: A list of all the found textures or None if none found.
    """
    regex = r'(?<=[\.|_])[1][0-9]{3}(?=[\.|_])|<udim>'
    file_node_type = cmds.nodeType(file_node)

    if file_node_type == 'file':
        texture_path = cmds.getAttr('{}.fileTextureName'.format(file_node)) or None

    else:
        texture_path = cmds.getAttr('{}.filename'.format(file_node)) or None

    if texture_path:
        udim_check = re.search(regex, texture_path, re.MULTILINE | re.IGNORECASE)

        if udim_check:
            check_path = re.sub(regex, '*', texture_path, flags=re.MULTILINE | re.IGNORECASE)
            all_textures = glob.glob(check_path)

            return all_textures

        else:
            return [texture_path]

    else:
        return None


def get_attribute_value(material, attribute):
    """Returns a material's attribute value handling texture mapped attributes too.
    Args:
        material (str): the name of the node to analyze.
        attribute (str): the name of the attribute to analyze.
    Returns:
        if attribute is normalCamera:
            list[None or str, float, bool], str or None: a list with: the bump_type (can be normal_tangent_space,
                normal_object_space or bump), the bump_value and whether or not the bump is flipped, and then
                the texture path or None if it is not set.
        else:
            tuple(float, str or None): the attribute value, the path to the texture or None if it was not set.
    """
    # bump_data = {}
    connection = cmds.listConnections(material + '.' + attribute) or None

    if connection is not None and attribute in static.accepting_textures:
        connection_type = cmds.nodeType(connection[0])

        if attribute != 'normalCamera':
            # Input is a texture node
            attribute_value = cmds.getAttr(material + '.' + attribute)

            if isinstance(attribute_value, list):
                attribute_value = attribute_value[0]

            else:
                attribute_value = float(attribute_value)

            texture_path = get_texture_path(connection[0])

            return attribute_value, texture_path

        else:
            # Input is a bump node
            bump_input_attr = static.supported_bump_nodes[connection_type]['input_attr']
            bump_file_node = cmds.listConnections('{c}.{b}'.format(c=connection[0], b=bump_input_attr)) or None

            bump_flip = False

            if bump_file_node:
                texture_path = get_texture_path(bump_file_node[0])
                bump_value = float(
                    cmds.getAttr(
                        '{bn}.{at}'.format(
                            bn=connection[0], at=static.supported_bump_nodes[connection_type]['value_attr']
                        )
                    )
                )

                if connection_type == 'bump2d':
                    bump_interpolation = cmds.getAttr(connection[0] + '.bumpInterp')
                    bump_flip = cmds.getAttr(connection[0] + '.aiFlipG')

                    if bump_interpolation != 0:
                        if bump_interpolation == 1:
                            bump_type = 'normal_tangent_space'

                        else:
                            bump_type = 'normal_object_space'

                    else:
                        bump_type = 'bump'

                if connection_type == 'aiBump2d':
                    bump_type = 'bump'

                if connection_type == 'aiNormalMap':
                    bump_flip = cmds.getAttr(connection[0] + '.invertY')

                    if bool(cmds.getAttr(connection[0] + '.tangentSpace')):
                        bump_type = 'normal_tangent_space'

                    else:
                        bump_type = 'normal_object_space'

                return [bump_type, bump_value, bump_flip], texture_path

            else:
                return [None, 0.0, bump_flip], None

    else:
        # No input, return attribute value
        if attribute != 'normalCamera':
            attribute_value = cmds.getAttr(material + '.' + attribute)

            if isinstance(attribute_value, list):
                attribute_value = attribute_value[0]

            else:
                attribute_value = float(attribute_value)

            return attribute_value, None

        else:
            return [None, 0.0, False], None


def get_material_meshes(material, short_name=True):
    """Returns a list of all transforms of meshes that are assigned to a material.
    Args:
        material (str): the shader name.
        short_name (bool, optional): whether or not to return short names. Defaults to True.
    Returns:
        list[str]: the list of transforms with meshes assigned to the material.

    """
    all_meshes = []
    shading_groups = cmds.listConnections(material + '.outColor')

    for shading_group in shading_groups:
        sg_meshes = cmds.listConnections(shading_group + '.dagSetMembers')

        if sg_meshes:
            all_meshes += sg_meshes

    if short_name:
        all_meshes = [mesh.split('|')[-1] for mesh in all_meshes]

    return all_meshes


def make_extension_lowercase(file):
    """Returns a path with lowercase extension.
    Args:
        file (str): the path to modify.
    Returns:
        str: the path with a lowercase extension.
    """
    file = os.path.splitext(file)

    return file[0] + file[1].lower()


def copy_textures(source_path, target_dir):
    """Copies a texture to a different path.
    Args:
        source_path (str): full path to source texture.
        target_dir (str): full path to destination folder.
    Raises:
        FileNotFoundError: if the destination folder does not exists or user does not have
            write access in destination folder.
        FileNotFoundError: if the source file does not exists or user has no read access.
    """
    if source_path:
        for path in source_path:
            texture_name = make_extension_lowercase(os.path.split(path)[-1])
            destination_path = os.path.join(target_dir, texture_name).replace('\\', '/')
            try:
                shutil.copy(path, destination_path)
            except shutil.SameFileError as e:
                print(e)


def get_eyes_data():
    """Returns a list of eye data read from file. Only eyes where all eye data is set will
    be returned.
    Returns:
        list[dict] or None: The data for the eyes stored in the file. If no eyes found, None
            will be returned.
    """
    all_data = []

    if check_data(key='eyes_mapping'):
        eye_mapping = read_data(key='eyes_mapping')

        for eye in eye_mapping.values():
            skip = False

            if eye['bone_field_value']:
                if cmds.objExists(eye['bone_field_value']):
                    for value in static.eye_values.keys():
                        # Check if all fields are set
                        if eye[value] is None:
                            skip = True
                            break
                else:
                    skip = True
            else:
                skip = True

            if skip:
                continue

            else:
                eye_data = {
                    'bone_name': eye['bone_field_value'],
                    'horizontal_rotation_axis': eye['horizontal_axis_menu_value'],
                    'vertical_rotation_axis': eye['vertical_axis_menu_value'],
                    'horizontal_min_max_value': [eye['horizontal_min_field_value'], eye['horizontal_max_field_value']],
                    'vertical_min_max_value': [eye['vertical_min_field_value'], eye['vertical_max_field_value']],
                }

                all_data.append(eye_data)

    if all_data:
        return all_data

    else:
        return None


def camel_case_split(text):
    """Returns a string of a split camel case string.
    Args:
        text (str): String in camel case format.
    Returns:
        str: Split camel case string.
    """

    split_text = re.findall(r'[a-z]+|[A-Z][a-z]*', text)
    split_text = ' '.join([word.capitalize() for word in split_text])

    return split_text


def get_pre_skin_history(mesh):
    """ List all non deforming history of a mesh
    Args:
        mesh (str): Mesh that needs checking
    Returns:
        list: List of all nodes that belong to non-deforming history
    """
    history_before_skin = []
    history = cmds.ls(cmds.listHistory(mesh), l=True)

    if not history:
        return history_before_skin

    for node in history[1:]: # first history is the shape itself
        if cmds.nodeType(node) == 'skinCluster':
            break

        history_before_skin.append(node)

    return history_before_skin
