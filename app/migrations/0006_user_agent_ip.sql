ALTER TABLE visit ADD COLUMN ip inet;
ALTER TABLE visit ADD COLUMN user_agent json not null default '{}';
