# Copyright 2025 Wonder Dynamics (an Autodesk Company)

# This source code is licensed under the GNU GPLv3
# found in the LICENSE file in the root directory of this source tree.

"""Module for main Validation UI."""

from functools import partial
import functools
import webbrowser
import importlib
from datetime import datetime

import maya.cmds as cmds

from wd_validator import static, utilities, validation_main as validate, validation_fixes as val_fix
from wd_validator import validation_tools, export_data, rig_retargeting_gui, eye_rotations_gui, script_output_window

importlib.reload(static)
importlib.reload(utilities)
importlib.reload(validate)
importlib.reload(val_fix)
importlib.reload(validation_tools)
importlib.reload(export_data)
importlib.reload(rig_retargeting_gui)
importlib.reload(eye_rotations_gui)
importlib.reload(script_output_window)


# Maya mel interface will add arguments to callbacks in ui widgets
# that you need to catch somehow
# pylint: disable=unused-argument


class ValidationUI(object):
    """Main UI for the validation add-on."""

    def __init__(self, scene_data):
        """
        Args:
            scene_data (CollectExportData): the object holding the scene data.
        """
        self.scene_data = scene_data
        self.validation_windows = {}
        self.export_enable = True
        self.retarget_ui = None
        self.eye_rotations_ui = None
        self.script_terminal = None

        self.window = 'character_validation'
        self.title = 'Flow Studio Character Validator'
        self.width = 515

        self.all_output_messages = ''

        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

        # Delete all child windows when the script is restarted
        if cmds.window('rig_retargeting', exists=True):
            cmds.deleteUI('rig_retargeting', window=True)

        if cmds.window('eye_rotations', exists=True):
            cmds.deleteUI('eye_rotations', window=True)

        if cmds.window('script_terminal_window', exists=True):
            cmds.deleteUI('script_terminal_window', window=True)

        # window_size = (self.width, self.width * 1.29)
        window_size = (self.width, self.width * 1.36)
        self.window = cmds.window(self.window, title=self.title, widthHeight=window_size, sizeable=True)

        # Main layout
        self.main_column = cmds.columnLayout(adjustableColumn=True)

        cmds.separator(height=10, style='out')
        cmds.text(label='Scene validation', align='center')
        cmds.separator(height=10, style='in')

        # Generate validation indicators
        self.generate_validation_windows()

        cmds.setParent(self.main_column)
        cmds.separator(h=20, style='none')
        cmds.separator()

        # Script controls
        controls_form = cmds.formLayout(numberOfDivisions=100)

        self.validate_button = cmds.button(label='Refresh Validation', command=self.start_validation)

        checkbox_annotation = 'Enable USD support to use all USD,\nMaya and Unreal export features in\nFlow Studio.'
        self.validate_usd_checkbox = cmds.checkBox(label='Enable USD Support: Required for USD, Maya and Unreal Engine export.', v=0, changeCommand=self.start_validation,
                                                   annotation=checkbox_annotation)
    
        separator_val = cmds.separator()
        separator_exp = cmds.separator()

        docs_button = cmds.button(label='Documentation', command=self.open_documentation)
        self.export_all_button = cmds.button(
            label='Export with xGen', enable=False, command=self.export_with_xgen
        )
        self.export_without_xgen_button = cmds.button(
            label='Export without xGen', enable=False, command=self.export_without_xgen
        )
        abort_button = cmds.button(label='Abort', command=self.close_window)
        terminal_button = cmds.button(label='>_', command=self.open_script_terminal)

        cmds.formLayout(
            controls_form,
            edit=True,
            attachForm=(
                (self.validate_usd_checkbox, 'left', 2),
                (self.validate_usd_checkbox, 'right', 2),
                (self.validate_usd_checkbox, 'top', 2),

                (separator_val, 'left', 2),
                (separator_val, 'right', 2),
                
                (self.validate_button, 'left', 2),
                (self.validate_button, 'right', 2),
                # (self.validate_button, 'top', 2),
                (docs_button, 'left', 2),
                (abort_button, 'right', 2),

                (separator_exp, 'left', 2),
                (separator_exp, 'right', 2),


                (self.export_all_button, 'left', 2),
                (self.export_without_xgen_button, 'right', 2),
            ),
            attachControl=(
                # (self.validate_usd_checkbox, 'left', 10, self.validate_button),
                # (self.validate_button, 'right', 10, self.validate_usd_checkbox),
                (self.validate_button, 'top', 2, self.validate_usd_checkbox),

                (separator_val, 'top', 2, self.validate_button),

                (docs_button, 'top', 2, separator_val),
                # (docs_button, 'top', 2, self.validate_button),
                (docs_button, 'right', 2, terminal_button),
                (abort_button, 'top', 2, separator_val),
                (terminal_button, 'top', 2, separator_val),

                (separator_exp, 'top', 2, docs_button),

                # (abort_button, 'top', 2, self.validate_button),
                # (terminal_button, 'top', 2, self.validate_button),
                (terminal_button, 'right', 2, abort_button),
                (self.export_all_button, 'top', 2, separator_exp),
                # (self.export_all_button, 'top', 2, docs_button),
                (self.export_all_button, 'right', 2, self.export_without_xgen_button),
                (self.export_without_xgen_button, 'top', 2, separator_exp),
                # (self.export_without_xgen_button, 'top', 2, docs_button),

            ),
            attachPosition=(
                # (self.validate_button, 'right', 0, 78),
                # (self.validate_usd_checkbox, 'left', 0, 80),
                (terminal_button, 'left', 0, 45),
                (abort_button, 'left', 0, 55),
                (self.export_without_xgen_button, 'left', 0, 50),
            ),
        )

        cmds.setParent(self.main_column)
        cmds.separator(height=5, style='out')
        cmds.text(label='Wonder Dynamics (an Autodesk Company) - {}'.format(static.ADDON_VERSION), align='center', height=18)
        cmds.separator(height=5, style='in')

        self.load_saved_data()

    def get_validation_mode(self):
        """Returns the mode for the validator.

        Returns:
            str: The validator mode. Can be either static.VALIDATOR_NORMAL or static.VALIDATOR_USD
        """
        mode = static.VALIDATION_NORMAL
        if hasattr(self, 'validate_usd_checkbox') and cmds.checkBox(self.validate_usd_checkbox, q=1, v=1):
            mode = static.VALIDATION_USD
        return mode

    def set_validation_mode(self, mode):
        """Sets the validation mode

        Args:
            mode (str): the validator mode. Can be either static.VALIDATOR_NORMAL or static.VALIDATOR_USD

        Returns:
            bool: Whether or not the mode was set
        """

        # if UI is not constructed
        if not hasattr(self, 'validate_usd_checkbox'):
            return False

        value = mode == static.VALIDATION_USD
        cmds.checkBox(self.validate_usd_checkbox, e=1, v=value)
        return True


    def open_window(self, *args):
        """Opens the Main Validator UI."""
        cmds.showWindow(self.window)

    def close_window(self, *args):
        """Closes Main Validation window and all dependent UIs (retarget, eyes and terminal)."""
        print('\nClosing all UI windows...')

        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

        try:
            self.retarget_ui.close_window()
        except Exception:
            print('Retargeting window already closed.')

        try:
            self.eye_rotations_ui.close_window()
        except Exception:
            print('Eye rotatitions window already closed.')

        try:
            self.script_terminal.close_window()
        except Exception:
            print('Script terminal window already closed.')

    def generate_validation_windows(self):
        """Populates the main UI with the defined checks."""
        for k, v_data in static.validation_windows_data.items():
            form1 = cmds.formLayout(numberOfDivisions=100, height=25, width=200)

            if k.split('_')[0] == 'header':
                text1 = cmds.text(label=v_data['message'], align='left', height=25, font='boldLabelFont')
                cmds.formLayout(
                    form1,
                    edit=True,
                    attachForm=[
                        (text1, 'left', 5),
                        (text1, 'top', 7),
                    ],
                )

                cmds.setParent(self.main_column)
                cmds.separator(style='none', height=5)

            else:
                self.validation_windows[k] = {}

                text1 = cmds.text(label=v_data['message'], align='left')
                status_button = cmds.iconTextButton(style='iconOnly', image='wd_skip_16px.png', height=18, width=18)
                help_button = cmds.button(label='Help', height=18, command=partial(self.open_help, k))
                cmds.formLayout(
                    form1,
                    edit=True,
                    attachForm=[
                        (text1, 'left', 15),
                        (text1, 'top', 7),
                        (status_button, 'top', 2),
                        (help_button, 'top', 2),
                        (help_button, 'right', 2),
                    ],
                    attachControl=[
                        (text1, 'right', 5, status_button),
                        (status_button, 'right', 20, help_button),
                    ],
                    attachPosition=(help_button, 'left', 0, 75),
                )

                if k == 'retargeting_check':
                    retarget_button = cmds.button(
                        label='Joint Mapping', height=16, command=self.open_retargeting_window
                    )
                    cmds.formLayout(
                        form1,
                        edit=True,
                        height=50,
                        attachForm=(
                            (retarget_button, 'left', 0),
                            (retarget_button, 'right', 0),
                            (retarget_button, 'bottom', 4),
                        ),
                        attachControl=((retarget_button, 'top', 6, text1)),
                        attachPosition=((retarget_button, 'left', 0, 15), (retarget_button, 'right', 0, 85)),
                    )

                if k == 'face_check':
                    face_text = cmds.text(label='Face geo:', align='left')
                    face_field = cmds.textField(editable=False, backgroundColor=(0.18, 0.18, 0.18))
                    face_button = cmds.iconTextButton(
                        label='+', style='iconOnly', image='wd_add_16px.png', height=20, width=20
                    )
                    cmds.iconTextButton(face_button, edit=True, command=self.set_face_geo)
                    eye_rotations_button = cmds.button(
                        label='Eye Bone Mapping', height=18, command=self.open_eye_rotations_window, enable=False
                    )
                    cmds.formLayout(
                        form1,
                        edit=True,
                        height=80,
                        attachForm=(
                            (face_text, 'left', 15),
                            (face_button, 'right', 2),
                            (eye_rotations_button, 'left', 0),
                            (eye_rotations_button, 'right', 0),
                        ),
                        attachControl=(
                            (face_text, 'top', 10, text1),
                            (face_field, 'top', 7, text1),
                            (face_field, 'left', 6, face_text),
                            (face_field, 'right', 2, face_button),
                            (face_button, 'top', 6, text1),
                            (eye_rotations_button, 'top', 6, face_field),
                        ),
                        attachPosition=((eye_rotations_button, 'left', 0, 15), (eye_rotations_button, 'right', 0, 85)),
                    )

                    self.validation_windows[k]['face_field'] = face_field
                    self.validation_windows[k]['face_button'] = face_button
                    self.validation_windows[k]['aux_button'] = eye_rotations_button

                self.validation_windows[k]['button'] = status_button

                cmds.setParent(self.main_column)
                cmds.separator()

    def open_help(self, help_key, *args):
        """Opens the url defined in static for help in the default web browser in your
        Operating System.
        """
        link = static.validation_windows_data[help_key]['help_path']

        if not isinstance(link, list):
            link = [link]

        for l in link:
            webbrowser.open(l)

    def open_documentation(self, *args):
        """Opens the url defiened in static for documentation in the default web browser
        in your Operating System.
        """
        webbrowser.open(static.documentation_links['docs'])

    def start_validation(self, *args):
        """Calls the validation process and then sets the enable state for the export buttons based on
        validation success.
        """
        mode = self.get_validation_mode()
        self.scene_data.metadata_json['usd'] =  mode == static.VALIDATION_USD
        validate.validation_run(self.scene_data, mode=mode)
        self.enable_export()

    def fix_button(self, val_type, *args):
        """Callback called by validation buttons when fix is available. This will
        fix the scene and save it. Then it will update the enable status of the export
        buttons according to validation status.
        Args:
            val_type (str): the name of the validator.
        """
        if val_type == 'file_nodes_check':
            val_fix.fix_empty_file_nodes(self.scene_data)

        if val_type == 'referenced_data':
            val_fix.reference_data_fix()

        if val_type == 'geo_check':
            val_fix.remove_animation_on_geo_fix(self.scene_data)

        if val_type == 'history_check':
            val_fix.remove_pre_skin_history(self.scene_data)

        if val_type == 'all_group_check':
            val_fix.all_group_fix(self.scene_data)

        if val_type == 'rig_check':
            val_fix.joint_name_fix(self.scene_data)
            val_fix.remove_animation_on_rig_fix(self.scene_data)


        # val_fix.save_scene()
        self.start_validation()
        self.enable_export()

    def empty_command(self, *args):
        pass

    def update_status(self, val_type, status):
        """Updates the icon, enabled state and callback for a validation button.
        The status for this validator is also stored in the validation_window's member data.
        Args:
            val_type (str): the name of the validator.
            status (str): The current status of the validator, it can be 'fix', 'pass', 'fail',
                'skip' and 'warning'.
        """
        if val_type.split('_')[0] != 'header':
            status_button = self.validation_windows[val_type]['button']
            enable_status = True

            if status.lower() == 'fix':
                enable_status = True
                icon = 'wd_fix_warning_16px.png'
                command = partial(self.fix_button, val_type)

            elif status.lower() == 'pass':
                icon = 'wd_check_16px.png'
                command = self.empty_command

            elif status.lower() == 'fail':
                icon = 'wd_failed_16px.png'
                command = self.empty_command

            elif status.lower() == 'skip':
                icon = 'wd_skip_16px.png'
                command = self.empty_command

            elif status.lower() == 'warning':
                icon = 'wd_warning_16px.png'
                command = self.empty_command

            elif status.lower() == 'warning_fix':
                enable_status = True
                icon = 'wd_fix_warning_16px.png'
                command = partial(self.fix_button, val_type)

            else:
                icon = 'wd_skip_16px.png'
                command = self.empty_command

            cmds.iconTextButton(status_button, e=True, image=icon, enable=enable_status, command=command)

            self.validation_windows[val_type]['status'] = status

    def set_face_geo(self, *args):
        """Calback called when the add button on the face validator is clicked. This will check
        all requirements for the face, update the face data in scene_data and update the UI to
        reflect the status and enable the export buttons if possible.
        """
        field = self.validation_windows['face_check']['face_field']
        button = self.validation_windows['face_check']['face_button']

        # restrict selection to only meshes and transforms, otherwise dg nodes can be selected
        selected = cmds.ls(sl=True, noIntermediate=True, long=True, type='mesh')
        selected += cmds.ls(sl=True, noIntermediate=True, long=True, type='transform')

        if selected:
            if cmds.objectType(selected[0]) == 'mesh':
                selected = cmds.listRelatives(selected[0], parent=True, fullPath=True)[0]

            else:
                selected = selected[0]

            if selected.split('|')[-2] == 'GEO':  # get parent from a full path
                status, message = validation_tools.face_check(face_geo=selected, scene_data=self.scene_data)
                self.update_status(val_type='face_check', status=status)
                self.update_script_output(message=message)

                cmds.textField(field, edit=True, text=selected.split('|')[-1])
                cmds.iconTextButton(button, edit=True, image='wd_subtract_16px.png', command=self.remove_face_geo)

                if status in ['pass', 'warning']:
                    eyes_button = self.validation_windows['face_check']['aux_button']
                    cmds.button(eyes_button, edit=True, enable=True)

                    self.scene_data.face_geo = selected
                    utilities.write_data('face_mesh', selected)

                else:
                    cmds.textField(field, edit=True, backgroundColor=(0.32, 0.18, 0.18))
                    self.scene_data.face_geo = None

            else:
                cmds.warning('Face geometry needs to be inside the \"GEO\" group.')
                self.update_status(val_type='face_check', status='skip')

        else:
            cmds.warning('Nothing is selected. Plese select mesh with face blendshapes.')
            self.update_status(val_type='face_check', status='skip')

        self.enable_export()

    def remove_face_geo(self, *args, enable_export=True):
        """Callback called when user removes a selected geo from the face validator.
        This will also close the Eye Rotation Window, remove data in the file for the face
        Enable and disable validator buttons accordingly and set the status to 'skip'.
        Args:
            enable_export (bool, optional): Wheter or not the export buttons should be updated.
                Defaults to True.
        """
        field = self.validation_windows['face_check']['face_field']
        button = self.validation_windows['face_check']['face_button']

        cmds.textField(field, edit=True, text='', backgroundColor=(0.18, 0.18, 0.18))
        cmds.iconTextButton(button, edit=True, image='wd_add_16px.png', command=self.set_face_geo)

        try:
            self.eye_rotations_ui.close_window()
        except Exception:
            print('Nothing to close.')

        eyes_button = self.validation_windows['face_check']['aux_button']
        cmds.button(eyes_button, edit=True, enable=False)

        self.scene_data.face_geo = None
        utilities.remove_data('face_mesh')
        self.update_status(val_type='face_check', status='skip')

        if enable_export:
            self.enable_export()

    def load_saved_data(self):
        """Updates face UI with the data persisted in the maya scene.
        It also updates the scene_data accordingly.
        """
        if utilities.check_data('face_mesh'):
            mesh = utilities.read_data('face_mesh')

            if cmds.objExists(mesh):
                field = self.validation_windows['face_check']['face_field']
                button = self.validation_windows['face_check']['face_button']

                status, _ = validation_tools.face_check(face_geo=mesh, scene_data=self.scene_data)
                self.update_status(val_type='face_check', status=status)

                if status in ['pass', 'warning']:
                    cmds.textField(field, edit=True, text=mesh.split('|')[-1])
                    cmds.iconTextButton(
                        button,
                        edit=True,
                        image='wd_subtract_16px.png',
                        command=partial(self.remove_face_geo, field, button),
                    )
                    self.scene_data.face_geo = mesh

                    eyes_button = self.validation_windows['face_check']['aux_button']
                    cmds.button(eyes_button, edit=True, enable=True)
            else:
                self.update_status(val_type='face_check', status='skip')
                self.scene_data.face_geo = None
        else:
            self.update_status(val_type='face_check', status='skip')
            self.scene_data.face_geo = None

    def update_script_output(self, message):
        """Add the message or list of messages to the global list of messages.
        It also prints this messages to the script editor and update them in
        the Terminal UI if it is open.
        Args:
            message (str or list[str]): The message(s) to display for the user.
        """
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        if isinstance(message, list):
            for i, msg_line in enumerate(message):
                msg = '[' + current_time + '] ' + msg_line + '\n'

                if i == 0:
                    msg = '\n' + msg

                self.all_output_messages += msg
                print(msg_line)

        else:
            msg = '\n' + '[' + current_time + '] ' + message + '\n'
            self.all_output_messages += msg
            print(message)

        if cmds.window('script_terminal_window', exists=True):
            self.script_terminal.update_terminal()

    def enable_export(self):
        """Sets the enable state of the export buttons based on whether or not
        all the validators have an accepted status. This enable state is also
        cached in a member variable.
        """
        accepted_statuses = ['pass', 'skip', 'warning', 'warning_fix']
        self.export_enable = True

        for val in self.validation_windows.values():
            if val['status'] not in accepted_statuses:
                self.export_enable = False

        if self.export_enable:
            export_char = True

            if self.validation_windows['xGen_check']['status'] == 'pass':
                export_all = True

            else:
                export_all = False

        else:
            export_all = False
            export_char = False

        cmds.button(self.export_without_xgen_button, e=True, enable=export_char)
        cmds.button(self.export_all_button, e=True, enable=export_all)

    def export_without_xgen(self, *args):
        """ Call the initiate_export method to export the character without xGen.
        """
        self.initiate_export()

    def export_with_xgen(self, *args):
        """ Call the initiate_export method to export the character with xGen.
        """
        self.initiate_export(xgen_export=True)

    def initiate_export(self, xgen_export=False):
        """Runs the validation process and if it is successful, exports the
        data to disk.
        Args:
            xgen_export (bool, optional): Whether or not to export XGen dynamic grooms for
                the character. Defaults to False.
        """

        # confirm user is aware of USD checks being skipped.
        if self.get_validation_mode() != static.VALIDATION_USD:
            msg = ('USD support validation is disabled!\n'
                    'This may cause issues with USD, Maya, and Unreal exports.')
            buttons = ['Cancel and enable USD support', 'Continue']
            answer = cmds.confirmDialog(message=msg, title='USD Validation Warning', button=buttons, defaultButton=buttons[0])

            # enable usd checks
            if answer == buttons[0]:
                self.set_validation_mode(static.VALIDATION_USD)
                self.start_validation()
                return

        # Validate the scene and character again in case of scene changes
        self.start_validation()

        if self.export_enable:
            if xgen_export:
                self.update_script_output(message='>>> Exporting character data with xGen...')
                export_data.export(xgen_export=True, scene_data=self.scene_data)

            else:
                self.update_script_output(message='>>> Exporting character data...')
                export_data.export(xgen_export=False, scene_data=self.scene_data)

        self.update_script_output(message='>>> Character data exported successfully.')

    def open_retargeting_window(self, *args):
        """Initializes and opens the retargetting window."""
        self.retarget_ui = rig_retargeting_gui.RigRetargetingUI(scene_data=self.scene_data)
        self.scene_data.retarget_gui_inst = self.retarget_ui
        self.retarget_ui.open_window()

    def open_eye_rotations_window(self, *args):
        """Initializes and opens the eye rotation window."""
        self.eye_rotations_ui = eye_rotations_gui.EyeRotationsUI(scene_data=self.scene_data)
        self.eye_rotations_ui.open_window()

    def open_script_terminal(self, *args):
        """Initializes and opens the terminal window."""
        self.script_terminal = script_output_window.ScriptOutputWindow(gui_inst=self)
        self.script_terminal.open_window()
