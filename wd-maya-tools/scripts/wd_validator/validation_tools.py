# Copyright 2023 Wonder Dynamics

# This source code is licensed under the GNU GPLv3
# found in the LICENSE file in the root directory of this source tree.

"""Module defining the check's messages and most of their logic."""

import os
import importlib
import maya.cmds as cmds

from wd_validator import utilities, static

importlib.reload(utilities)
importlib.reload(static)


# Code should be Python27 compatible
# pylint: disable=consider-using-f-string


def scene_saved_check(scene_data):
    """Check if the current scene exists on disk. The status for this check is stored
    in the scene_data object.
    Args:
        scene_data (CollectExportData): the object with the scene data already initialized.
    Returns:
        tuple(str, str): the result of the check, first status (fail|pass) the then the
            message explaining the status.
    """
    scene_existance = cmds.file(q=True, exists=True)

    if not scene_existance:
        status = 'fail'
        message = [
            '>>> [ERROR] Scene save status check - FAIL.',
            '  > Make sure that the scene is saved before exporting the data.',
        ]

    else:
        status = 'pass'
        message = '>>> Scene save status check - PASS.'

    scene_data.validation_data['scene_saved'] = status
    return status, message


def referenced_data_check(scene_data):
    """Check if the current scene has referenced files. The status for this check is stored
    in the scene_data object.
    Args:
        scene_data (CollectExportData): the object with the scene data already initialized.
    Returns:
        tuple(str, str): the result of the check, first status (fix|pass) the then the
            message explaining the status.
    """
    all_references = cmds.file(query=True, reference=True)

    if all_references:
        status = 'fix'
        message = [
            '>>> [ERROR] Checking if there is referenced data - FAIL.',
            '  > Make sure that all referenced data is imported and namespaces removed.',
            '  > Automatic fix available. Click on the \"FIX?\" button to start.',
        ]

    else:
        status = 'pass'
        message = '>>> Checking if there is referenced data - PASS.'

    scene_data.validation_data['referenced_data'] = status
    return status, message


def geo_group_check(scene_data):
    """Check if the current scene data has a geo group defined and if the geo has children.
    The status for this check is stored in the scene_data object.
    Args:
        scene_data (CollectExportData): the object with the scene data already initialized.
    Returns:
        tuple(str, str): the result of the check, first status (fail|pass) the then the
            message explaining the status.
    """
    geo_group = scene_data.geo_group or []

    # keeping existing group
    valid_geo_groups = [grp for grp in geo_group if grp and cmds.objExists(grp)]

    if valid_geo_groups:
        group_contents = cmds.listRelatives(valid_geo_groups, ad=True) or None

        if group_contents:
            status = 'pass'
            message = '>>> Checking if the \"GEO\" group exists - PASS.'

        else:
            status = 'fail'
            message = [
                '>>> [ERROR] The \"GEO\" group is empty - FAIL.',
                '  > Make sure that all character geometries are inside the \"GEO\" group.',
            ]

    else:
        status = 'fail'
        message = [
            '>>> [ERROR] Checking if the \"GEO\" group exists - FAIL.',
            '  > All geometries must be contained within the \"GEO\" group.',
        ]

    scene_data.validation_data['geo_check'] = status
    return status, message


def rig_group_check(scene_data):
    """Check if the current scene data has a rig group defined. The status for this check is stored
    in the scene_data object.
    Args:
        scene_data (CollectExportData): the object with the scene data already initialized.
    Returns:
        tuple(str, str): the result of the check, first status (fail|pass) the then the
            message explaining the status.
    """
    rig_group = scene_data.rig_group

    if rig_group:
        status = 'pass'
        message = '>>> Rig group suffix check - PASS.'
    else:
        status = 'fail'
        message = [
            '>>> [ERROR] Rig group suffix check - FAIL.',
            '  > Wrong skeleton/armature name! The main skeleton/armature name does not end with the tag "BODY"!',
            '  > Rig and blendshapes need to be contained inside a group with the \"_BODY\" suffix.',
            '  > Rig group name example: \"character_BODY\".',
        ]

    scene_data.validation_data['rig_group_check'] = status
    return status, message


