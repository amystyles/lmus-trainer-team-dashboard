-- ════════════════════════════════════════════════════════════════
-- LMUS TAP — Phase 2 schema
-- Run this once in Supabase SQL Editor (or via `supabase db push`)
-- ════════════════════════════════════════════════════════════════

-- ── Extensions ────────────────────────────────────────────────
create extension if not exists "pgcrypto";

-- ── trainers ──────────────────────────────────────────────────
-- One row per person who can sign in. Email links to Supabase Auth.
create table if not exists public.trainers (
  id           uuid primary key default gen_random_uuid(),
  name         text not null unique,
  email        text unique,
  region       text,
  is_admin     boolean not null default false,
  is_rc        boolean not null default false,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

create index if not exists trainers_email_idx  on public.trainers (lower(email));
create index if not exists trainers_region_idx on public.trainers (region);

-- ── bookings ──────────────────────────────────────────────────
create table if not exists public.bookings (
  id              uuid primary key default gen_random_uuid(),
  booking_id      text unique,                    -- e.g. "TB-151084"
  event           text not null,
  trainer_name    text not null,
  trainer_id      uuid references public.trainers(id) on delete set null,
  event_type      text,                           -- "Initial Training", "Dual Training", etc.
  program         text,
  start_date      date,
  region          text,
  is_online       boolean not null default false,
  fiscal_year     text,                           -- "FY2026"
  fiscal_quarter  text,                           -- "Q1"
  status          text,
  confirmed       boolean not null default false,
  dual_group      text,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);

create index if not exists bookings_trainer_name_idx  on public.bookings (trainer_name);
create index if not exists bookings_trainer_id_idx    on public.bookings (trainer_id);
create index if not exists bookings_region_idx        on public.bookings (region);
create index if not exists bookings_start_date_idx    on public.bookings (start_date);
create index if not exists bookings_fy_q_idx          on public.bookings (fiscal_year, fiscal_quarter);
create index if not exists bookings_program_idx       on public.bookings (program);
create index if not exists bookings_event_type_idx    on public.bookings (event_type);

-- updated_at triggers
create or replace function public.touch_updated_at() returns trigger
language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trainers_touch on public.trainers;
create trigger trainers_touch before update on public.trainers
  for each row execute procedure public.touch_updated_at();

drop trigger if exists bookings_touch on public.bookings;
create trigger bookings_touch before update on public.bookings
  for each row execute procedure public.touch_updated_at();

-- ── helper: is the current auth user an admin? ────────────────
create or replace function public.is_admin() returns boolean
language sql stable security definer as $$
  select exists (
    select 1 from public.trainers
    where lower(email) = lower(auth.email())
      and is_admin
  );
$$;

-- ── helper: current auth user's trainer row ───────────────────
create or replace function public.current_trainer() returns public.trainers
language sql stable security definer as $$
  select * from public.trainers
  where lower(email) = lower(auth.email())
  limit 1;
$$;

-- ════════════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY
-- ════════════════════════════════════════════════════════════════

alter table public.trainers enable row level security;
alter table public.bookings enable row level security;

-- ── trainers policies ─────────────────────────────────────────
-- Any signed-in trainer can read all trainer rows (needed for team view).
-- Sensitive fields (email, role flags) are still visible — the dashboard
-- is intended for internal team use. Tighten later if needed.
drop policy if exists "trainers_select_authed" on public.trainers;
create policy "trainers_select_authed" on public.trainers
  for select using (auth.role() = 'authenticated');

-- Only admins can insert/update/delete trainers.
drop policy if exists "trainers_write_admin" on public.trainers;
create policy "trainers_write_admin" on public.trainers
  for all using (public.is_admin()) with check (public.is_admin());

-- ── bookings policies ─────────────────────────────────────────
-- A signed-in trainer can SELECT a booking if:
--   (a) they own it (trainer_name matches their trainer record), OR
--   (b) the booking is in their region (powers "My Regions Pulse"), OR
--   (c) they are an admin.
drop policy if exists "bookings_select_own_or_region_or_admin" on public.bookings;
create policy "bookings_select_own_or_region_or_admin" on public.bookings
  for select using (
    public.is_admin()
    or exists (
      select 1 from public.trainers t
      where lower(t.email) = lower(auth.email())
        and (
          t.name   = bookings.trainer_name
          or t.region = bookings.region
        )
    )
  );

-- Only admins can write bookings (CSV upload uses service-role from the regional-ops admin path).
drop policy if exists "bookings_write_admin" on public.bookings;
create policy "bookings_write_admin" on public.bookings
  for all using (public.is_admin()) with check (public.is_admin());
