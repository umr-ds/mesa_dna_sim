--
-- PostgreSQL database cluster dump
--

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE dna_sim;
ALTER ROLE dna_sim WITH NOSUPERUSER INHERIT NOCREATEROLE CREATEDB LOGIN NOREPLICATION NOBYPASSRLS PASSWORD 'md5396c5cbd4d531156f17cfc21d70eddad';
CREATE ROLE postgres;
ALTER ROLE postgres WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS PASSWORD 'md5d687de3dba5d4067c60c3657a420b873';






\connect template1

--
-- PostgreSQL database dump
--

-- Dumped from database version 11.3
-- Dumped by pg_dump version 11.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 11.3
-- Dumped by pg_dump version 11.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: dna_sim; Type: DATABASE; Schema: -; Owner: dna_sim
--

CREATE DATABASE dna_sim WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';


ALTER DATABASE dna_sim OWNER TO dna_sim;

\connect dna_sim

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: Apikey; Type: TABLE; Schema: public; Owner: dna_sim
--

CREATE TABLE public."Apikey" (
    id integer NOT NULL,
    created integer,
    apikey text,
    owner_id integer NOT NULL
);


ALTER TABLE public."Apikey" OWNER TO dna_sim;

--
-- Name: User; Type: TABLE; Schema: public; Owner: dna_sim
--

CREATE TABLE public."User" (
    user_id integer NOT NULL,
    email text,
    password text NOT NULL,
    created integer,
    validated boolean DEFAULT false NOT NULL,
    is_admin boolean DEFAULT false NOT NULL
);


ALTER TABLE public."User" OWNER TO dna_sim;

--
-- Name: api_id_seq; Type: SEQUENCE; Schema: public; Owner: dna_sim
--

CREATE SEQUENCE public.api_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.api_id_seq OWNER TO dna_sim;

--
-- Name: api_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dna_sim
--

ALTER SEQUENCE public.api_id_seq OWNED BY public."Apikey".id;


--
-- Name: err_rates; Type: TABLE; Schema: public; Owner: dna_sim
--

CREATE TABLE public.err_rates (
    id integer NOT NULL,
    method_id integer NOT NULL,
    submethod_id integer NOT NULL,
    err_data jsonb
);


ALTER TABLE public.err_rates OWNER TO dna_sim;

--
-- Name: err_rates_id_seq; Type: SEQUENCE; Schema: public; Owner: dna_sim
--

CREATE SEQUENCE public.err_rates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.err_rates_id_seq OWNER TO dna_sim;

--
-- Name: err_rates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dna_sim
--

ALTER SEQUENCE public.err_rates_id_seq OWNED BY public.err_rates.id;


--
-- Name: error_probability; Type: TABLE; Schema: public; Owner: dna_sim
--

CREATE TABLE public.error_probability (
    id integer NOT NULL,
    type text,
    jsonblob jsonb,
    user_id integer NOT NULL,
    validated boolean DEFAULT false,
    created integer,
    name text NOT NULL,
    awaits_validation boolean DEFAULT false NOT NULL,
    validation_desc text
);


ALTER TABLE public.error_probability OWNER TO dna_sim;

--
-- Name: error_probability_id_seq; Type: SEQUENCE; Schema: public; Owner: dna_sim
--

CREATE SEQUENCE public.error_probability_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.error_probability_id_seq OWNER TO dna_sim;

--
-- Name: error_probability_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dna_sim
--

ALTER SEQUENCE public.error_probability_id_seq OWNED BY public.error_probability.id;


--
-- Name: meth_categories; Type: TABLE; Schema: public; Owner: dna_sim
--

CREATE TABLE public.meth_categories (
    id integer NOT NULL,
    method text NOT NULL
);


ALTER TABLE public.meth_categories OWNER TO dna_sim;

--
-- Name: mutation_attributes; Type: TABLE; Schema: public; Owner: dna_sim
--

CREATE TABLE public.mutation_attributes (
    id integer NOT NULL,
    method_id integer NOT NULL,
    submethod_id integer NOT NULL,
    attributes jsonb
);


ALTER TABLE public.mutation_attributes OWNER TO dna_sim;

--
-- Name: mutation_attributes_id_seq; Type: SEQUENCE; Schema: public; Owner: dna_sim
--

CREATE SEQUENCE public.mutation_attributes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mutation_attributes_id_seq OWNER TO dna_sim;

--
-- Name: mutation_attributes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dna_sim
--

ALTER SEQUENCE public.mutation_attributes_id_seq OWNED BY public.mutation_attributes.id;


--
-- Name: pcr; Type: TABLE; Schema: public; Owner: dna_sim
--

CREATE TABLE public.pcr (
    id integer NOT NULL,
    method_id integer NOT NULL,
    err_data json,
    user_id integer,
    validated boolean DEFAULT false NOT NULL,
    err_attributes json,
    name text,
    awaits_validation boolean DEFAULT false NOT NULL,
    validation_desc text
);


ALTER TABLE public.pcr OWNER TO dna_sim;

--
-- Name: pcr_id_seq; Type: SEQUENCE; Schema: public; Owner: dna_sim
--

CREATE SEQUENCE public.pcr_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pcr_id_seq OWNER TO dna_sim;

--
-- Name: pcr_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dna_sim
--

ALTER SEQUENCE public.pcr_id_seq OWNED BY public.pcr.id;


--
-- Name: seq_err_rates; Type: TABLE; Schema: public; Owner: dna_sim
--

CREATE TABLE public.seq_err_rates (
    id integer NOT NULL,
    method_id integer NOT NULL,
    err_data json,
    user_id integer NOT NULL,
    validated boolean DEFAULT false NOT NULL,
    err_attributes json,
    name text,
    awaits_validation boolean DEFAULT false NOT NULL,
    validation_desc text
);


ALTER TABLE public.seq_err_rates OWNER TO dna_sim;

--
-- Name: seq_err_rates_id_seq; Type: SEQUENCE; Schema: public; Owner: dna_sim
--

CREATE SEQUENCE public.seq_err_rates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_err_rates_id_seq OWNER TO dna_sim;

--
-- Name: seq_err_rates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dna_sim
--

ALTER SEQUENCE public.seq_err_rates_id_seq OWNED BY public.seq_err_rates.id;


--
-- Name: storage; Type: TABLE; Schema: public; Owner: dna_sim
--

