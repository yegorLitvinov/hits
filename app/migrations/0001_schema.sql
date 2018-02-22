--
-- Account
--

create table if not exists account (
    api_key         uuid            unique      not null,
    domain          varchar(100)    not null,
    email           varchar(100)    not null,
    id              integer         unique      not null,
    is_active       boolean         default false   not null,
    is_superuser    boolean         not null,
    password        varchar(1000)   not null,
    unique(email, domain)
);
ALTER TABLE account OWNER TO metric;
CREATE INDEX account__id__index ON account USING btree (id);
CREATE INDEX account__email__index ON account USING btree (email);
CREATE INDEX account__domain__api_key__index ON account USING btree (domain, api_key);

CREATE SEQUENCE account_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE account_id_seq OWNER TO metric;
ALTER SEQUENCE account_id_seq OWNED BY account.id;
ALTER TABLE ONLY account ALTER COLUMN id SET DEFAULT nextval('account_id_seq'::regclass);

--
-- Visitor
--

create table visitor (
    account_id  integer         not null,
    date        date            not null,
    path        varchar(1000)   not null,
    id          integer         not null,
    cookie      uuid            not null,
    hits        integer         default 1   not null    check(hits > 0),
    unique(cookie, date, account_id, path)
);
ALTER TABLE visitor OWNER TO metric;
CREATE INDEX visitor__id__index ON visitor USING btree (account_id, date, path);
ALTER TABLE ONLY visitor
    ADD CONSTRAINT visitor_account_id_fk_account FOREIGN KEY (account_id) REFERENCES account(id) DEFERRABLE INITIALLY DEFERRED;

CREATE SEQUENCE visitor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE visitor_id_seq OWNER TO metric;
ALTER SEQUENCE visitor_id_seq OWNED BY visitor.id;
ALTER TABLE ONLY visitor ALTER COLUMN id SET DEFAULT nextval('visitor_id_seq'::regclass);
