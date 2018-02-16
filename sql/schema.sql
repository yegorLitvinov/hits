--
-- Account
--

create table if not exists account (
    domain          varchar(100)    unique      not null,
    email           varchar(100)    not null,
    id              integer         unique      not null,
    is_active       boolean         default false   not null,
    is_superuser    boolean         not null,
    password        varchar(1000)   not null
);
ALTER TABLE account OWNER TO hits;
CREATE INDEX account_id_index ON account USING btree (id);

CREATE SEQUENCE account_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE account_id_seq OWNER TO hits;
ALTER SEQUENCE account_id_seq OWNED BY account.id;
ALTER TABLE ONLY account ALTER COLUMN id SET DEFAULT nextval('account_id_seq'::regclass);

--
-- Hit
--

create table hit (
    account_id  integer         not null,
    date        date            not null,
    endpoint    varchar(1000)   not null,
    id          integer         not null,
    ip          varchar(20)     not null,
    visits      integer         not null    check(visits > 0),
    unique(ip, date, account_id, endpoint)
);
ALTER TABLE hit OWNER TO hits;
CREATE INDEX hit_id_index ON hit USING btree (account_id, date, endpoint);
ALTER TABLE ONLY hit
    ADD CONSTRAINT hit_account_id_fk_account FOREIGN KEY (account_id) REFERENCES account(id) DEFERRABLE INITIALLY DEFERRED;

CREATE SEQUENCE hit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE hit_id_seq OWNER TO hits;
ALTER SEQUENCE hit_id_seq OWNED BY hit.id;
ALTER TABLE ONLY hit ALTER COLUMN id SET DEFAULT nextval('hit_id_seq'::regclass);
