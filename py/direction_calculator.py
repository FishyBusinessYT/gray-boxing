import numpy as np

def get_direction(v1, v2):
    dirVector = v1 - v2
    return dirVector / np.linalg.norm(dirVector)

def rotate_vector(vector, sin_angle, cos_angle):
    # Rotate the vector around the y-axis (feet to head) to make it "face" the camera
    rotation_matrix = np.array([[cos_angle, 0, sin_angle],
                                [0, 1, 0],
                                [-sin_angle, 0, cos_angle]])
    return rotation_matrix @ vector

def calculate_player_rotation_offset(pose_world_landmarks):
    """Returns sin_angle, cos_angle"""

    # First, get the front vector of the player, which comes from the cross product
    # Transpose them all to get column vectors
    left_shoulder = np.array([pose_world_landmarks[12].x, pose_world_landmarks[12].y, pose_world_landmarks[12].z]).T
    right_shoudler = np.array([pose_world_landmarks[11].x, pose_world_landmarks[11].y, pose_world_landmarks[11].z]).T
    left_hip = np.array([pose_world_landmarks[24].x, pose_world_landmarks[24].y, pose_world_landmarks[24].z]).T
    # Make the left shoulder the coordinate origin
    right_shoudler -= left_shoulder
    left_hip -= left_shoulder
    # Calculate the front vector
    player_front = np.cross(right_shoudler, left_hip)
    # Project the front vector onto the xz plane, and calculate the angle between it and the z-axis
    player_front[1] = 0
    camera_front = np.array([0, 0, 1])

    player_front_norm = np.linalg.norm(player_front)
    camera_front_norm = np.linalg.norm(camera_front)

    # Sin angle calculation explained in math_docs
    # The signed length of the cross product is in the y-component of it. If I used the norm, I would loose the sign
    sin_angle = np.cross(player_front, camera_front)[1] / (player_front_norm * camera_front_norm)
    cos_angle = np.dot(player_front, camera_front) / (player_front_norm * camera_front_norm)
    return sin_angle, cos_angle

def calculate_directions(landmarks, sin_angle, cos_angle):
    nodes = {
        'head': np.array([landmarks[0].x, landmarks[0].y, landmarks[0].z]),
        'neck': (np.array([landmarks[11].x, landmarks[11].y, landmarks[11].z]) + np.array([landmarks[12].x, landmarks[12].y, landmarks[12].z])) / 2,
        'l_sh': np.array([landmarks[12].x, landmarks[12].y, landmarks[12].z]),
        'l_el': np.array([landmarks[14].x, landmarks[14].y, landmarks[14].z]),
        'l_wr': np.array([landmarks[16].x, landmarks[16].y, landmarks[16].z]),
        'l_ha': np.array([landmarks[20].x, landmarks[20].y, landmarks[20].z]),
        'r_sh': np.array([landmarks[11].x, landmarks[11].y, landmarks[11].z]),
        'r_el': np.array([landmarks[13].x, landmarks[13].y, landmarks[13].z]),
        'r_wr': np.array([landmarks[15].x, landmarks[15].y, landmarks[15].z]),
        'r_ha': np.array([landmarks[19].x, landmarks[19].y, landmarks[19].z]),
        'l_hi': np.array([landmarks[24].x, landmarks[24].y, landmarks[24].z]),
        'l_kn': np.array([landmarks[26].x, landmarks[26].y, landmarks[26].z]),
        'l_an': np.array([landmarks[28].x, landmarks[28].y, landmarks[28].z]),
        'l_he': np.array([landmarks[30].x, landmarks[30].y, landmarks[30].z]),
        'l_to': np.array([landmarks[32].x, landmarks[32].y, landmarks[32].z]),
        'r_hi': np.array([landmarks[23].x, landmarks[23].y, landmarks[23].z]),
        'r_kn': np.array([landmarks[25].x, landmarks[25].y, landmarks[25].z]),
        'r_an': np.array([landmarks[27].x, landmarks[27].y, landmarks[27].z]),
        'r_he': np.array([landmarks[29].x, landmarks[29].y, landmarks[29].z]),
        'r_to': np.array([landmarks[31].x, landmarks[31].y, landmarks[31].z]),
        'eye': np.array([landmarks[7].x, landmarks[7].y, landmarks[7].z])
        }

    # First rotate the vectors, and then make their directions relative
    for key in nodes:
        nodes[key] = rotate_vector(nodes[key], sin_angle, cos_angle)

    return [
        *get_direction(nodes['neck'], nodes['head']),  # neck_head
        *get_direction(nodes['l_sh'], nodes['r_sh']),  # l_shoulder_shoulder
        *get_direction(nodes['l_sh'], nodes['l_el']),  # l_shoulder_elbow
        *get_direction(nodes['l_el'], nodes['l_wr']),  # l_elbow_wrist
        *get_direction(nodes['l_wr'], nodes['l_ha']),  # l_wrist_hand
        *get_direction(nodes['r_sh'], nodes['r_el']),  # r_shoulder_elbow
        *get_direction(nodes['r_el'], nodes['r_wr']),  # r_elbow_wrist
        *get_direction(nodes['r_wr'], nodes['r_ha']),  # r_wrist_hand
        *get_direction(nodes['l_sh'], nodes['l_hi']),  # l_shoulder_hip
        *get_direction(nodes['r_sh'], nodes['r_hi']),  # r_shoulder_hip
        *get_direction(nodes['l_hi'], nodes['r_hi']),  # l_hip_hip
        *get_direction(nodes['l_hi'], nodes['l_kn']),  # l_hip_knee
        *get_direction(nodes['l_kn'], nodes['l_an']),  # l_knee_ankle
        *get_direction(nodes['l_he'], nodes['l_to']),  # l_heel_toe
        *get_direction(nodes['r_hi'], nodes['r_kn']),  # r_hip_knee
        *get_direction(nodes['r_kn'], nodes['r_an']),  # r_knee_ankle
        *get_direction(nodes['r_he'], nodes['r_to']),  # r_heel_toe
        *get_direction(nodes['head'], nodes['eye'])    # head_r_eye
        ]
