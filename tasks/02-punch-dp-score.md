# S2 — Punch, DP, score

## Outcome
Hands hit the dummy. Each hit produces DP and adds to the round score. Live score is visible. Avatar takes no damage.

## Acceptance
- Hand contact with a dummy segment registers one hit event.
- Contact from non-hand avatar parts deals no damage.
- Avatar suffers no damage.
- DP is derived from collision strength and clamped to 0-100.
- Repeated hits in quick succession yield lower DP scores.
- Score equals the sum of final per-hit DP for the round.
- All dummy segments register separately: `RChest`, `LChest`, `Abdomen`, `Head`.
- Score HUD updates during the round.

## Current base
- `Scripts/dummy.gd` receives `body_shape_entered` and prints the segment only.
- The dummy is a `RigidBody3D` with four collision shapes and contact monitoring enabled.
- No score or damage calculation exists.

## Notes
- Locked score rule: total DP dealt in the round, per-hit cap 100, decay applied before sum.
- Decay window and curve are tuning constants; the required behavior is that rapid repeats score less.
- Do not add dummy health or a knockout state.
- DP cap applies per hit, not to the round total.
- Injury selection is S5. Dummy visual damage is S12.
