# S1 — Avatar stage

## Outcome
Start a round from the main menu. Avatar and dummy appear. Avatar mirrors the player from the hips up. Both fit the 1920x1080 projector frame.

## Acceptance
- Main menu start button spawns the game scene with both avatar and dummy.
- Avatar tracks live pose data for hips, torso, head, and arms.
- No leg geometry or leg bones exist in the avatar.
- Player legs leaving the frame is not a problem.
- Dummy stays still when untouched.
- At 1920x1080, the avatar is fully inside the frame and not oversized.
- Dummy is reachable from the avatar's hands and its screen area is not larger than the avatar's.
- No backend change is required.

## Current base
- `Scenes/character.tscn` is WIP, includes legs, and pairs `fully_constrained.gd` with incompatible node types.
- `Scripts/player_controller.gd` already receives 54-float UDP pose packets.
- `Scenes/game_scene.tscn` already has the dummy, camera at `(0, 6, 11)` with 40° FOV, and a floor.
- Main menu and game-scene flow exist in `Scripts/ui_controller.gd`.

## Notes
- This slice owns the avatar representation decision. Resolve the scene/script mismatch before building further.
- Avatar translation is not tracked; only body directions arrive from the backend. The avatar remains anchored for the round.
- Dummy immobility is part of this slice; springy reaction is S12.
- Framing is functional here; final art and final framing check are S15.
- Dummy hit detection and scoring are S2.
