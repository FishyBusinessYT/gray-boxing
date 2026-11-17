extends PhysicalBoneSimulator3D

const BodyPartScript := preload("res://Scripts/body_part.gd")

@export var controller_skeleton: Skeleton3D
@export var linear_stiffness: float = 200.0
@export var linear_damping: float = 10.0
@export var angular_stiffness: float = 100.0
@export var angular_damping: float = 5.0

## Stiffness used while the ragdoll is limp after a strong head hit.
@export var limp_stiffness: float = 5.0
## Damping used while the ragdoll is limp after a strong head hit.
@export var limp_damping: float = 1.0
## How long the ragdoll stays limp, in seconds.
@export var limp_duration: float = 3.0

var bones: Array[PhysicalBone3D] = []

var _head_part: BodyPartScript
var _limp_timer: Timer
var _is_limp: bool = false

var _default_linear_stiffness: float
var _default_linear_damping: float
var _default_angular_stiffness: float
var _default_angular_damping: float

@export var highHitPlayer: AudioStreamPlayer

func _ready() -> void:
    bones.assign(get_children().filter(func(c): return c is PhysicalBone3D))
    _default_linear_stiffness = linear_stiffness
    _default_linear_damping = linear_damping
    _default_angular_stiffness = angular_stiffness
    _default_angular_damping = angular_damping
    _setup_limp_timer()
    _connect_head_hit()
    physical_bones_start_simulation()

func _physics_process(delta: float) -> void:
    for b in bones:
        var strength := 1.0
        if not _is_limp and b is BodyPartScript:
            strength = (b as BodyPartScript).get_ragdoll_strength_multiplier()

        var target: Transform3D = (
            controller_skeleton.global_transform
            * controller_skeleton.get_bone_global_pose(b.get_bone_id())
            * b.body_offset
        )

        # Resorte lineal (Hooke): F = k*x - c*v
        var pos_error := target.origin - b.global_position
        var force := linear_stiffness * pos_error - linear_damping * b.linear_velocity
        b.apply_central_impulse(force * delta * strength)

        # Resorte angular (Hooke): α = k*θ - c*ω
        var err_q := target.basis.get_rotation_quaternion() * b.global_transform.basis.get_rotation_quaternion().inverse()
        if err_q.w < 0.0:
            err_q = -err_q # camino más corto
        var rot_error := err_q.get_axis() * err_q.get_angle() # eje * ángulo

        var angular_accel := angular_stiffness * rot_error - angular_damping * b.angular_velocity
        b.angular_velocity += angular_accel * delta * strength

func _setup_limp_timer() -> void:
    _limp_timer = Timer.new()
    _limp_timer.name = "LimpTimer"
    _limp_timer.one_shot = true
    _limp_timer.timeout.connect(_end_limp)
    add_child(_limp_timer)

func _connect_head_hit() -> void:
    for b in bones:
        var part := b as BodyPartScript
        if part != null and part.get_bone_name() == "Head":
            _head_part = part
            _head_part.strong_hit.connect(_on_head_strong_hit)
            return

func _on_head_strong_hit(_amount: float, _source: Node) -> void:
    highHitPlayer.play()
    _start_limp()

## Drops the whole ragdoll to weak settings. While limp, the per-part weakened
## multiplier is skipped so every bone uses exactly `limp_stiffness` and
## `limp_damping`.
func _start_limp() -> void:
    _is_limp = true
    linear_stiffness = limp_stiffness
    linear_damping = limp_damping
    angular_stiffness = limp_stiffness
    angular_damping = limp_damping
    _limp_timer.start(limp_duration)

func _end_limp() -> void:
    if not _is_limp:
        return

    _is_limp = false
    linear_stiffness = _default_linear_stiffness
    linear_damping = _default_linear_damping
    angular_stiffness = _default_angular_stiffness
    angular_damping = _default_angular_damping
