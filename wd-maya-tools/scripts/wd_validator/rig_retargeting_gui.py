# Copyright 2023 Wonder Dynamics

# This source code is licensed under the GNU GPLv3
# found in the LICENSE file in the root directory of this source tree.

""" This module implements the ui and the related functionality for mapping joints in the maya
scene to bones in the expected skeleton for the Wonder Studio Character.
"""

import copy
import importlib
import webbrowser
from functools import partial

import maya.cmds as cmds

from wd_validator import static, utilities, validation_tools as validate

importlib.reload(static)
importlib.reload(utilities)
importlib.reload(validate)

# Maya mel interface will add arguments to callbacks in ui widgets
# that you need to catch somehow
# pylint: disable=unused-argument

# Code should be Python27 compatible
# pylint: disable=consider-using-f-string

retarget_fields_template = {
    'Head/Torso': ['Head', 'Neck', ['LeftShoulder', 'RightShoulder'], 'Spine', 'Spine1', 'Spine2', 'Hips'],
    'Arms': [['LeftArm', 'RightArm'], ['LeftForeArm', 'RightForeArm'], ['LeftHand', 'RightHand']],
    'Hands': [
        ['LeftHandIndex1', 'RightHandIndex1'],
        ['LeftHandIndex2', 'RightHandIndex2'],
        ['LeftHandIndex3', 'RightHandIndex3'],
        ['LeftHandMiddle1', 'RightHandMiddle1'],
        ['LeftHandMiddle2', 'RightHandMiddle2'],
        ['LeftHandMiddle3', 'RightHandMiddle3'],
        ['LeftHandPinky1', 'RightHandPinky1'],
        ['LeftHandPinky2', 'RightHandPinky2'],
        ['LeftHandPinky3', 'RightHandPinky3'],
        ['LeftHandRing1', 'RightHandRing1'],
        ['LeftHandRing2', 'RightHandRing2'],
        ['LeftHandRing3', 'RightHandRing3'],
        ['LeftHandThumb1', 'RightHandThumb1'],
        ['LeftHandThumb2', 'RightHandThumb2'],
        ['LeftHandThumb3', 'RightHandThumb3'],
    ],
    'Legs': [
        ['LeftUpLeg', 'RightUpLeg'],
        ['LeftLeg', 'RightLeg'],
        ['LeftFoot', 'RightFoot'],
        ['LeftToeBase', 'RightToeBase'],
    ],
}