CREATE TABLE public.storage (
    id integer NOT NULL,
    err_data json,
    user_id integer,
    validated boolean DEFAULT false NOT NULL,
    err_attributes json,
    name text,
    awaits_validation boolean DEFAULT false NOT NULL,
    validation_desc text,
    method_id integer
);


ALTER TABLE public.storage OWNER TO dna_sim;

--
-- Name: storage_id_seq; Type: SEQUENCE; Schema: public; Owner: dna_sim
--

CREATE SEQUENCE public.storage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.storage_id_seq OWNER TO dna_sim;

--
-- Name: storage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dna_sim
--

ALTER SEQUENCE public.storage_id_seq OWNED BY public.storage.id;


--
-- Name: synth_err_rates; Type: TABLE; Schema: public; Owner: dna_sim
--

CREATE TABLE public.synth_err_rates (
    id integer NOT NULL,
    method_id integer NOT NULL,
    err_data json,
    user_id integer,
    validated boolean DEFAULT false NOT NULL,
    err_attributes json,
    name text,
    awaits_validation boolean DEFAULT false NOT NULL,
    validation_desc text
);


ALTER TABLE public.synth_err_rates OWNER TO dna_sim;

--
-- Name: synth_err_rates_id_seq; Type: SEQUENCE; Schema: public; Owner: dna_sim
--

CREATE SEQUENCE public.synth_err_rates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.synth_err_rates_id_seq OWNER TO dna_sim;

--
-- Name: synth_err_rates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dna_sim
--

ALTER SEQUENCE public.synth_err_rates_id_seq OWNED BY public.synth_err_rates.id;


--
-- Name: synth_meth_id_seq; Type: SEQUENCE; Schema: public; Owner: dna_sim
--

CREATE SEQUENCE public.synth_meth_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.synth_meth_id_seq OWNER TO dna_sim;

--
-- Name: synth_meth_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dna_sim
--

ALTER SEQUENCE public.synth_meth_id_seq OWNED BY public.meth_categories.id;


--
-- Name: undesiredsubsequences; Type: TABLE; Schema: public; Owner: dna_sim
--

CREATE TABLE public.undesiredsubsequences (
    id integer NOT NULL,
    sequence text NOT NULL,
    error_prob double precision DEFAULT 0.0 NOT NULL,
    created integer,
    validated boolean DEFAULT false NOT NULL,
    owner_id integer,
    description text,
    awaits_validation boolean DEFAULT false NOT NULL,
    validation_desc text
);


ALTER TABLE public.undesiredsubsequences OWNER TO dna_sim;

--
-- Name: undesiredsubsequences_id_seq; Type: SEQUENCE; Schema: public; Owner: dna_sim
--

CREATE SEQUENCE public.undesiredsubsequences_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.undesiredsubsequences_id_seq OWNER TO dna_sim;

--
-- Name: undesiredsubsequences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dna_sim
--

ALTER SEQUENCE public.undesiredsubsequences_id_seq OWNED BY public.undesiredsubsequences.id;


--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: dna_sim
--

CREATE SEQUENCE public.user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_id_seq OWNER TO dna_sim;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dna_sim
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."User".user_id;


--
-- Name: Apikey id; Type: DEFAULT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public."Apikey" ALTER COLUMN id SET DEFAULT nextval('public.api_id_seq'::regclass);


--
-- Name: User user_id; Type: DEFAULT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public."User" ALTER COLUMN user_id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Name: err_rates id; Type: DEFAULT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.err_rates ALTER COLUMN id SET DEFAULT nextval('public.err_rates_id_seq'::regclass);


--
-- Name: error_probability id; Type: DEFAULT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.error_probability ALTER COLUMN id SET DEFAULT nextval('public.error_probability_id_seq'::regclass);


--
-- Name: meth_categories id; Type: DEFAULT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.meth_categories ALTER COLUMN id SET DEFAULT nextval('public.synth_meth_id_seq'::regclass);


--
-- Name: mutation_attributes id; Type: DEFAULT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.mutation_attributes ALTER COLUMN id SET DEFAULT nextval('public.mutation_attributes_id_seq'::regclass);


--
-- Name: pcr id; Type: DEFAULT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.pcr ALTER COLUMN id SET DEFAULT nextval('public.pcr_id_seq'::regclass);


--
-- Name: seq_err_rates id; Type: DEFAULT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.seq_err_rates ALTER COLUMN id SET DEFAULT nextval('public.seq_err_rates_id_seq'::regclass);


--
-- Name: storage id; Type: DEFAULT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.storage ALTER COLUMN id SET DEFAULT nextval('public.storage_id_seq'::regclass);


--
-- Name: synth_err_rates id; Type: DEFAULT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.synth_err_rates ALTER COLUMN id SET DEFAULT nextval('public.synth_err_rates_id_seq'::regclass);


--
-- Name: undesiredsubsequences id; Type: DEFAULT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.undesiredsubsequences ALTER COLUMN id SET DEFAULT nextval('public.undesiredsubsequences_id_seq'::regclass);


--
-- Data for Name: Apikey; Type: TABLE DATA; Schema: public; Owner: dna_sim
--

COPY public."Apikey" (id, created, apikey, owner_id) FROM stdin;
0	1557739999	TESTlKG-b6GTESTT7cgGTESTw_MRTESTj_e44wnTEST	0
\.


--
-- Data for Name: User; Type: TABLE DATA; Schema: public; Owner: dna_sim
--

COPY public."User" (user_id, email, password, created, validated, is_admin) FROM stdin;
0	nouser@mosla.de	$2b$12$vVMNCKX7T3HfpsVEhP3U52x2ZZwDDDfDD5GpAW.bUNA0GPb1I3o0m	1557738292	f	t
\.


--
-- Data for Name: err_rates; Type: TABLE DATA; Schema: public; Owner: dna_sim
--

COPY public.err_rates (id, method_id, submethod_id, err_data) FROM stdin;
1	1	1	{"deletion": 0.0024, "mismatch": 0.81, "raw_rate": 0.0021, "insertion": 0.0013}
2	1	2	{"deletion": 0.0018, "mismatch": 0.79, "raw_rate": 0.0032, "insertion": 0.0011}
3	2	3	{"deletion": 0.20, "mismatch": 0.75, "raw_rate": 0.02, "insertion": 0.05}
4	2	4	{"deletion": 0.21, "mismatch": 0.37, "raw_rate": 0.14, "insertion": 0.42}
5	3	5	{"deletion": 0.37, "mismatch": 0.48, "raw_rate": 0.2, "insertion": 0.15}
6	3	6	{"deletion": 0.36, "mismatch": 0.41, "raw_rate": 0.13, "insertion": 0.23}
7	4	7	{}
\.


