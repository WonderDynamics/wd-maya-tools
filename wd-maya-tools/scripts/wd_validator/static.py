# Copyright 2023 Wonder Dynamics

# This source code is licensed under the GNU GPLv3
# found in the LICENSE file in the root directory of this source tree.

"""Module that defines constants and static values."""

material_attributes = {
    'aiStandardSurface': {
        'base': ['diffuseWeight_value', 'diffuseWeight_texture'],
        'baseColor': ['diffuse_value', 'diffuse_texture'],
        'metalness': ['metalness_value', 'metalness_texture'],
        'specular': ['specularWeight_value', 'specularWeight_texture'],
        'specularColor': ['specular_value', 'specular_texture'],
        'specularRoughness': ['roughness_value', 'roughness_texture'],
        'specularAnisotropy': ['anisotropic_value', 'anisotropic_texture'],
        'specularRotation': ['anisotropicRotation_value', 'anisotropicRotation_texture'],
        'transmission': ['transmissionWeight_value', 'transmissionWeight_texture'],
        'transmissionColor': ['transmission_value', 'transmission_texture'],
        'specularIOR': ['ior_value', 'ior_texture'],
        'subsurface': ['sssWeight_value', 'sssWeight_texture'],
        'subsurfaceColor': ['sss_value', 'sss_texture'],
        'subsurfaceRadius': ['sssRadius_value', 'sssRadius_texture'],
        'coat': ['coatWeight_value', 'coatWeight_texture'],
        'coatColor': ['coat_value', 'coat_texture'],
        'emission': ['emissionWeight_value', 'emissionWeight_texture'],
        'emissionColor': ['emission_value', 'emission_texture'],
        'opacity': ['opacity_value', 'opacity_texture'],
        'normalCamera': ['bumpWeight_value', 'bump_texture'],
    },
    'standardSurface': {
        'base': ['diffuseWeight_value', 'diffuseWeight_texture'],
        'baseColor': ['diffuse_value', 'diffuse_texture'],
        'metalness': ['metalness_value', 'metalness_texture'],
        'specular': ['specularWeight_value', 'specularWeight_texture'],
        'specularColor': ['specular_value', 'specular_texture'],
        'specularRoughness': ['roughness_value', 'roughness_texture'],
        'specularAnisotropy': ['anisotropic_value', 'anisotropic_texture'],
        'specularRotation': ['anisotropicRotation_value', 'anisotropicRotation_texture'],
        'transmission': ['transmissionWeight_value', 'transmissionWeight_texture'],
        'transmissionColor': ['transmission_value', 'transmission_texture'],
        'specularIOR': ['ior_value', 'ior_texture'],
        'subsurface': ['sssWeight_value', 'sssWeight_texture'],
        'subsurfaceColor': ['sss_value', 'sss_texture'],
        'subsurfaceRadius': ['sssRadius_value', 'sssRadius_texture'],
        'coat': ['coatWeight_value', 'coatWeight_texture'],
        'coatColor': ['coat_value', 'coat_texture'],
        'emission': ['emissionWeight_value', 'emissionWeight_texture'],
        'emissionColor': ['emission_value', 'emission_texture'],
        'opacity': ['opacity_value', 'opacity_texture'],
        'normalCamera': ['bumpWeight_value', 'bump_texture'],
    },
    'aiFlat': {'color': ['emission_value', 'emission_texture']},
}

accepting_textures = [
    'baseColor',
    'metalness',
    'specularColor',
    'specularRoughness',
    'transmissionColor',
    'subsurfaceColor',
    'coatColor',
    'emissionColor',
    'opacity',
    'normalCamera',
]

ADDON_VERSION = '1.0.0'
METADATA_VERSION = '1.0.0'
MAX_NAME_LENGHT = 50

GITBOOK_ROOT = 'https://help.wonderdynamics.com'
GITBOOK_CHAR_PREP = GITBOOK_ROOT + '/character-creation/maya-add-on'
GITBOOK_MAYA_PREP = GITBOOK_ROOT + '/character-creation/getting-started/character-setup'
GITBOOK_VALIDATION = GITBOOK_ROOT + '/character-creation/character-validation-messages'

