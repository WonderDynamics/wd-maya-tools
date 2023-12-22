"""Module with utilities to add the plates to maya cameras in the Wonder Studio Maya scene."""
import os
import platform
import subprocess
import re
import glob
import shutil
from typing import Dict, List, Any, Tuple

from maya import cmds, mel

FRAME_START = 'frame.'
FRAME_EXT = '.jpg'


def browse_for_plate_folder() -> str:
    """Opens dialog for user to select the folder where the clean plates are.
    Returns:
        str: Path to the plates folder or empty string if dialog was cancelled.
    """
    result = cmds.fileDialog2(
        caption='Select the folder containing the clean plate sequence',
        fileMode=2,
        dialogStyle=2,
        okCaption='Use This Folder',
    )
    if result:
        return result[0]

    msg = 'User Cancelled browsing for plate.'
    print(msg)
    return ''


def get_scene_name() -> str:
    """Returns the scene name or empty string if not named.
    Returns:
        str: The full path to the maya scene or empty string if not named
    """
    scene = cmds.file(query=True, sceneName=True)
    if not scene or not os.path.isfile(scene):
        msg = 'File is not saved! Please save it before starting process.'
        print(msg)
        return ''
    return scene


def get_project_folder() -> str:
    """Get the path to the maya project folder.
    Returns:
        str: The full path to the current maya project folder.
    """
    project = cmds.workspace(rootDirectory=True, query=True)
    if not os.path.isdir(project):
        msg = 'Maya project is not set! Please set it with File > Set Project...'
        print(msg)
    return project


def convert_sequence_to_maya_compatible(folder: str, dst_folder: str) -> Tuple[str, subprocess.Popen]:
    """Convert the wonder studio clean plate sequence in one that maya can load and
    understand it's frames.
    Args:
        folder (str): Full path to the folder holding the frames.
        dst_folder (str): Full path to the parent folder where the new folder with the
            renamed frames will be stored.
    Raises:
        IOError: If original frames cannot be found in the folder.
        IOError: If frame numbers cannot be found in the basename of the files.
    Returns:
        Tuple[str, subprocess.Popen]: The glob for listing the output frames and a the process
            that is generating the frames.
    """
    full_dst_folder = os.path.join(dst_folder, 'maya_image_plane')

    if os.path.isdir(full_dst_folder):
        shutil.rmtree(full_dst_folder)

    os.makedirs(full_dst_folder, exist_ok=True)

    maya_magick = os.path.join(os.getenv('MAYA_LOCATION', ''), 'bin', 'magick')
    if platform.system() == 'Windows':
        maya_magick = maya_magick + '.exe'

    if not os.path.isfile(maya_magick):
        raise IOError(f'Could not find Mayas image magick! Expected path was {maya_magick}')

    src = os.path.join(folder, '*' + FRAME_EXT)
    src_frames = sorted(os.path.normpath(p) for p in glob.iglob(src))
    if not src_frames:
        raise IOError(f'Could not find sequences with pattern {src}')

    # get start frame
    start_frames_found = re.findall('[0-9]+', os.path.basename(src_frames[0]))
    if not start_frames_found:
        raise IOError(f'Could not find frame number in {src_frames[0]}')

    start_frame = int(start_frames_found[-1])

    dst = os.path.join(full_dst_folder, FRAME_START + '%06d' + FRAME_EXT)

    if platform.system() == 'Linux':
        cmd = f'"{maya_magick}" convert "{src}" -scene {start_frame} "{dst}"'
    else:
        cmd = [maya_magick, 'convert', src, '-scene', str(start_frame), dst]

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(f'Converting plates on {src} to {dst}')

    dst_glob = dst.replace('%06d', '?' * 6)

    return dst_glob, proc


