create table migration (
    id serial primary key,
    name varchar(1000) unique not null,
    applied_at timestamp with time zone not null DEFAULT now()
);
ALTER TABLE migration OWNER TO metric;