documentation_links = {
    'docs': GITBOOK_CHAR_PREP,
    'retarget_docs': GITBOOK_CHAR_PREP + '/joint-mapping-maya',
    'eye_rotations_docs': GITBOOK_CHAR_PREP + '/eye-bone-mapping-maya',
}

validation_windows_data = {
    'header_1': {'message': 'Scene validation:'},
    'scene_saved': {
        'message': 'Checking if the scene is saved...',
        'help_path': GITBOOK_VALIDATION + '/maya-specific-messages/scene-saved-validation',
    },
    'referenced_data': {
        'message': 'Checking for referenced scenes...',
        'help_path': GITBOOK_VALIDATION + '/maya-specific-messages/referenced-scenes-validation',
    },
    'header_2': {'message': 'Character validation'},
    'geo_check': {
        'message': 'Checking if "GEO" group exists...',
        'help_path': GITBOOK_VALIDATION + '/maya-specific-messages/geo-group-validation',
    },
    'rig_check': {
        'message': 'Checking the rig...',
        'help_path': GITBOOK_VALIDATION + '/maya-specific-messages/character-rig-validation',
    },
    'rig_group_check': {
        'message': 'Checking rig group suffix...',
        'help_path': GITBOOK_VALIDATION + '/error-messages/wrong-skeleton-armature-name',
    },
    'history_check': {
        'message': 'Checking for construction history...',
        'help_path': GITBOOK_VALIDATION + '/maya-specific-messages/construction-history-validation',
    },
    'poly_count_check': {
        'message': 'Checking the polygon count...',
        'help_path': GITBOOK_VALIDATION + '/error-messages/poly-count-limit-exceeded',
    },
    'retargeting_check': {
        'message': 'Checking joint mapping data...',
        'help_path': GITBOOK_VALIDATION + '/error-messages/hips-bone-not-found',
    },
        'ik_check': {
        'message': 'Checking IK joint chains...',
        'help_path': GITBOOK_VALIDATION + '/warning-messages/unable-to-establish-all-ik-bone-chains',
    },
    'face_check': {
        'message': 'Checking face geometry...',
        'help_path': [
            GITBOOK_VALIDATION + '/error-messages/wrong-face-mesh-name',
            GITBOOK_VALIDATION + '/error-messages/no-valid-blendshapes',
            GITBOOK_VALIDATION + '/error-messages/multiple-main-face-meshes',
        ]
    },
    'material_type_check': {
        'message': 'Checking materials type...',
        'help_path': GITBOOK_VALIDATION + '/maya-specific-messages/materials-type-validation',
    },
        'naming_check': {
        'message': 'Checking naming...',
        'help_path': GITBOOK_VALIDATION + '/maya-specific-messages/naming-validation',
    },
    'material_connections_check': {
        'message': 'Checking material shading graph...',
        'help_path': GITBOOK_VALIDATION + '/maya-specific-messages/materials-shading-graph-validation',
    },
    'file_nodes_check': {
        'message': 'Checking for empty file nodes...',
        'help_path': GITBOOK_VALIDATION + '/maya-specific-messages/empty-file-nodes-validation',
    },
    'textures_check': {
        'message': 'Checking the textures...',
        'help_path': GITBOOK_VALIDATION + '/error-messages/missing-or-unsupported-texture-files-detected',
    },
    'xGen_check': {
        'message': 'Checking xGen grooms...',
        'help_path': GITBOOK_VALIDATION + '/maya-specific-messages/xgen-materials-validation',
    },
}

supported_bump_nodes = {
    'bump2d': {'input_attr': 'bumpValue', 'value_attr': 'bumpDepth', 'key': 'both'},
    'aiBump2d': {'input_attr': 'bumpMap', 'value_attr': 'bumpHeight', 'key': 'TEX_BUMP'},
    'aiNormalMap': {'input_attr': 'input', 'value_attr': 'strength', 'key': 'TEX_NORM'},
}