--
-- Data for Name: error_probability; Type: TABLE DATA; Schema: public; Owner: dna_sim
--

COPY public.error_probability (id, type, jsonblob, user_id, validated, created, name, awaits_validation, validation_desc) FROM stdin;
23	gc	{"data": [{"x": 0, "y": 100}, {"x": 40, "y": 0}, {"x": 60.17, "y": 0}, {"x": 100, "y": 100}], "maxX": 100, "maxY": 100, "label": "Error Probability", "xLabel": "GC-Percentage", "xRound": 2, "yRound": 2, "interpolation": true}	0	t	1559745908	Soft Bandpass	f	\N
19	homopolymer	{"data": [{"x": 0, "y": 0}, {"x": 2, "y": 0}, {"x": 4, "y": 0}, {"x": 5, "y": 0}, {"x": 6, "y": 0}, {"x": 7, "y": 0}, {"x": 8, "y": 100}, {"x": 20, "y": 100}], "maxX": 20, "maxY": 100, "label": "Error Probability", "xLabel": "Homopolymer length", "xRound": 0, "yRound": 2, "interpolation": true}	0	t	1559565822	0-to-7	f	\N
37	kmer	{"data": [{"x": 0, "y": 0}, {"x": 3, "y": 0}, {"x": 10, "y": 100}, {"x": 40, "y": 100}, {"x": 60, "y": 100}, {"x": 100, "y": 100}], "maxX": 20, "maxY": 100, "label": "Error Probability", "xLabel": "Kmer repeats", "xRound": 0, "yRound": 2, "interpolation": true}	16	t	1572608400	0to3	f	\N
\.


--
-- Data for Name: meth_categories; Type: TABLE DATA; Schema: public; Owner: dna_sim
--

COPY public.meth_categories (id, method) FROM stdin;
1	Column Synthesized Oligos
2	Microarray based Oligo Pools
0	User defined
6	None
3	Illumina
4	PacBio
5	Nanopore
7	Eukaryotes
8	Prokaryotes
9	Polymerases
\.


--
-- Data for Name: mutation_attributes; Type: TABLE DATA; Schema: public; Owner: dna_sim
--

