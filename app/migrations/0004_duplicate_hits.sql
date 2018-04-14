alter table visitor drop constraint visitor_cookie_date_account_id_path_key;

CREATE OR REPLACE FUNCTION duplicate_hits() RETURNS VOID AS
$BODY$
DECLARE v visitor%rowtype;
BEGIN
for v in select * from visitor where hits > 1 loop
    for i in 2..v.hits loop
    insert into visitor(account_id, date, path, cookie, hits)
        values (v.account_id, v.date, v.path, v.cookie, v.hits);
    end loop;
end loop;
END;
$BODY$
LANGUAGE plpgsql;
select * from duplicate_hits();
