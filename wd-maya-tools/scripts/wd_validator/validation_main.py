# Copyright 2025 Wonder Dynamics (an Autodesk Company)

# This source code is licensed under the GNU GPLv3
# found in the LICENSE file in the root directory of this source tree.

"""Module that holds the functions for executing the validation process.

To add a validation:
 - Define it static.validation_windows_data. The key you define there will
    be the identifier all through the process
 - Define a check in validation tools module
    See examples there
 - add the check in the flow of character_validation function
 - if fixes needed:
    - remember to flag it in the check with 'fix' or 'warning_fix'
    - define fix function in validation_fixes module
    - add it to the flow in gui.ValidationUI.fix_button

"""

import importlib

from wd_validator import validation_tools as validate, utilities, static

importlib.reload(validate)
importlib.reload(utilities)
importlib.reload(static)


def scene_validation(scene_data):
    """Runs the scene validation process and returns whether or not it succeeded. This
    validation runs before the character validation and is independent of it.
    Args:
        scene_data (CollectExportData): the object with the scene data already initialized.
    Returns:
        bool: whether or not the 'scene' validation passed.
    """
    # Checking if scene is saved
    scene_status, message = validate.scene_saved_check(scene_data)
    scene_data.gui_inst.update_status(val_type='scene_saved', status=scene_status)
    scene_data.gui_inst.update_script_output(message=message)

    # Checking if there are referenced files in the scene
    ref_status, message = validate.referenced_data_check(scene_data)
    scene_data.gui_inst.update_status(val_type='referenced_data', status=ref_status)
    scene_data.gui_inst.update_script_output(message=message)

    if scene_status == 'pass' and ref_status == 'pass':
        return True
    else:
        return False


def character_validation(scene_data, mode=static.VALIDATION_NORMAL):
    """Runs the character (full) validation process and if any of the validation fails it
    will abort the process and reflect this in the main UI.
    Args:
        scene_data (CollectExportData): the object with the scene data already initialized.
        mode (str): The mode the validation is running on. It can be either static.VALIDATION_NORMAL
            or static.VALIDATION_USD
    """
    # Checking if "GEO" group exists
    geo_status, message = validate.geo_group_check(scene_data)
    scene_data.gui_inst.update_status(val_type='geo_check', status=geo_status)
    scene_data.gui_inst.update_script_output(message=message)

    if geo_status == 'pass':
        # Checking the rig
        rig_status, message = validate.rig_check(scene_data, mode=mode)
        scene_data.gui_inst.update_status(val_type='rig_check', status=rig_status)
        scene_data.gui_inst.update_script_output(message=message)

        if rig_status in ['pass', 'warning_fix']:
            # Checking if rig group exists and is named correctly
            rig_grop_stat, message = validate.rig_group_check(scene_data)
            scene_data.gui_inst.update_status(val_type='rig_group_check', status=rig_grop_stat)
            scene_data.gui_inst.update_script_output(message=message)

            # Checking if geometries have construction history
            status, message = validate.history_check(scene_data)
            scene_data.gui_inst.update_status(val_type='history_check', status=status)
            scene_data.gui_inst.update_script_output(message=message)

            # Checking if all grp is ok
            all_status, all_message = validate.all_group_check(scene_data, mode=mode)
            scene_data.gui_inst.update_status(val_type='all_group_check', status=all_status)
            scene_data.gui_inst.update_script_output(message=all_message)

            if rig_grop_stat == 'pass':
                # Checking poly count
                status, message = validate.poly_count_check(scene_data)
                scene_data.gui_inst.update_status(val_type='poly_count_check', status=status)
                scene_data.gui_inst.update_script_output(message=message)

                # Checking retargeting data
                status, message = validate.retargeting_check(scene_data)
                scene_data.gui_inst.update_status(val_type='retargeting_check', status=status)
                scene_data.gui_inst.update_script_output(message=message)

                # Checking existance of IK joint chains
                ik_status, message = validate.rig_ik_check(scene_data)
                scene_data.gui_inst.update_status(val_type='ik_check', status=ik_status)
                scene_data.gui_inst.update_script_output(message=message)

                # Checking face setup
                status, message = validate.face_check(scene_data=scene_data)
                scene_data.gui_inst.update_status(val_type='face_check', status=status)
                scene_data.gui_inst.update_script_output(message=message)

                # Checking material types
                mat_status, message = validate.materials_check(scene_data)
                scene_data.gui_inst.update_status(val_type='material_type_check', status=mat_status)
                scene_data.gui_inst.update_script_output(message=message)

                if mat_status == 'pass':
                    # Checking if naming of objects isn't too long
                    status, message = validate.naming_check(scene_data)
                    scene_data.gui_inst.update_status(val_type='naming_check', status=status)
                    scene_data.gui_inst.update_script_output(message=message)

                    # Checking material incoming connections
                    status, message = validate.material_connections_check(scene_data)
                    scene_data.gui_inst.update_status(val_type='material_connections_check', status=status)
                    scene_data.gui_inst.update_script_output(message=message)

                    # Checking if there are empty file nodes
                    status, message = validate.empty_file_nodes_check(scene_data)
                    scene_data.gui_inst.update_status(val_type='file_nodes_check', status=status)
                    scene_data.gui_inst.update_script_output(message=message)

                    # Checking if there are missing textures
                    status, message = validate.textures_check(scene_data)
                    scene_data.gui_inst.update_status(val_type='textures_check', status=status)
                    scene_data.gui_inst.update_script_output(message=message)

                    # Checking the xGen materials
                    status, message = validate.groom_materials_check(scene_data)
                    scene_data.gui_inst.update_status(val_type='xGen_check', status=status)
                    scene_data.gui_inst.update_script_output(message=message)

                    scene_data.gui_inst.enable_export()

                else:
                    utilities.abort_validation(scene_data)
            else:
                utilities.abort_validation(scene_data)
        else:
            utilities.abort_validation(scene_data)
    else:
        utilities.abort_validation(scene_data)


def validation_run(scene_data, mode=static.VALIDATION_NORMAL):
    """Runs the full validation process.
    Args:
        scene_data (CollectExportData): the object with the scene data already initialized.
        mode (str): The mode the validation is running on. It can be either static.VALIDATION_NORMAL
            or static.VALIDATION_USD
    """
    scene_data.gui_inst.update_script_output(
        message='============================================================================='
    )
    scene_data.gui_inst.update_script_output(message='>>> Starting scene and character validation...')

    utilities.reset_validation_data(scene_data)


    scene_validation_status = scene_validation(scene_data)

    if scene_validation_status:
        scene_data.collect_data()
        # since metadata was reset, we need to add this value coming from the ui
        scene_data.metadata_json['usd'] = mode == static.VALIDATION_USD
        character_validation(scene_data, mode=mode)

    else:
        utilities.abort_validation(scene_data)