def poly_count_check(scene_data, poly_limit=1500000):
    """Check if the sum of faces of all the meshes stored in scene_data are less than the
    poly_limit (defaults to 1_500_000). The status for this check is stored
    in the scene_data object.
    Args:
        scene_data (CollectExportData): the object with the scene data already initialized.
        poly_limit (int): the threshold number of faces to pass the test. Optional, defaults
            to 1_500_000 (1.5 million).
    Returns:
        tuple(str, str): the result of the check, first status (fail|pass) the then the
            message explaining the status.
    """
    polycount = 0

    for mesh in scene_data.all_meshes:
        polycount += cmds.polyEvaluate(mesh, face=True)

    if polycount > poly_limit:
        status = 'fail'
        message = [
            '>>> [ERROR] Polycount check - FAIL.',
            '  > Poly count limit exceeded!',
            '  > Poly count exceeds the allowed amount of {} polygons per character!'.format(poly_limit),
            '  > Note that subdivision counts towards your poly count.',
        ]

    else:
        status = 'pass'
        message = '>>> Polycount check - PASS.'

    scene_data.validation_data['poly_count_check'] = status
    return status, message


def rig_hierarchy_check(scene_data):
    """Checks if rig is placed inside the "_BODY" group.

    Args:
        scene_data (CollectExportData): the object with the scene data already initialized.
    Returns:
        bool: the result of the check, True if hierarchy is correct and Fals if it's not.
    """
    rig_parents = cmds.listRelatives(scene_data.rig_selection, parent=True, fullPath=True)

    if not scene_data.rig_group:
        return False

    rig_group = '|' + scene_data.rig_group

    if not rig_parents:
        return False

    if rig_parents[0] != rig_group:
        return False

    return True


def rig_check(scene_data):
    """Check if the current scene data has a rig defined. The status for this check is stored
    in the scene_data object.
    Args:
        scene_data (CollectExportData): the object with the scene data already initialized.
    Returns:
        tuple(str, str): the result of the check, first status (fail|pass) the then the
            message explaining the status.
    """
    character_rig = scene_data.rig_selection

    if not character_rig:
        status = 'fail'

        # Check if any rig exists in the scene
        joints = cmds.ls(type='joint')
        message = ['>>> [ERROR] Character rig check - FAIL.']

        if not joints:
            message.append('  > No rig found.')

        message.append('  > Make sure that the character is rigged and skinned to the rig.')

        scene_data.validation_data['rig_check'] = status
        return status, message

    if not rig_hierarchy_check(scene_data):
        status = 'fail'
        message = ['>>> [ERROR] Character rig check - FAIL.',]

        if scene_data.rig_group:
            message.append('  > Make sure that the rig is directly parented to the \"{}\" group.'.format(scene_data.rig_group))

        else:
            message.append('  > Rig and blendshapes need to be contained inside a group with the \"_BODY\" suffix.')

        scene_data.validation_data['rig_check'] = status
        return status, message

    status = 'pass'
    message = '>>> Character rig check - PASS.'

    scene_data.validation_data['rig_check'] = status
    return status, message


def retargeting_check(scene_data):
    """Check if the current scene data has a rig_mapping defined and if there is a Hip joint defined.
    Bones defined in the rig_mapping that do not exists in scene will be removed from scene_data object.
    The status for this check is stored in the scene_data object too.
    Args:
        scene_data (CollectExportData): the object with the scene data already initialized.
    Returns:
        tuple(str, str): the result of the check, first status (fail|pass) the then the
            message explaining the status.
    """
    if utilities.check_data('rig_mapping'):
        all_bones = utilities.read_data('rig_mapping')

        # Check for changes
        for key, bone in all_bones.items():
            if bone:
                if cmds.objExists(bone) is False:
                    all_bones[key] = None
                    try:
                        scene_data.retarget_gui_inst.clear_bone(key=key)
                    except Exception:
                        print('Joint mapping window closed.')

        # Save changes
        utilities.write_data('rig_mapping', all_bones)

        if all_bones['Hips']:
            # check all bones for warning
            if None in all_bones.values():
                status = 'warning'
                message = [
                    '>>> [WARNING] Pose bones missing! Missing bones may negatively impact animation quality.',
                    '  > Please make sure missing bones are left out intentionally.',
                ]

            else:
                status = 'pass'
                message = '>>> Character joint mapping data check - PASS.'

        else:
            status = 'fail'
            message = [
                '>>> [ERROR] Character joint mapping data check - FAIL.',
                '  > Hips bone not found!',
            ]
    else:
        status = 'fail'
        message = [
            '>>> [ERROR] Character joint mapping data check - FAIL.',
            '  > No joint mapping data found. ',
            '  > Make sure to map all availabe bones using the joint mapping UI.',
        ]

    scene_data.validation_data['retargeting_check'] = status
    return status, message


