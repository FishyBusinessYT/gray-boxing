# AGENTS.md — Gray Boxing

## What this project is

A motion-controlled boxing demo built for a one-minute, event-style game loop
(start → mirror → punch → score → 60s end → name entry → save → restart).

The repository has two halves:

- `godot-project/` — the game itself, made with **Godot 4.7**, **Jolt Physics**
  and the Forward+ renderer.
- `py/` — a Python/MediaPipe pose backend. It reads the camera, computes body
  directions and sends them over UDP to Godot (see `Scripts/player_controller.gd`).
- `tasks/` — design slices and acceptance criteria. Read the relevant slice
  before changing gameplay behaviour; the constraints there are intentional.

The current shell's working directory is `py/`, but most gameplay work happens
under `godot-project/`. Always pass the Godot path explicitly when running tools.

## Godot conventions

- GDScript files use **tabs**, typed variables, typed function signatures and
  `snake_case`.
- Reusable script classes use `class_name` (for example `BodyPart`).
- Project scripts live in `godot-project/Scripts/`; character/attachment
  scripts that belong to a scene live next to that scene under
  `godot-project/Scenes/Character/`.
- Keep the gray-boxing look. Do not replace the box/mesh placeholder art unless
  the task explicitly asks for an art pass.
- The main scene is configured in `godot-project/project.godot`; autoloads are
  `BackendManager` (Python process management) and the MCP game helper.

## Character / ragdoll architecture

`Scenes/Character/character_player.tscn` and
`Scenes/Character/character_enemy.tscn` both contain two parallel rigs:

1. A **Ragdoll** rig: a `PhysicalBoneSimulator3D` with `PhysicalBone3D` children
   that simulate and collide.
2. An **Animator/character** rig: a `Skeleton3D` that drives the visible meshes
   and, for the enemy, the attack animations.

`Scripts/ragdoll.gd` keeps every physical bone close to the animated skeleton
with a spring/damper controller. The enemy's physical bones are on
`collision_layer = 2`; the player's hand rigidbodies have `contact_monitor`
enabled so they can report impacts.

