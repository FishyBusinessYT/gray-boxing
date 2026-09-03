extends Node
class_name PlayerController

const PORT = 52346
const PACKET_SIZE = 18 * 3 * 4  # 17 vectors * 3 axes * 4-bytes per float

var udp := PacketPeerUDP.new()
var directions := {
    "neck_head": Vector3(),
    "l_shoulder_shoulder": Vector3(),
    "l_shoulder_elbow": Vector3(),
    "l_elbow_wrist": Vector3(),
    "l_wrist_hand": Vector3(),
    "r_shoulder_elbow": Vector3(),
    "r_elbow_wrist": Vector3(),
    "r_wrist_hand": Vector3(),
    "l_shoulder_hip": Vector3(),
    "r_shoulder_hip": Vector3(),
    "l_hip_hip": Vector3(),
    "l_hip_knee": Vector3(),
    "l_knee_ankle": Vector3(),
    "l_heel_toe": Vector3(),
    "r_hip_knee": Vector3(),
    "r_knee_ankle": Vector3(),
    "r_heel_toe": Vector3(),
    "head_r_eye": Vector3()
}


func _ready():
    udp.bind(PORT, "127.0.0.1")

func _process(_delta):
    if udp.get_available_packet_count() == 0:
        return

    var packet := udp.get_packet()
    if packet.size() != PACKET_SIZE:
        return

    var raw := packet.to_float32_array()
    for i in directions.size():
        var key = directions.keys()[i]
        directions[key] = Vector3(raw[i * 3], raw[i * 3 + 1], raw[i * 3 + 2])
    
    # Manually invert some vectors components so the player related stuff works
    directions["l_shoulder_hip"].y *= -1
    directions["l_shoulder_elbow"].y *= -1
    directions["r_shoulder_elbow"].y *= -1
    directions["l_elbow_wrist"].y *= -1
    directions["r_elbow_wrist"].y *= -1
    directions["r_hip_knee"].z *= -1
    directions["r_knee_ankle"].z *= -1

func _exit_tree() -> void:
    udp.close()
