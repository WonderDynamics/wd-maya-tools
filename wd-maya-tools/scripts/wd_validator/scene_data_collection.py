# Copyright 2025 Wonder Dynamics (an Autodesk Company)

# This source code is licensed under the GNU GPLv3
# found in the LICENSE file in the root directory of this source tree.

"""Module that defines the scene data object that is used throughout the whole validation process."""

import copy
import importlib

import maya.cmds as cmds

from wd_validator import utilities, static

importlib.reload(utilities)
importlib.reload(static)


# Code should be Python27 compatible
# pylint: disable=consider-using-f-string


class CollectExportData:
    """Class responsible for handling the scene and validation data."""

    def __init__(self):
        self.gui_inst = None
        self.retarget_gui_inst = None

        self.geo_group = None
        self.all_meshes = None
        self.rig_selection = None
        self.rig_group = None
        self.blendshapes = []
        self.face_geo = None
        self.face_blendshapes = []
        self.meshes_with_history = []

        self.materials = []
        self.file_nodes = {}
        self.bump_data = {}

        self.validation_data = {}
        self.export_dir = None
        self.metadata_json = copy.deepcopy(static.metadata_template)

    def collect_data(self):
        """Collects data from the scene, like geo group, meshes inside group,
        root joint rigging a mesh inside geo group, blendshapes targets in the scene
        and the group holding the root joint.
        """
        self.reset_variables()

        geo_grp = cmds.ls('GEO')

        if geo_grp:
            self.geo_group = geo_grp
            meshes = cmds.listRelatives(self.geo_group, ad=True, type='mesh', noIntermediate=True, fullPath=True)

            if meshes:
                self.all_meshes = []

                for mesh in meshes:
                    if cmds.getAttr('%s.intermediateObject' % mesh) == 0:
                        self.all_meshes.append(mesh)
            else:
                self.all_meshes = None

        else:
            self.geo_group = None

        # Find root joint
        all_shapes = cmds.listRelatives(self.geo_group, ad=True, noIntermediate=True, type='shape', fullPath=True)

        if all_shapes:
            for shape in all_shapes:
                # Get skin cluster
                skin_cluster = cmds.listConnections(shape, type='skinCluster')

                if skin_cluster is not None:
                    joints = cmds.listConnections(skin_cluster[0], type='joint')

                    if joints is not None:
                        # Find root joints
                        root_joint = joints[0]

                        while True:
                            parent = cmds.listRelatives(root_joint, parent=True, type='joint')

                            if not parent:
                                break

                            root_joint = parent[0]

                        self.rig_selection = root_joint

                        break

        # Find all blendshapes
        all_blendshapes = cmds.listConnections('shapeEditorManager', type='blendShape')

        if all_blendshapes is not None:
            for blendshape in all_blendshapes:
                bs_geometries = cmds.listConnections(blendshape + '.inputTarget')

                if bs_geometries:
                    for bs_geo in bs_geometries:
                        self.blendshapes.append(bs_geo)

        # Find rig group
        if self.rig_selection:

            top_joint_parent = cmds.listRelatives(self.rig_selection, p=1, f=1)
            rig_group = top_joint_parent[0] if top_joint_parent else ''

            suffix = 'BODY'

            if rig_group.endswith(suffix):
                self.rig_group = rig_group

    def reset_variables(self):
        """Resets the object's scene data properties."""
        self.geo_group = None
        self.all_meshes = None
        self.rig_selection = None
        self.rig_group = None
        self.blendshapes = []
        self.materials = []
        self.file_nodes = {}
        self.meshes_with_history = []
        self.metadata_json = copy.deepcopy(static.metadata_template)
