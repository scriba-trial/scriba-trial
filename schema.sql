-- Run this in the Supabase SQL editor for the new project

CREATE TABLE trials (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name        TEXT NOT NULL,
  email       TEXT NOT NULL UNIQUE,
  field       TEXT NOT NULL,
  target_client TEXT NOT NULL,
  pain_point  TEXT NOT NULL,
  voice_signal TEXT,
  status      TEXT DEFAULT 'new',
  chosen_topic TEXT,
  topics_json JSONB,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE posts (
  id           UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  trial_id     UUID REFERENCES trials(id) ON DELETE CASCADE,
  topic        TEXT,
  facebook_text TEXT,
  linkedin_text TEXT,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast status lookups
CREATE INDEX idx_trials_status ON trials(status);
CREATE INDEX idx_trials_email  ON trials(email);