supported_textures = ['.png', '.jpg', '.jpeg', '.tif', '.tiff', '.exr']

eye_values = {
    'bone_field_value': 'bone_field',
    'horizontal_axis_menu_value': 'horizontal_axis_menu',
    'horizontal_min_field_value': 'horizontal_min_field',
    'horizontal_max_field_value': 'horizontal_max_field',
    'vertical_axis_menu_value': 'vertical_axis_menu',
    'vertical_min_field_value': 'vertical_min_field',
    'vertical_max_field_value': 'vertical_max_field',
}

metadata_template = {
    'software': 'maya',
    'version': METADATA_VERSION,
    'materials': [],
    'eyes_rig': [],
    'body': {
        'armature_name': None,
        'bone_names': {
            "Hips": None,
            "LeftUpLeg": None,
            "RightUpLeg": None,
            "Spine": None,
            "LeftLeg": None,
            "RightLeg": None,
            "Spine1": None,
            "LeftFoot": None,
            "RightFoot": None,
            "Spine2": None,
            "LeftToeBase": None,
            "RightToeBase": None,
            "Neck": None,
            "LeftShoulder": None,
            "RightShoulder": None,
            "Head": None,
            "LeftArm": None,
            "RightArm": None,
            "LeftForeArm": None,
            "RightForeArm": None,
            "LeftHand": None,
            "RightHand": None,
            "LeftHandIndex1": None,
            "LeftHandIndex2": None,
            "LeftHandIndex3": None,
            "LeftHandMiddle1": None,
            "LeftHandMiddle2": None,
            "LeftHandMiddle3": None,
            "LeftHandPinky1": None,
            "LeftHandPinky2": None,
            "LeftHandPinky3": None,
            "LeftHandRing1": None,
            "LeftHandRing2": None,
            "LeftHandRing3": None,
            "LeftHandThumb1": None,
            "LeftHandThumb2": None,
            "LeftHandThumb3": None,
            "RightHandIndex1": None,
            "RightHandIndex2": None,
            "RightHandIndex3": None,
            "RightHandMiddle1": None,
            "RightHandMiddle2": None,
            "RightHandMiddle3": None,
            "RightHandPinky1": None,
            "RightHandPinky2": None,
            "RightHandPinky3": None,
            "RightHandRing1": None,
            "RightHandRing2": None,
            "RightHandRing3": None,
            "RightHandThumb1": None,
            "RightHandThumb2": None,
            "RightHandThumb3": None,
        },
    },
    'face': {
        'mesh_name': None,
        'blendshape_names': {
            "Basis": None,
            "browInnerDnL": None,
            "browInnerDnR": None,
            "browInnerUpL": None,
            "browInnerUpR": None,
            "browOuterDnL": None,
            "browOuterDnR": None,
            "browOuterUpL": None,
            "browOuterUpR": None,
            "browSqueezeL": None,
            "browSqueezeR": None,
            "cheekBlowL": None,
            "cheekBlowR": None,
            "cheekUpL": None,
            "cheekUpR": None,
            "eyeBlinkL": None,
            "eyeBlinkR": None,
            "eyeCompressL": None,
            "eyeCompressR": None,
            "eyeDn": None,
            "eyeL": None,
            "eyeR": None,
            "eyeSquintL": None,
            "eyeSquintR": None,
            "eyeUp": None,
            "eyeWidenLowerL": None,
            "eyeWidenLowerR": None,
            "eyeWidenUpperL": None,
            "eyeWidenUpperR": None,
            "jawClenchL": None,
            "jawClenchR": None,
            "jawIn": None,
            "jawL": None,
            "jawOpen": None,
            "jawOut": None,
            "jawR": None,
            "lipChinRaiserL": None,
            "lipChinRaiserR": None,
            "lipCloseLower": None,
            "lipCloseUpper": None,
            "lipCornerDnL": None,
            "lipCornerDnR": None,
            "lipCornerUpL": None,
            "lipCornerUpR": None,
            "lipDimplerL": None,
            "lipDimplerR": None,
            "lipFunnelerLower": None,
            "lipFunnelerUpper": None,
            "lipLowerDnL": None,
            "lipLowerDnR": None,
            "lipLowerPullDnL": None,
            "lipLowerPullDnR": None,
            "lipLowerUpL": None,
            "lipLowerUpR": None,
            "lipNarrowL": None,
            "lipNarrowR": None,
            "lipPoutLower": None,
            "lipPoutUpper": None,
            "lipPresserL": None,
            "lipPresserR": None,
            "lipPucker": None,
            "lipPullL": None,
            "lipPullR": None,
            "lipPushLower": None,
            "lipPushUpper": None,
            "lipSmileClosedL": None,
            "lipSmileClosedR": None,
            "lipSmileOpenL": None,
            "lipSmileOpenR": None,
            "lipSneerL": None,
            "lipSneerR": None,
            "lipStickyL": None,
            "lipStickyR": None,
            "lipSuckLower": None,
            "lipSuckUpper": None,
            "lipSwingL": None,
            "lipSwingR": None,
            "lipTightnerL": None,
            "lipTightnerR": None,
            "lipUpperDnL": None,
            "lipUpperDnR": None,
            "lipUpperUpL": None,
            "lipUpperUpR": None,
            "lipWidenL": None,
            "lipWidenR": None,
            "noseCompress": None,
            "noseFlare": None,
            "noseSneerL": None,
            "noseSneerR": None,
            "noseWrinklerL": None,
            "noseWrinklerR": None,
        },
    },
}

