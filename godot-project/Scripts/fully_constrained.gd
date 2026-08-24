extends BoneAttachment3D

@export_enum(
    "l_foot", "l_thigh", "r_foot", "r_thigh", 
    "l_hand", "l_forearm", "l_upper_arm", "r_hand", "r_forearm", "r_upper_arm",
    "head", "torso", "hips"
) var body_part: String
@export var controller: PlayerController

@export var disabled := false
@export var bone_axis := Vector3.UP

func _vecs_to_basis(x, y, z):
    var basis: Basis
    if x == null:
        basis = Basis(y.cross(z), y, z)
    elif y == null:
        basis = Basis(x, z.cross(x), z)
    elif z == null:
        basis = Basis(x, y, x.cross(y))
    else:
        push_error("All vectors are 0")
    basis = basis.orthonormalized()
    return basis

func _build_basis_for_body_part():
    var parts = controller.directions
    
    match body_part:
        "l_foot":
            return _vecs_to_basis(null, parts["l_knee_ankle"] * (-1), parts["l_heel_toe"])
        "l_thigh":
            return _vecs_to_basis(parts["l_hip_hip"] * (-1), parts["l_hip_knee"], null)
        "r_foot":
            return _vecs_to_basis(null, parts["r_knee_ankle"] * (-1), parts["r_heel_toe"])
        "r_thigh":
            return _vecs_to_basis(parts["l_hip_hip"], parts["r_hip_knee"] * (-1), null)
        "torso":
            return _vecs_to_basis(parts["l_shoulder_shoulder"] * (-1), parts["l_shoulder_hip"] * (-1), null)
        "hips":
            return _vecs_to_basis(parts["l_hip_hip"] * (-1), parts["l_shoulder_hip"] * (-1), null)
        "head":
            var u: Vector3 = parts["head_r_eye"] * (-1)
            var v: Vector3 = parts["neck_head"]
            var u_into_v = (u.dot(v) / v.dot(v)) * v # Project u onto v
            var x = u - u_into_v # x is the u vector projected onto the orthogonal subspace of v
            DebugDraw3D.draw_arrow(
                global_position, global_position + u * 3, Color.RED, 0.1
            )
            #return _vecs_to_basis(x, parts["neck_head"], null)
            return Basis(Vector3.ZERO, Vector3.ZERO, Vector3.ZERO)

func _process(_delta: float) -> void:    
    if disabled: return

    var basis = _build_basis_for_body_part()
    if basis == Basis(Vector3.ZERO, Vector3.ZERO, Vector3.ZERO): return;

    #DebugDraw3D.draw_arrow(
        #global_position, global_position + basis.x, Color.RED, 0.1
    #)
    #DebugDraw3D.draw_arrow(
        #global_position, global_position + basis.y, Color.GREEN, 0.1
    #)
    #DebugDraw3D.draw_arrow(
        #global_position, global_position + basis.z, Color.YELLOW, 0.1
    #)

    global_transform.basis = Basis(basis)
