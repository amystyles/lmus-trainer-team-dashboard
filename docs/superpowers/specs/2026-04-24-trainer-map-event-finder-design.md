# Trainer Map & Event Finder — Design Spec
**Date:** 2026-04-24
**Project:** LMUS TAP Dashboard
**File to create:** `map.html`

---

## Overview

A new standalone page (`map.html`) that plots all 56 trainers on an interactive US map, lets users click regions to explore trainer bookings, and provides an event location finder that ranks available trainers by proximity for a given program and date.

---

## Architecture

- **Single static HTML file** (`map.html`) — no backend, no build step
- **Leaflet.js** (CDN) for interactive map with OpenStreetMap tiles
- **Haversine formula** (in-browser JS) for distance calculations
- **FileReader API** for CSV booking data upload
- **localStorage** to persist uploaded booking data across sessions
- **Hardcoded trainer data** — all 56 trainer addresses geocoded to lat/lng from the PDF roster

---

## Data Model

### TRAINERS array (hardcoded)
```js
{
  name: "Alyx Sparrow",
  city: "Littleton",
  state: "CO",
  zip: "80128",
  lat: 39.5936,
  lng: -105.0172,
  region: "Central"
}
```
All 56 trainers from the LMUS 2026 Trainer Team PDF. Region assigned per existing booking data (matching `index.html` region values: East Coast, Mid West, South Central, Central, West Coast).

There are two certified trainer role types used in this feature:

| Role | Description |
|------|-------------|
| **Trainer (T)** | Standard trainer for a program |
| **Advanced Trainer (AT)** | Senior trainer designation, sourced from a separate Advanced Trainer role matrix |

Both qualify for event finder results. Advanced Trainers are visually distinguished with an **AT** badge in results and the trainer list. Results sort order: available Advanced Trainers first (by distance), then available Trainers (by distance), then booked trainers (AT then T, by distance).

Each trainer carries two arrays: `trainerPrograms` (T role) and `advancedPrograms` (AT role). A trainer can appear in both for the same program.

Advanced Trainers from the AT matrix (17 trainers): Andres Camargo, Andy Parrish, Ashley Lyon, Barb Knutson, Colleen King, Dan Maroun, Jaime Terrill, Jen Parrish, Karen Torrell, Keri Ball, Lauren Vibbert, Luca Callini, Nikki Snow-Ybe, Mohamed Bounaim, Sanna Ronkko, Stacy Dee Rathbone, Sydnee Weinberg.

Programs per trainer are **hardcoded from the certification spreadsheet** (LMUS 2026 Trainer Team role matrix). Each trainer has a `trainerPrograms` array listing only the programs where their role contains **T** (Trainer): values T, T/P, T/A, T/A/P all qualify. Roles of I (Instructor) or P (Presenter) alone do not qualify — those trainers are excluded from event finder results and program-filtered map pins for that program.

Program column codes map to full names:
| Code | Program |
|------|---------|
| BA | BODYATTACK |
| BC | BODYCOMBAT |
| BB | BODYBALANCE |
| BJ | BODYJAM |
| BP | BODYPUMP |
| BPH | BODYPUMP HEAVY |
| BS | BODYSTEP |
| BTM | LES MILLS CEREMONY |
| TONE | LES MILLS TONE |
| CORE | LES MILLS CORE |
| GR | LES MILLS GRIT |
| RPM | RPM |
| SP | LES MILLS SPRINT |
| TRIP | LES MILLS CONQUER |
| DANC | LES MILLS DANCE |
| CEF | LES MILLS CEREMONY STUDIO |
| YOG | LES MILLS YOGA |
| SD | STRENGTH DEVELOPMENT |
| SHAP | LES MILLS SHAPES |
| FS | LES MILLS FUNCTIONAL STRENGTH |
| PL | LES MILLS PILATES |
| THRI | LES MILLS THRIVE |

### BOOKINGS array
Copied from `index.html` as seed data. Can be overridden by CSV upload. Structure:
```js
{
  bookingId, trainer, event, eventType, program,
  startDate, region, isOnline, fiscalYear,
  fiscalQuarter, status, confirmed
}
```

### City lookup table (hardcoded)
~200 major US cities → lat/lng, used to resolve the event location input without a geocoding API. If the entered city is not found, the finder shows an inline error: "City not found — try a nearby major city." No search is run.

---

## Layout

```
┌─────────────────────────────────────────────────────────────┐
│ HEADER: LMUS TAP  ← Dashboard          [Update Bookings]    │
├────────────────────────────┬────────────────────────────────┤
│                            │  EVENT FINDER                  │
│                            │  City _____ State __           │
│   LEAFLET MAP              │  Program [searchable ▼]        │
│   (region polygons +       │  Date [____]                   │
│    trainer pins)           │  [Find Trainers]               │
│                            │  ─────────────────────         │
│                            │  ★ TOP 3 AVAILABLE             │
│                            │  ranked results list...        │
│                            │  ─────────────────────         │
│                            │  TRAINER LIST                  │
│                            │  (filtered by region)          │
└────────────────────────────┴────────────────────────────────┘
```

