# Copyright 2025 Wonder Dynamics (an Autodesk Company)

# This source code is licensed under the GNU GPLv3
# found in the LICENSE file in the root directory of this source tree.

"""Module that defines the Script Output Window."""

import maya.cmds as cmds

# Maya mel interface will add arguments to callbacks in ui widgets
# that you need to catch somehow
# pylint: disable=unused-argument

class ScriptOutputWindow(object):
    """Class that creates and handles the terminal like script output window."""

    def __init__(self, gui_inst):
        self.window = 'script_terminal_window'
        self.title = 'Flow Studio Character Validator - Script Terminal'
        self.width = 400

        self.main_gui = gui_inst

        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

        window_size = (self.width, int(self.width * 1.5))
        self.window = cmds.window(self.window, title=self.title, widthHeight=window_size, sizeable=True)

        form = cmds.formLayout(numberOfDivisions=100, width=self.width)

        self.scroll_list = cmds.scrollField(editable=False)
        close_button = cmds.button(label='Close', command=self.close_window)

        cmds.formLayout(
            form,
            edit=True,
            attachForm=(
                (self.scroll_list, 'left', 5),
                (self.scroll_list, 'right', 5),
                (self.scroll_list, 'top', 5),
                (close_button, 'left', 5),
                (close_button, 'right', 5),
                (close_button, 'bottom', 5),
            ),
            attachControl=((self.scroll_list, 'bottom', 5, close_button)),
        )

        self.update_terminal()

    def open_window(self, *args):
        """Show the Script Output Window."""
        cmds.showWindow(self.window)

    def close_window(self, *args):
        """Hides and deletes the Script Output Window."""
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

    def update_terminal(self):
        """Updates the text in the Script Output Window with all the output messages
        stored in the main ui.
        """
        cmds.scrollField(self.scroll_list, text=self.main_gui.all_output_messages, e=True)
