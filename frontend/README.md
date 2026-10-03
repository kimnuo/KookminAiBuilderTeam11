# Frontend feed prototype

This static page implements the Frontend B screens from `docs/PRD.md`: feed filters and sorting, notice details, recommendation reasons, and the P3 preparation panel.

Serve the `frontend/` directory from the same origin as the API so `/api` requests and session cookies reach the backend. The page reads these API routes from the PRD:

- `GET /api/feed?sort=recommend|deadline`
- `GET /api/sources`
- `GET /api/notices/{id}`
- `GET /api/notices/{id}/requirements`

Feed responses may be an array or an object with `items` or `notices`. Recommendation reasons are read from `recommendationReasons`, `reasons`, or `recommendationReason` until the backend contract settles.

The support panel reads profile values only from this browser's `localStorage` key `kmu.profile`. It does not send those values to the API. The profile may contain fields such as `name`, `phone`, `email`, `studentId`, `major`, and `year`. The requirements response should identify the matching profile key in `profileField`, `field`, or `key`, and may include an `evidence` string. Agree on this key and response shape with Frontend A and the backend before integration.

The repo does not yet select a frontend framework or package manager. This prototype uses browser modules and CSS without third-party runtime dependencies; it expects the API to provide real notices and does not include fabricated notice data.
