# Android Integration Guide

This document briefs the future native Android app for **Home Warehouse**. It is a
reference for whoever builds that app — it describes how to talk to the existing
backend REST API and how to keep the app's look-and-feel consistent with the
already-implemented web UI. It does not describe work to be done now; see the
closing section.

The live, authoritative API contract is always the OpenAPI docs served by the
running backend at `/docs` (Swagger UI) and `/openapi.json`. This document is a
curated, human-readable companion to that — if the two ever disagree, trust
`/docs`.

## 1. Architecture overview

- **One backend, two clients.** The FastAPI backend (`backend/app`) exposes a
  single REST API under `/api/v1`. The existing Vue 3 + Tailwind web app and the
  future Android app are both just clients of that same API — there is no
  mobile-specific backend, no GraphQL layer, no BFF.
- **The Android app is the primary client.** It is what the product owner will
  use day-to-day on a Pixel phone (adding items, checking cables in/out, browsing
  locations). The web UI is a secondary fallback, mainly useful for bulk admin
  work (managing users, categories, locations) from a desktop browser.
- **AI inference is on-device, not server-side.** There is deliberately no
  `/items/{id}/analyze` or similar endpoint, and no server-side call to any
  vision/LLM API. The backend's only role regarding AI is to **store metadata
  the app already computed** (`ai_analyzed`, `ai_confidence`, `ai_raw_response`).
  See [Section 4](#4-on-device-ai-flow).
- **Self-hosted, home-network deployment.** This is not a cloud SaaS product.
  The backend + web frontend run via `docker-compose` on a machine on the home
  network (see `docker-compose.yml`, `.env.example`). The Android app talks to
  that machine directly over the LAN (or VPN, if the owner sets one up) — there
  is no public API gateway to assume.

## 2. Base URL & auth flow

### 2.1 Base URL

The backend is fronted by the frontend container's nginx, which reverse-proxies
`/api/` to the FastAPI service. In the default `docker-compose.yml` setup, the
externally exposed port is `${PORT}` (default `8084`, see `.env.example`). So a
typical base URL is:

```
http://<home-server-ip-or-hostname>:8084/api/v1
```

e.g. `http://192.168.1.50:8084/api/v1` or `http://homewarehouse.local:8084/api/v1`
if the host has a resolvable local name.

There is no cloud endpoint and no auto-discovery mechanism implemented today.
**Keep it simple:** add a one-time "Server settings" screen where the user types
the host (IP or hostname) and port once; persist it (e.g. in
`EncryptedSharedPreferences` alongside the token, or plain `SharedPreferences`
since it's not secret). Validate it by hitting `GET /health` (outside the
`/api/v1` prefix, no auth required) or `GET /api/v1/auth/me` once a token exists.

*Stretch idea, not required for v1:* mDNS/NSD (`NsdManager`) could let the app
discover the server automatically if it advertises itself via Bonjour/Avahi on
the LAN. Don't build this up front — manual entry of an IP/hostname is the
simplest thing that works for a single home server and should ship first.

### 2.2 Login

```
POST /api/v1/auth/login
Content-Type: application/json

{ "username": "admin", "password": "changeme-admin-password" }
```

Response `200`:

```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

`401` on bad credentials or a deactivated account (`is_active = false`).

There is **no self-registration endpoint**. Accounts are multi-user with roles
(`admin` / `member` / `viewer`) and are created only by an admin via
`POST /api/v1/users` (see [Section 3.6](#36-users-admin-only)). The Android
app's login screen is just a username + password form posting to
`/auth/login` — there's no "sign up" path to build.

### 2.3 Using the token

Every other endpoint requires:

```
Authorization: Bearer <jwt>
```

Store the JWT in **Android Keystore-backed `EncryptedSharedPreferences`**
(via `androidx.security:security-crypto`), not plain `SharedPreferences` — it's
a long-lived credential, not a session cookie.

Token lifetime is controlled server-side by `ACCESS_TOKEN_EXPIRE_MINUTES`
(default `43200` = 30 days — see `backend/app/config.py`). This is intentionally
long because re-logging-in on a phone repeatedly is annoying for a home app.
Even so, the app **must** handle a `401 Unauthorized` response from any endpoint
by clearing the stored token and routing the user back to the login screen
(token could be expired, revoked by an admin deactivating the user, or the
secret key could have rotated).

`GET /api/v1/auth/me` returns the current user's profile (`id`, `username`,
`role`, `is_active`, `created_at`) — useful right after login to know the
user's role and decide which UI actions to show (e.g. hide checkout/edit actions
for a `viewer`).

## 3. REST endpoint reference

All endpoints below are under the `/api/v1` prefix and require
`Authorization: Bearer <token>` unless noted. Mutating endpoints additionally
require role `member` or `admin` (a `viewer` gets `403 Forbidden`); user
management requires `admin` (`403` for everyone else).

### 3.1 Items

| Method | Path | Role | Notes |
|---|---|---|---|
| GET | `/items/` | any | list, filterable |
| POST | `/items/` | member+ | create |
| GET | `/items/{id}` | any | detail |
| PATCH | `/items/{id}` | member+ | partial update |
| POST | `/items/{id}/checkout` | member+ | mark in use |
| POST | `/items/{id}/checkin` | member+ | mark stored |
| DELETE | `/items/{id}` | member+ | deletes item + its images/files |

**List/filter** — `GET /items/?status=stored&category_id=1&location_id=2&search=usb&skip=0&limit=50`

- `status`: one of `stored`, `in_use`, `lost`, `defect`
- `search`: substring match on `name`
- `limit` is capped server-side at `200` (default `50`)

**Create** — `POST /items/`

```json
{
  "name": "USB-C zu USB-C Kabel",
  "description": "1m, geflochten",
  "category_id": 1,
  "connector_a": "USB-C",
  "connector_b": "USB-C",
  "cable_length_cm": 100,
  "color": "schwarz",
  "brand": "Anker",
  "location_id": 3,
  "ai_analyzed": true,
  "ai_confidence": 0.91,
  "ai_raw_response": "{\"model\":\"cable-classifier-v1\",\"labels\":[...]}"
}
```

All fields except `name` are optional. Response `201` returns the full
`ItemRead` object (see below). The item's `status` always starts as `stored`
and `stored_at` is set to the creation time server-side; you don't send
`status` on create.

**Update** — `PATCH /items/{id}` accepts the same field set as create (all
optional, partial update / "only send what changed"). `404` if the item
doesn't exist.

**Checkout** — `POST /items/{id}/checkout`

```json
{ "usage_purpose_id": 2, "usage_note": "Laptop am Schreibtisch" }
```

- Both fields optional. `400` if the item is already `in_use`.
- `404` if `usage_purpose_id` is given but doesn't exist.
- **`requires_note` validation**: if the referenced usage purpose has
  `requires_note: true` and `usage_note` is empty/missing, the server returns
  `400` with a message like `"Usage purpose 'Reparatur' requires a usage_note"`.
  The app should pre-check this client-side (load usage purposes once, and if
  the user picks one with `requires_note: true`, make the note field required
  in the UI) so the user isn't surprised by a server-side rejection — but still
  handle the `400` gracefully as a fallback.
- On success: `status` → `in_use`, `location_id` is cleared (an item that's
  "in use" isn't *at* a location), `checked_out_at` is set.

**Checkin** — `POST /items/{id}/checkin`

```json
{ "location_id": 3 }
```

- `location_id` is **required** (where it's being put back).
- On success: `status` → `stored`, `usage_purpose_id`/`usage_note` cleared,
  `stored_at` updated.

**Delete** — `DELETE /items/{id}` → `204`. Also deletes all associated image
files from disk and their DB rows. `404` if not found.

**`ItemRead` shape** (returned by all of the above except delete):

```json
{
  "id": 42,
  "name": "USB-C zu USB-C Kabel",
  "description": "1m, geflochten",
  "category_id": 1,
  "connector_a": "USB-C",
  "connector_b": "USB-C",
  "cable_length_cm": 100,
  "color": "schwarz",
  "brand": "Anker",
  "status": "stored",
  "location_id": 3,
  "usage_purpose_id": null,
  "usage_note": null,
  "ai_analyzed": true,
  "ai_confidence": 0.91,
  "ai_raw_response": "{...}",
  "created_by_id": 1,
  "updated_by_id": 1,
  "created_at": "2026-06-30T10:00:00",
  "updated_at": "2026-06-30T10:00:00",
  "stored_at": "2026-06-30T10:00:00",
  "checked_out_at": null,
  "images": [
    {
      "id": 7,
      "item_id": 42,
      "filename": "42_a1b2c3.jpg",
      "thumbnail_filename": "42_a1b2c3_thumb.jpg",
      "is_primary": true,
      "sort_order": 0,
      "created_at": "2026-06-30T10:01:00"
    }
  ]
}
```

`status` is one of: `stored` ("eingelagert"), `in_use` ("in Verwendung"),
`lost` ("vermisst"), `defect` ("defekt"). These four map directly to the
status badges described in [Section 5.4](#54-status-badges).

Image files are served as static files at `/images/<filename>` on the same
host (proxied by nginx in the web deployment) — build the full image URL as
`<base-host>/images/<filename>` (note: **not** under `/api/v1`).

### 3.2 Images

Images belong to an item and support multiple photos per item.

| Method | Path | Role | Notes |
|---|---|---|---|
| GET | `/items/{item_id}/images` | any | list, ordered by `sort_order` |
| POST | `/items/{item_id}/images` | member+ | multipart upload, multiple files |
| PATCH | `/items/{item_id}/images/{image_id}` | member+ | set primary flag |
| DELETE | `/items/{item_id}/images/{image_id}` | member+ | removes file + row |

**Upload** — `POST /items/{item_id}/images`, `multipart/form-data`, **repeated
`files` field** for multiple images in one request:

```
POST /api/v1/items/42/images
Content-Type: multipart/form-data; boundary=...

--boundary
Content-Disposition: form-data; name="files"; filename="cable_front.jpg"
Content-Type: image/jpeg

<bytes>
--boundary
Content-Disposition: form-data; name="files"; filename="cable_connector.jpg"
Content-Type: image/jpeg

<bytes>
--boundary--
```

- Allowed content types: `image/jpeg`, `image/png`, `image/webp`. Anything else
  → `400`.
- The server generates a thumbnail automatically (`thumbnail_filename`).
- The **first image uploaded for an item** (when it has none yet) is
  automatically marked `is_primary: true`; subsequent uploads default to
  non-primary. Use the `PATCH` endpoint to change which image is primary.
- Response `201`: array of `ItemImageRead` (one per uploaded file, in order).
- `404` if `item_id` doesn't exist.
- nginx in the reference deployment caps request body size at `20M`
  (`client_max_body_size 20M;`) — keep this in mind if the app uploads several
  full-resolution photos in one batch; consider compressing/resizing on-device
  before upload (also saves mobile data/storage).

**Set primary** — `PATCH /items/{item_id}/images/{image_id}?is_primary=true`
(query parameter, not a JSON body). Setting one image primary unsets any other
primary image for the same item.

**Delete image** — `204`. If the deleted image was primary, the server
automatically promotes the next image (by `sort_order`) to primary, if any
remain.

Recommendation for the Android app: encourage capturing **multiple angles per
item** (e.g. full cable, both connector ends close-up) at item-creation time —
this is useful for the user visually identifying cables later, and the extra
images are also valuable future training/reference data for improving the
on-device model (see [Section 4](#4-on-device-ai-flow)).

### 3.3 Categories

| Method | Path | Role |
|---|---|---|
| GET | `/categories/` | any |
| POST | `/categories/` | member+ |
| PATCH | `/categories/{id}` | member+ |
| DELETE | `/categories/{id}` | member+ |

Shape: `{ id, name, icon, color, description, created_at }` (`icon`/`color`/
`description` optional, free-text — `icon` is presumably an icon-name/emoji
convention shared with the web UI; confirm against seeded data via `/docs`).

`POST` → `409 Conflict` if `name` already exists. `DELETE` → `409 Conflict` if
any item still references the category (`category_id`); the app should catch
this and show something like "Kategorie wird noch von Items verwendet" rather
than a generic error.

### 3.4 Locations

Locations are hierarchical (e.g. "Keller" → "Regal 2" → "Schublade 3").

| Method | Path | Role | Notes |
|---|---|---|---|
| GET | `/locations/` | any | **flat** list — good for dropdowns/search |
| GET | `/locations/tree` | any | **hierarchical** tree — good for drill-down picker |
| POST | `/locations/` | member+ | create, optional `parent_id` |
| PATCH | `/locations/{id}` | member+ | |
| DELETE | `/locations/{id}` | member+ | |

`GET /locations/` returns `LocationRead[]`: `{ id, name, description, parent_id,
created_at }`, flat (no nesting) — use this when you just need an id→name
lookup or a flat picker.

`GET /locations/tree` returns `LocationTreeNode[]`, recursively nested:

```json
[
  {
    "id": 1, "name": "Keller", "description": null, "parent_id": null,
    "created_at": "2026-01-01T00:00:00",
    "children": [
      {
        "id": 2, "name": "Regal 2", "description": null, "parent_id": 1,
        "created_at": "2026-01-01T00:00:00",
        "children": []
      }
    ]
  }
]
```

Use `/locations/tree` to build a drill-down location picker in the app (mirror
the web UI's navigation pattern: tap into a location to see its children/
contents). Use the flat `/locations/` when you just need every location as a
simple list (e.g. for a search-as-you-type field).

`POST` → `404` if `parent_id` doesn't reference an existing location.
`PATCH` → `400` if you try to set a location as its own parent.
`DELETE` → `409 Conflict` if the location still has items in it
(`location_id` references), **or** `409` if it still has child locations.
Both are real, expected situations in everyday use (e.g. trying to delete a
shelf that still has cables on it, or a room with sub-locations) — surface
these as a friendly inline message, not a crash/generic error toast.

### 3.5 Usage purposes

Usage purposes describe *why* something was checked out (e.g. "Reise",
"Reparatur", "Verliehen an ...").

| Method | Path | Role |
|---|---|---|
| GET | `/usage-purposes/` | any |
| POST | `/usage-purposes/` | member+ |
| PATCH | `/usage-purposes/{id}` | member+ |
| DELETE | `/usage-purposes/{id}` | member+ |

Shape: `{ id, name, description, requires_note, created_at }`.

`requires_note: true` means: when this purpose is selected during
`POST /items/{id}/checkout`, the `usage_note` field becomes mandatory (server
enforces this with a `400` — see [Section 3.1](#31-items)). The app should
load the usage-purposes list (e.g. once at startup or lazily on the checkout
screen), and dynamically show the note field as required/optional based on the
selected purpose's `requires_note` flag, to avoid a round-trip failure.

`POST` → `409` if `name` already exists. `DELETE` → `409` if any item still
references it via `usage_purpose_id`.

### 3.6 Users (admin only)

Account management — **no self-registration**; only an `admin` can create
accounts. The Android app will rarely touch this (the product owner is
presumably the sole admin), but it's available if a "manage users" screen is
ever wanted on mobile too.

| Method | Path | Role |
|---|---|---|
| GET | `/users/` | admin |
| POST | `/users/` | admin |
| PATCH | `/users/{id}` | admin |
| DELETE | `/users/{id}` | admin |

`POST /users/`:

```json
{ "username": "partner", "password": "...", "role": "member" }
```

`role` ∈ `admin` / `member` / `viewer` (default `member`). `409` if username
taken.

`PATCH /users/{id}` accepts any of `password`, `role`, `is_active` (partial
update — e.g. set `is_active: false` to deactivate/lock out a user without
deleting them; their existing token will then fail on next use and the app
must bounce them to login, per [Section 2.3](#23-using-the-token)).

### 3.7 Status codes worth handling explicitly

| Code | Meaning in this API | App behavior |
|---|---|---|
| 400 | Validation/business-rule failure (e.g. missing required `usage_note`, already checked out, self-parented location) | Show the server's `detail` message inline near the offending field |
| 401 | Missing/invalid/expired token | Clear stored token, route to login |
| 403 | Authenticated but role insufficient (e.g. `viewer` trying to POST) | Hide/disable the action in the UI for that role rather than relying on the error; still handle gracefully if reached |
| 404 | Referenced resource (item/location/category/usage purpose/user/image) not found | Generic "not found" / refresh list |
| 409 | Conflict — duplicate name on create, or delete blocked by a still-referencing item/child | Friendly "still in use, can't delete" message |

## 4. On-device AI flow

This is the flow from camera capture to a saved item, and it is the part of
the app that differs most from a "thin REST client":

1. **Capture (offline).** User taps "Kabel hinzufügen" → app opens the camera
   (e.g. CameraX) and takes one or more photos. This step has **no network
   dependency** at all.
2. **On-device classification (offline).** The photo(s) are run through an
   on-device model (e.g. ML Kit custom model, a bundled TensorFlow Lite /
   LiteRT model, or any other local-inference approach — the specific library
   is an implementation choice for whoever builds the app, not mandated here).
   The model suggests things like connector type(s) (`connector_a`,
   `connector_b`), maybe a guessed `name`, and a confidence score.
3. **Confirmation, not auto-save.** The AI suggestion **pre-fills an editable
   form** — it must never be saved silently/blindly. The user reviews and can
   correct any field (name, connectors, color, brand, length, category,
   location) before confirming. This keeps the human in the loop and avoids
   garbage data from a wrong classification.
4. **Create the item via REST.** Once confirmed, the app calls
   `POST /api/v1/items/` with the (possibly corrected) fields plus the AI
   metadata:

   ```json
   {
     "name": "USB-C zu USB-C Kabel",
     "connector_a": "USB-C",
     "connector_b": "USB-C",
     "category_id": 1,
     "location_id": 3,
     "ai_analyzed": true,
     "ai_confidence": 0.87,
     "ai_raw_response": "{\"model\":\"cable-net-v1\",\"top_labels\":[{\"label\":\"USB-C\",\"score\":0.87},{\"label\":\"USB-A\",\"score\":0.09}]}"
   }
   ```

   - `ai_analyzed`: `true` whenever the on-device model was used to produce
     the (initial) suggestion, regardless of how much the user edited it
     afterward. `false` for fully manual entry.
   - `ai_confidence`: the model's own confidence (0.0–1.0) for its top
     prediction.
   - `ai_raw_response`: the on-device model's raw output, **JSON-stringified**
     by the app, stored as opaque text by the backend. This is intentionally
     unstructured from the backend's point of view — its purpose is future
     debugging and potential retraining of the on-device model, not anything
     the backend parses or acts on today.
5. **Upload photos.** After the item is created (response includes the new
   `id`), upload the captured photo(s) via
   `POST /api/v1/items/{id}/images` (multipart, repeated `files` field —
   see [Section 3.2](#32-images)). Uploading multiple angles is encouraged.

**Hard constraint: no cloud AI.** At no point does any image, or any
derived data, get sent to a third-party cloud vision/LLM API. Inference
happens entirely on the Pixel. The *only* network call in this whole flow is
the plain REST traffic to the self-hosted backend in steps 4–5 (item
creation + image storage) — that backend call is for **persistence**, not
analysis. The backend has no AI endpoint to call even if the app wanted to;
`ai_analyzed`/`ai_confidence`/`ai_raw_response` are just three columns it
stores verbatim (see `backend/app/models/item.py`, `backend/app/schemas/item.py`).

This also means: if the phone is offline (no Wi-Fi/no backend reachable), the
capture-and-classify steps (1–3) still work fully; only the save (step 4–5)
needs connectivity. Consider an offline queue/retry for step 4–5 as a future
enhancement, but that's outside this document's scope.

## 5. Design / layout consistency

The Android app should look and feel like the same product as the web UI, not
a different app that happens to share a backend. The web frontend (Vue 3 +
Tailwind) defines the following design system; mirror it.

### 5.1 Color

- **Primary/accent color**: Indigo, `#4f46e5` (Tailwind `indigo-600`). Use this
  as the seed color for a Material 3 color scheme (`ColorScheme` /
  `dynamicColorScheme` substitute) — i.e. build light and dark theme variants
  derived from this seed (e.g. via Material You's `androidx.compose.material3`
  color scheme builders or a tool like Material Theme Builder), rather than
  using Android's per-device dynamic color (Material You wallpaper-based
  theming), so the app's branding stays consistent regardless of the user's
  wallpaper.