COPY public.mutation_attributes (id, method_id, submethod_id, attributes) FROM stdin;
1	1	1	{"deletion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"random": 1}}, "mismatch": {"pattern": {"A": {"C": 0.25, "G": 0.50, "T": 0.25}, "C": {"A": 0.25, "G": 0.50, "T": 0.25}, "G": {"A": 0.25, "C": 0.25, "T": 0.50}, "T": {"A": 0.25, "C": 0.25, "G": 0.50}}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"random": 1}}}
2	1	2	{"deletion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"random": 1}}, "mismatch": {"pattern": {"A": {"C": 0.25, "G": 0.50, "T": 0.25}, "C": {"A": 0.25, "G": 0.50, "T": 0.25}, "G": {"A": 0.25, "C": 0.25, "T": 0.50}, "T": {"A": 0.25, "C": 0.25, "G": 0.50}}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"random": 1}}}
3	2	3	{"deletion": {"pattern": {"A": 0.15, "C": 0.35, "G": 0.35, "T": 0.15}, "position": {"random": 0.15, "homopolymer": 0.85}}, "mismatch": {"pattern": {"CG": ["CA", "TG"]}}, "insertion": {"pattern": {"A": 0.35, "C": 0.15, "G": 0.15, "T": 0.35}, "position": {"random": 0.15, "homopolymer": 0.85}}}
4	2	4	{"deletion": {"pattern": {"A": 0.15, "C": 0.35, "G": 0.35, "T": 0.15}, "position": {"random": 0.15, "homopolymer": 0.85}}, "mismatch": {"pattern": {"CG": ["CA", "TG"]}}, "insertion": {"pattern": {"A": 0.35, "C": 0.15, "G": 0.15, "T": 0.35}, "position": {"random": 0.15, "homopolymer": 0.85}}}
5	3	5	{"deletion": {"pattern": {"A": 0.15, "C": 0.35, "G": 0.35, "T": 0.15}, "position": {"random": 0.54, "homopolymer": 0.46}}, "mismatch": {"pattern": {"TAC": "TGC", "TAG": "TGG"}}, "insertion": {"pattern": {"A": 0.35, "C": 0.15, "G": 0.15, "T": 0.35}, "position": {"random": 0.54, "homopolymer": 0.46}}}
6	3	6	{"deletion": {"pattern": {"A": 0.15, "C": 0.35, "G": 0.35, "T": 0.15}, "position": {"random": 0.54, "homopolymer": 0.46}}, "mismatch": {"pattern": {"TAC": "TGC", "TAG": "TGG"}}, "insertion": {"pattern": {"A": 0.35, "C": 0.15, "G": 0.15, "T": 0.35}, "position": {"random": 0.54, "homopolymer": 0.46}}}
7	4	7	{}
\.


--
-- Data for Name: pcr; Type: TABLE DATA; Schema: public; Owner: dna_sim
--

COPY public.pcr (id, method_id, err_data, user_id, validated, err_attributes, name, awaits_validation, validation_desc) FROM stdin;
2	9	{"raw_rate": 0.000043, "mismatch": 0.99, "deletion": 0.01, "insertion": 0}	0	t	{"deletion": {"position": {"homopolymer": 0, "random": 1}, "pattern": {"G": 0.25, "C": 0.25, "A": 0.25, "T": 0.25}}, "insertion": {"position": {"homopolymer": 0, "random": 1}, "pattern": {"A": 0.25, "T": 0.25, "C": 0.25, "G": 0.25}}, "mismatch": {"pattern": {"A": {"G": 0.97, "T": 0.01, "C": 0.02}, "T": {"C": 0.97, "A": 0.01, "G": 0.02}, "G": {"A": 1, "T": 0, "C": 0}, "C": {"T": 1, "G": 0, "A": 0}}}}	Taq	f	\N
3	9	{"raw_rate": 0.0000024, "mismatch": 1, "deletion": 0, "insertion": 0}	0	t	{"deletion": {"position": {"homopolymer": 0, "random": 1}, "pattern": {"G": 0.25, "C": 0.25, "A": 0.25, "T": 0.25}}, "insertion": {"position": {"homopolymer": 0, "random": 1}, "pattern": {"A": 0.25, "T": 0.25, "C": 0.25, "G": 0.25}}, "mismatch": {"pattern": {"A": {"G": 1, "T": 0, "C": 0}, "T": {"C": 0.67, "A": 0.33, "G": 0}, "G": {"A": 0.57, "T": 0, "C": 0.43}, "C": {"T": 1, "G": 0, "A": 0}}}}	Pwo	f	\N
4	9	{"raw_rate": 0.0000028, "mismatch": 1, "deletion": 0, "insertion": 0}	0	t	{"deletion": {"position": {"homopolymer": 0, "random": 1}, "pattern": {"G": 0.25, "C": 0.25, "A": 0.25, "T": 0.25}}, "insertion": {"position": {"homopolymer": 0, "random": 1}, "pattern": {"A": 0.25, "T": 0.25, "C": 0.25, "G": 0.25}}, "mismatch": {"pattern": {"A": {"G": 0.75, "T": 0.25, "C": 0}, "T": {"C": 0.75, "A": 0.25, "G": 0}, "G": {"A": 1, "T": 0, "C": 0}, "C": {"T": 1, "G": 0, "A": 0}}}}	Pfu	f	\N
1	9	{"raw_rate": 0.0000026, "mismatch": 0.84, "deletion": 0.08, "insertion": 0.08}	0	t	{"deletion": {"position": {"homopolymer": 0, "random": 1}, "pattern": {"G": 0.25, "C": 0.25, "A": 0.25, "T": 0.25}}, "insertion": {"position": {"homopolymer": 0, "random": 1}, "pattern": {"A": 0.25, "T": 0.25, "C": 0.25, "G": 0.25}}, "mismatch": {"pattern": {"A": {"G": 1, "T": 0, "C": 0}, "T": {"C": 1, "A": 0, "G": 0}, "G": {"A": 1, "T": 0, "C": 0}, "C": {"T": 1, "G": 0, "A": 0}}}}	Phusion	f	\N
7	6	{"deletion": 0.3333, "insertion": 0.3333, "mismatch": 0.33340000000000003, "raw_rate": 0.0}	0	t	{"deletion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0.5, "random": 0.5}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0.5, "random": 0.5}}, "mismatch": {"pattern": {}}}	None	f	\N
\.


--
-- Data for Name: seq_err_rates; Type: TABLE DATA; Schema: public; Owner: dna_sim
--

COPY public.seq_err_rates (id, method_id, err_data, user_id, validated, err_attributes, name, awaits_validation, validation_desc) FROM stdin;
41	6	{"raw_rate": 0, "mismatch": 0.3, "deletion": 0.3, "insertion": 0.4}	0	t	{"deletion": {"position": {"homopolymer": 0.46, "random": 0.54},\n                                          "pattern": {"G": 0.35, "C": 0.35, "A": 0.15, "T": 0.15}},\n                             "insertion": {"position": {"homopolymer": 0.46, "random": 0.54},\n                                           "pattern": {"A": 0.35, "T": 0.35, "C": 0.15, "G": 0.15}},\n                             "mismatch": {"pattern": {"TAG": {"TGG":1.0}, "TAC": {"TGC":1.0}}}}	None	f	\N
40	5	{"raw_rate": 0.13, "mismatch": 0.41, "deletion": 0.36, "insertion": 0.23}	0	t	{"deletion": {"position": {"homopolymer": 0.46, "random": 0.54},\n                                          "pattern": {"G": 0.35, "C": 0.35, "A": 0.15, "T": 0.15}},\n                             "insertion": {"position": {"homopolymer": 0.46, "random": 0.54},\n                                           "pattern": {"A": 0.35, "T": 0.35, "C": 0.15, "G": 0.15}},\n                             "mismatch": {"pattern": {"TAG": {"TGG":1.0}, "TAC": {"TGC":1.0}}}}	2D	f	\N
37	4	{"raw_rate": 0.02, "mismatch": 0.75, "deletion": 0.20, "insertion": 0.05}	0	t	{"deletion": {"position": {"homopolymer": 0.85, "random": 0.15},\n                                          "pattern": {"G": 0.35, "C": 0.35, "A": 0.15, "T": 0.15}},\n                             "insertion": {"position": {"homopolymer": 0.85, "random": 0.15},\n                                           "pattern": {"A": 0.35, "T": 0.35, "C": 0.15, "G": 0.15}},\n                             "mismatch": {"pattern": {"CG": {"CA": 0.5, "TG": 0.5}}}}	Subread	f	\N
36	3	{"raw_rate": 0.0032, "mismatch": 0.79, "deletion": 0.0018, "insertion": 0.0011}	0	t	{"deletion": {"position": {"random": 1},\n                                          "pattern": {"G": 0.25, "C": 0.25, "A": 0.25, "T": 0.25}},\n                             "insertion": {"position": {"random": 1},\n                                           "pattern": {"G": 0.25, "C": 0.25, "A": 0.25, "T": 0.25}},\n                             "mismatch": {"pattern": {"A": {"G": 0.50, "T": 0.25, "C": 0.25},\n                                                      "T": {"G": 0.50, "A": 0.25, "C": 0.25},\n                                                      "C": {"G": 0.50, "A": 0.25, "T": 0.25},\n                                                      "G": {"T": 0.50, "A": 0.25, "C": 0.25}}}}	Paired End	f	\N
39	5	{"raw_rate": 0.2, "mismatch": 0.48, "deletion": 0.37, "insertion": 0.15}	0	t	{"deletion": {"position": {"homopolymer": 0.46, "random": 0.54},\n                                          "pattern": {"G": 0.35, "C": 0.35, "A": 0.15, "T": 0.15}},\n                             "insertion": {"position": {"homopolymer": 0.46, "random": 0.54},\n                                           "pattern": {"A": 0.35, "T": 0.35, "C": 0.15, "G": 0.15}},\n                             "mismatch": {"pattern": {"TAG": {"TGG":1.0}, "TAC": {"TGC":1.0}}}}	1D	f	\N
38	4	{"raw_rate": 0.14, "mismatch": 0.37, "deletion": 0.21, "insertion": 0.42}	0	t	{"deletion": {"position": {"homopolymer": 0.85, "random": 0.15},\n                                          "pattern": {"G": 0.35, "C": 0.35, "A": 0.15, "T": 0.15}},\n                             "insertion": {"position": {"homopolymer": 0.85, "random": 0.15},\n                                           "pattern": {"A": 0.35, "T": 0.35, "C": 0.15, "G": 0.15}},\n                             "mismatch": {"pattern": {"CG": {"CA": 0.5, "TG": 0.5}}}}	CCS	f	\N
35	0	{"deletion": 0.0024, "insertion": 0.0013, "mismatch": 0.9963, "raw_rate": 0.0021}	0	t	{"deletion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0, "random": 1}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0, "random": 1}}, "mismatch": {"pattern": {"A": {"C": 0.25, "G": 0.5, "T": 0.25}, "C": {"A": 0.25, "G": 0.5, "T": 0.25}, "T": {"G": 0.50, "A": 0.25, "C": 0.25}, "G": {"A": 0.25, "C": 0.25, "T": 0.5}}}}	Single End	f	\N
\.


--
-- Data for Name: storage; Type: TABLE DATA; Schema: public; Owner: dna_sim
--

COPY public.storage (id, err_data, user_id, validated, err_attributes, name, awaits_validation, validation_desc, method_id) FROM stdin;
3	{"deletion": 0.33, "insertion": 0.33, "mismatch": 0.34, "raw_rate": 0.000000021}	0	t	{"deletion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0, "random": 1}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0, "random": 1}}, "mismatch": {"pattern": {}}}	D melanogaster	f	Drake JW, Charlesworth B, Charlesworth D, Crow JF. Rates of spontaneous mutation. Genetics. 1998 Apr148(4):1667-86. And Evolution of the Insertion-Deletion Mutation Rate\nAcross the Tree of Life	7
5	{"deletion": 0.13, "insertion": 0.13, "mismatch": 0.74, "raw_rate": 0.000000079}	0	t	{"deletion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0, "random": 1}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0, "random": 1}}, "mismatch": {"pattern": {}}}	S cerevisiae	f	Drake JW, Charlesworth B, Charlesworth D, Crow JF. Rates of spontaneous mutation. Genetics. 1998 Apr148(4):1667-86. And Evolution of the Insertion-Deletion Mutation Rate\nAcross the Tree of Life	7
4	{"deletion": 0.08, "insertion": 0.08, "mismatch": 0.84, "raw_rate": 0.000000317}	0	t	{"deletion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0, "random": 1}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0, "random": 1}}, "mismatch": {"pattern": {}}}	E coli	f	Lee H, Popodi E, Tang H, Foster PL. Rate and molecular spectrum of spontaneous mutations in the bacterium Escherichia coli as determined by whole-genome sequencing. Proc Natl Acad Sci U S A. 2012 Oct 9 109(41):E2774-83. doi: 10.1073/pnas.1210309109 and Evolution of the Insertion-Deletion Mutation Rate\nAcross the Tree of Life	8
1	{"deletion": 0.06, "insertion": 0.06, "mismatch": 0.88, "raw_rate": 0.000000000069}	0	t	{"deletion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0, "random": 1}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0, "random": 1}}, "mismatch": {"pattern": {}}}	H sapiens	f	Nachman MW, Crowell SL. Estimate of the mutation rate per nucleotide in humans. Genetics. 2000 Sep156(1):297-304 and Evolution of the Insertion-Deletion Mutation Rate\nAcross the Tree of Life	7
2	{"deletion": 0.025, "insertion": 0.025, "mismatch": 0.95, "raw_rate": 0.0000000044}	0	t	{"deletion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0, "random": 1}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0, "random": 1}}, "mismatch": {"pattern": {}}}	M musculus	f	Drake JW, Charlesworth B, Charlesworth D, Crow JF. Rates of spontaneous mutation. Genetics. 1998 Apr148(4):1667-86. And Evolution of the Insertion-Deletion Mutation Rate\nAcross the Tree of Life	7
8	{"deletion": 0.3333, "insertion": 0.3333, "mismatch": 0.33340000000000003, "raw_rate": 0.0}	0	t	{"deletion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0.5, "random": 0.5}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0.5, "random": 0.5}}, "mismatch": {"pattern": {}}}	None	f	\N	6
10	{"deletion": 0.0, "insertion": 0.0, "mismatch": 1.0, "raw_rate": 0.005}	16	t	{"deletion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0.5, "random": 0.5}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0.5, "random": 0.5}}, "mismatch": {"pattern": {"A": {"T": 0.3333, "G": 0.33340000000000003, "C": 0.3333}, "T": {"A": 0.3333, "G": 0.33340000000000003, "C": 0.3333}, "C": {"G": 0.3333, "T": 0.33340000000000003, "A": 0.3333}, "G": {"A": 0.3333, "T": 0.33340000000000003, "C": 0.3333}}}}	White Gaussian Noise with an error probability of 05 percent	f	\N	0
15	{"deletion": 1, "insertion": 0, "mismatch": 0, "raw_rate": 9e-08}	16	t	{"deletion": {"pattern": {"A": 0.5, "C": 0.0, "G": 0.5, "T": 0.0}, "position": {"homopolymer": 0.0, "random": 1.0}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0.5, "random": 0.5}}, "mismatch": {"pattern": {}}}	Depurination at pH 7 and 253K (invitro)	f	\N	0
12	{"deletion": 1, "insertion": 0, "mismatch": 0, "raw_rate": 1e-08}	16	t	{"deletion": {"pattern": {"A": 0.5, "C": 0.0, "G": 0.5, "T": 0.0}, "position": {"homopolymer": 0.0, "random": 1.0}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0.5, "random": 0.5}}, "mismatch": {"pattern": {}}}	Depurination at pH 8 and 253K	f	\N	0
11	{"deletion": 1, "insertion": 0, "mismatch": 0, "raw_rate": 1.283e-05}	16	t	{"deletion": {"pattern": {"A": 0.5, "C": 0.0, "G": 0.5, "T": 0.0}, "position": {"homopolymer": 0.0, "random": 1.0}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0.5, "random": 0.5}}, "mismatch": {"pattern": {}}}	Depurination at pH 8 and 293K (invitro)	f	\N	0
9	{"deletion": 1, "insertion": 0, "mismatch": 0, "raw_rate": 0.005}	16	t	{"deletion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0.0, "random": 1.0}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0.5, "random": 0.5}}, "mismatch": {"pattern": {}}}	Erasure Channel with an error probability of 05 percent	f	\N	0
14	{"deletion": 1, "insertion": 0, "mismatch": 0, "raw_rate": 0}	16	t	{"deletion": {"pattern": {"A": 0.5, "C": 0.0, "G": 0.5, "T": 0.0}, "position": {"homopolymer": 0.0, "random": 1.0}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0.5, "random": 0.5}}, "mismatch": {"pattern": {}}}	Depurination at pH 7 and 193K (invitro)	f	\N	0
13	{"deletion": 1, "insertion": 0, "mismatch": 0, "raw_rate": 0}	16	t	{"deletion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0.5, "random": 0.5}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0.5, "random": 0.5}}, "mismatch": {"pattern": {}}}	Depurination at pH 8 and 193K (invitro)	f	\N	0
16	{"deletion": 1, "insertion": 0, "mismatch": 0, "raw_rate": 0.0001231}	16	t	{"deletion": {"pattern": {"A": 0.5, "C": 0.0, "G": 0.5, "T": 0.0}, "position": {"homopolymer": 0.0, "random": 1.0}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0.5, "random": 0.5}}, "mismatch": {"pattern": {}}}	Depurination at pH 7 and 293K (invitro)	f	\N	0
\.


--
-- Data for Name: synth_err_rates; Type: TABLE DATA; Schema: public; Owner: dna_sim
--

COPY public.synth_err_rates (id, method_id, err_data, user_id, validated, err_attributes, name, awaits_validation, validation_desc) FROM stdin;
68	1	{"raw_rate": 0.0001, "mismatch": 0.15, "deletion": 0.7, "insertion": 0.15}	0	t	{"deletion": {"position": {"homopolymer": 0.0, "random": 1}, "pattern": {"G": 0.2, "C": 0.2, "A": 0.4, "T": 0.2}},"insertion": {"position": {"homopolymer": 0, "random": 1},"pattern": {"A": 0.25, "T": 0.25, "C": 0.25, "G": 0.25}},"mismatch": {}}	MutS	f	\N
69	1	{"raw_rate": 0.000125, "mismatch": 0.15, "deletion": 0.7, "insertion": 0.15}	0	t	{"deletion": {"position": {"homopolymer": 0.0, "random": 1}, "pattern": {"G": 0.2, "C": 0.2, "A": 0.4, "T": 0.2}},"insertion": {"position": {"homopolymer": 0, "random": 1},"pattern": {"A": 0.25, "T": 0.25, "C": 0.25, "G": 0.25}},"mismatch": {}}	Consensus Shuffle	f	\N
70	2	{"raw_rate": 0.00011, "mismatch": 0.2, "deletion": 0.6, "insertion": 0.2}	0	t	{"deletion": {"position": {"homopolymer": 0.0, "random": 1}, "pattern": {"G": 0.2, "C": 0.2, "A": 0.4, "T": 0.2}},"insertion": {"position": {"homopolymer": 0, "random": 1},"pattern": {"A": 0.25, "T": 0.25, "C": 0.25, "G": 0.25}},"mismatch": {}}	NGS-based error correction	f	\N
5	2	{"raw_rate": 0.0017, "mismatch": 0.2, "deletion": 0.6, "insertion": 0.2}	0	t	{"deletion": {"position": {"homopolymer": 0.0, "random": 1}, "pattern": {"G": 0.2, "C": 0.2, "A": 0.4, "T": 0.2}},"insertion": {"position": {"homopolymer": 0, "random": 1},"pattern": {"A": 0.25, "T": 0.25, "C": 0.25, "G": 0.25}},"mismatch": {"pattern": {"AAAA": {"ACGT":1.0}, "ACCC": {"ACGC":1.0}}}}	High-temperature ligation/hybridization based error correction	f	\N
6	2	{"raw_rate": 0.00125, "mismatch": 0.2, "deletion": 0.6, "insertion": 0.2}	0	t	{"deletion": {"position": {"homopolymer": 0.0, "random": 1}, "pattern": {"G": 0.2, "C": 0.2, "A": 0.4, "T": 0.2}},"insertion": {"position": {"homopolymer": 0, "random": 1},"pattern": {"A": 0.25, "T": 0.25, "C": 0.25, "G": 0.25}},"mismatch": {}}	ErrASE	f	\N
7	2	{"raw_rate": 0.00033, "mismatch": 0.2, "deletion": 0.6, "insertion": 0.2}	0	t	{"deletion": {"position": {"homopolymer": 0.0, "random": 1}, "pattern": {"G": 0.2, "C": 0.2, "A": 0.4, "T": 0.2}},"insertion": {"position": {"homopolymer": 0, "random": 1},"pattern": {"A": 0.25, "T": 0.25, "C": 0.25, "G": 0.25}},"mismatch": {}}	Nuclease-based error correction	f	\N
3	1	{"raw_rate": 0.000025, "mismatch": 0.2, "deletion": 0.6, "insertion": 0.2}	0	t	{"deletion": {"pattern": {"A": 0.4, "C": 0.2, "G": 0.2, "T": 0.2}, "position": {"homopolymer": 0, "random": 1}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0, "random": 1}}, "mismatch": {"pattern": {}}}	ErrASE	f	\N
4	2	{"raw_rate": 0.0004, "mismatch": 0.2, "deletion": 0.6, "insertion": 0.2}	0	t	{"deletion": {"pattern": {"A": 0.4, "C": 0.2, "G": 0.2, "T": 0.2}, "position": {"homopolymer": 0, "random": 1}}, "insertion": {"pattern": {"A": 0.25, "C": 0.25, "G": 0.25, "T": 0.25}, "position": {"homopolymer": 0, "random": 1}}, "mismatch": {"pattern": {}}}	Oligo Hybridization based error correction	f	\N
71	6	{"raw_rate": 0, "mismatch": 0.3, "deletion": 0.3, "insertion": 0.3}	0	t	{"deletion": {"position": {"homopolymer": 0.0, "random": 1}, "pattern": {"G": 0.2, "C": 0.2, "A": 0.4, "T": 0.2}},"insertion": {"position": {"homopolymer": 0, "random": 1},"pattern": {"A": 0.25, "T": 0.25, "C": 0.25, "G": 0.25}},"mismatch": {}}	None	f	\N
\.


--
-- Data for Name: undesiredsubsequences; Type: TABLE DATA; Schema: public; Owner: dna_sim
--

COPY public.undesiredsubsequences (id, sequence, error_prob, created, validated, owner_id, description, awaits_validation, validation_desc) FROM stdin;
57	TATAAA	1	1572601880	t	16	Eukaryotic promotor recognition motif httpsdoiorg10101600222836(90)902239	f	\N
80	GGATACTT	1	1572603504	t	16	Lox site spacer lox3 httpsdoiorg10118614712164773	f	\N
58	TTGACA	1	1572601974	t	16	Prokaryotic promoter recognition motif httpsdoiorg101016jjmb201101018	f	\N
59	TGTATAATG	1	1572602092	t	16	Prokaryotic promoter recognition motif httpsdoiorg101016jjmb201101018	f	\N
60	GCCACCATGG	1	1572602249	t	16	Eukaryotic ribosomal binding site httpsdoiorg10101600222836(87)904189	f	\N
61	ACCACCATGG	1	1572602275	t	16	Eukaryotic ribosomal binding site httpsdoiorg10101600222836(87)904189	f	\N
62	AATAAA	1	1572602545	t	16	Eukaryotic polyadenylation signal httpsdoiorg10101600928674(87)902923	f	\N
63	TTGTGTGTTG	1	1572602565	t	16	Eukaryotic polyadenylation signal httpsdoiorg10101600928674(87)902923	f	\N
65	ATAACTTCGTATAGCATACATTATACGAACGGTA	1	1572602735	t	16	loxR httpsdoiorg101016jjbiotec201606033	f	\N
81	TACTATAC	1	1572603524	t	16	Lox site spacer lox4 httpsdoiorg10118614712164773	f	\N
68	TACCGTTCGTATATGGTATTATATACGAAGTTAT	1	1572603087	t	16	lox1R httpsdoiorg101016jjbiotec201606033	f	\N
67	TACCGTTCGTATAGCATACATTATACGAACGGTA	1	1572603059	t	16	loxLR httpsdoiorg101016jjbiotec201606033	f	\N
82	CTATAGCC	1	1572603541	t	16	Lox site spacer lox5 httpsdoiorg10118614712164773	f	\N
66	TACCGTTCGTATAGCATACATTATACGAAGTTAT	1	1572602757	t	16	loxL httpsdoiorg101016jjbiotec201606033	f	\N
69	TACCGTTCGTATATTCTATCTTATACGAAGTTAT	1	1572603112	t	16	lox2R httpsdoiorg101016jjbiotec201606033	f	\N
70	TACCGTTCGTATAGGATACTTTATACGAAGTTAT	1	1572603134	t	16	lox3R httpsdoiorg101016jjbiotec201606033	f	\N
71	TACCGTTCGTATATACTATACTATACGAAGTTAT	1	1572603157	t	16	lox4R httpsdoiorg101016jjbiotec201606033	f	\N
72	TACCGTTCGTATACTATAGCCTATACGAAGTTAT	1	1572603185	t	16	lox5R httpsdoiorg101016jjbiotec201606033	f	\N
73	ATAACTTCGTATATGGTATTATATACGAACGGTA	1	1572603211	t	16	Lox1L httpsdoiorg101016jjbiotec201606033	f	\N
74	ATAACTTCGTATAGTATACCTTATACGAAGTTAT	1	1572603228	t	16	loxN httpsdoiorg101016jjbiotec201606033	f	\N
75	ATAACTTCGTATAGTATACATTATACGAAGTTAT	1	1572603245	t	16	loxP 511 httpsdoiorg101016jjbiotec201606033	f	\N
76	ATAACTTCGTATAGTACACATTATACGAAGTTAT	1	1572603261	t	16	lox 5171 httpsdoiorg101016jjbiotec201606033	f	\N
77	GCATACAT	1	1572603300	t	16	Lox site spacer loxP WT	f	\N
78	TGGTATTA	1	1572603458	t	16	Lox site spacer lox1 httpsdoiorg10118614712164773	f	\N
79	TTCTATCT	1	1572603481	t	16	Lox site spacer lox2 httpsdoiorg10118614712164773	f	\N
83	AGGTATGC	1	1572603634	t	16	Lox site spacer lox6 httpsdoiorg101007978981103874733	f	\N
84	TTGTATGG	1	1572603651	t	16	Lox site spacer lox7 httpsdoiorg101007978981103874733	f	\N
85	GGATAGTA	1	1572603671	t	16	Lox site spacer lox8 httpsdoiorg101007978981103874733	f	\N
86	GTGTATTT	1	1572603691	t	16	Lox site spacer lox9 httpsdoiorg101007978981103874733	f	\N
87	GGTTACGG	1	1572607663	t	16	Lox site spacer lox10 httpsdoiorg101007978981103874733	f	\N
88	TTTTAGGT	1	1572607694	t	16	Lox site spacer lox11 httpsdoiorg101007978981103874733	f	\N
89	GTATACCT	1	1572607736	t	16	Lox site spacer loxN httpsdoiorg101038nature06293	f	\N
90	GTACACAT	1	1572607788	t	16	Lox site spacer loxP 5171 httpsdoiorg101007978981103874733	f	\N
91	GAAGAC	1	1572607808	t	16	BbsI	f	\N
92	GGTCTC	1	1572607824	t	16	BsaI	f	\N
93	CGTCTC	1	1572607837	t	16	BsmBI	f	\N
94	GCTCTTC	1	1572607848	t	16	BspQI	f	\N
95	GCGATG	1	1572607862	t	16	BtgZI	f	\N
96	CGTCTC	1	1572607874	t	16	Esp3I	f	\N
97	GCTCTTC	1	1572607886	t	16	SapI	f	\N
98	CTCGTAGACTGCGTACCA	1	1572607899	t	16	Adapter F httpsdoiorg10118617464811832	f	\N
99	GACGATGAGTCCTGAGTA	1	1572607910	t	16	Adapter R httpsdoiorg10118617464811832	f	\N
100	GGTTCCACGTAAGCTTCC	1	1572607980	t	16	H1 (HindIII) httpsdoiorg101016jjbiotec200308005	f	\N
101	GCGATTACCCTGTACACC	1	1572608007	t	16	B4 (BsrGI) httpsdoiorg101016jjbiotec200308005	f	\N
102	GCCAGTACATCAATTGCC	1	1572608027	t	16	M3 (MfeI) httpsdoiorg101016jjbiotec200308005	f	\N
64	ATAACTTCGTATAGCATACATTATACGAAGTTAT	1	1572602607	f	16	loxP httpsdoiorg101016jjbiotec201606033	f	\N
\.


--
-- Name: api_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dna_sim
--

SELECT pg_catalog.setval('public.api_id_seq', 19, true);


--
-- Name: err_rates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dna_sim
--

SELECT pg_catalog.setval('public.err_rates_id_seq', 7, true);


--
-- Name: error_probability_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dna_sim
--

SELECT pg_catalog.setval('public.error_probability_id_seq', 37, true);


--
-- Name: mutation_attributes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dna_sim
--

SELECT pg_catalog.setval('public.mutation_attributes_id_seq', 7, true);


--
-- Name: pcr_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dna_sim
--

SELECT pg_catalog.setval('public.pcr_id_seq', 7, true);


--
-- Name: seq_err_rates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dna_sim
--

SELECT pg_catalog.setval('public.seq_err_rates_id_seq', 41, true);


--
-- Name: storage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dna_sim
--

SELECT pg_catalog.setval('public.storage_id_seq', 17, true);


--
-- Name: synth_err_rates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dna_sim
--

SELECT pg_catalog.setval('public.synth_err_rates_id_seq', 80, true);


--
-- Name: synth_meth_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dna_sim
--

SELECT pg_catalog.setval('public.synth_meth_id_seq', 4, true);


--
-- Name: undesiredsubsequences_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dna_sim
--

SELECT pg_catalog.setval('public.undesiredsubsequences_id_seq', 102, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dna_sim
--

SELECT pg_catalog.setval('public.user_id_seq', 18, true);


--
-- Name: Apikey apikey_pk; Type: CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public."Apikey"
    ADD CONSTRAINT apikey_pk PRIMARY KEY (id);


--
-- Name: err_rates err_rates_pkey; Type: CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.err_rates
    ADD CONSTRAINT err_rates_pkey PRIMARY KEY (id);


--
-- Name: error_probability error_probability_pk; Type: CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.error_probability
    ADD CONSTRAINT error_probability_pk PRIMARY KEY (id);


--
-- Name: mutation_attributes mutation_attributes_pkey; Type: CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.mutation_attributes
    ADD CONSTRAINT mutation_attributes_pkey PRIMARY KEY (id);


--
-- Name: pcr pcr_pkey; Type: CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.pcr
    ADD CONSTRAINT pcr_pkey PRIMARY KEY (id);


--
-- Name: seq_err_rates seq_err_rates_pk; Type: CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.seq_err_rates
    ADD CONSTRAINT seq_err_rates_pk PRIMARY KEY (id);


--
-- Name: storage storage_pkey; Type: CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.storage
    ADD CONSTRAINT storage_pkey PRIMARY KEY (id);


--
-- Name: synth_err_rates synth_err_rates_pkey; Type: CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.synth_err_rates
    ADD CONSTRAINT synth_err_rates_pkey PRIMARY KEY (id);


--
-- Name: meth_categories synth_meth_pkey; Type: CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.meth_categories
    ADD CONSTRAINT synth_meth_pkey PRIMARY KEY (id);


--
-- Name: undesiredsubsequences undesiredsubsequences_pk; Type: CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.undesiredsubsequences
    ADD CONSTRAINT undesiredsubsequences_pk PRIMARY KEY (id);


--
-- Name: User user_pk; Type: CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public."User"
    ADD CONSTRAINT user_pk PRIMARY KEY (user_id);


--
-- Name: apikey_apikey_uindex; Type: INDEX; Schema: public; Owner: dna_sim
--

CREATE UNIQUE INDEX apikey_apikey_uindex ON public."Apikey" USING btree (apikey);


--
-- Name: error_probability_id_uindex; Type: INDEX; Schema: public; Owner: dna_sim
--

CREATE UNIQUE INDEX error_probability_id_uindex ON public.error_probability USING btree (id);


--
-- Name: seq_err_rates_id_uindex; Type: INDEX; Schema: public; Owner: dna_sim
--

CREATE UNIQUE INDEX seq_err_rates_id_uindex ON public.seq_err_rates USING btree (id);


--
-- Name: user_email_uindex; Type: INDEX; Schema: public; Owner: dna_sim
--

CREATE UNIQUE INDEX user_email_uindex ON public."User" USING btree (email);


--
-- Name: user_user_id_uindex; Type: INDEX; Schema: public; Owner: dna_sim
--

CREATE UNIQUE INDEX user_user_id_uindex ON public."User" USING btree (user_id);


--
-- Name: Apikey apikey_user_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public."Apikey"
    ADD CONSTRAINT apikey_user_id_fk FOREIGN KEY (owner_id) REFERENCES public."User"(user_id);


--
-- Name: error_probability error_probability_user_user_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.error_probability
    ADD CONSTRAINT error_probability_user_user_id_fk FOREIGN KEY (user_id) REFERENCES public."User"(user_id);


--
-- Name: pcr pcr_meth_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.pcr
    ADD CONSTRAINT pcr_meth_id_fk FOREIGN KEY (method_id) REFERENCES public.meth_categories(id);


--
-- Name: seq_err_rates seq_err_rates_meth_categories_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.seq_err_rates
    ADD CONSTRAINT seq_err_rates_meth_categories_id_fk FOREIGN KEY (method_id) REFERENCES public.meth_categories(id);


--
-- Name: seq_err_rates seq_err_rates_user_user_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.seq_err_rates
    ADD CONSTRAINT seq_err_rates_user_user_id_fk FOREIGN KEY (user_id) REFERENCES public."User"(user_id);


--
-- Name: storage storage_meth_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.storage
    ADD CONSTRAINT storage_meth_id_fk FOREIGN KEY (method_id) REFERENCES public.meth_categories(id);


--
-- Name: storage storage_user_user_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.storage
    ADD CONSTRAINT storage_user_user_id_fk FOREIGN KEY (user_id) REFERENCES public."User"(user_id);


--
-- Name: synth_err_rates synth_err_rates_synth_meth_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.synth_err_rates
    ADD CONSTRAINT synth_err_rates_synth_meth_id_fk FOREIGN KEY (method_id) REFERENCES public.meth_categories(id);


--
-- Name: synth_err_rates synth_err_rates_user_user_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.synth_err_rates
    ADD CONSTRAINT synth_err_rates_user_user_id_fk FOREIGN KEY (user_id) REFERENCES public."User"(user_id);


--
-- Name: undesiredsubsequences undesiredsubsequences_user_user_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.undesiredsubsequences
    ADD CONSTRAINT undesiredsubsequences_user_user_id_fk FOREIGN KEY (owner_id) REFERENCES public."User"(user_id);


--
-- Name: pcr user_user_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: dna_sim
--

ALTER TABLE ONLY public.pcr
    ADD CONSTRAINT user_user_id_fk FOREIGN KEY (user_id) REFERENCES public."User"(user_id);


--
-- PostgreSQL database dump complete
--

\connect postgres

--
-- PostgreSQL database dump
--

-- Dumped from database version 11.3
-- Dumped by pg_dump version 11.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database cluster dump complete
--