def rig_ik_check(scene_data):
    """Check if all bones needed for IK handles are in the correct hierarchy.
    Args:
        scene_data (CollectExportData): the object with the scene data already initialized.
    Returns:
        tuple(str, str): the result of the check, first status (warning|pass) the then the
            message explaining the status.
    """

    all_bones = utilities.read_data('rig_mapping')

    # Check if any bones are mapped
    if not all_bones:
        status = 'warning'
        message = [
            '>>> [WARNING] IK joints chain check - FAIL.',
            '  > No joint mapping data found.',
            '  > Make sure to map all available joins before continuing with character validation.',
        ]
        return status, message

    # Check if all joint pairs are in the same joint hierarchy.
    for pair_dict in static.ik_pairs.values():
        chain_start, chain_end = pair_dict['keys']
        all_children = cmds.listRelatives(all_bones[chain_start], allDescendents=True, type='joint') or []
        pair_dict['status'] = all_bones[chain_end] in all_children

    # Check the IK data and generate status and messages to be returned.
    status = 'pass'
    all_messages = []

    for key, data in static.ik_pairs.items():
        all_messages.append(
            '  > {ik_chain} joint chain IK compatible - {stat}'.format(
                ik_chain=utilities.camel_case_split(key), stat=str(data['status'])
            )
        )

        if not data['status']:
            status = 'warning'

    if status == 'pass':
        message = ['>>> IK joints chain check - PASS.']
        message += all_messages

    else:
        message = ['>>> [WARNING] IK joints chain check - FAIL.']
        message += all_messages
        message += [
            '  > Unable to establish some or all IK bone chains.',
            '  > IK features, in Live Action Advanced projects, may not be applied for some limbs.',
        ]

    scene_data.validation_data['ik_check'] = status
    return status, message