**Map:** ~65% width, full content height. Sidebar: ~35% width, scrollable.

---

## Map Behaviour

### Region polygons
- 5 GeoJSON polygons covering US regions (East Coast, Mid West, South Central, Central, West Coast)
- Color-coded to match TAP Map reference: East Coast `#c8b400`, Mid West `#c0392b`, South Central `#27ae60`, Central `#1a6fd4`, West Coast `#e07040`
- Click region → polygon highlights, sidebar Trainer List filters to that region, map zooms to region bounds
- Click map background → deselects region, shows all trainers

### Trainer pins
- Circle markers, colored by region
- Click → Leaflet popup: name, city/state, certified programs (derived), total bookings count
- Pins visible at all zoom levels
- When a program is selected in the Event Finder, pins for trainers not certified in that program are hidden from the map. Only certified trainers remain visible.

---

## Right Sidebar

### Event Finder panel

**Inputs:**
- City (text), State (text, 2-char)
- Program: searchable autocomplete — user types, list filters live against all known programs from BOOKINGS data
- Date: date picker input

**On "Find Trainers":**
1. Resolve city+state to lat/lng via hardcoded city lookup table
2. Filter trainers to those certified for the selected program (appear in any booking for that program)
3. Calculate Haversine distance from event lat/lng to each trainer's lat/lng
4. Check conflict: trainer flagged **Booked** if any `confirmed: true` booking has a `startDate` within ±14 days of the event date (online bookings included — travel buffer applies)
5. Sort results: available trainers first, then booked, both groups sorted by distance ascending

**Results row (each trainer):**
- Name, home city/state
- Distance badge (e.g. "142 mi")
- Status: **Available** (green pill) or **Booked** (red pill + conflicting event name shown)
- Region badge

**Available trainers callout:**
- All available trainers for the selected program are surfaced at the top of results in a highlighted block (LMUS `--accent` green style), sorted by distance ascending. No cap on the number shown. Booked trainers appear below in a separate section, also sorted by distance.

### Trainer List panel

- Shown below Event Finder
- Defaults to all trainers (alphabetical)
- Filters by **both** active region (from map click) **and** active program (from Event Finder program input) simultaneously — a trainer only appears if they match both conditions
- If no region is selected, shows all regions; if no program is selected, shows all programs
- Trainers whose `trainerPrograms` does not include the selected program are excluded entirely — not dimmed, removed from the list
- Each row: name, city/state, region badge, program tags (up to 4 shown, "+N more" if overflow)
- Clicking a trainer row flies the map to their pin and opens their popup

---

## CSV Upload

- **"Update Bookings" button** in header opens native file picker (`.csv` only)
- FileReader API reads the file client-side
- Parser validates required columns: `trainer`, `program`, `startDate`, `confirmed`, `region`, `eventType`, `status`
- On success: replaces in-memory BOOKINGS, saves raw CSV string to `localStorage` key `lmus_bookings_csv`
- On page load: checks localStorage first; falls back to hardcoded seed data if not present
- Upload error (wrong columns, bad CSV) shows an inline error message — does not replace existing data

---

## Styling

Matches LMUS TAP design system from `index.html` and `LUMS.html`:
- Font: Inter + Barlow Condensed
- Colours: `--accent: #00FF63`, dark header `#0A0A0A`, light body `#F7F7F7`
- Same card, badge, pill, filter-bar component styles
- Leaflet map container styled flush (no default blue border)
- Sidebar scrollbar matches existing custom scrollbar style

---

## Navigation

- Header includes `← Dashboard` link to `index.html`
- `index.html` header gets a `Map View` link pointing to `map.html`

---

## Page Roles

| Page | Audience | Access |
|------|----------|--------|
| `index.html` | Trainers | Public — no login required |
| `map.html` | Admin / TAP team | Password-gated |

`index.html` is the trainer-facing bookings dashboard (existing). It gets a subtle "Admin" link in the header pointing to `map.html`.

`map.html` shows a login screen on first load. On correct password entry, sets a `localStorage` flag (`lmus_admin_auth`) and reveals the map. On subsequent page loads, checks the flag and skips the login screen. A "Sign Out" button in the header clears the flag and returns to the login screen.

**Authentication approach:** Single hardcoded password checked client-side. This is an internal tool with no sensitive PII — the goal is access separation, not cryptographic security. Password is stored as a constant in the JS (not hashed). Default password: `lmus-tap-2026` — can be changed by editing the constant. If stronger security is needed in future, this can be replaced with a real auth layer.

---

## Out of Scope

- Live geocoding API (all locations hardcoded)
- Backend or database
- Editing/saving trainer profiles
- Multi-date range conflict checking (single event date + 14-day window only)
- Assessor-specific logic (Trainers only for this feature)
