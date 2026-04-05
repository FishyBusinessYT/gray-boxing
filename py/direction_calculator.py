class Vector3:
    def __init__(self, base):
        self.x = base.x
        self.y = base.y
        self.z = base.z

    def sum(self):
        return self.x + self.y + self.z

    def __sub__(self, other):
        result = Vector3(self)
        result.x -= other.x
        result.y -= other.y
        result.z -= other.z

        return result

    def __add__(self, other):
        result = Vector3(self)
        result.x += other.x
        result.y += other.y
        result.z += other.z

        return result

    def __truediv__(self, other):
        if type(other) is not int:
            raise TypeError()

        result = Vector3(self)
        result.x /= other
        result.y /= other
        result.z /= other

        return result

    def __pow__(self, other):
        if type(other) is not int and type(other) is not float:
            raise TypeError()

        result = Vector3(self)
        result.x **= other
        result.y **= other
        result.z **= other

        return result


def get_direction(node1, node2):
    dirVector = node1 - node2
    dirVectorLength = (dirVector ** 2).sum() ** (1/2)

    directionNormalized = [
        dirVector.x / dirVectorLength,
        dirVector.y / dirVectorLength,
        dirVector.z / dirVectorLength
        ]

    return directionNormalized


def calculate_directions(landmarks):
    nodes = {
        'head': Vector3(landmarks[0]),
        'neck': (Vector3(landmarks[11]) + Vector3(landmarks[12])) / 2,
        'l_sh': Vector3(landmarks[11]),
        'r_sh': Vector3(landmarks[12]),
        'l_el': Vector3(landmarks[13]),
        'r_el': Vector3(landmarks[14]),
        'l_wr': Vector3(landmarks[15]),
        'r_wr': Vector3(landmarks[16]),
        'l_ha': Vector3(landmarks[19]),
        'r_ha': Vector3(landmarks[20]),
        'l_hi': Vector3(landmarks[23]),
        'r_hi': Vector3(landmarks[24]),
        'l_kn': Vector3(landmarks[25]),
        'r_kn': Vector3(landmarks[26]),
        'l_an': Vector3(landmarks[27]),
        'r_an': Vector3(landmarks[28]),
        'l_he': Vector3(landmarks[29]),
        'r_he': Vector3(landmarks[30]),
        'l_to': Vector3(landmarks[31]),
        'r_to': Vector3(landmarks[32]),
        }

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
        *get_direction(nodes['l_an'], nodes['l_he']),  # l_ankle_heel
        *get_direction(nodes['l_an'], nodes['l_to']),  # l_ankle_toe
        *get_direction(nodes['r_hi'], nodes['r_kn']),  # r_hip_knee
        *get_direction(nodes['r_kn'], nodes['r_an']),  # r_knee_ankle
        *get_direction(nodes['r_an'], nodes['r_he']),  # r_ankle_heel
        *get_direction(nodes['r_an'], nodes['r_to']),  # r_ankle_toe
        ]
