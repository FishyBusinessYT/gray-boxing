class_name BodyPart
extends PhysicalBone3D

const InjuryTable := preload("res://Scripts/injury_table.gd")
const RoundLog := preload("res://Scripts/round_log.gd")

## Group used by the damage HUD to find every damageable body part.
const GROUP := "body_parts"

## Emitted every time this body part takes damage.
signal damaged(amount: float, remaining_health: float, source: Node)
## Emitted once when this body part runs out of health.
signal depleted(source: Node)
## Emitted when an incoming hit is strong enough to spawn a particle burst.
signal strong_hit(amount: float, source: Node)
## Emitted once per damaging hit with the selected injury.
signal injury_sustained(segment: String, damage: float, injury: String, source: Node)

## Health this body part starts with.
@export var max_health: float = 100.0
@export var damage_divisor = 1
## Injury region override. Leave empty to infer it from `bone_name`.
@export var injury_region: String = ""

## Colour used while the part is at full health.
@export var healthy_color: Color = Color.WHITE
## Colour used when the part has no health left.
@export var depleted_color: Color = Color.RED

## Minimum incoming damage that spawns a particle burst.
@export var burst_damage_threshold: float = 40.0
## Number of particles in a burst.
@export var burst_amount: int = 12
## How long each burst particle lives, in seconds.
@export var burst_lifetime: float = 0.4
## Maximum speed of burst particles.
@export var burst_speed: float = 2.0
## Radius of each burst particle in world units.
@export var burst_particle_size: float = 0.08
## Colour of a minimum-intensity burst particle.
@export var burst_color: Color = Color(0.5, 1.0, 0.908, 1.0)
## Colour of a full-intensity burst particle.
@export var burst_hot_color: Color = Color(1.0, 0.2, 0.05)
## Damage that fills the burst intensity range. Larger hits keep maximum visuals.
@export var burst_full_damage: float = 80.0
## Burst spread in degrees at minimum intensity.
@export var burst_min_spread: float = 60.0
## Burst spread in degrees at full intensity.
@export var burst_max_spread: float = 180.0

## Health ratio below which the ragdoll moves this part with reduced strength.
@export var weakened_health_ratio: float = 0.2
## Multiplier applied to the ragdoll's strength while this part is weakened.
@export var weakened_strength_multiplier: float = 0.2

## Current health. Reaches zero when the part is depleted.
var health: float

var _materials: Array[BaseMaterial3D] = []
var _burst: CPUParticles3D
var _burst_mesh: SphereMesh

@export var mediumHitPlayer: AudioStreamPlayer

func _ready() -> void:
    health = max_health
    add_to_group(GROUP)
    _collect_materials()
    _update_tint()
    _setup_burst_particles()

## Subtracts damage from this part and returns how much was actually applied.
## The applied damage is clamped to the remaining health, so health never drops
## below zero and a depleted part ignores further hits.
func apply_damage(amount: float, source: Node = null) -> float:
    if amount <= 0.0 or health <= 0.0:
        return 0.0

    var hit_damage := amount
    amount = amount / damage_divisor

    var applied := minf(amount, health)
    health -= applied / 10
    _update_tint()

    if amount >= burst_damage_threshold:
        _spawn_burst(hit_damage)
        strong_hit.emit(amount, source)
        if !mediumHitPlayer.playing:
            mediumHitPlayer.play()

    var segment := get_bone_name()
    var injury := InjuryTable.get_injury(get_injury_region(), hit_damage)
    RoundLog.record_hit(segment, hit_damage, injury)
    injury_sustained.emit(segment, hit_damage, injury, source)

    damaged.emit(applied, health, source)
    if health <= 0.0:
        depleted.emit(source)

    return applied

## PhysicalBone3D exposes `bone_name` as a dynamic property that GDScript
## cannot reference by identifier on this engine version.
func get_bone_name() -> String:
    return str(get("bone_name"))

## Region used to select an injury. The side suffix ("Forearm.R") is ignored.
func get_injury_region() -> String:
    if not injury_region.is_empty():
        return injury_region
    return InjuryTable.get_region_for_bone(get_bone_name())

func get_health_ratio() -> float:
    if max_health <= 0.0:
        return 0.0
    return health / max_health

func is_depleted() -> bool:
    return health <= 0.0

## True while this part is weak enough for the ragdoll to hold it loosely.
func is_weakened() -> bool:
    return get_health_ratio() < weakened_health_ratio

