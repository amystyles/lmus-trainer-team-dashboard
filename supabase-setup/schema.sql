-- LMUS TAP Team Dashboard — Supabase Schema
-- Run this in the Supabase SQL Editor before running migrate.py

-- ── TEAM MEMBERS (trainers + assessors) ─────────────────────────
CREATE TABLE IF NOT EXISTS team_members (
  id            SERIAL PRIMARY KEY,
  first_name    TEXT NOT NULL,
  last_name     TEXT NOT NULL,
  full_name     TEXT NOT NULL,
  email         TEXT,
  address       TEXT,
  city          TEXT,
  state         TEXT,
  zip           TEXT,
  home_region   TEXT NOT NULL,
  role          TEXT NOT NULL CHECK (role IN ('Trainer', 'Assessor')),
  is_rc         BOOLEAN DEFAULT FALSE,
  is_at         BOOLEAN DEFAULT FALSE,
  is_dt         BOOLEAN DEFAULT FALSE,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (full_name)
);

-- ── BOOKINGS ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bookings (
  id              SERIAL PRIMARY KEY,
  event           TEXT,
  booking_id      TEXT UNIQUE,
  trainer         TEXT NOT NULL,
  event_type      TEXT,
  program         TEXT,
  start_date      DATE,
  region          TEXT,
  is_online       BOOLEAN DEFAULT FALSE,
  fiscal_year     TEXT,
  fiscal_quarter  TEXT,
  status          TEXT,
  confirmed       BOOLEAN DEFAULT FALSE,
  dual_group      TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── ALLOW ANON ACCESS (internal tool — no real auth) ────────────
ALTER TABLE team_members DISABLE ROW LEVEL SECURITY;
ALTER TABLE bookings     DISABLE ROW LEVEL SECURITY;

-- ── INDEXES ─────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_bookings_trainer     ON bookings (trainer);
CREATE INDEX IF NOT EXISTS idx_bookings_program     ON bookings (program);
CREATE INDEX IF NOT EXISTS idx_bookings_start_date  ON bookings (start_date);
CREATE INDEX IF NOT EXISTS idx_bookings_region      ON bookings (region);
CREATE INDEX IF NOT EXISTS idx_team_members_role    ON team_members (role);
CREATE INDEX IF NOT EXISTS idx_team_members_region  ON team_members (home_region);
