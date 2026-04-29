-- Run in Supabase SQL Editor → New query
ALTER TABLE team_members ADD COLUMN IF NOT EXISTS programs JSONB DEFAULT '{}';
