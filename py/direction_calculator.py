class Vector3:
    def __init__(self, landmark):
        self.x = landmark.x
        self.y = landmark.y
        self.z = landmark.z

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
        if other is not int:
            TypeError()

        result = Vector3(self)
        result.x /= other
        result.y /= other
        result.z /= other

        return result

    def __pow__(self, other):
        if type(other) is not int and type(other) is not float:
            TypeError()

        result = Vector3(self)
        result.x ** other
        result.y ** other
        result.z ** other

        return result


def get_direction(node1, node2):
    dirVector = node1 - node2
    dirVectorLength = abs((dirVector ** 2).sum()) ** (1/2)

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
        'l_shoulder': Vector3(landmarks[11]),
        'r_shoulder': Vector3(landmarks[12]),
        'l_elbow': Vector3(landmarks[13]),
        'r_elbow': Vector3(landmarks[14]),
        'l_wrist': Vector3(landmarks[15]),
        'r_wrist': Vector3(landmarks[16]),
        'l_hand': Vector3(landmarks[19]),
        'r_hand': Vector3(landmarks[20]),
        'l_hip': Vector3(landmarks[23]),
        'r_hip': Vector3(landmarks[24]),
        'l_knee': Vector3(landmarks[25]),
        'r_knee': Vector3(landmarks[26]),
        'l_ankle': Vector3(landmarks[27]),
        'r_ankle': Vector3(landmarks[28]),
        'l_heel': Vector3(landmarks[29]),
        'r_heel': Vector3(landmarks[30]),
        'l_toe': Vector3(landmarks[31]),
        'r_toe': Vector3(landmarks[32]),
        }

    return {
        "neck_head": get_direction(nodes['neck'], nodes['head']),
        "l_shoulder_shoulder": get_direction(nodes['l_shoulder'], nodes['r_shoulder']),
        "l_shoulder_elbow": get_direction(nodes['l_shoulder'], nodes['l_elbow']),
        "l_elbow_wrist": get_direction(nodes['l_elbow'], nodes['l_wrist']),
        "l_wrist_hand": get_direction(nodes['l_wrist'], nodes['l_hand']),
        "r_shoulder_elbow": get_direction(nodes['r_shoulder'], nodes['r_elbow']),
        "r_elbow_wrist": get_direction(nodes['r_elbow'], nodes['r_wrist']),
        "r_wrist_hand": get_direction(nodes['r_wrist'], nodes['r_hand']),
        "l_shoulder_hip": get_direction(nodes['l_shoulder'], nodes['l_hip']),
        "r_shoulder_hip": get_direction(nodes['r_shoulder'], nodes['r_hip']),
        "l_hip_hip": get_direction(nodes['l_hip'], nodes['r_hip']),
        "l_hip_knee": get_direction(nodes['l_hip'], nodes['l_knee']),
        "l_knee_ankle": get_direction(nodes['l_knee'], nodes['l_ankle']),
        "l_ankle_heel": get_direction(nodes['l_ankle'], nodes['l_heel']),
        "l_ankle_toe": get_direction(nodes['l_ankle'], nodes['l_toe']),
        "r_hip_knee": get_direction(nodes['r_hip'], nodes['r_knee']),
        "r_knee_ankle": get_direction(nodes['r_knee'], nodes['r_ankle']),
        "r_ankle_heel": get_direction(nodes['r_ankle'], nodes['r_heel']),
        "r_ankle_toe": get_direction(nodes['r_ankle'], nodes['r_toe']),
        }
