alter table visitor alter column date type timestamp with time zone;
alter table visitor drop column hits;
alter table visitor rename to visit;
-- ALTER TABLE visit ADD COLUMN ip inet not null default '127.0.0.1';
-- ALTER TABLE visit ADD COLUMN browser varchar(1000) not null default '';