The ragdoll asks each bone for a strength factor before applying its spring
forces. A `BodyPart` whose health is below `weakened_health_ratio` (default
`0.2`) returns `weakened_strength_multiplier` (default `0.5`), so both the
linear impulse and the angular acceleration for that bone are halved. Parts
without the `BodyPart` script (for example the player's bones) always use
`1.0`.

A hit to the head that is strong enough to spawn its particle burst also makes
the **whole** ragdoll limp for a few seconds. `ragdoll.gd` listens to the
head's `strong_hit` signal, sets linear/angular stiffness to `limp_stiffness`
(default `5`) and damping to `limp_damping` (default `1`), then restores the
original values after `limp_duration` (default `3` seconds). Another strong
head hit restarts the timer. While limp, the per-part weakened multiplier is
skipped so all bones use the exact limp values. The player's ragdoll has no
`BodyPart` head, so it never enters this state.

The player's hands are `RigidBody3D` nodes under `Physical Bone LHand` and
`Physical Bone RHand`, running `Scenes/Character/hands.gd`. Each hand is
teleported to its parent physical bone's transform every physics frame.

## Damage system (current implementation)

Damage is **per body part**, not per whole character yet.

### `Scripts/body_part.gd` — `class_name BodyPart extends PhysicalBone3D`

- `@export var max_health: float = 100.0`
- `@export var healthy_color: Color = Color.WHITE`
- `@export var depleted_color: Color = Color.RED`
- `@export var weakened_health_ratio: float = 0.2`
- `@export var weakened_strength_multiplier: float = 0.5`
- `health: float` — initialised to `max_health` in `_ready()`
- `apply_damage(amount: float, source: Node = null) -> float`
  - ignores non-positive damage and already-depleted parts
  - clamps applied damage to the remaining health so health never goes below 0
  - currently reduces `health` by `applied / 10` (user tuning; `max_health`
    therefore lasts about ten full hits)
  - emits `damaged(amount, remaining_health, source)`
  - emits `depleted(source)` once when health reaches 0
  - emits `strong_hit(amount, source)` when the incoming `amount` reaches
    `burst_damage_threshold` (the same condition that spawns the burst)
  - returns the amount actually applied
- Helpers: `get_health_ratio()`, `is_depleted()`, `is_weakened()`,
  `get_ragdoll_strength_multiplier()`, `reset_health()`
  - `is_weakened()` is true when `health / max_health < weakened_health_ratio`
  - `get_ragdoll_strength_multiplier()` returns
    `weakened_strength_multiplier` while weakened, otherwise `1.0`; the ragdoll
    multiplies its linear impulse and angular acceleration by this factor
- Visual feedback: on ready it duplicates the materials of its visible
  `MeshInstance3D` children and tints `albedo_color` from `healthy_color` to
  `depleted_color` as health drops. At full health it is white; at zero health
  it is fully red. Materials are duplicated per part, so tinting one part
  cannot affect another part that shares a source material. Textured
  materials (such as the head) keep their texture and are multiplied by the
  tint.
- Particle burst: `_ready()` also builds a `CPUParticles3D` named
  `DamageBurst` as a child of every part. It is a one-shot, non-emitting
  burst positioned at the visible mesh's global AABB centre when triggered.
  `apply_damage()` spawns it when the incoming `amount` (not the clamped
  applied amount) is `>= burst_damage_threshold` (default `10`). Tunables:
  `burst_damage_threshold`, `burst_amount`, `burst_lifetime`, `burst_speed`,
  `burst_particle_size`, `burst_color`.
  - The emission node uses `top_level = true`, `local_coords = false` and an
    identity basis at spawn time. This matters because the visible meshes are
    scaled up by 100 while the `PhysicalBone3D` is scaled 1:1; without it the
    particle size and direction would be distorted by the mesh scale.
  - The particle mesh is a small unshaded `SphereMesh` using
    `vertex_color_use_as_albedo`, so `burst_color` drives its albedo.

This script is attached to **all 15 enemy `PhysicalBone3D` nodes** in
`Scenes/Character/character_enemy.tscn`. Each part has independent health and
can be tuned through `max_health` in the Inspector.

### `Scenes/Character/hands.gd` — impact force and damage

- Tracks the hand's movement manually because the parent bone teleports the
  `RigidBody3D`; the engine's own `linear_velocity` does not represent punch
  speed.
- On `body_entered`, only acts if the collider is a `BodyPart`:
  - `impact_force = mass * |tracked_velocity - part.linear_velocity|`
  - ignores hits below `minimum_impact_force`
  - `damage = min(impact_force * damage_per_force, maximum_damage)`
  - calls `part.apply_damage(damage, self)`
- Tunables (exported on each hand): `minimum_impact_force`,
  `damage_per_force`, `maximum_damage`.
- `hands.gd` preloads `body_part.gd` as `BodyPartScript` so it does not depend
  on the editor's global-class cache being up to date.

### What is deliberately not implemented yet

- No sounds, stagger, knockout, or injury selection. Health-based white → red
  tinting, threshold particle bursts, weakened ragdoll control and the
  temporary head-hit limp are implemented.
- No aggregate enemy health pool.
- No health on the player avatar or on the practice dummy.

Those belong to later slices. To add reactions, connect to a part's `damaged`
or `depleted` signal instead of changing the damage math.

## Gameplay constraints to preserve

From `tasks/02-punch-dp-score.md`:

- The avatar takes **no damage**.
- The practice dummy (`Scripts/dummy.gd`) must **not** get health or a knockout
  state. Dummy feedback is a later task.
- Score is DP derived from collision strength, not health.

Do not treat the new `BodyPart` health as a score or knockout system on its own.

## Validation

Run from the repository root (or adjust the path):

```sh
godot --headless --path godot-project --check-only --script res://Scripts/body_part.gd
godot --headless --path godot-project --check-only --script res://Scenes/Character/hands.gd
godot --headless --path godot-project --editor --quit
```

`--check-only --script` validates one script without opening the editor. The
editor/import command refreshes the global class cache and scene imports. When
running headless, the `BackendManager` autoload may try to launch the Python
backend and complain about a missing camera; that is unrelated to script or
scene validity.

## Gotchas

- `hands.gd` assigns `global_transform` directly in `_physics_process()`. Keep
  that in mind when adding physics logic: forces/velocities of the hand body
  may not reflect the teleported movement.
- Impact detection requires `contact_monitor = true` and
  `max_contacts_reported > 0` on the hand `RigidBody3D` nodes.
- The enemy's collision bodies are the `PhysicalBone3D` nodes, not the visible
  `BoneAttachment3D` meshes. Add gameplay scripts to the physical bones.
- `DamageBurst` nodes are created procedurally in `BodyPart._ready()`, not
  stored in `character_enemy.tscn`. Do not add them to the scene manually; tune
  the exports instead.
- Inspect `git status`/`git diff` before editing: the working tree can contain
  in-progress user changes, especially in the character scripts and scenes.
