# Home Warehouse

Mobile-first Lagerverwaltung fuer den Heimgebrauch: Gegenstaende (initial Kabel) mit Foto(s),
Beschreibung, Lagerort und Verwendungsstatus erfassen und behalten so den Ueberblick, ob ein
Kabel eingelagert oder gerade in Verwendung ist.

Die Web-Oberflaeche ist die Verwaltungs-/Zweit-Ansicht. Der primaere Client wird spaeter eine
native Android-App mit On-Device-KI-Kabelerkennung sein, die ueber dieselbe REST-API spricht
(siehe [`ANDROID_INTEGRATION.md`](./ANDROID_INTEGRATION.md)).

## Stack

- **Backend**: Python 3.12, FastAPI, SQLModel (SQLite, WAL-Mode), Alembic, Pillow, JWT-Auth
- **Frontend**: Vue 3, Vite, Tailwind CSS, Pinia, vue-router
- **Deployment**: Docker Compose (Nginx serviert das Frontend und reverse-proxied `/api/` und `/images/` an das Backend)

## Setup

```bash
cp .env.example .env
# .env anpassen: DATA_PATH/IMAGES_PATH auf existierende Host-Verzeichnisse zeigen lassen,
# SECRET_KEY und ADMIN_USERNAME/ADMIN_PASSWORD setzen

docker compose up -d --build
```

Die App ist danach unter `http://<host>:${PORT}` erreichbar (Standard-Port siehe `.env`).
Beim ersten Start wird automatisch ein Admin-Benutzer aus `ADMIN_USERNAME`/`ADMIN_PASSWORD`
angelegt, sofern noch kein Benutzer existiert. Damit kannst du dich einloggen und ueber
*Einstellungen -> Benutzerverwaltung* weitere Benutzer (Rollen: `admin`, `member`, `viewer`)
anlegen.

Die OpenAPI-Doku des Backends ist unter `http://<host>:${PORT}/docs` erreichbar (von Nginx an
das Backend durchgereicht).

## Lokale Entwicklung

**Backend**

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
DATA_PATH=./data IMAGES_PATH=./images uvicorn app.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

`vite.config.js` proxyt `/api` und `/images` im Dev-Modus an `http://localhost:8000`.

## Datenmodell-Highlights

- **Multi-User mit Rollen**: `admin` (inkl. Benutzerverwaltung), `member` (Items/Orte/Kategorien/
  Verwendungszwecke verwalten), `viewer` (nur lesen).
- **Mehrere Bilder pro Item**: eigene `item_image`-Tabelle, ein Bild ist als `is_primary`
  markiert (Titelbild fuer Listen/Thumbnails).
- **Hierarchische Lagerorte**: `location.parent_id` erlaubt beliebig tiefe Verschachtelung
  (z.B. Raum -> Regal -> Kiste). `/locations` liefert eine flache Liste, `/locations/tree` den
  verschachtelten Baum fuer die Drill-Down-Navigation in der UI.
- **Verwendungszwecke mit Pflicht-Freitext**: ein Verwendungszweck kann `requires_note=true`
  haben ("Zusatzinformation erfassen"); beim Auschecken mit diesem Zweck ist `usage_note` dann
  Pflicht.
- **KI-Metadaten**: `ai_analyzed`, `ai_confidence`, `ai_raw_response` werden von der (spaeteren)
  Android-App nach On-Device-Analyse mitgeliefert. Es gibt bewusst keinen serverseitigen
  KI-Analyse-Endpoint in v1 (kein Cloud-Aufruf), siehe `ANDROID_INTEGRATION.md`.

## Konfiguration

Siehe `.env.example` fuer alle Variablen (Pfade, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`,
Erstbenutzer, CORS, KI-Provider-Platzhalter).