face_rig_template = {
    "bone_name": None,
    "horizontal_rotation_axis": None,
    "vertical_rotation_axis": None,
    "horizontal_min_max_value": [None, None],  # Left, Right
    "vertical_min_max_value": [None, None],  # Down, Up
}

# WD bones, unrealEngine bones, daz3d bones, character creator 4,
retargeting_templates_names = ['Wonder Dynamics', 'Unreal Engine', 'DAZ 3d', 'Character Creator 4', 'Quick Rig']
retargeting_templates = {
    'Hips': ['Hips', 'pelvis', 'hip', 'CC_Base_Hip', 'QuickRigCharacter_Hips'],
    'LeftUpLeg': ['LeftUpLeg', 'thigh_l', 'lThigh', 'CC_Base_L_Thigh', 'QuickRigCharacter_LeftUpLeg'],
    'RightUpLeg': ['RightUpLeg', 'thigh_r', 'rThigh', 'CC_Base_R_Thigh', 'QuickRigCharacter_RightUpLeg'],
    'Spine': ['Spine', 'spine_03', 'abdomen', 'CC_Base_Waist', 'QuickRigCharacter_Spine'],
    'LeftLeg': ['LeftLeg', 'calf_l', 'lShin', 'CC_Base_L_Calf', 'QuickRigCharacter_LeftLeg'],
    'RightLeg': ['RightLeg', 'calf_r', 'rShin', 'CC_Base_R_Calf', 'QuickRigCharacter_RightLeg'],
    'Spine1': ['Spine1', 'spine_04', 'abdomen2', 'CC_Base_Spine01', 'QuickRigCharacter_Spine1'],
    'LeftFoot': ['LeftFoot', 'foot_l', 'lFoot', 'CC_Base_L_Foot', 'QuickRigCharacter_LeftFoot'],
    'RightFoot': ['RightFoot', 'foot_r', 'rFoot', 'CC_Base_R_Foot', 'QuickRigCharacter_RightFoot'],
    'Spine2': ['Spine2', 'spine_05', 'chest', 'CC_Base_Spine02', 'QuickRigCharacter_Spine2'],
    'LeftToeBase': ['LeftToeBase', 'ball_l', 'lToe', 'CC_Base_L_ToeBase', 'QuickRigCharacter_LeftToeBase'],
    'RightToeBase': ['RightToeBase', 'ball_r', 'rToe', 'CC_Base_R_ToeBase', 'QuickRigCharacter_RightToeBase'],
    'Neck': ['Neck', 'neck_01', 'neck', 'CC_Base_NeckTwist01', 'QuickRigCharacter_Neck'],
    'LeftShoulder': ['LeftShoulder', 'clavicle_l', 'lCollar', 'CC_Base_L_Clavicle', 'QuickRigCharacter_LeftShoulder'],
    'RightShoulder': ['RightShoulder', 'clavicle_r', 'rCollar', 'CC_Base_R_Clavicle', 'QuickRigCharacter_RightShoulder'],
    'Head': ['Head', 'head', 'head', 'CC_Base_Head', 'QuickRigCharacter_Head'],
    'LeftArm': ['LeftArm', 'upperarm_l', 'lShldr', 'CC_Base_L_Upperarm', 'QuickRigCharacter_LeftArm'],
    'RightArm': ['RightArm', 'upperarm_r', 'rShldr', 'CC_Base_R_Upperarm', 'QuickRigCharacter_RightArm'],
    'LeftForeArm': ['LeftForeArm', 'lowerarm_l', 'lForeArm', 'CC_Base_L_Forearm', 'QuickRigCharacter_LeftForeArm'],
    'RightForeArm': ['RightForeArm', 'lowerarm_r', 'rForeArm', 'CC_Base_R_Forearm', 'QuickRigCharacter_RightForeArm'],
    'LeftHand': ['LeftHand', 'hand_l', 'lHand', 'CC_Base_L_Hand', 'QuickRigCharacter_LeftHand'],
    'RightHand': ['RightHand', 'hand_r', 'rHand', 'CC_Base_R_Hand', 'QuickRigCharacter_RightHand'],
    'LeftHandIndex1': ['LeftHandIndex1', 'index_01_l', 'lIndex1', 'CC_Base_L_Index1', 'QuickRigCharacter_LeftHandIndex1'],
    'LeftHandIndex2': ['LeftHandIndex2', 'index_02_l', 'lIndex2', 'CC_Base_L_Index2', 'QuickRigCharacter_LeftHandIndex2'],
    'LeftHandIndex3': ['LeftHandIndex3', 'index_03_l', 'lIndex3', 'CC_Base_L_Index3', 'QuickRigCharacter_LeftHandIndex3'],
    'LeftHandMiddle1': ['LeftHandMiddle1', 'middle_01_l', 'lMid1', 'CC_Base_L_Mid1', 'QuickRigCharacter_LeftHandMiddle1'],
    'LeftHandMiddle2': ['LeftHandMiddle2', 'middle_02_l', 'lMid2', 'CC_Base_L_Mid2', 'QuickRigCharacter_LeftHandMiddle2'],
    'LeftHandMiddle3': ['LeftHandMiddle3', 'middle_03_l', 'lMid3', 'CC_Base_L_Mid3', 'QuickRigCharacter_LeftHandMiddle3'],
    'LeftHandPinky1': ['LeftHandPinky1', 'pinky_01_l', 'lPinky1', 'CC_Base_L_Pinky1', 'QuickRigCharacter_LeftHandPinky1'],
    'LeftHandPinky2': ['LeftHandPinky2', 'pinky_02_l', 'lPinky2', 'CC_Base_L_Pinky2', 'QuickRigCharacter_LeftHandPinky2'],
    'LeftHandPinky3': ['LeftHandPinky3', 'pinky_03_l', 'lPinky3', 'CC_Base_L_Pinky3', 'QuickRigCharacter_LeftHandPinky3'],
    'LeftHandRing1': ['LeftHandRing1', 'ring_01_l', 'lRing1', 'CC_Base_L_Ring1', 'QuickRigCharacter_LeftHandRing1'],
    'LeftHandRing2': ['LeftHandRing2', 'ring_02_l', 'lRing2', 'CC_Base_L_Ring2', 'QuickRigCharacter_LeftHandRing2'],
    'LeftHandRing3': ['LeftHandRing3', 'ring_03_l', 'lRing3', 'CC_Base_L_Ring3', 'QuickRigCharacter_LeftHandRing3'],
    'LeftHandThumb1': ['LeftHandThumb1', 'thumb_01_l', 'lThumb1', 'CC_Base_L_Thumb1', 'QuickRigCharacter_LeftHandThumb1'],
    'LeftHandThumb2': ['LeftHandThumb2', 'thumb_02_l', 'lThumb2', 'CC_Base_L_Thumb2', 'QuickRigCharacter_LeftHandThumb2'],
    'LeftHandThumb3': ['LeftHandThumb3', 'thumb_03_l', 'lThumb3', 'CC_Base_L_Thumb3', 'QuickRigCharacter_LeftHandThumb3'],
    'RightHandIndex1': ['RightHandIndex1', 'index_01_r', 'rIndex1', 'CC_Base_R_Index1', 'QuickRigCharacter_RightHandIndex1'],
    'RightHandIndex2': ['RightHandIndex2', 'index_02_r', 'rIndex2', 'CC_Base_R_Index2', 'QuickRigCharacter_RightHandIndex2'],
    'RightHandIndex3': ['RightHandIndex3', 'index_03_r', 'rIndex3', 'CC_Base_R_Index3', 'QuickRigCharacter_RightHandIndex3'],
    'RightHandMiddle1': ['RightHandMiddle1', 'middle_01_r', 'rMid1', 'CC_Base_R_Mid1', 'QuickRigCharacter_RightHandMiddle1'],
    'RightHandMiddle2': ['RightHandMiddle2', 'middle_02_r', 'rMid2', 'CC_Base_R_Mid2', 'QuickRigCharacter_RightHandMiddle2'],
    'RightHandMiddle3': ['RightHandMiddle3', 'middle_03_r', 'rMid3', 'CC_Base_R_Mid3', 'QuickRigCharacter_RightHandMiddle3'],
    'RightHandPinky1': ['RightHandPinky1', 'pinky_01_r', 'rPinky1', 'CC_Base_R_Pinky1', 'QuickRigCharacter_RightHandPinky1'],
    'RightHandPinky2': ['RightHandPinky2', 'pinky_02_r', 'rPinky2', 'CC_Base_R_Pinky2', 'QuickRigCharacter_RightHandPinky2'],
    'RightHandPinky3': ['RightHandPinky3', 'pinky_03_r', 'rPinky3', 'CC_Base_R_Pinky3', 'QuickRigCharacter_RightHandPinky3'],
    'RightHandRing1': ['RightHandRing1', 'ring_01_r', 'rRing1', 'CC_Base_R_Ring1', 'QuickRigCharacter_RightHandRing1'],
    'RightHandRing2': ['RightHandRing2', 'ring_02_r', 'rRing2', 'CC_Base_R_Ring2', 'QuickRigCharacter_RightHandRing2'],
    'RightHandRing3': ['RightHandRing3', 'ring_03_r', 'rRing3', 'CC_Base_R_Ring3', 'QuickRigCharacter_RightHandRing3'],
    'RightHandThumb1': ['RightHandThumb1', 'thumb_01_r', 'rThumb1', 'CC_Base_R_Thumb1', 'QuickRigCharacter_RightHandThumb1'],
    'RightHandThumb2': ['RightHandThumb2', 'thumb_02_r', 'rThumb2', 'CC_Base_R_Thumb2', 'QuickRigCharacter_RightHandThumb2'],
    'RightHandThumb3': ['RightHandThumb3', 'thumb_03_r', 'rThumb3', 'CC_Base_R_Thumb3', 'QuickRigCharacter_RightHandThumb3'],
}

# Pairs for checking IK chains
ik_pairs = {
        'leftArm' : {
            'keys':['LeftArm','LeftHand'],
            'status': None
        },
        'rightArm' : {
            'keys':['RightArm','RightHand'],
            'status': None
        },
        'leftLeg' : {
            'keys':['LeftUpLeg','LeftFoot'],
            'status': None
        },
        'rightLeg' : {
            'keys':['RightUpLeg','RightFoot'],
            'status': None
        }
    }

# Nodes that will fail a construction history check
history_nodes = ['deleteComponent', 'geometryFilter', 'polyBase']