class RigRetargetingUI(object):
    """Class that implements the UI and it's methods for mapping joints to
    bones in the Wonder Studio character.
    """

    def __init__(self, scene_data):
        """
        Args:
            scene_data (CollectExportData): the object holding the scene data.
        """
        self.window = 'rig_retargeting'
        self.title = 'Joint Mapping'
        self.width = 400

        self.scene_data = scene_data
        self.fileds_data = {}
        self.set_bones = []

        self.status_data = self.load_saved_fields('rig_status')
        self.mapping_dict = self.load_saved_fields('rig_mapping')

        for bone in self.mapping_dict.values():
            if bone:
                self.set_bones.append(bone)

        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

        window_size = (self.width, self.width)
        self.window = cmds.window(self.window, title=self.title, widthHeight=window_size, sizeable=True)

        # Main layout
        form = cmds.formLayout()

        separator_1 = cmds.separator(height=10, style='out')
        main_text = cmds.text(label=self.title, align='center')
        separator_2 = cmds.separator(height=10, style='in')
        status_text = cmds.text(label='Status:', align='center')

        # Status indicator
        status_start = 0
        status_lenght = int(100 / len(retarget_fields_template.keys()))
        status_layout = cmds.formLayout(numberOfDivisions=100, height=20)

        status_attach_position = []
        status_attach_form = []
        status_attach_control = []

        for tab in retarget_fields_template:
            status_icon = cmds.iconTextStaticLabel(style='iconOnly', image='wd_warning_16px.png', l=tab, height=20, width=20)
            stat_text = cmds.text(label=tab, align='left')

            self.status_data[tab] = {}
            self.status_data[tab]['icon'] = status_icon
            self.status_data[tab]['text'] = stat_text

            status_attach_form += [(stat_text, 'top', 5)]
            status_attach_control += [(stat_text, 'left', 5, status_icon)]
            status_attach_position += [(status_icon, 'left', 25, status_start)]

            status_start += status_lenght

        cmds.formLayout(
            status_layout,
            edit=True,
            attachPosition=status_attach_position,
            attachControl=status_attach_control,
            attachForm=status_attach_form,
        )
        cmds.setParent(form)

        # Tabs window
        tabs = cmds.tabLayout(
            innerMarginWidth=50, innerMarginHeight=50, scrollable=True, childResizable=True, height=400
        )

        cmds.formLayout(
            form,
            edit=True,
            attachForm=(
                (separator_1, 'left', 0),
                (separator_1, 'right', 0),
                (separator_1, 'top', 0),
                (main_text, 'left', 0),
                (main_text, 'right', 0),
                (separator_2, 'left', 0),
                (separator_2, 'right', 0),
                (status_text, 'left', 0),
                (status_text, 'right', 0),
                (status_layout, 'left', 0),
                (status_layout, 'right', 0),
                (tabs, 'left', 0),
                (tabs, 'right', 0),
            ),
            attachControl=(
                (main_text, 'top', 0, separator_1),
                (separator_2, 'top', 0, main_text),
                (status_text, 'top', 0, separator_2),
                (status_layout, 'top', 10, status_text),
                (tabs, 'top', 5, status_layout),
            ),
        )

        # Create tabs procedurally using retarget_filds_template dictionary
        all_tabs = []

        for tab_name, elements in retarget_fields_template.items():
            self.status_data[tab_name]['bones'] = []

            # Main tab layout
            tab_column = cmds.columnLayout(adjustableColumn=True)

            text_field = tab_name + ' bones:'
            cmds.separator(height=10, style='out')
            cmds.text(label=text_field, align='center')
            cmds.separator(height=10, style='in')

            # Adding bone fields
            for element_list in elements:
                if not isinstance(element_list, list):
                    element_list = [element_list]

                start_position = 0
                field_lenght = int(100 / len(element_list))
                field_layout = cmds.formLayout(numberOfDivisions=100, height=20)

                attach_form = []
                attach_control = []
                attach_position = []

                for i, element in enumerate(element_list):
                    self.status_data[tab_name]['bones'].append(element)

                    text = cmds.text(label=element + ':', align='left')
                    text_field = cmds.textField(enterCommand=partial(self.set_bone_field, element), aie=True)
                    button = cmds.iconTextButton(
                        label='+',
                        style='iconOnly',
                        image='wd_add_16px.png',
                        height=20,
                        width=20,
                        command=partial(self.set_bone_button, element),
                    )

                    attach_form += [
                        (text, 'left', 2),
                        (text, 'top', 5),
                        (text_field, 'top', 1),
                    ]
                    attach_control += [
                        (text_field, 'left', 2, text),
                        (text_field, 'right', 2, button),
                    ]
                    attach_position += [(text, 'left', 5, start_position)]

                    if i < len(element_list) - 1:
                        field_separator = cmds.separator(style='double', horizontal=False)

                        attach_form += [
                            (field_separator, 'right', 2),
                            (field_separator, 'top', 0),
                            (field_separator, 'bottom', 0),
                        ]
                        attach_control += [(button, 'right', 5, field_separator)]
                        attach_position += [(field_separator, 'right', 5, start_position + field_lenght)]

                    else:
                        attach_form += [(button, 'right', 2)]
                        attach_position += [(button, 'right', 5, start_position + field_lenght)]

                    start_position += field_lenght

                    self.fileds_data[element] = {}
                    self.fileds_data[element]['button'] = button
                    self.fileds_data[element]['text_field'] = text_field

                    # Apply saved data
                    if self.mapping_dict[element]:
                        if cmds.objExists(self.mapping_dict[element]):
                            cmds.textField(
                                text_field,
                                edit=True,
                                text=self.mapping_dict[element],
                                bgc=(0.18, 0.32, 0.18),
                            )
                            cmds.iconTextButton(
                                button,
                                edit=True,
                                style='iconOnly',
                                image='wd_subtract_16px.png',
                                command=partial(self.clear_bone, element),
                            )

                cmds.formLayout(
                    field_layout,
                    edit=True,
                    attachForm=attach_form,
                    attachControl=attach_control,
                    attachPosition=attach_position,
                )
                cmds.setParent(tab_column)
                cmds.separator(height=10)

            cmds.setParent(tabs)

            all_tabs.append([tab_column, tab_name])

        cmds.tabLayout(tabs, edit=True, tabLabel=all_tabs)
        cmds.setParent(form)

        # Controll buttons
        lower_separator_1 = cmds.separator(style='double')
        auto_fill_button = cmds.button(label='Auto Assign Bones', command=self.auto_resolve)
        reset_all_button = cmds.button(label='Reset All', command=self.clear_all_fields)
        help_button = cmds.button(label='Help', command=self.help)
        close_button = cmds.button(label='Close', command=self.close_window)

        lower_separator_2 = cmds.separator(height=10, style='out')
        version_text = cmds.text(label='Wonder Dynamics 2023', align='center')
        lower_separator_3 = cmds.separator(height=10, style='in')

        cmds.formLayout(
            form,
            edit=True,
            attachForm=(
                (lower_separator_1, 'left', 0),
                (lower_separator_1, 'right', 0),
                (auto_fill_button, 'left', 3),
                (auto_fill_button, 'right', 3),
                (reset_all_button, 'left', 3),
                (close_button, 'right', 3),
                (lower_separator_2, 'left', 0),
                (lower_separator_2, 'right', 0),
                (version_text, 'left', 0),
                (version_text, 'right', 0),
                (lower_separator_3, 'left', 0),
                (lower_separator_3, 'right', 0),
                (lower_separator_3, 'bottom', 0),
            ),
            attachControl=(
                (tabs, 'bottom', 2, lower_separator_1),
                (lower_separator_1, 'bottom', 2, auto_fill_button),
                (auto_fill_button, 'bottom', 2, reset_all_button),
                (reset_all_button, 'bottom', 0, lower_separator_2),
                (reset_all_button, 'right', 2, help_button),
                (help_button, 'bottom', 0, lower_separator_2),
                (help_button, 'right', 2, close_button),
                (close_button, 'bottom', 0, lower_separator_2),
                (lower_separator_2, 'bottom', 0, version_text),
                (version_text, 'bottom', 0, lower_separator_3),
            ),
            attachPosition=((help_button, 'left', 2, 33), (close_button, 'left', 2, 66)),
        )

        self.check_saved_fields()
        self.check_remapping_status(run_validation=False)

    def open_window(self, *args):
        """Shows the Retargeting Window on Maya interface."""
        cmds.showWindow(self.window)

    def close_window(self, *args):
        """Closes and deletes the Retargeting Window in Maya."""
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

    def load_saved_fields(self, key):
        """Returns data for key stored on maya file or an appropriate default if data not found.
        Args:
            key (str): the valid key names, 'rig_mapping' or 'rig_status'.
        Returns:
            dict or None: the requested data if it is a valid key name or None if the key is unknown.
        """
        if key == 'rig_mapping':
            if utilities.check_data(key):
                return utilities.read_data(key)

            else:
                bone_names = copy.deepcopy(static.metadata_template['body']['bone_names'])
                return bone_names

        if key == 'rig_status':
            if utilities.check_data(key):
                return utilities.read_data(key)

            else:
                return {}

    def check_saved_fields(self):
        """Updates the set_bones and mapping_dict member variables with only the valid bones.
        It also updates the bone field in ui if the bone does not exists and update iconTextButton
        command accordingly.
        """

        bones = []

        for key, bone in self.mapping_dict.items():
            if bone is not None and cmds.objExists(bone):
                bones.append(bone)

            else:
                self.mapping_dict[key] = None
                cmds.textField(self.fileds_data[key]['text_field'], edit=True, text='', bgc=(0.18, 0.18, 0.18))
                cmds.iconTextButton(
                    self.fileds_data[key]['button'],
                    edit=True,
                    style='iconOnly',
                    image='wd_add_16px.png',
                    height=20,
                    width=20,
                    command=partial(self.set_bone_button, key),
                )

        self.set_bones = bones
        utilities.write_data('rig_mapping', self.mapping_dict)

    def help(self, *args):
        """Opens in default webbrowser the documentation for retargeting."""
        webbrowser.open(static.documentation_links['retarget_docs'])

    def set_bone_button(self, key, *args):
        """Action command for bone button that takes joint selection and adds it to the ui and
        to the set_bone member variable with its role.
        Args:
            key (str): the joint role key, for example 'Hips' or 'Spine'.
        """
        selection = cmds.ls(sl=True, type='joint')

        if selection:
            if not len(selection) > 1:
                if selection[0] not in self.set_bones:
                    self.set_bone(key=key, bone=selection[0])
                    self.check_remapping_status()

                else:
                    cmds.warning('Bone already mapped.')

            else:
                cmds.warning('Make sure to select only one joint.')

        else:
            cmds.warning('Make sure to select the joint before assigning it.')

    def set_bone_field(self, key, text, *args):
        """Adds a bone to the ui field if it's valid, otherwise clears the field.
        Args:
            key (str): the bone role key.
            text (str): the bone candidate name.
        """
        joints = cmds.ls(type='joint')
        current_text = self.mapping_dict[key]

        if text:
            if text is not current_text:
                if text in joints:
                    if text not in self.set_bones:
                        self.set_bone(key=key, bone=text, replace=current_text)

                    else:
                        cmds.warning('Joint: {} is already set.'.format(text))
                        self.clear_bone(key=key)
                else:
                    cmds.warning('Object: {} is not of type \"joint\".'.format(text))
                    self.clear_bone(key=key)
        else:
            self.clear_bone(key=key)

        self.check_remapping_status()

    def set_bone(self, key, bone, replace=None, save=True):
        """Set a bone in the UI and in the set_bones member variable.
        Args:
            key (str): the bone role key.
            bone (str): the candidate bone name.
            replace (str, optional): a bone in the set_bones to remove when the bone is added. Defaults to None.
            save (bool, optional): Whether or not to persist the rig_mapping data in the maya file. Defaults to True.
        """
        text_field = self.fileds_data[key]['text_field']
        button = self.fileds_data[key]['button']

        cmds.textField(text_field, edit=True, text=bone, bgc=(0.18, 0.32, 0.18))
        cmds.iconTextButton(
            button, edit=True, style='iconOnly', image='wd_subtract_16px.png', command=partial(self.clear_bone, key)
        )

        self.mapping_dict[key] = bone

        if not replace:
            self.set_bones.append(bone)

        else:
            self.set_bones.remove(replace)
            self.set_bones.append(bone)

        if save:
            utilities.write_data('rig_mapping', self.mapping_dict)

    def clear_bone(self, key, check_status=True):
        """Removes the bone candidate in the UI and in the mapping dict and persist the
        rig_mapping data in the maya file.
        Args:
            key (str): the bone role key.
            check_status (bool, optional): Whether or not to run the remapping check status. Defaults to True.
        """
        current_text = self.mapping_dict[key]
        text_field = self.fileds_data[key]['text_field']
        button = self.fileds_data[key]['button']

        self.mapping_dict[key] = None

        if current_text in self.set_bones:
            self.set_bones.remove(current_text)

        cmds.textField(text_field, edit=True, text='', bgc=(0.18, 0.18, 0.18))
        cmds.iconTextButton(
            button,
            edit=True,
            style='iconOnly',
            image='wd_add_16px.png',
            height=20,
            width=20,
            command=partial(self.set_bone_button, key),
        )

        utilities.write_data('rig_mapping', self.mapping_dict)

        if check_status:
            self.check_remapping_status()

    def clear_all_fields(self, *args):
        """Clear all bone mapping fields and update the status validation accordingly."""
        for bone in self.mapping_dict.keys():
            self.clear_bone(key=bone, check_status=False)

        self.check_remapping_status()

    def check_remapping_status(self, run_validation=True):
        """Check that all bones are mapped and update the icons accordingly.
        Also, the rig status is persisted in the maya scene. Optionally, it
        also runs the rig remap validation.
        Args:
            run_validation (bool, optional): whether or not to run the rig remap validation.
                Defaults to True.
        """
        for key, data in self.status_data.items():
            icon = self.status_data[key]['icon']
            cmds.iconTextStaticLabel(icon, edit=True, image='wd_check_16px.png')

            self.status_data[key]['status'] = 'pass'

            for bone in data['bones']:
                if not self.mapping_dict[bone]:
                    cmds.iconTextStaticLabel(icon, edit=True, image='wd_warning_16px.png')
                    self.status_data[key]['status'] = 'warning'
                    break

        utilities.write_data('rig_status', self.status_data)

        if run_validation:
            self.validate_rig_remapping()

    def auto_resolve(self, *args, any_map=False):
        """Auto select the bones for retargeting based on templates defined in static file
        and set them in the ui and class data.
        Args:
            *args: Something to catch the arguments Maya Mel widgets add to callbacks
            any_map (bool): whether or not to match names from any template. Optional,
                defaults to False so it matches the behavior on Blender Add-on.
        """
        func = self.auto_resolve_any_map if any_map else self.auto_resolve_single_template
        return func()

    def auto_resolve_any_map(self):
        """Auto select the bones for retargeting based on templates defined in static file
        and set them in the ui and class data.
        Notes:
            Can match bones from different templates.
        """

        # check we have valid data
        if not cmds.objExists(self.scene_data.rig_selection):
            msg = '  > Could not find root joint {}. Please re run validation to update data'
            msg = msg.format(self.scene_data.rig_selection)
            print(msg)
            return

        all_joints = [self.scene_data.rig_selection]
        all_joints += cmds.listRelatives(all_joints[0], type='joint', ad=True)

        for joint in all_joints:
            base_name = joint.split(':')[-1]

            for key, template_joints in static.retargeting_templates.items():
                if base_name in template_joints:
                    self.set_bone(key=key, bone=joint, save=False)
                    break

        utilities.write_data('rig_mapping', self.mapping_dict)
        self.check_remapping_status()

    def auto_resolve_single_template(self):
        """Auto select the bones for retargeting based on templates defined in static file
        and set them in the ui and class data. Only one template can be used, and to define
        the template, first it will check the hip, and if the hip does not conform, it will
        check all bones to find the most popular template among bones.
        """

        all_joints = [self.scene_data.rig_selection]
        all_joints += cmds.listRelatives(all_joints[0], type='joint', ad=True)

        def get_hip_bone():
            """Find Hip bone"""
            rig_sel = self.scene_data.rig_selection.split(':')[-1]
            # check if rig selection is a hip bone
            if rig_sel in static.retargeting_templates['Hips']:
                return rig_sel
            # if not try to find the hip bone
            for jnt in all_joints:
                jnt_split = jnt.split(':')[-1]
                if jnt_split in static.retargeting_templates['Hips']:
                    return jnt_split
            return None

        def get_naming_index_from_hip():
            """Get the template from guessing the Hip"""
            hip_templates = static.retargeting_templates['Hips']
            hip = get_hip_bone()
            for index, value in enumerate(hip_templates):
                if value == hip:
                    return index
            return -1

        # check we have valid data
        if not cmds.objExists(self.scene_data.rig_selection):
            msg = 'Could not find root joint {}. Please re run validation to update data'
            msg = msg.format(self.scene_data.rig_selection)
            print(msg)
            return

        # get template from hip and check it is valid
        index = get_naming_index_from_hip()

        if index == -1:
            msg = 'Could not guess template from Hip bone {}'.format(self.scene_data.rig_selection)
            print(msg)
            return

        template_name = static.retargeting_templates_names[index]
        msg = '\nDiscovering Bones based on {} naming...\n'.format(template_name)

        rev_map = {v[index]: k for k, v in static.retargeting_templates.items()}
        for joint in all_joints:
            base_name = joint.split(':')[-1]
            key = rev_map.get(base_name)
            if not key:
                # case where the bone has an unknown name for this template
                continue
            self.set_bone(key=key, bone=joint, save=False)

        utilities.write_data('rig_mapping', self.mapping_dict)
        self.check_remapping_status()

    def validate_rig_remapping(self):
        """Validates the data in the UI for retargeting and update status accordingly.
        Also enables the export button based on status.
        """
        status, message = validate.retargeting_check(self.scene_data)
        self.scene_data.gui_inst.update_status(val_type='retargeting_check', status=status)
        self.scene_data.gui_inst.update_script_output(message=message)
        self.scene_data.gui_inst.enable_export()
