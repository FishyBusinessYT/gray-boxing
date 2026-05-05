extends Node
class_name PlayerController

const PORT = 52346
const PACKET_SIZE = 17 * 3 * 4  # 17 vectors * 3 axes * 4-bytes per float

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
    "r_heel_toe": Vector3()
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

func _exit_tree() -> void:
    udp.close()
