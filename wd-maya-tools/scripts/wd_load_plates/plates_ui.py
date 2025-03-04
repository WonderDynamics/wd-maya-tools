"""Module to load Flow Studio clean plates to maya scene.

To run this tool, type on the script editor the following:

from wd_load_plates import plates_ui
plates_ui.add_all_plates_ui()

"""

import os
import traceback
import webbrowser

from maya import cmds

from wd_load_plates import plates_utils


def main_ui() -> None:
    """Main entry point for the tool. Will show instructions and a confirmation button."""
    message = (
        '\nThis is the Flow Studio Load Plates utility, it is used to add clean plates downloaded '
        'from the platform into your scene.\n\nMake sure you:\n - have downloaded and unzipped your '
        'clean plates into a folder\n - have the Maya project set to the Flow Studio Maya scene '
        'folder.\n - have the Flow Studio Maya scene open.\n\n When ready, click the "Add Plates '
        'to Cameras" button.\n\nOnce you proceed to add plates to cameras, you will:\n\n - be '
        'prompted to browse for the folder where you have extracted the clean plates\n - be prompt '
        'about where you want to store the Maya-compatible clean plates (either on the Maya project '
        'or next to the Maya scene folder).\n\nWhen the process finishes, you will find the clean '
        'plates added as Maya image plates next to where the cameras are in the outliner.\n\nWARNING: '
        'Running this tool multiple times will create multiple copies of the same image plane.\n'
    )

    buttons = ['Cancel', 'More Information', 'Add Plates to Cameras']
    answer = cmds.confirmDialog(message=message, title='Flow Studio Load Plates Utility', button=buttons)

    if answer == buttons[0]:
        print('User cancelled process for adding plates to cameras.')
        return

    if answer == buttons[1]:
        browse_for_doc_url()
        return

    if answer == buttons[2]:
        add_all_plates_ui()
        return


def browse_for_doc_url() -> None:
    """Opens the documentation web page in the default web browser."""
    url = (
        'https://help.wonderdynamics.com/'
        'working-with-wonder-studio/export-elements/export-scenes/maya-scene#camera-plate-addon'
    )
    webbrowser.open(url)


def add_all_plates_ui() -> None:
    """Prompts user with plates location and destination and adds an image plane to
    all cameras in the sequencer.
    """
    scene_name = plates_utils.get_scene_name()
    if not scene_name:
        msg = 'Current scene has no name. Are you sure you are in a WS Maya Scene?'
        cmds.confirmDialog(message=msg, title='Flow Studio Load Plates Utility', button=['Close'])
        return

    scene_folder = os.path.dirname(scene_name)

    project_folder = plates_utils.get_project_folder()

    # check for sequencer first
    cut_data_list = plates_utils.get_cut_data_from_sequencer()
    if not cut_data_list:
        msg = 'Could not find any sequencer shot. Are you sure you are in a WS Maya Scene?'
        cmds.confirmDialog(message=msg, title='Flow Studio Load Plates Utility', button=['Close'])
        return

    folder = plates_utils.browse_for_plate_folder()
    if not folder or not os.path.isdir(folder):
        # user canceled when browsing for clean plates dir
        return

    plates_root = resolve_plate_location(scene_folder, project_folder)
    if plates_root == 'none':
        # case where user closed prompt instead of picking a location.
        return

    try:
        cmds.waitCursor(state=True)
        result = plates_utils.add_all_plates(folder, plates_root)
        cmds.waitCursor(state=False)
        if result:
            msg = f'Success!\n\nAdded the following image planes ({len(result)}):\n\n  - ' + '\n  - '.join(result)
            msg += '\n\nYou will find the image planes next to each camera in the outliner.'
        else:
            msg = 'Could not add any image plane! Please check script editor for more information.'

    except Exception as exc:  # pylint: disable=broad-exception-caught
        cmds.waitCursor(state=False)
        traceback.print_exc()
        msg = f'Could not add plates. Please check script editor for more information. Error was {exc}'

    cmds.confirmDialog(message=msg, title='Load Plates Tool Result', button=['Close'])


def prompt_for_location(scene_folder: str, project_folder: str) -> str:
    """Prompts the user to decide if the plates should be located in the project
    folder or next to the current scene.
    Args:
        scene_folder (str): Full path to the maya scene folder.
        project_folder (str): Full path to the maya project folder.
    Returns:
        str: The location name to store the renamed plates. Can be one of this:
            none -> user cancelled
            scene -> next to scene
            project -> in project folder
    """
    message = (
        'Where should I store the maya plates?\n\n'
        f'Project Folder:\n    {project_folder}\n\nScene Folder:\n    {scene_folder}\n'
    )
    buttons = ['In the scene folder', 'In the project folder']
    answer = cmds.confirmDialog(message=message, title='Load Plates Tool: Please select:', button=buttons)
    mapping = {'dismiss': 'none', buttons[0]: 'scene', buttons[1]: 'project'}

    return mapping[answer]


def resolve_plate_location(scene_folder: str, project_folder: str) -> str:
    """Resolves if the renamed plates will be placed in the project or next
    to the maya scene.
    Args:
        scene_folder (str): Full path to the maya scene folder.
        project_folder (str): Full path to the maya project folder.
    Returns:
        str: The folder where the renamed plates should be created (in their own folder)
    """

    if not os.path.isdir(project_folder):
        return scene_folder

    location = prompt_for_location(scene_folder, project_folder)
    if location == 'none':
        msg = 'User Cancelled!'
        print(msg)
        return 'none'

    if location == 'project':
        return project_folder
    return scene_folder
