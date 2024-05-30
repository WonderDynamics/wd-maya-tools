# Copyright 2023 Wonder Dynamics

# This source code is licensed under the GNU GPLv3
# found in the LICENSE file in the root directory of this source tree.

"""Module for the Eye Rotations UI."""

import importlib
import webbrowser
from functools import partial

import maya.cmds as cmds

from wd_validator import static, utilities

importlib.reload(static)
importlib.reload(utilities)


# Maya mel interface will add arguments to callbacks in ui widgets
# that you need to catch somehow
# pylint: disable=unused-argument

# Code should be Python27 compatible
# pylint: disable=consider-using-f-string


class EyeRotationsUI(object):
    """Class that creates the Eye Rotations UI and handles updates, validation and persistency of it's data."""

    def __init__(self, scene_data):
        self.window = 'eye_rotations'
        self.title = 'Eye Bone Mapping'
        self.width = 400

        self.scene_data = scene_data

        self.mapping_dict = {}
        self.body_bones = []

        self.update_body_bones()

        self.set_bones = []

        self.eyes_data = self.load_saved_data(key='eyes_mapping')

        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

        window_size = (self.width, int(self.width * 1.5))
        self.window = cmds.window(self.window, title=self.title, widthHeight=window_size, sizeable=False)

        self.form = cmds.formLayout(numberOfDivisions=100, width=self.width)

        separator_1 = cmds.separator(height=10, style='out')
        main_text = cmds.text(label=self.title, align='center')
        separator_2 = cmds.separator(height=10, style='in')
        assign_bone_text = cmds.text(label='Assign Eye Bones:', align='center')
        separator_3 = cmds.separator(height=10, style='out')
        add_bone_button = cmds.button(label='Add Eye Bone', command=self.generate_mapping_controls)

        self.scroll_layout = cmds.scrollLayout(
            backgroundColor=(0.18, 0.18, 0.18), width=self.width - 15, verticalScrollBarAlwaysVisible=True
        )

        cmds.setParent(self.form)

        lower_separator_1 = cmds.separator(style='double')
        help_button = cmds.button(label='Help', command=self.open_help)
        close_button = cmds.button(label='Close', command=self.close_window)
        lower_separator_2 = cmds.separator(height=10, style='out')
        version_text = cmds.text(label='Wonder Dynamics', align='center')
        lower_separator_3 = cmds.separator(height=10, style='in')

        cmds.formLayout(
            self.form,
            edit=True,
            attachForm=(
                (separator_1, 'left', 0),
                (separator_1, 'right', 0),
                (separator_1, 'top', 0),
                (main_text, 'left', 0),
                (main_text, 'right', 0),
                (separator_2, 'left', 0),
                (separator_2, 'right', 0),
                (assign_bone_text, 'left', 0),
                (assign_bone_text, 'right', 0),
                (separator_3, 'left', 0),
                (separator_3, 'right', 0),
                (self.scroll_layout, 'left', 0),
                (self.scroll_layout, 'right', 0),
                (lower_separator_1, 'left', 0),
                (lower_separator_1, 'right', 0),
                (help_button, 'left', 3),
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
                (main_text, 'top', 0, separator_1),
                (separator_2, 'top', 0, main_text),
                (assign_bone_text, 'top', 10, separator_2),
                (separator_3, 'top', 0, assign_bone_text),
                (add_bone_button, 'top', 8, assign_bone_text),
                (self.scroll_layout, 'top', 2, add_bone_button),
                (self.scroll_layout, 'bottom', 2, lower_separator_1),
                (lower_separator_1, 'bottom', 3, help_button),
                (help_button, 'bottom', 0, lower_separator_2),
                (help_button, 'right', 3, close_button),
                (close_button, 'bottom', 0, lower_separator_2),
                (lower_separator_2, 'bottom', 0, version_text),
                (version_text, 'bottom', 0, lower_separator_3),
            ),
            attachPosition=(
                (add_bone_button, 'left', 0, 25),
                (add_bone_button, 'right', 0, 75),
                (close_button, 'left', 3, 50),
            ),
        )

        cmds.setParent(self.scroll_layout)

        self.check_saved_data()

        if not self.eyes_data:
            self.generate_mapping_controls()

        else:
            data = self.eyes_data
            self.eyes_data = {}

            for values in data.values():
                self.set_bones.append(values['bone_field_value'])
                self.generate_mapping_controls(stored_data=values)

    def open_window(self, *args):
        """Opens the Eye Rotation UI."""
        cmds.showWindow(self.window)

    def close_window(self, *args):
        """Closes and deletes the Eye Rotation UI."""
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

    def generate_mapping_controls(self, *args, stored_data=None):
        """Creates the UI component for a single eye UI, set its values (if stored_data is
        passed) and persists the values in scene with fileInfo. Buttons enabled state are updated too.
        Args:
            stored_data (dict, optional): The values to set on the eye ui. The key names are taken from
                static.eye_values. Defaults to setting no data.
        """
        eye_ctrl_form = cmds.formLayout(
            numberOfDivisions=100, parent=self.scroll_layout, width=self.width - 15, height=170
        )

        separator = cmds.separator(height=10, style='in')

        bone_name_text = cmds.text(label='Eye Bone Name:', align='right')
        bone_name_field = cmds.textField(editable=False)
        bone_add_button = cmds.iconTextButton(
            label='+',
            style='iconOnly',
            image='wd_add_16px.png',
            height=20,
            width=20,
            command=partial(self.add_bone, eye_ctrl_form),
        )

        middle_separator_1 = cmds.separator(height=5)

        horizontal_axis_text = cmds.text(label='Horizontal Axis:', align='right')
        horizontal_axis_menu = cmds.optionMenu(
            w=96,
            backgroundColor=(0.365, 0.365, 0.365),
            changeCommand=partial(self.set_axis, eye_ctrl_form, 'horizontal_axis_menu', 'horizontal_axis_menu_value'),
        )
        cmds.menuItem(label='Y')
        cmds.menuItem(label='X')
        cmds.menuItem(label='Z')

        look_left_text = cmds.text(label='Look Left:', align='right')
        look_left_field = cmds.textField(
            editable=True,
            aie=True,
            enterCommand=partial(self.set_value_field, eye_ctrl_form, 'horizontal_min_field', 'horizontal_axis_menu'),
        )
        look_left_button = cmds.button(
            label='Set',
            backgroundColor=(0.365, 0.365, 0.365),
            height=18,
            enable=False,
            command=partial(self.set_value_button, eye_ctrl_form, 'horizontal_min_field', 'horizontal_axis_menu'),
        )
        look_right_text = cmds.text(label='Look Right:', align='right')
        look_right_field = cmds.textField(
            editable=True,
            aie=True,
            enterCommand=partial(self.set_value_field, eye_ctrl_form, 'horizontal_max_field', 'horizontal_axis_menu'),
        )
        look_right_button = cmds.button(
            label='Set',
            backgroundColor=(0.365, 0.365, 0.365),
            height=18,
            enable=False,
            command=partial(self.set_value_button, eye_ctrl_form, 'horizontal_max_field', 'horizontal_axis_menu'),
        )

        middle_separator_2 = cmds.separator(height=5)

        vertical_axis_text = cmds.text(label='Vertical Axis:', align='right')
        vertical_axis_menu = cmds.optionMenu(
            w=96,
            backgroundColor=(0.365, 0.365, 0.365),
            changeCommand=partial(self.set_axis, eye_ctrl_form, 'vertical_axis_menu', 'vertical_axis_menu_value'),
        )
        cmds.menuItem(label='Z')
        cmds.menuItem(label='Y')
        cmds.menuItem(label='X')

        look_down_text = cmds.text(label='Look Down:', align='right')
        look_down_field = cmds.textField(
            editable=True,
            aie=True,
            enterCommand=partial(self.set_value_field, eye_ctrl_form, 'vertical_min_field', 'vertical_axis_menu'),
        )
        look_down_button = cmds.button(
            label='Set',
            backgroundColor=(0.365, 0.365, 0.365),
            height=18,
            enable=False,
            command=partial(self.set_value_button, eye_ctrl_form, 'vertical_min_field', 'vertical_axis_menu'),
        )
        look_up_text = cmds.text(label='Look Up:', align='right')
        look_up_field = cmds.textField(
            editable=True,
            aie=True,
            enterCommand=partial(self.set_value_field, eye_ctrl_form, 'vertical_max_field', 'vertical_axis_menu'),
        )
        look_up_button = cmds.button(
            label='Set',
            backgroundColor=(0.365, 0.365, 0.365),
            height=18,
            enable=False,
            command=partial(self.set_value_button, eye_ctrl_form, 'vertical_max_field', 'vertical_axis_menu'),
        )

        middle_separator_3 = cmds.separator(height=5)

        status_text = cmds.text(
            label='Status:',
            align='right',
        )
        stauts_icon = cmds.iconTextStaticLabel(
            style='iconOnly', image='wd_failed_16px.png', height=20, width=20, parent=eye_ctrl_form
        )
        remove_button = cmds.button(label='Remove', command=partial(self.remove_mapping_control, eye_ctrl_form))

        lower_separator = cmds.separator(height=10, style='out')

        attach_form = (
            (separator, 'left', 0),
            (separator, 'right', 0),
            (bone_name_text, 'left', 0),
            (bone_add_button, 'right', 3),
            (middle_separator_1, 'left', 0),
            (middle_separator_1, 'right', 0),
            (horizontal_axis_text, 'left', 0),
            (look_left_text, 'left', 0),
            (look_right_button, 'right', 3),
            (middle_separator_2, 'left', 0),
            (middle_separator_2, 'right', 0),
            (vertical_axis_text, 'left', 0),
            (look_down_text, 'left', 0),
            (look_up_button, 'right', 3),
            (middle_separator_3, 'left', 0),
            (middle_separator_3, 'right', 0),
            (remove_button, 'right', 0),
            (status_text, 'left', 0),
            (lower_separator, 'left', 0),
            (lower_separator, 'right', 0),
        )

        attach_control = (
            (bone_name_text, 'right', 3, bone_name_field),
            (bone_name_text, 'top', 3, separator),
            (bone_name_field, 'right', 2, bone_add_button),
            (bone_name_field, 'top', 0, separator),
            (bone_add_button, 'top', 0, separator),
            (middle_separator_1, 'top', 5, bone_name_text),
            (horizontal_axis_text, 'top', 5, middle_separator_1),
            (horizontal_axis_text, 'right', 3, horizontal_axis_menu),
            (horizontal_axis_menu, 'top', 2, middle_separator_1),
            (look_left_text, 'top', 8, horizontal_axis_text),
            (look_left_text, 'right', 3, look_left_field),
            (look_left_field, 'top', 5, horizontal_axis_text),
            (look_left_field, 'right', 0, look_left_button),
            (look_left_button, 'top', 5, horizontal_axis_text),
            (look_left_button, 'right', 0, look_right_text),
            (look_right_text, 'top', 8, horizontal_axis_text),
            (look_right_text, 'right', 3, look_right_field),
            (look_right_field, 'top', 5, horizontal_axis_text),
            (look_right_field, 'right', 0, look_right_button),
            (look_right_button, 'top', 5, horizontal_axis_text),
            (middle_separator_2, 'top', 5, look_left_text),
            (vertical_axis_text, 'top', 5, middle_separator_2),
            (vertical_axis_text, 'right', 3, vertical_axis_menu),
            (vertical_axis_menu, 'top', 2, middle_separator_2),
            (look_down_text, 'top', 8, vertical_axis_text),
            (look_down_text, 'right', 3, look_down_field),
            (look_down_field, 'top', 5, vertical_axis_text),
            (look_down_field, 'right', 0, look_down_button),
            (look_down_button, 'top', 5, vertical_axis_text),
            (look_down_button, 'right', 0, look_up_text),
            (look_up_text, 'top', 8, vertical_axis_text),
            (look_up_text, 'right', 3, look_up_field),
            (look_up_field, 'top', 5, vertical_axis_text),
            (look_up_field, 'right', 0, look_up_button),
            (look_up_button, 'top', 5, vertical_axis_text),
            (middle_separator_3, 'top', 5, look_down_text),
            (status_text, 'top', 8, middle_separator_3),
            (status_text, 'right', 3, stauts_icon),
            (stauts_icon, 'top', 4, middle_separator_3),
            (stauts_icon, 'right', 20, remove_button),
            (remove_button, 'top', 2, middle_separator_3),
            (lower_separator, 'top', 0, remove_button),
        )

        attach_position = (
            (bone_name_field, 'left', 0, 25),
            (horizontal_axis_menu, 'left', 0, 25),
            (look_left_field, 'left', 0, 17),
            (look_right_field, 'left', 0, 67),
            (look_right_text, 'left', 0, 50),
            (vertical_axis_menu, 'left', 0, 25),
            (look_down_field, 'left', 0, 17),
            (look_up_field, 'left', 0, 67),
            (look_up_text, 'left', 0, 50),
            (remove_button, 'left', 0, 50),
            (remove_button, 'right', 0, 75),
        )

        cmds.formLayout(
            eye_ctrl_form,
            edit=True,
            attachForm=attach_form,
            attachControl=attach_control,
            attachPosition=attach_position,
        )

        self.top_element = lower_separator

        self.eyes_data[eye_ctrl_form] = {}
        self.eyes_data[eye_ctrl_form]['bone_field'] = bone_name_field
        self.eyes_data[eye_ctrl_form]['bone_field_value'] = None
        self.eyes_data[eye_ctrl_form]['bone_button'] = bone_add_button

        self.eyes_data[eye_ctrl_form]['horizontal_axis_menu'] = horizontal_axis_menu
        self.eyes_data[eye_ctrl_form]['horizontal_axis_menu_value'] = cmds.optionMenu(
            horizontal_axis_menu, query=True, value=True
        )
        self.eyes_data[eye_ctrl_form]['horizontal_min_field'] = look_left_field
        self.eyes_data[eye_ctrl_form]['horizontal_min_field_value'] = None
        self.eyes_data[eye_ctrl_form]['horizontal_min_button'] = look_left_button
        self.eyes_data[eye_ctrl_form]['horizontal_max_field'] = look_right_field
        self.eyes_data[eye_ctrl_form]['horizontal_max_field_value'] = None
        self.eyes_data[eye_ctrl_form]['horizontal_max_button'] = look_right_button

        self.eyes_data[eye_ctrl_form]['vertical_axis_menu'] = vertical_axis_menu
        self.eyes_data[eye_ctrl_form]['vertical_axis_menu_value'] = cmds.optionMenu(
            vertical_axis_menu, query=True, value=True
        )
        self.eyes_data[eye_ctrl_form]['vertical_min_field'] = look_down_field
        self.eyes_data[eye_ctrl_form]['vertical_min_field_value'] = None
        self.eyes_data[eye_ctrl_form]['vertical_min_button'] = look_down_button
        self.eyes_data[eye_ctrl_form]['vertical_max_field'] = look_up_field
        self.eyes_data[eye_ctrl_form]['vertical_max_field_value'] = None
        self.eyes_data[eye_ctrl_form]['vertical_max_button'] = look_up_button

        self.eyes_data[eye_ctrl_form]['status_icon'] = stauts_icon

        if stored_data:
            for value, field in static.eye_values.items():
                if value in stored_data:
                    if field.split('_')[-1] != 'menu':
                        try:
                            field_value = round(stored_data[value], 3)
                        except TypeError:
                            field_value = stored_data[value]

                        cmds.textField(self.eyes_data[eye_ctrl_form][field], edit=True, text=field_value)

                    else:
                        cmds.optionMenu(self.eyes_data[eye_ctrl_form][field], edit=True, value=stored_data[value])

                    self.eyes_data[eye_ctrl_form][value] = stored_data[value]

            # Check buttons
            for key in self.eyes_data[eye_ctrl_form].keys():
                if key.split('_')[-1] == 'button':
                    field_key = '_'.join(key.split('_')[:-1]) + '_field'
                    field_value_key = '_'.join(key.split('_')[:-1]) + '_field_value'

                    if self.eyes_data[eye_ctrl_form][field_value_key] is not None:
                        if key != 'bone_button':
                            axis_key = '_'.join(key.split('_')[:-2]) + '_axis_menu'

                            cmds.button(
                                self.eyes_data[eye_ctrl_form][key],
                                edit=True,
                                label='Del',
                                command=partial(
                                    self.clear_value,
                                    eye_ctrl_form,
                                    field_key,
                                    self.eyes_data[eye_ctrl_form][key],
                                    axis_key,
                                ),
                            )

                        else:
                            cmds.iconTextButton(
                                self.eyes_data[eye_ctrl_form]['bone_button'],
                                edit=True,
                                image='wd_subtract_16px.png',
                                command=partial(self.remove_bone, eye_ctrl_form),
                            )

            self.check_status(key=eye_ctrl_form)
            utilities.write_data('eyes_mapping', self.eyes_data)

        self.enable_inputs(key=eye_ctrl_form)

    def remove_mapping_control(self, layout, *args):
        """Removes the form for one eye from the Eye Rotations UI.
        Args:
            layout (str): the name of this eye form.
        """
        if layout in self.eyes_data:
            if self.eyes_data[layout]['bone_field_value']:
                try:
                    self.set_bones.remove(self.eyes_data[layout]['bone_field_value'])
                except Exception:
                    print('Bone already removed from list.')

            self.eyes_data.pop(layout)

        cmds.deleteUI(layout, layout=True)

        utilities.write_data('eyes_mapping', self.eyes_data)

    def add_bone(self, form_key, *args):
        """Adds a bone to the name field in eye form. Also persists the eye data
        in the file and updates the enable state in the buttons of the form.
        Args:
            form_key (str): the name of this eye form.
        """
        # Check if rig is mapped
        rig_mapping = utilities.read_data('rig_mapping')
        if not rig_mapping:
            cmds.warning('Make sure to map all joints first before mapping eye rotations.')
            return

        # Check if hips are mapped
        if rig_mapping['Hips'] == None:
            cmds.warning('Make sure to map all joints first before mapping eye rotations.')
            return

        # Check selection
        selection = cmds.ls(sl=True, type='joint')

        if not selection:
            cmds.warning('Make sure to select the joint before assigning it.')
            return

        if len(selection) > 1:
            cmds.warning('Make sure to select only one joint.')
            return

        # Check that we are not using any skel name for an eye joint
        skel_names = []
        for values in static.retargeting_templates.values():
            skel_names.extend(values)

        joint_short_name = selection[0].split('|')[-1]
        if joint_short_name in skel_names:  # skel names have are always shortnames
            cmds.warning('Make sure to avoid using names common in skeletons. See list in script editor')
            print('\nAvoid using the following names for Eye joints:')
            for i, name in enumerate(sorted(skel_names)):
                if i % 5 == 0:
                    print()
                print('{:20}'.format(name), end='')
            return

        # update body bones to have an updated list of currently assigned bones
        # and be able to avoid double assignment
        self.update_body_bones()
        if selection[0] in self.body_bones:
            cmds.warning('Make sure to select bones that are not already mapped to the body.')
            return

        # Check if joint belongs to the rig
        all_rig_joints = [jnt.split('|')[-1] for jnt in cmds.listRelatives(self.scene_data.rig_selection, ad=True)]
        if joint_short_name not in all_rig_joints:
            cmds.warning('Make sure that the selected joint belongs to the rig.')
            return

        # Make sure to avoid same bone assignment
        if selection[0] in self.set_bones:
            cmds.warning('Eye bone already assigned.')
            return

        self.eyes_data[form_key]['bone_field_value'] = selection[0]
        self.set_bones.append(selection[0])

        bone_field = self.eyes_data[form_key]['bone_field']
        cmds.textField(bone_field, edit=True, text=selection[0])
        cmds.iconTextButton(
            self.eyes_data[form_key]['bone_button'],
            edit=True,
            image='wd_subtract_16px.png',
            command=partial(self.remove_bone, form_key),
        )

        utilities.write_data('eyes_mapping', self.eyes_data)
        self.enable_inputs(key=form_key)

    def remove_bone(self, form_key, *args):
        """Removes a bone added to eye form. Also persists the current eye info, enables buttons based
        on status and check the validity of all the eye data so far, reflecting it in the UI.
        Args:
            form_key (str): the name of this eye form.
        """
        cmds.textField(self.eyes_data[form_key]['bone_field'], edit=True, text='')
        cmds.iconTextButton(
            self.eyes_data[form_key]['bone_button'],
            edit=True,
            image='wd_add_16px.png',
            command=partial(self.add_bone, form_key),
        )

        if self.eyes_data[form_key]['bone_field_value']:
            try:
                self.set_bones.remove(self.eyes_data[form_key]['bone_field_value'])
            except Exception:
                print('Bone already removed from list.')

        self.eyes_data[form_key]['bone_field_value'] = None
        utilities.write_data('eyes_mapping', self.eyes_data)
        self.enable_inputs(key=form_key)
        self.check_status(key=form_key)

    def update_body_bones(self):
        """Updates the cache of currenlty used bones. The body bones property is used when trying
        to prevent a joint to be used multiple time.
        """
        self.mapping_dict = utilities.read_data('rig_mapping') or {}
        self.body_bones = []

        for joint in self.mapping_dict.values():
            if not joint:
                continue
            self.body_bones.append(joint)

    def set_value_button(self, form_key, field_key, axis_key, *args):
        """Sets the look value for an eye in an axis based on the current value of the joint
        in the form text field. This is the callback called when clicking the 'Set' button.
        Args:
            form_key (str): the name of the eye form.
            field_key (str): the key holding the name of the field where the number should be set.
            axis_key (str): the key holding the name of the option menu defining the XYZ axis of the object
                to take into account for setting the value field.
        """
        eye_bone = self.eyes_data[form_key]['bone_field_value']
        text_field = self.eyes_data[form_key][field_key]
        axis_menu = self.eyes_data[form_key][axis_key]
        button = self.eyes_data[form_key]['_'.join(['button' if i == 'field' else i for i in field_key.split('_')])]

        set_axis = cmds.optionMenu(axis_menu, query=True, value=True)
        rotation = cmds.getAttr('{bone}.rotate{axis}'.format(bone=eye_bone, axis=set_axis.upper()))

        other_field_value = field_key.split('_')
        other_field_value = ['max' if item == 'min' else 'min' if item == 'max' else item for item in other_field_value]
        other_field_value = '_'.join(other_field_value) + '_value'

        if self.eyes_data[form_key][other_field_value] != rotation:
            cmds.textField(text_field, edit=True, text=round(rotation, 3))
            self.eyes_data[form_key][field_key + '_value'] = rotation
            cmds.button(
                button, edit=True, label='Del', command=partial(self.clear_value, form_key, field_key, button, axis_key)
            )

        else:
            cmds.warning('Min and Max values for the eyes must be different!')
            cmds.textField(text_field, edit=True, text='')

        utilities.write_data('eyes_mapping', self.eyes_data)
        self.check_status(key=form_key)

    def set_value_field(self, form_key, field_key, axis_key, *args):
        """Sets the look value for an eye in an axis based on the current value of the look text field.
        This is the callback called when hitting enter in the look field.
        Args:
            form_key (str): the name of the eye form.
            field_key (str): the key holding the name of the field where the number should be set.
            axis_key (str): the key holding the name of the option menu defining the XYZ axis of the object
                to take into account for setting the value field.
        """
        text_field = self.eyes_data[form_key][field_key]
        button = self.eyes_data[form_key]['_'.join(['button' if i == 'field' else i for i in field_key.split('_')])]

        rotation = cmds.textField(text_field, query=True, text=True)

        try:
            rotation = float(rotation)

            other_field_value = field_key.split('_')
            other_field_value = [
                'max' if item == 'min' else 'min' if item == 'max' else item for item in other_field_value
            ]
            other_field_value = '_'.join(other_field_value) + '_value'

            if self.eyes_data[form_key][other_field_value] != rotation:
                self.eyes_data[form_key][field_key + '_value'] = rotation
                cmds.button(
                    button,
                    edit=True,
                    label='Del',
                    command=partial(self.clear_value, form_key, field_key, button, axis_key),
                )

            else:
                cmds.warning('Min and Max values for the eyes must be different!')
                cmds.textField(text_field, edit=True, text='')

        except ValueError:
            cmds.warning('Please enter only numbers.')
            cmds.textField(text_field, edit=True, text='')

        utilities.write_data('eyes_mapping', self.eyes_data)
        self.check_status(key=form_key)

    def set_axis(self, form_key, menu_key, value_key, *args):
        """Callback on the optionMenu for the axis that check if the this axis is different from
        the other axis in this eye, and if it is the same, it warns the user and reverts the change.
        The value of the axis is persisted in the scene.
        Args:
            form_key (str): the name of the eye form.
            menu_key (str): the key holding the name of the option menu where the axis is set.
            value_key (str): the axis key, can be either 'vertical_axis_menu_value' or
                'horizontal_axis_menu_value'.
        """
        other_axis = (
            'vertical_axis_menu_value' if value_key == 'horizontal_axis_menu_value' else 'horizontal_axis_menu_value'
        )
        axis = cmds.optionMenu(self.eyes_data[form_key][menu_key], query=True, value=True)

        if self.eyes_data[form_key][other_axis] != axis:
            self.eyes_data[form_key][value_key] = axis

        else:
            cmds.optionMenu(self.eyes_data[form_key][menu_key], edit=True, value=self.eyes_data[form_key][value_key])
            message = 'Horizontal and vartical axes can\'t be the same!'
            cmds.warning(message)
            cmds.confirmDialog(title='Warning', message=message, button=['OK'], defaultButton='OK', cancelButton='OK')

        utilities.write_data('eyes_mapping', self.eyes_data)

    def clear_value(self, form_key, field_key, button, axis_key, *args):
        """Callback for when clicking the 'Del' button in the look section.
        This will remove the value from the field, persist the update on
        the maya scene and update the status for this eye.
        Args:
            form_key (str): the name of the from being cleared.
            field_key (str): the key that holds the name of the field with the value to clear.
            button (str): the name of the button that will be converted from 'Del' to 'Set'.
            axis_key (str): the key holding the name of the option menu defining the XYZ axis of the object.
        """
        cmds.textField(self.eyes_data[form_key][field_key], edit=True, text='')
        cmds.button(
            button, edit=True, label='Set', command=partial(self.set_value_button, form_key, field_key, axis_key)
        )

        self.eyes_data[form_key][field_key + '_value'] = None

        utilities.write_data('eyes_mapping', self.eyes_data)

        self.check_status(key=form_key)

    def load_saved_data(self, key):
        """Safe way of getting data persisted in the scene because it will always return a
        dictionary. Dictionary can be empty though.
        Args:
            key (str): the key to the data to retrieve. Valid options are 'eyes_mapping',
                'rig_mapping', 'rig_status' and 'face_mesh'
        Returns:
            dict: the persisted data or an empty dictionary
        """
        if utilities.check_data(key):
            return utilities.read_data(key)

        else:
            return {}

    def check_saved_data(self):
        """Updates eyes_data by filtering what elements exist in the scene and also
        stores that info in the maya scene.
        """
        checked_data = {}

        for key, data in self.eyes_data.items():
            bone_name = data['bone_field_value']

            if bone_name:
                if cmds.objExists(bone_name):
                    checked_data[key] = data

        self.eyes_data = checked_data
        utilities.write_data('eyes_mapping', self.eyes_data)

    def enable_inputs(self, key):
        """Enable Look buttons on this eye form based on whether or not the bone field value is set.
        Args:
            key (str): the from key to access the eye UI widget names.
        """
        button_keys = ['horizontal_min_button', 'horizontal_max_button', 'vertical_min_button', 'vertical_max_button']

        for button_key in button_keys:
            if 'bone_field_value' in self.eyes_data[key] and self.eyes_data[key]['bone_field_value'] is not None:
                cmds.button(self.eyes_data[key][button_key], edit=True, enable=True)

            else:
                cmds.button(self.eyes_data[key][button_key], edit=True, enable=False)

    def check_status(self, key):
        """Sets the status icon for this eye form based on whether all values are set.
        Args:
            key (str): the from key to access the eye UI widget names.
        """
        status = True

        for element, value in self.eyes_data[key].items():
            if element.split('_')[-1] == 'value':
                if value is None:
                    status = False
                    break

        if status:
            cmds.iconTextStaticLabel(self.eyes_data[key]['status_icon'], edit=True, image='wd_check_16px.png')

        else:
            cmds.iconTextStaticLabel(self.eyes_data[key]['status_icon'], edit=True, image='wd_failed_16px.png')

    def open_help(self, *args):
        """Opens eye documents on default web browser."""
        webbrowser.open(static.documentation_links['eye_rotations_docs'])