- **Backgrounds**: white or very light gray (`gray-50`-ish) for screen
  backgrounds.
- **Cards/surfaces**: white surface, rounded corners (~`12dp` radius), subtle
  elevation/shadow (small, not a heavy Material drop shadow — keep it close to
  the flat, light feel of the web cards).
- **Text**: near-black for primary text (item names, headings); medium gray
  for secondary/meta text (e.g. "USB-C → USB-C, 100cm", timestamps).

### 5.2 Buttons

- **Primary action**: filled indigo (`#4f46e5`) background, white text,
  rounded corners. Used for the main action on a screen (e.g. "Speichern",
  "Auslagern").
- **Secondary action**: outline/ghost button (indigo or gray outline,
  transparent/white fill) for less prominent actions (e.g. "Abbrechen").
- **Destructive action**: red, for delete/remove actions (e.g. "Löschen").

### 5.3 Card layout pattern (item list)

Mirror the web `ItemCard` composition exactly in the Android list item:

```
+-----------------------------------------------------+
| [thumbnail] | Name (bold, near-black)                |
|   image     | Connector info (gray, e.g. USB-C→C)    |
|             | [Status-Badge-Pill]                    |
+-----------------------------------------------------+
```

- Thumbnail on the **left** (use the `thumbnail_filename` of the primary
  image, or a placeholder icon if the item has no images yet).
