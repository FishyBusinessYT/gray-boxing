---
task_name: avatar-stage
description: S1 — hips-up avatar mirrors live pose; dummy staged and frozen; 1920x1080 framing.
---

## 1. Task Brief

### Problem Statement
Players cannot see themselves in a round. The game scene has no working avatar. The WIP avatar includes legs, and it pairs `fully_constrained.gd` (`BoneAttachment3D`) with `RigidBody3D` nodes, so the scene is invalid. The dummy has no confirmed rest behavior, staging, or hand reach. Without a valid hips-up avatar and a reachable dummy, the punch and score loop cannot start.

### Expected Outcome
The main menu Start game button opens the game scene with a hips-up avatar and a dummy. The avatar mirrors the live player pose for hips, torso, head, and both arms. It has no legs. Both fit the 1920x1080 projector frame. The dummy is reachable from the avatar's hands and stays still when untouched.

### Acceptance Criteria
1. Project base window is 1920x1080 at launch.
2. Main menu Start game opens `Scenes/game_scene.tscn` with both the avatar and the dummy visible.
3. Avatar root stays fixed at one world anchor for the whole round. Pose data never translates it.
4. A synthetic 54-float UDP packet with changed upper-body vectors visibly changes hips, torso, head, and both arms on the next processed frame.
5. One live backend check confirms the same pose tracking with a real player.
6. Head follows `neck_head` for tilt and `head_r_eye` for yaw/twist. If `head_r_eye` is zero, head falls back to `neck_head`.
7. Spawned avatar has no leg geometry, meshes, nodes, or bones. Its scene tree contains no thigh, shin, calf, or foot parts.
8. Leg direction vectors are ignored. No backend file or packet format changes.
9. Dummy stays still when untouched. It does not drift, fall, or self-move.
10. Manual 1920x1080 framing check passes at rest and with arms extended: avatar and dummy fully inside the frame with clear margin; avatar does not dominate the frame; dummy screen area is no larger than the avatar's.
11. Manual reach check passes: from the fixed anchor, arms reach forward and at least one hand visibly touches or overlaps the dummy front surface. The avatar does not translate.
12. Avatar shows a neutral pose before the first valid pose packet. It does not disappear or error.
13. Existing 5-second placeholder timer and game-over flow remain unchanged. S3 owns round duration and game over.

### Out of Scope
- Punch hit detection, DP, score, and dummy recoil (S2, S12).
- 60-second round, game over, restart, and pause (S3).
- `plyr404` freeze and out-of-frame overlay (S11).
- Final art, materials, lighting, and final framing pass (S15).
- Spanish UI (S8), audio (S9), leaderboard and persistence (S6, S7), and export (S4).
- Backend changes.
- Avatar locomotion or world translation.
- Player leg geometry or leg tracking.
- Dummy injury and damage visuals (S5, S12).

## 2. Context

### Codebase
<!-- bullet list · required -->
- `<path or module>` — <why it matters>

### Conventions & Prior Art
<!-- bullet list · optional -->
- <Pattern, ADR, or past work> — <how it applies>

### Related Work
<!-- bullet list · optional -->
- <Ticket / PR / branch> — <relationship>

### External References
<!-- bullet list · optional -->
- <Doc / API / spec> — <what it's needed for>

### Constraints
<!-- bullet list · optional -->
- <constraint>

## 3. Decision Log
<!-- bullet list · required -->
- **Q1** — Task name: `avatar-stage`.
- **Q2** — Avatar representation: two half-built paths exist. S1 selects the path that best fits the constraints and builds on it. The exact representation stays a Step 2/3 design decision.
- **Q3** — Head tracking: full head orientation. `neck_head` gives tilt; `head_r_eye` gives yaw/twist; a zero eye vector falls back to `neck_head`.
- **Q4** — Framing check: manual visual check at 1920x1080. Both avatar and dummy fully inside with clear margin; avatar not dominating; dummy screen area no larger than the avatar's.
- **Q5** — Reachability: manual visual check. From the fixed anchor, arms reach forward; at least one hand touches or overlaps the dummy front surface; avatar does not translate.
- **Q6** — Staging: S1 may move the camera, avatar anchor, and dummy. Dummy is fully frozen until S12.
- **Q7** — Base resolution: project base window is set to 1920x1080. S14 handles other sizes.
- **Q8** — Pose verification: synthetic 54-float UDP packets for repeatable checks, plus one live backend check.
- **Q9** — Framing check scope: both avatar and dummy, at rest and with arms extended.
- **Q10** — Round timer: leave the 5-second placeholder timer and game-over flow untouched. S3 owns round duration and game over.
- **Q11** — Avatar base paths: confirmed `character.tscn` (RigidBody3D plus `fully_constrained.gd`) and `character_ar_test.tscn` (Skeleton3D plus BoneAttachment3D) are the two paths.