def face_check(scene_data, face_geo=None):
    """Check if the face is defined either on scene data or on the face_geo parameter, then check if the
    object exists in Maya and respects the expected naming. It also check it it has at least one blendshapes
    with the predefined names. The status for this check is stored in the scene_data object.
    Args:
        scene_data (CollectExportData): the object with the scene data already initialized.
        face_geo (str): a transform name to use as face if it is not defined in scene_data.
            Optional.
    Returns:
        tuple(str, str): the result of the check, first status (fail|warning|pass|skip) the then the
            message explaining the status.
    """

    prevent_multi_blendshapes = False
    prevent_multi_shapes = False

    face_geo = face_geo or scene_data.face_geo

    if not face_geo or not cmds.objExists(face_geo):
        status = 'skip'
        message = '>>> Face geometry check - Skipping.'
        scene_data.gui_inst.remove_face_geo(enable_export=False)

        scene_data.validation_data['face_check'] = status
        return status, message

    error_messages = []
    warn_messages = []

    valid_blendshape_names = [n for n in scene_data.metadata_json['face']['blendshape_names'] if n != 'basis']

    # Naming check
    if face_geo.split('_')[-1] != 'FACE':
        error_messages.append('  > Wrong face mesh name! Main face mesh name does not end with the tag "FACE"!')

    # Blendshapes check
    face_history = cmds.listHistory(face_geo)
    face_blendshape_node = cmds.ls(face_history, type='blendShape')

    if len(face_blendshape_node) > 1:
        warn_msg = [
            '  > Multiple Blendshape deformers on Face.',
            '  > This could yield unexpected results in Maya rigs.'
        ]
        if prevent_multi_blendshapes:
            error_messages += warn_msg
        else:
            warn_messages += warn_msg

    # clear previous blendshapes so we keep only the ones in current blendshape nodes
    scene_data.face_blendshapes = []
    existing_blendshapes = []

    for bshn in face_blendshape_node:
        blendshape_names = cmds.listAttr(bshn + '.w', m=True)

        if not blendshape_names:
            warn_messages += ['  > No face blendshapes found on deformer {}.'.format(bshn)]
            continue

        for bs_name in blendshape_names:
            if bs_name not in valid_blendshape_names:
                continue

            if bs_name in existing_blendshapes:
                warn_msg = [
                    '  > Blendshape {} appears multiple times in different deformers.'.format(bs_name),
                    '  > Last one will be ignored.'
                ]
                if prevent_multi_shapes:
                    error_messages += warn_msg
                else:
                    warn_messages += warn_msg
                continue

            scene_data.face_blendshapes.append(bs_name)
            existing_blendshapes.append(bs_name)

    # asses valid found blendshapes
    if not scene_data.face_blendshapes:
        error_messages += [
            '  > No valid blendshapes! There are no blendshapes to apply animation data to.',
        ]
    else:
        # check for missing shapes from the full list
        if len(scene_data.face_blendshapes) < len(valid_blendshape_names):
            warn_msg = [
                '  > Some face blendshapes missing! Missing blendshapes may negatively impact facial animation quality.',
                '  > Please make sure missing blendshapes are left out intentionally.',
            ]
            warn_messages += warn_msg

    # Make sure that there are no other geometries with "_FACE" suffix.
    all_face_geo = []
    if scene_data.all_meshes:
        for mesh in scene_data.all_meshes:
            transform = cmds.listRelatives(mesh, parent=True, fullPath=True)[0]
            if transform.split('_')[-1] == 'FACE':
                all_face_geo.append(transform)

    if len(all_face_geo) > 1:
        error_messages += ['  > Multiple main face meshes!', '  > More than one mesh with the tag \"FACE\" detected.']

    # construct final message and status

    if error_messages:
        status = 'fail'
        message = ['>>> [ERROR] Face geometry check - FAIL.']
        message += error_messages

    elif warn_messages:
        status = 'warning'
        message = ['>>> [WARNING] Face geometry check warnings:']
        message += warn_messages

    else:
        status = 'pass'
        message = '>>> Face geometry check - PASS.'

    scene_data.validation_data['face_check'] = status
    return status, message


def materials_check(scene_data):
    """Collects and stores in scene_data all supported materials assigned to meshes
    stored in scene_data. If any mesh does not have a supported material assigned,
    the check will fail.
    The status for this check is stored in the scene_data object.
    Args:
        scene_data (CollectExportData): the object with the scene data already initialized.
    Returns:
        tuple(str, str): the result of the check, first status (fail|pass) the then the
            message explaining the status.
    """
    checked_materials = []
    all_messages = []
    scene_data.materials = []

    for mesh in scene_data.all_meshes:
        shading_groups = cmds.listConnections(mesh, type='shadingEngine') or None

        if shading_groups:
            for shading_group in shading_groups:
                material = cmds.listConnections('%s.surfaceShader' % shading_group) or [None]
                material = material[0]

                if material:
                    if material not in checked_materials:
                        checked_materials.append(material)
                        material_type = cmds.nodeType(material)

                        if material_type in static.material_attributes:
                            scene_data.materials.append(material)

                        else:
                            all_messages.append(
                                '  > Material \"{mat}\" is of type \"{t}\" which is not supported.'.format(
                                    mat=material, t=material_type
                                )
                            )

                else:
                    all_messages.append(
                        '  > Mesh \"{m}\" with the shading group \"{sg}\" has no material assinged.'.format(
                            m=mesh, sg=shading_group
                        )
                    )

        else:
            all_messages.append('  > Mesh \"{m}\" is missing a shading group and a material.'.format(m=mesh))

    if all_messages:
        status = 'fail'
        message = ['>>> [ERROR] Character materials type check - FAIL.']
        message += all_messages
        message.append('  > Please make sure that all geometries have the correct materials assigned.')

    else:
        status = 'pass'
        message = '>>> Character materials type check - PASS.'

    scene_data.validation_data['material_type_check'] = status
    return status, message


