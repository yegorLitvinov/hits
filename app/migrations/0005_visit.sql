alter table visitor alter column date type timestamp with time zone;
alter table visitor drop column hits;
alter table visitor rename to visit;