def convert_sequence_to_maya_compatible_wait(folder: str, dst_folder: str) -> List[str]:
    """Convert the wonder studio clean plate sequence in one that maya can load and
    understand it's frames. WAITS FOR THE PROCESS TO END and returns existing frames.
    Args:
        folder (str): Full path to the folder holding the frames.
        dst_folder (str): Full path to the parent folder where the new folder with the
            renamed frames will be stored.
    Returns:
        List[str]: The list of generated frames.
    """
    frames = []
    try:
        converted_plates_glob, process = convert_sequence_to_maya_compatible(folder, dst_folder)
    except IOError as exc:
        print(f'ERROR: Exception raised while trying to create the maya compatible frames. Error was {exc}')
        return frames

    print('Started converting frames ...')
    process.communicate()
    print('Finished converting frames!')

    frames = sorted(os.path.normpath(p) for p in glob.iglob(converted_plates_glob))
    if not frames:
        msg = 'WARNING! Could not find any converted frames'
        print(msg)
    return frames


def get_cut_data_from_sequencer() -> List[Dict[str, Any]]:
    """List sequencer shots and gets it's data.
    Returns:
        List[Dict[str, Any]]: A list of dictionaries each describing a shot with the
            following keys:
                name (str) the shot name
                start (int): the shot start frame.
                end (int): the shot end frame.
                camera (str): the maya camera connected to this shot.
    """
    shots = cmds.ls(type='shot')
    shots_data = []
    for shot in shots:
        camera = cmds.shot(shot, query=True, currentCamera=True)

        if not camera or not cmds.objExists(camera):
            msg = f'Could not find a camera attached to shot {shot}, skipping it!'
            print(msg)
            continue

        name = cmds.shot(shot, query=True, shotName=True)
        start = cmds.shot(shot, query=True, startTime=True)
        end = cmds.shot(shot, query=True, endTime=True)
        shots_data.append({'name': name, 'start': start, 'end': end, 'camera': camera})
    return shots_data


def add_image_plane(camera: str, first_frame: str) -> str:
    """Creates an image plane, attaches it to the camera and adds an image
    sequence which first frame is first_frame.
    Args:
        camera (str): The node for the camera shape.
        first_frame (str): Full path to the first frame of the sequence to
           add to the image plane.
    Returns:
        str: The created image plane transform.
    """
    image_plane = cmds.imagePlane(lookThrough=camera, showInAllViews=False)

    mel.eval(f'cameraImagePlaneUpdate "{camera}" "{image_plane[1]}";')

    cmds.setAttr(image_plane[1] + '.imageName', first_frame, type='string')
    cmds.setAttr(image_plane[1] + '.useFrameExtension', True)

    # parent to where the camera is
    parents = cmds.listRelatives(camera, p=1, pa=1)
    if parents:
        image_plane[0] = cmds.parent(image_plane[0], parents[0])[0]

    ip_trf = cmds.rename(image_plane[0], camera + '_ip')

    return ip_trf


def add_all_plates(folder: str, dst_folder: str) -> List[str]:
    """Adds  plates to all cameras on sequencer
    Args:
        folder (str): Full path to the folder holding the clean plate frames
            as downloaded from the platform.
        dst_folder (str): Full path to the parent folder where the new folder with the
            renamed frames will be stored.
    Returns:
        List[str]: The list of image planes created.
    """
    image_planes = []

    cut_data_list = get_cut_data_from_sequencer()
    if not cut_data_list:
        msg = 'Could not find any sequencer shot. Are you sure you are in a WS Maya Scene?'
        print(msg)
        return image_planes

    converted_plates = convert_sequence_to_maya_compatible_wait(folder, dst_folder)
    if not converted_plates:
        msg = 'WARNING: Could not find any converted clean plate frames!'
        print(msg)
        return image_planes

    for data in cut_data_list:
        msg = f'Adding plate for cut {data["name"]} and camera {data["camera"]}'
        print(msg)
        image_plane = add_image_plane(data['camera'], converted_plates[0])
        image_planes.append(image_plane)

    return image_planes
