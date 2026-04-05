extends Node2D

const PORT = 52346
const EXPECTED_FLOATS = 57  # 19 directions × 3 components
const EXPECTED_BYTES = EXPECTED_FLOATS * 4  # 32-bit floats

var udp := PacketPeerUDP.new()
var directions := {}

const DIRECTION_KEYS = [
	"neck_head",
	"l_shoulder_shoulder", "l_shoulder_elbow", "l_elbow_wrist", "l_wrist_hand",
	"r_shoulder_elbow", "r_elbow_wrist", "r_wrist_hand",
	"l_shoulder_hip", "r_shoulder_hip",
	"l_hip_hip", "l_hip_knee", "l_knee_ankle", "l_ankle_heel", "l_ankle_toe",
	"r_hip_knee", "r_knee_ankle", "r_ankle_heel", "r_ankle_toe",
]

func _ready():
	udp.bind(PORT, '127.0.0.1')

func _process(_delta):
	if udp.get_available_packet_count() == 0:
		return

	var packet := udp.get_packet()
	if packet.size() != EXPECTED_BYTES:
		return

	var raw := packet.to_float32_array()
	for i in DIRECTION_KEYS.size():
		directions[DIRECTION_KEYS[i]] = Vector3(
			raw[i * 3],
			raw[i * 3 + 1],
			raw[i * 3 + 2]
		)
	
	$Label.text = str(directions)