## Strength factor the ragdoll should use for this part (1.0 normally,
## `weakened_strength_multiplier` once health drops below the threshold).
func get_ragdoll_strength_multiplier() -> float:
    if is_weakened():
        return weakened_strength_multiplier
    return 1.0

func reset_health() -> void:
    health = max_health
    _update_tint()

## Duplicates the part's mesh materials so tinting one body part cannot affect
## another part that happens to share a material.
func _collect_materials() -> void:
    for node in find_children("*", "MeshInstance3D", true, false):
        var mesh_instance := node as MeshInstance3D
        if mesh_instance == null or mesh_instance.mesh == null:
            continue

        for surface in mesh_instance.mesh.get_surface_count():
            var source := mesh_instance.get_active_material(surface)
            var material: BaseMaterial3D
            if source is BaseMaterial3D:
                material = source.duplicate() as BaseMaterial3D
            else:
                material = StandardMaterial3D.new()

            mesh_instance.set_surface_override_material(surface, material)
            _materials.append(material)

func _update_tint() -> void:
    var damage_ratio := 1.0 - get_health_ratio()
    var tint := healthy_color.lerp(depleted_color, damage_ratio)
    for material in _materials:
        material.albedo_color = tint

## Builds a one-shot particle burst owned by this body part. It is created in
## code so every part gets one without adding nodes to the character scene.
func _setup_burst_particles() -> void:
    _burst = CPUParticles3D.new()
    _burst.name = "DamageBurst"
    _burst.top_level = true
    _burst.emitting = false
    _burst.one_shot = true
    _burst.explosiveness = 1.0
    _burst.local_coords = false
    _burst.amount = burst_amount
    _burst.lifetime = burst_lifetime
    _burst.direction = Vector3.UP
    _burst.spread = 180.0
    _burst.gravity = Vector3(0.0, -4.0, 0.0)
    _burst.initial_velocity_min = burst_speed * 0.5
    _burst.initial_velocity_max = burst_speed
    _burst.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
    _burst.emission_sphere_radius = burst_particle_size
    _burst.color = burst_color

    _burst_mesh = SphereMesh.new()
    _burst_mesh.radius = burst_particle_size
    _burst_mesh.height = burst_particle_size * 2.0
    _burst_mesh.radial_segments = 4
    _burst_mesh.rings = 2

    var particle_material := StandardMaterial3D.new()
    particle_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    particle_material.vertex_color_use_as_albedo = true
    _burst_mesh.material = particle_material
    _burst.mesh = _burst_mesh

    add_child(_burst)

## Restarts the burst at the centre of this part's visible mesh. The emission
## node uses an identity basis because the visible meshes are scaled up by 100
## while the physical bone is scaled 1:1.
## `hit_damage` drives the intensity: stronger hits make more, larger, faster
## and hotter particles with a wider spread.
func _spawn_burst(hit_damage: float) -> void:
    if _burst == null:
        return

    var intensity := 1.0
    if burst_full_damage > 0.0:
        intensity = clampf(hit_damage / burst_full_damage, 0.0, 1.0)

    var size_scale := lerpf(0.75, 2.0, intensity)
    var particle_size := burst_particle_size * size_scale

    _burst.amount = maxi(1, roundi(burst_amount * lerpf(0.75, 2.5, intensity)))
    _burst.lifetime = burst_lifetime * lerpf(0.8, 1.8, intensity)
    _burst.spread = lerpf(burst_min_spread, burst_max_spread, intensity)
    _burst.initial_velocity_min = burst_speed * lerpf(0.5, 1.5, intensity)
    _burst.initial_velocity_max = burst_speed * lerpf(1.0, 2.5, intensity)
    _burst.emission_sphere_radius = particle_size
    _burst.color = burst_color.lerp(burst_hot_color, intensity)

    if _burst_mesh != null:
        # Light hits use round sparks; heavy hits stretch them into shards.
        _burst_mesh.radius = particle_size * lerpf(1.0, 0.65, intensity)
        _burst_mesh.height = particle_size * 2.0 * lerpf(1.0, 1.7, intensity)

    var spawn_global := global_position
    var mesh_instance := _first_mesh_instance()
    if mesh_instance != null:
        spawn_global = mesh_instance.global_transform * mesh_instance.get_aabb().get_center()

    _burst.global_transform = Transform3D(Basis.IDENTITY, spawn_global)
    _burst.restart()
    _burst.emitting = true

func _first_mesh_instance() -> MeshInstance3D:
    for node in find_children("*", "MeshInstance3D", true, false):
        var mesh_instance := node as MeshInstance3D
        if mesh_instance != null and mesh_instance.mesh != null:
            return mesh_instance
    return null