- Name + connector summary + status badge stacked on the **right**.
- Use this same row layout for item lists everywhere in the app (overview,
  search results, location contents) for visual consistency with the web app.

### 5.4 Status badges

These four colors must match the web UI **exactly** since the product owner
will switch between both clients:

| Status (API value) | German label | Badge color | Approx. tokens |
|---|---|---|---|
| `stored` | "eingelagert" | green | bg `green-100` (`#dcfce7`) / text `green-700` (`#15803d`) |
| `in_use` | "in Verwendung" | amber/orange | bg `amber-100` (`#fef3c7`) / text `amber-700` (`#b45309`) |
| `defect` | "defekt" | red | bg `red-100` (`#fee2e2`) / text `red-700` (`#b91c1c`) |
| `lost` | "vermisst" | gray | bg `gray-200` (`#e5e7eb`) / text `gray-600` (`#4b5563`) |

Render as a small rounded "pill" (high corner radius, padded text), background
= the light tone, text = the dark tone of the same hue — same convention as
Tailwind's `bg-{color}-100 text-{color}-700` pattern used on the web.

### 5.5 Navigation

Bottom navigation with **exactly 4 destinations**, same order, same German
labels as the web app:

1. **Übersicht** (overview/dashboard)
2. **Kabel** (items list)
3. **Orte** (locations)
4. **Einstellungen** (settings — includes server URL config, account, logout)

