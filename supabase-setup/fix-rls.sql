-- Run this in Supabase SQL Editor → New query

-- 1. Allow anon to read and write (internal dashboard — no real auth)
CREATE POLICY IF NOT EXISTS "anon_select" ON team_members FOR SELECT TO anon USING (true);
CREATE POLICY IF NOT EXISTS "anon_insert" ON team_members FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY IF NOT EXISTS "anon_select" ON bookings FOR SELECT TO anon USING (true);
CREATE POLICY IF NOT EXISTS "anon_insert" ON bookings FOR INSERT TO anon WITH CHECK (true);

-- 2. Insert the remaining 4 assessors
INSERT INTO team_members (first_name, last_name, full_name, address, city, state, zip, home_region, role, is_rc, is_at, is_dt)
VALUES
  ('Kristen','Strickland','Kristen Strickland','4157 Notch Trail','Colorado Springs','CO','80924','North Central','Assessor',false,false,false),
  ('Nadia','Hasan','Nadia Hasan','11150 Pennway Drive','North Chesterfield','VA','23236','East Coast','Assessor',false,false,false),
  ('Nicci','Hoickenberry','Nicci Hoickenberry','535 Bruce Ave','Mount Joy','PA','17552','Mid East','Assessor',false,false,false),
  ('Katie','Kattner','Katie Kattner','2743 Round Hill Ct','Katy','TX','77494','South Central','Assessor',false,false,false)
ON CONFLICT (full_name) DO NOTHING;