def material_connections_check(scene_data):
    """Goes through all materials defined in scene_data and check that the connection is
    supported. If any material has connected an unsupported node, the check will fail.
    The status for this check is stored in the scene_data object.
    Args:
        scene_data (CollectExportData): the object with the scene data already initialized.
    Returns:
        tuple(str, str): the result of the check, first status (fail|pass) the then the
            message explaining the status.
    Notes:
        Values for keys on scene_data.file_nodes are left as empty strings because they
            will be filled with the resolved textures on empty_file_nodes_check function.
    """
    all_messages = []

    for material in scene_data.materials:
        material_type = cmds.nodeType(material)

        for attr in static.material_attributes[material_type]:
            if attr in static.accepting_textures:
                input_connection = cmds.listConnections('{m}.{a}'.format(m=material, a=attr)) or None

                if input_connection:
                    connection_type = cmds.nodeType(input_connection[0])

                    if attr != 'normalCamera':
                        if connection_type == 'file' or connection_type == 'aiImage':
                            scene_data.file_nodes[input_connection[0]] = ''

                        else:
                            all_messages.append(
                                '  > Connection to \"{m}.{a}\" is not supported.'.format(m=material, a=attr)
                            )

                    else:
                        if connection_type in static.supported_bump_nodes:
                            bump_node_data = static.supported_bump_nodes[connection_type]
                            bump_input = (
                                cmds.listConnections(
                                    '{n}.{at}'.format(n=input_connection[0], at=bump_node_data['input_attr'])
                                )
                                or None
                            )

                            if bump_input:
                                input_type = cmds.nodeType(bump_input[0])

                                if input_type == 'file' or input_type == 'aiImage':
                                    scene_data.file_nodes[bump_input[0]] = ''

                                else:
                                    all_messages.append(
                                        '  > Connection to \"{m}\" bump node \"{b}.{a}\" is not supported.'.format(
                                            m=material, a=bump_node_data['input_attr'], b=input_connection[0]
                                        )
                                    )

                        else:
                            all_messages.append('  > Bump input to \"{m}\" is not supported.'.format(m=material))

    if all_messages:
        status = 'fail'
        message = ['>>> [ERROR] Material incoming connections check - FAIL.']
        message += all_messages
        message.append('  > Please make sure that only \"file\" or \"aiImage\" nodes are connected to materials.')

    else:
        status = 'pass'
        message = '>>> Material incoming connections check - PASS.'

    scene_data.validation_data['material_connections_check'] = status
    return status, message


def empty_file_nodes_check(scene_data):
    """Goes through all file nodes defined in scene_data and check that they have a valid
    texture file assigned. If any file node does not define a texture, the check will fail.
    The status for this check is stored in the scene_data object.
    Args:
        scene_data (CollectExportData): the object with the scene data already initialized.
    Returns:
        tuple(str, str): the result of the check, first status (fix|pass) the then the
            message explaining the status.
    Notes:
        Whether or not the assigned textures exist on disk will be checked in textures_check
            function.
    """
    all_messages = []

    if scene_data.file_nodes:
        for file_node in scene_data.file_nodes.keys():
            texture_path = utilities.get_texture_path(file_node)
            scene_data.file_nodes[file_node] = texture_path

            if not texture_path:
                all_messages.append('  > File node \"{}\" is missing a texture input.'.format(file_node))

    if all_messages:
        status = 'fix'
        message = ['>>> [ERROR] Empty file nodes check - FAIL.']
        message += all_messages
        message.append('  > Make sure that all \"file\" and \"aiImage\" nodes have textures loaded.')

    else:
        status = 'pass'
        message = '>>> Empty file nodes check - PASS.'

    scene_data.validation_data['file_nodes_check'] = status
    return status, message