Use Jetpack Compose Material 3 `NavigationBar` with 4 `NavigationBarItem`
destinations mirroring this exact set, in this exact order, with matching
icons where sensible (the web app's icon choices, if any, should be checked
once that UI exists — if not yet implemented, pick conventional Material
icons: e.g. home/dashboard, cable, location/map-pin, settings).

### 5.6 Language

All UI text is **German**, hardcoded — no i18n framework is used on the web
side and none is needed on Android either. Keep terminology consistent with
the API's German domain comments and the status labels above (e.g. always
"Auslagern"/"Einlagern" for checkout/checkin, "Ort" for location, "Kategorie"
for category, "Verwendungszweck" for usage purpose).

### 5.7 Recommended stack

**Jetpack Compose + Material 3** is the natural Android equivalent of the
web stack (component-based, utility-driven theming comparable to Tailwind's
design-token approach). This is a recommendation for the future implementer,
not a constraint enforced by the backend — any Android stack that can do JSON
over HTTPS/HTTP and on-device ML works against this API.

## 6. Status of this document

This file is a **reference for when Android development starts**, written
against the backend as it exists today (REST routes in
`backend/app/routers/*.py`, schemas in `backend/app/schemas/*.py`, models in
`backend/app/models/*.py`). It is not itself an implementation task, and no
Android project exists in this repository yet. Before starting the Android
project, re-check this document against the live `/docs` (Swagger UI) on the
running backend in case the API has evolved since this was written.
