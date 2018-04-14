alter table visitor drop constraint visitor_cookie_date_account_id_path_key;
alter table visitor rename to visit;
alter table visit drop column hits;
-- ALTER TABLE visit ADD COLUMN ip inet not null default '127.0.0.1';
-- ALTER TABLE visit ADD COLUMN browser varchar(1000) not null default '';
alter table visit alter column date type timestamp with time zone;