def textures_check(scene_data):
    """Goes through all file nodes defined in scene_data and check that the file textures
    they have assigned exist on disk. If any file node has a texture that do not exist on disk,
    the check will fail. The status for this check is stored in the scene_data object.
    Args:
        scene_data (CollectExportData): the object with the scene data already initialized.
    Returns:
        tuple(str, str): the result of the check, first status (fail|pass) the then the
            message explaining the status.
    """
    all_messages = []

    supported_extensions_label = ", ".join(static.supported_textures)

    for file_node, texture_path in scene_data.file_nodes.items():
        if texture_path:
            for texture in texture_path:
                if not os.path.exists(texture):
                    all_messages.append(
                        '  > File node \"{fn}\" can\'t access the following texture: "{tex}"'.format(
                            fn=file_node, tex=texture
                        )
                    )

                if os.path.splitext(texture)[-1].lower() not in static.supported_textures:
                    all_messages.append(
                        '  > Format for texture \"{}\" is not supported.'.format(os.path.split(texture)[-1])
                    )

    if all_messages:
        status = 'fail'
        message = [
            '>>> [ERROR] Missing textures check - FAIL.',
            '  > Missing or unsupported texture files detected!',
            '  > Please provide all texture files used by the character in one of the supported file formats',
            '  > Supported file formats: {}'.format(supported_extensions_label),
        ]
        message += all_messages

    else:
        status = 'pass'
        message = '>>> Missing textures check - PASS.'

    scene_data.validation_data['textures_check'] = status
    return status, message


def groom_materials_check(scene_data):
    """Goes through all xgen interactive groom nodes in the scene making sure they have the
    supported material assigned (aiStandardHair). If there are xgen setup but without their
    corresponding interactive hair or the interactive hair has an unsupported shader, status
    will be a warning. If there are no xgen setups, the status will be skip. If all interactive
    grooms have supported shaders, the status will be pass. The status for this check is stored
    in the scene_data object.
    Args:
        scene_data (CollectExportData): the object with the scene data already initialized.
    Returns:
        tuple(str, str): the result of the check, first status (skip|warning|pass) the then the
            message explaining the status.
    """
    if utilities.xgen_check():
        ig_spline_bases = cmds.ls(type='xgmSplineBase') or None
        messages = []

        if ig_spline_bases:
            for spline_base in ig_spline_bases:
                interactive_groom = cmds.listConnections(
                    '{}.outSplineData'.format(spline_base), type='xgmSplineDescription'
                )[0]
                interactive_groom_shape = cmds.listRelatives(interactive_groom, type='xgmSplineDescription')[0]
                interactive_groom_sg = (
                    cmds.listConnections('{}.instObjGroups'.format(interactive_groom_shape), type='shadingEngine')
                    or None
                )
                material = cmds.listConnections('{}.surfaceShader'.format(interactive_groom_sg[0])) or None

                if material:
                    material_type = cmds.objectType(material[0])

                    if material_type != 'aiStandardHair':
                        msg = '  > Material \"{}\" is not supported. Only \"aiStandardHair\" materials are supported.'
                        messages.append(msg.format(material[0]))
                else:
                    msg = '  > \"{}\" has no material assigned. Make sure that all xGen descriptions '
                    msg += 'have \"aiStandardHair\" assigned to them."'
                    messages.append(msg.format(interactive_groom))

            if messages:
                status = 'warning'
                message = ['>>> [ERROR] XGen materials check - FAIL.']
                message += messages
                message.append('  > Make sure that all xGen descriptions have \"aiStandardHair\" assigned to them.')

            else:
                status = 'pass'
                message = '>>> XGen materials check - PASS.'

        else:
            status = 'warning'
            message = [
                '>>> No interactive grooms found - Skipping.',
                '  > All xGen descriptions need to be converted to Interactive Grooms before exporting.',
            ]

    else:
        status = 'skip'
        message = '>>> No xGen found in the scene - Skipping.'

    scene_data.validation_data['xGen_check'] = status
    return status, message
