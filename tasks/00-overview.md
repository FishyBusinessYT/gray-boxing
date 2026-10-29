# Gray Boxing demo — task slices

## Event constraints
- Deadline: November 12, 2026.
- Rounds: 1 minute, strangers playing all day.
- Play space: 4 m².
- Display: 1920x1080 projector.
- Runtime: exported Linux build on the development machine.
- Required loop: start, mirror, punch, score, 60s end, name entry, save, restart without relaunch.

## Slice order
| # | Slice | Priority | Needs |
|---|---|---|---|
| 1 | Avatar stage | P1 | none |
| 2 | Punch, DP, score | P1 | S1 |
| 3 | 60-second round, game over, restart, pause | P1 | S2 |
| 4 | Exportable Linux build | P1 | S3 |
| 5 | Injury engine | P2 | S2 |
| 6 | Name entry, JSON persistence, in-game leaderboard | P2 | S3, S5 |
| 7 | HTML live leaderboard | P2 | S6 |
| 8 | Spanish UI pass | P2 | S3, S6 |
| 9 | Audio | P3 | S2, S3 |
| 10 | Trauma report list | P3 | S5, S6 |
| 11 | `plyr404` freeze and out-of-frame overlay | P4 | S1 |
| 12 | Dummy feedback | P4 | S2, S5 |
| 13 | Menu completeness and navigation | P4 | S3 |
| 14 | Responsive UI | P4 | S8, S10, S11, S13 |
| 15 | Art and beautify | P5 | S12, S13, S14 |
| 16 | Event dry run | gate | all |

## Guardrails
- Hardware and the feedback system are out of scope.
- Backend changes are out of scope except fixes. The Godot side must handle `plyr404`; do not add backend endpoints.
- I18n and translation systems are out of scope. Spanish copy is hardcoded.
- Keep the box-based gray-boxing look. S15 improves materials, lighting, and art without replacing the boxes.
- Every slice after S8 ships Spanish copy.
