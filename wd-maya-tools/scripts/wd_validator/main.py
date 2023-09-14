# Copyright 2023 Wonder Dynamics

# This source code is licensed under the GNU GPLv3
# found in the LICENSE file in the root directory of this source tree.

"""Entry point for the Validation add-on."""

import importlib

from wd_validator import gui, scene_data_collection, validation_main

importlib.reload(gui)
importlib.reload(scene_data_collection)
importlib.reload(validation_main)


def run():
    """Creates the scene data object, then creates and shows the main UI.
    A full validation is run inmidiately after showing the UI.
    """
    scene_data = scene_data_collection.CollectExportData()
    user_interface = gui.ValidationUI(scene_data=scene_data)

    scene_data.gui_inst = user_interface

    user_interface.open_window()
    validation_main.validation_run(scene_data)

    return user_interface
