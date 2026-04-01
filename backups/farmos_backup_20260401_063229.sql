--
-- PostgreSQL database dump
--

\restrict 0ZkdCg4DOGOOdwXp1SuUbnKChTNcHg2pHWZRjc7q1quuJ3fSX26PFwzhHTvQeYU

-- Dumped from database version 16.13 (Debian 16.13-1.pgdg13+1)
-- Dumped by pg_dump version 16.13 (Debian 16.13-1.pgdg13+1)

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
-- Name: categoryenum; Type: TYPE; Schema: public; Owner: farm_user
--

CREATE TYPE public.categoryenum AS ENUM (
    'livestock_sales',
    'byproduct_sales',
    'other_income',
    'feed',
    'medicine',
    'labor',
    'assets',
    'livestock_purchases',
    'maintenance',
    'utilities',
    'consumables',
    'transport',
    'other_expense'
);


ALTER TYPE public.categoryenum OWNER TO farm_user;

--
-- Name: statusenum; Type: TYPE; Schema: public; Owner: farm_user
--

CREATE TYPE public.statusenum AS ENUM (
    'paid',
    'unpaid',
    'partially_paid'
);


ALTER TYPE public.statusenum OWNER TO farm_user;

--
-- Name: transactiontypeenum; Type: TYPE; Schema: public; Owner: farm_user
--

CREATE TYPE public.transactiontypeenum AS ENUM (
    'income',
    'expense'
);


ALTER TYPE public.transactiontypeenum OWNER TO farm_user;

--
-- Name: unitofmeasureenum; Type: TYPE; Schema: public; Owner: farm_user
--

CREATE TYPE public.unitofmeasureenum AS ENUM (
    'kg',
    'liters',
    'head',
    'month',
    'day',
    'job',
    'other',
    'ml',
    'grams'
);


ALTER TYPE public.unitofmeasureenum OWNER TO farm_user;

--
-- Name: userrole; Type: TYPE; Schema: public; Owner: farm_user
--

CREATE TYPE public.userrole AS ENUM (
    'ADMIN',
    'STAFF'
);


ALTER TYPE public.userrole OWNER TO farm_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: farm_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO farm_user;

--
-- Name: farm_transactions; Type: TABLE; Schema: public; Owner: farm_user
--

CREATE TABLE public.farm_transactions (
    id integer NOT NULL,
    txn_date date NOT NULL,
    txn_type public.transactiontypeenum NOT NULL,
    category public.categoryenum NOT NULL,
    item_description character varying NOT NULL,
    qty double precision NOT NULL,
    unit_of_measure public.unitofmeasureenum NOT NULL,
    unit_price double precision NOT NULL,
    total_amount double precision NOT NULL,
    amount_paid double precision NOT NULL,
    payment_status public.statusenum NOT NULL,
    entity_name character varying,
    reference_tag character varying,
    remarks character varying
);


ALTER TABLE public.farm_transactions OWNER TO farm_user;

--
-- Name: farm_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: farm_user
--

CREATE SEQUENCE public.farm_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.farm_transactions_id_seq OWNER TO farm_user;

--
-- Name: farm_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: farm_user
--

ALTER SEQUENCE public.farm_transactions_id_seq OWNED BY public.farm_transactions.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: farm_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying NOT NULL,
    email character varying NOT NULL,
    hashed_password character varying NOT NULL,
    full_name character varying NOT NULL,
    role public.userrole NOT NULL,
    is_active boolean NOT NULL
);


ALTER TABLE public.users OWNER TO farm_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: farm_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO farm_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: farm_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: farm_transactions id; Type: DEFAULT; Schema: public; Owner: farm_user
--

ALTER TABLE ONLY public.farm_transactions ALTER COLUMN id SET DEFAULT nextval('public.farm_transactions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: farm_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: farm_user
--

COPY public.alembic_version (version_num) FROM stdin;
09c39f25bdc3
\.


--
-- Data for Name: farm_transactions; Type: TABLE DATA; Schema: public; Owner: farm_user
--

COPY public.farm_transactions (id, txn_date, txn_type, category, item_description, qty, unit_of_measure, unit_price, total_amount, amount_paid, payment_status, entity_name, reference_tag, remarks) FROM stdin;
46	2025-12-09	expense	feed	Feed Ingredient - SoyaMeal	5	kg	540	2700	2700	paid	Farm Support	\N	Purchase of 5kg of SoyaMeal from Farm Support
44	2025-12-09	expense	feed	Feed Ingredient - Maize	50	kg	460	23000	23000	paid	Farm Support	\N	Purchase 50kg of Maize from farm support Support.
50	2025-12-18	expense	feed	Feed Ingredient - PKC	100	kg	254	25400	25400	paid	Iya Eji Farm	\N	Purchase of PKC from Iya Eji Oke Aro Farm
5	2025-10-31	expense	consumables	Disinfectant (Morigrd)	1	liters	14500	14500	14500	paid	Epiphany Vets	\N	Disinfecting and washing the Pen.
27	2025-12-01	expense	medicine	Needle and Syinge 2mls	2	job	50	100	100	paid	Epiphany Vets	\N	Stored in the farm Medicine cabinet.
24	2025-12-01	expense	medicine	Ivanor Injection L.A 2% 100ml (Invermectin)	100	ml	30.5	3050	3050	paid	Epiphany Vets	\N	Stored in the farm Medicine cabinet.
28	2025-12-01	expense	medicine	Needle and Syinge 5mls	5	job	50	250	250	paid	Epiphany Vets	\N	Stored in the farm Medicine cabinet.
29	2025-12-01	expense	medicine	Multinor Injection 100ml	100	ml	17	1700	1700	paid	Epiphany Vets	\N	Stored in the farm Medicine cabinet.
30	2025-12-01	expense	medicine	Albenor 2.5% 100ml (Albendazole)	100	ml	6.8	680	680	paid	Epiphany Vets	\N	Stored in the farm Medicine cabinet.
31	2025-12-01	expense	medicine	Tetranor (Oxytet) 20% L.A 100ml	100	ml	25.5	2550	2550	paid	Epiphany Vets	\N	Stored in the farm Medicine cabinet.
32	2025-12-01	expense	medicine	I.D NOR Iron Dextran 100ml	100	ml	18.8	1880	1880	paid	Epiphany Vets	\N	Stored in the farm Medicine cabinet.
43	2025-12-08	expense	medicine	Needle and Syinge 5ml	2	job	70	140	140	paid	El-Bolus Farm Limited 	\N	Stored in the farm Medicine cabinet.
39	2025-12-08	expense	medicine	Medicine - Gent (100ml)	100	ml	54.5	5450	5450	paid	El-Bolus Farm Limited 	\N	Stored in the farm Medicine cabinet.
42	2025-12-08	expense	medicine	Needle and Syinge 2mls	2	job	60	120	120	paid	El-Bolus Farm Limited 	\N	Stored in the farm Medicine cabinet.
53	2025-12-16	expense	transport	Commute - Farm Visit (To & Fro)	1	other	2000	2000	2000	paid	Public Transport	\N	Transport to Farm Oke Aro TO and Fro
11	2025-11-01	expense	labor	Pen Cleaning and Disinfection.	1	job	6000	6000	6000	paid	Dada	\N	Paid to Dada for the first cleaning and washing of pen
13	2025-11-03	expense	labor	Labor - Bricklayer	1	job	4000	4000	4000	paid	Baba Dada	\N	Repair of Pen and Water Diversion by Bricklayer.
20	2025-11-04	expense	labor	In-Pig Gilt Transportation	2	job	2500	5000	5000	paid	Iya Eji Farm Transport	\N	TY Transport to New Location after leaning and Purcahse.
49	2025-12-11	expense	labor	Labor - Bush Clearing	1	job	3000	3000	3000	paid	Dada and Friends	\N	Clearing the Bush areound the Pen.
1	2025-10-30	expense	livestock_purchases	Purchase of In-Pig Gilt	2	head	350000	700000	700000	paid	Iya Eji Farm	\N	First Gilt Stock acquisition From Iya Eji Farms.
34	2025-12-01	expense	utilities	Security Levy - [1 Year]	1	other	1500	1500	1500	paid	Mrs. Fumilola	\N	Sent to Mrs. Fumilola for yearly Security Levy.
14	2025-11-04	expense	assets	Security Hardware - Small Padlock	1	other	5300	5300	5300	paid	Mrs. Fumilola Store Oke Aro	\N	For Security and bought from Mrs Fumilola Store Oke Aro.
15	2025-11-04	expense	consumables	Rain Boot	1	other	6500	6500	6500	paid	Taiwo Farm Agro Tech	\N	Protective gear for farm supervision.
16	2025-11-04	expense	consumables	Big Bowl	1	other	4500	4500	4500	paid	Mrs. Fumilola Store Oke Aro	\N	For Cleaning and Washing of the Pen, feed measurement. 
18	2025-11-04	expense	consumables	Farm Tool - Water Fetcher (Bucket/Bowl)	1	other	2700	2700	2700	paid	Oke Aro Farm Store	\N	Fetcher and Rope for water.
12	2025-11-03	expense	maintenance	Building Material - Cement	25	kg	208	5200	5200	paid	Unknown	\N	Purchase of Half Bag of Cement for pen maintenance.
4	2025-10-31	expense	utilities	Security Levy - [1 Year]	1	other	4500	4500	4500	paid	Mrs. Fumilola	\N	Sent to Mrs. Fumilola for yearly Security Levy.
6	2025-10-31	expense	consumables	Broom	1	other	1000	1000	1000	paid	Sleepwell Ventures.	\N	Washing the Pen.
7	2025-10-31	expense	consumables	Bucket	1	other	1500	1500	1500	paid	Sleepwell Ventures.	\N	For Cleaning and Washing of the Pen, feed measurement. 
38	2025-05-12	expense	maintenance	Building Material - Nylon	10	job	700	7000	7000	paid	Unknown	\N	Nylon to stop Rain from entering the Pen from the Window .
33	2025-12-01	expense	utilities	Pen Space Rent - [1 Year]	2	job	45000	90000	90000	paid	Mrs. Fumilola	\N	Sent to Mrs. Fumilola
37	2025-12-05	expense	labor	Staff Salary - Farm Assistant	1	month	6000	6000	6000	paid	Dada	\N	Worker Salary Paid in full 
2	2025-10-30	expense	utilities	Pen Space Rent - [1 Year]	3	job	40000	120000	120000	paid	Mrs. Fumilola	\N	Sent to Iya Eji and handed to Mrs. Fumilola
36	2025-05-12	expense	transport	Commute - Farm Visit (To & Fro)	2	head	2000	4000	4000	paid	Public Transport	\N	Transportation to Farm twice on day of littering.
22	2025-11-30	expense	transport	Commute - Farm Visit (To & Fro)	15	head	2000	30000	30000	paid	Public Transport	\N	Routine check on the weaning pigs at Oke Aro for November.
40	2025-12-08	expense	transport	Commute - Farm Visit (To & Fro)	2	head	1800	3600	3600	paid	Public Transport	\N	Transport to Farm Twice.
47	2025-12-09	expense	transport	Commute - Farm Visit (To & Fro)	1	head	1800	1800	1800	paid	Public Transport	\N	Transport to Farm (Oke Aro) to and fro.
48	2025-12-10	expense	transport	Commute - Farm Visit (To & Fro)	1	head	1800	1800	1800	paid	Public Transport	\N	Transport to Farm (Oke Aro) to and fro
52	2025-12-15	expense	transport	Commute - Farm Visit (To & Fro)	2	head	1800	3600	3600	paid	Public Transport	\N	Transport to Farm Oke Aro TO and Fro
51	2025-12-13	expense	transport	Commute - Farm Visit (To & Fro)	1	head	1800	1800	1800	paid	Public Transport	\N	Transport to Farm(Oke Aro) to and fro
54	2025-12-17	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Transport to Farm Oke Aro TO and Fro
41	2025-12-08	expense	transport	Transport to El-Bolus Farm	1	head	1400	1400	1400	paid	Public Transport	\N	Transport to get drugs from El-Bolus Farm to and fro.
77	2026-01-05	expense	feed	Feed Ingredient - Maize	25	kg	350	8750	8750	paid	Farm Support	\N	Purchase of maize of 25kg from Farm Support.
78	2026-01-05	expense	feed	Feed Ingredient - SoyaMeal	25	kg	540	13500	13500	paid	Farm Support	\N	Purchase of Soyameal of 25kg from farm Support
83	2026-01-06	expense	feed	Feed - Broiler Starter Feed 	25	kg	1000	25000	25000	paid	Oke Aro Farm Store	\N	Broiler Starter Feed for weaning 25kg.
106	2026-02-03	expense	feed	Feed - Broiler Starter Feed 	2	kg	1300	2600	2600	paid	Oke Aro Farm Store	\N	Purchase of Starter feed for Piglets
94	2026-01-21	expense	medicine	Medicine - Sulphonor Injection 100ml	100	ml	30	3000	3000	paid	Oke Aro Farm Store	\N	Stored in the farm Medicine cabinet.
99	2026-01-22	expense	medicine	Medicine - Tetracaclyn	1	other	500	500	500	paid	Oke Aro Farm Store	\N	Stored in the farm cabinet for regulating Diarrhea.
71	2026-01-29	expense	consumables	Disinfectant (Izal)	2	other	800	1600	1600	paid	Oke Aro Farm Store	\N	Disinfecting and washing the Pen.
70	2026-01-29	expense	consumables	Disinfectant (Morigrd)	2	other	1600	3200	3200	paid	Oke Aro Farm Store	\N	Disinfecting and washing the Pen.
100	2026-01-30	expense	medicine	Medication - Ivernor (100ml Bottle)	100	ml	30	3000	3000	paid	Oke Aro Farm Store	\N	Stored in the farm Medicine cabinet.
104	2026-02-02	expense	medicine	Medicine - Tetracaclyn	1	other	900	900	900	paid	Unknown	\N	Stored in the farm medication cabinet for regulating Diarrhea.
63	2025-12-29	expense	labor	Worker Bonus	1	job	3000	3000	3000	paid	Dada	\N	Workers fee for Pen Maintenance and Xmas bonus Gift.
58	2025-12-29	expense	labor	Food on Farm	1	other	1350	1350	1350	paid	Farm Manager - Victor	\N	Buying food at farm to refill for energy.
109	2026-02-05	expense	labor	Staff Salary - Farm Assistant	1	other	7000	7000	7000	paid	Dada	\N	Full payment for worker Salary for 3 pen and less than 30 days work.
84	2026-01-05	expense	labor	Staff Salary - Farm Assistant	1	month	6000	6000	6000	paid	Dada	\N	Full Payment of worker Salary 3000 per pen.
69	2025-12-02	expense	transport	Commute - Farm Visit (To & Fro)	1	other	2000	2000	2000	paid	Public Transport	\N	Routine Farm Check.
85	2026-01-09	expense	labor	Labor - Bricklayer	1	job	9000	9000	9000	paid	Baba Dada	\N	Full payment for Bricklayer labor 
95	2026-01-21	expense	maintenance	Building Material - Cement	5	kg	200	1000	1000	paid	Unknown	\N	Purchase of cement for maintenance
66	2025-12-30	expense	consumables	Brush	1	job	1200	1200	1200	paid	Sleepwell Ventures.	\N	Farm Maintenance Kit
64	2025-12-29	expense	consumables	Soap	1	job	500	500	500	paid	Unknown	\N	Washing the Pen.
62	2025-12-29	expense	maintenance	Wood - 2 by 2	1	other	1000	1000	1000	paid	Oke Aro Sawmill	\N	Purchase of wood for farm construction work
73	2026-01-03	expense	maintenance	Building Material - Cement	50	kg	206	10300	10300	paid	Unknown	\N	Purchase of cement for renovation of Pens before weaning.
60	2025-12-29	expense	maintenance	Farm Tools - Nails	1	other	900	900	900	paid	Unknown	\N	Purchase of nails for farm construction work
59	2025-12-29	expense	maintenance	Farm Tool - Hammer	1	other	3500	3500	3500	paid	\N	\N	Purchase hammer for farm construction work
61	2025-12-29	expense	maintenance	Building Material - Plank	1	other	4000	4000	4000	paid	Oke Aro Sawmill	\N	Purchase of wood for farm construction work
107	2026-02-03	expense	consumables	Disinfectant (Izal)	1	other	1200	1200	1200	paid	Unknown	\N	Purchase of Izal to wash the floor 
86	2026-01-09	expense	maintenance	Building Materials - Stones Purcahse	1	other	2000	2000	2000	paid	Unknown	\N	Purchase of stone used to mould feeding section inside pen
89	2026-01-09	expense	consumables	Soap	1	other	500	500	500	paid	Unknown	\N	Purchase of Soap for washing the pen
55	2025-12-18	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Transport to Farm Oke Aro TO and Fro
56	2025-12-25	expense	transport	Commute - Farm Visit (To & Fro)	4	head	2000	8000	8000	paid	Public Transport	\N	Transport to Farm Oke Aro TO and Fro
57	2025-12-29	expense	transport	Commute - Farm Visit (To & Fro)	1	head	3100	3100	3100	paid	Public Transport	\N	Transport to Farm Oke Aro TO and Fro
65	2025-12-29	expense	transport	Transport (Errands)	1	job	1000	1000	1000	paid	Public Transport	\N	Farm Maintenance for moving planks to farm.
76	2026-01-02	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2100	2100	2100	paid	Public Transport	\N	Transport to Farm Oke Aro TO and Fro
74	2026-01-03	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2100	2100	2100	paid	Public Transport	\N	Transport to Farm Oke Aro TO and Fro
68	2025-12-30	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Transport to Farm Oke Aro TO and Fro
82	2026-01-06	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2100	2100	2100	paid	Public Transport	\N	Transport to farm Oke Aro TO and Fro
87	2026-01-09	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Transport to Oke Aro to and fro for routine check.
90	2026-01-16	expense	transport	Commute - Farm Visit (To & Fro)	4	head	2000	8000	8000	paid	Public Transport	\N	Transport to Oke Aro to and fro for 4 days from 12 to 19
93	2026-01-21	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Transport to Oke Aro to and fro for routine check.
97	2026-01-22	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Transport to Oke Aro to and fro for routine check.
101	2026-01-30	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Transport to Oke Aro to and fro for routine check.
105	2026-02-03	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2999	paid	Public Transport	\N	Transport to Oke Aro to and fro for routine check.
108	2026-02-05	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Transport to Oke Aro to and fro for routine check.
23	2025-11-24	expense	feed	Feed Ingredients - PKC	100	kg	254	25400	25400	paid	Iya Eji Farm Store	\N	Sourced from Iya Eji Farm, good feed. Restocking of Feed after 20days, i.e each Gilt ate 1 pags for 10 days
67	2025-12-30	expense	feed	Feed - Broiler Starter	1	kg	1400	1400	1400	paid	Epiphany Farm	\N	Feed Starter from Oke Aro Farm 
79	2026-01-05	expense	feed	Feed Ingredient - Salt	5	kg	500	2500	2500	paid	Oke Aro Farm Store	\N	Purchase of 5kg of salt from Farm Support.
80	2026-01-05	expense	feed	Feed Ingredient - PKC	100	kg	250	25000	25000	paid	Iya Eji Farm	\N	Purchase of 100kg of PKC for the rate of 250 per kg from Iya Eji Store.
21	2025-11-04	expense	feed	Feed Ingredient - PKC	100	kg	240	24000	24000	paid	Unknown Vendor	\N	Sourced from town. Moisture content was low, excellent quality.
98	2026-01-22	expense	medicine	Medicine - Flagyl	1	other	1000	1000	1000	paid	Oke Aro Farm Store	\N	Stored in the farm cabinet for regulating Diarrhea.
72	2026-01-29	expense	medicine	Medicine - Oxytoxin	2	other	500	1000	1000	paid	Oke Aro Farm Store	\N	Stored in the farm Medicine cabinet.
103	2026-02-02	expense	medicine	Medicine - Flagyl	1	other	1000	1000	1000	paid	Unknown	\N	Stored in the farm medication cabinet for regulating Diarrhea.
9	2025-10-31	expense	labor	Land Clearing	1	job	6000	6000	6000	paid	Dada and Friends	\N	Payment for Labor to clear the surroundings for maintenance. 
19	2025-11-04	expense	labor	Feed Transportation	1	job	3000	3000	3000	paid	Public Transport	\N	Bike man to bring Feed From town.
88	2026-01-09	expense	labor	Labor - Extra Work	1	job	1000	1000	1000	paid	Dada	\N	Payment to labor to help with pen work and maintenence
112	2026-02-10	expense	labor	Labor - Bush Clearing	1	other	1000	1000	1000	paid	AY	\N	Clearing of bush around the pen
17	2025-11-04	expense	consumables	Small Bowl	1	other	1500	1500	1500	paid	Mrs. Fumilola Store Oke Aro	\N	For Cleaning and Washing of the Pen, feed measurement.
10	2025-11-01	expense	assets	Heavy Duty Feed Drum	1	other	52000	52000	52000	paid	Mrs. Fumilola Store Oke Aro	\N	For storing feeds to avoid waste and theft.
8	2025-10-31	expense	consumables	Bailer	1	other	500	500	500	paid	Sleepwell Ventures.	\N	cleaning the pen and feed measurement.
113	2026-02-10	expense	consumables	Soap	1	other	500	500	500	paid	Unknown	\N	Purchase of Soap for washing the pen
91	2026-01-20	expense	consumables	Disinfectant (Izal)	1	other	800	800	800	paid	Unknown	\N	Purchase of Izal to wash the floor for weaning
45	2025-12-09	expense	transport	Transport to Farm Support (To and Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Tranport for To and fro to Farm Support.
81	2026-01-05	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2050	2050	4100	paid	Public Transport	\N	Transport to Farm Support to and fro
92	2026-01-20	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Transport to Oke Aro to and fro for routine check.
102	2026-02-02	expense	transport	Commute - Farm Visit (To & Fro)	1	head	3000	3000	3000	paid	Public Transport	\N	Transport to Oke Aro to and fro for routine check.
110	2026-02-09	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Transport to Oke Aro to and fro for routine check.
111	2026-02-10	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Transport to Oke Aro to and fro for routine check.
114	2026-02-03	expense	other_expense	Breeding Service - Boar Mating	1	job	5000	5000	5000	paid	Unknown	SOW-B	Failed mating service for Sow-B.
115	2026-02-13	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Transport to Oke Aro to and fro for routine check.
116	2026-02-03	expense	transport	Transportation of Boar	1	job	2000	2000	2000	paid	Unknown	SOW-B	Transportation of boar.
117	2026-02-13	expense	feed	Feed Ingredient - PKC	100	kg	230	23000	23000	paid	Iya Eji Farm	\N	Sourced from Iya Eji Farm.
118	2026-02-13	expense	feed	Feed Ingredient - Weaners Feed Mixture	70.9	kg	375	26587.500000000004	26600	paid	Iya Eji Farm	\N	Sourced from Iya Eji Farm, good feed, Mixed with 2 bags of PKC for weaners
119	2026-02-16	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Transport to Oke Aro to and fro for routine check.
120	2026-02-16	expense	medicine	Medicine - Flagyl	1	other	1500	1500	1500	paid	Unknown	\N	Stored in the farm Medicine cabinet.
121	2026-02-16	expense	medicine	Medicine - Tetracaclyn	1	other	900	900	900	paid	Unknown	\N	Stored in the farm Medicine cabinet for controlling diarrhea.
123	2026-02-20	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Routine Farm Check
125	2026-02-23	expense	consumables	Farm Tool - Water Fetcher (Bucket/Bowl)	1	other	1600	1600	1600	paid	Unknown	\N	Fetcher for all Pen. Used for daily watering and mixing disinfectants.
126	2026-02-24	expense	transport	Transportation of Boar	1	job	1500	1500	1500	paid	Unknown	SOW-A	Boar transportation.
127	2026-02-24	expense	other_expense	Breeding Service - Boar Mating	1	job	5000	5000	5000	paid	Unknown	SOW-A	Boar Mating.
128	2026-02-26	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Routine Farm Check
122	2026-02-16	expense	maintenance	Building Material - Nails	1	other	650	650	650	paid	Unknown	\N	Purchase of Nails for maintenance.
129	2026-02-27	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Routine Farm Check.
124	2026-02-23	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Routine Farm Check.
130	2026-02-27	expense	feed	Feed Ingredient - Grower Feed Mixture	71	kg	366	25986	26000	paid	Iya Eji Farm	\N	Sourced from Iya Eji Farm, good feed.
131	2026-02-27	expense	feed	Feed Ingredient - PKC	100	kg	230	23000	23000	paid	Iya Eji Farm	\N	Sourced from Iya Eji Farm, good feed.
132	2026-03-02	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Routine Farm Check
133	2026-03-05	expense	labor	Staff Salary - Farm Assistant	1	month	6000	6000	6000	paid	AY	\N	Paid in full (2000 x 3pen).
136	2026-03-06	expense	consumables	Security Hardware - Small Padlock	1	job	1200	1200	1200	paid	Unknown	\N	Security and locking of the back door.
134	2026-03-06	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Routine Farm Check.
135	2026-03-06	expense	other_expense	Breeding Service - Boar Mating	1	job	5000	5000	5000	paid	Unknown	SOW-B	Paid for mating of sow B
137	2026-03-06	expense	consumables	Farm Needs - Kerosene	1	other	1000	1000	1000	paid	Unknown	\N	For fly control.
138	2026-03-09	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Routine Farm Check.
139	2026-03-11	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Routine Farm Check.
140	2026-03-11	expense	feed	Feed Ingredient - Grower Feed Mixture	72	kg	375	27000	27000	paid	Iya Eji Farm	\N	Sourced from Iya Eji Farm, good feed.
141	2026-03-13	expense	transport	Commute - Farm Visit (To & Fro)	2	head	1650	3300	3300	paid	Public Transport	\N	Routine Farm Check.
143	2026-02-20	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2000	2000	2000	paid	Public Transport	\N	Routine Farm Check.
144	2026-03-20	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2100	2100	2100	paid	Public Transport	\N	Routine Farm Check.
142	2026-03-16	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2100	2100	2100	paid	Public Transport	\N	Routine Farm Check.
145	2026-03-22	expense	medicine	Medicine - Flagyl	1000	job	8	8000	8000	paid	Hospital Road	\N	Stored in the farm Medicine cabinet for controlling diarrhea.
146	2026-03-22	expense	medicine	Medicine - Tetracaclyn	100	job	28	2800	2800	paid	Hospital Road	\N	Stored in the farm Medicine cabinet for controlling diarrhea.
147	2026-03-22	expense	medicine	Medicine - Livamisole Dewormer	100	ml	30	3000	3000	paid	Unknown	\N	Stored in the farm Medicine cabinet.
148	2026-03-22	expense	medicine	Needle and Syinge 2mls	5	job	50	250	250	paid	Oke Aro Farm Store	\N	Stored in the farm Medicine cabinet.
149	2026-03-22	expense	medicine	Needle and Syinge 5mls	5	job	50	250	250	paid	Oke Aro Farm Store	\N	Stored in the farm Medicine cabinet.
150	2026-03-22	expense	medicine	Needle and Syinge 10mls	5	job	100	500	500	paid	Oke Aro Farm Store	\N	Stored in the farm Medicine cabinet.
151	2026-03-22	expense	consumables	Disinfectant (Morigrd)	1	liters	1600	1600	1600	paid	Unknown	\N	Disinfecting and washing the Pen.
153	2026-03-22	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2100	2100	2100	paid	Public Transport	\N	Routine Farm Check.
152	2026-03-22	expense	consumables	Soap	1	other	200	200	200	paid	Unknown	\N	Disinfecting and washing the Pen.
154	2026-03-23	expense	feed	Feed Ingredient - PKC	150	kg	220	33000	33000	paid	Iya Eji Farm	\N	Feed Mixture for growers + 25kg starter feed
155	2026-03-23	expense	feed	Feed - Starter Feed	25	kg	960	24000	24000	paid	Iya Eji Farm	\N	Sourced from Iya Eji Farm, good feed.
156	2026-03-23	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2100	2100	2100	paid	Public Transport	\N	Routine Farm Check.
157	2026-03-25	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2100	2100	2100	paid	Public Transport	\N	Routine Farm Check.
158	2026-01-26	expense	feed	Feed Ingredient - Weaners Feed Mixture	65	kg	407.6	26494	26500	paid	Iya Eji Farm	\N	Sourced from Iya Eji Farm, good feed.
159	2026-01-27	expense	medicine	Medicine - Flagyl	1	other	1000	1000	1000	paid	Unknown	\N	Stored in the farm Medicine cabinet.
160	2026-01-27	expense	medicine	Medicine - Tetracaclyn	1	other	500	500	500	paid	Unknown	\N	Stored in the farm Medicine cabinet.
161	2026-03-27	expense	transport	Commute - Farm Visit (To & Fro)	1	head	2200	2200	2200	paid	Public Transport	\N	Routine Farm Check.
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: farm_user
--

COPY public.users (id, username, email, hashed_password, full_name, role, is_active) FROM stdin;
1	profadept	admin@yourfarm.com	$2b$12$sFHe2wqu8G5r9HQwZjFtauAeRr3fe8uofYDlur8HJWL33Fkfub18i	Farm SuperUser	ADMIN	t
3	viki	kolawolevictor843@gmail.com	$2b$12$j.MbH4H6JPTne4q26zhxluCLJr.3CakMsW1crfkM1F7w2WqZi5taC	Kolawole Victor	STAFF	t
4	admin	ifafoyesaidat@gmail.com	$2b$12$dxcwPkWZX0BLWyrhSP5Lvegskq3avp225hylWp4shBIOUingN46be	Ifafoye Omolara	STAFF	t
\.


--
-- Name: farm_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: farm_user
--

SELECT pg_catalog.setval('public.farm_transactions_id_seq', 161, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: farm_user
--

SELECT pg_catalog.setval('public.users_id_seq', 4, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: farm_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: farm_transactions farm_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: farm_user
--

ALTER TABLE ONLY public.farm_transactions
    ADD CONSTRAINT farm_transactions_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: farm_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: farm_user
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: farm_user
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- PostgreSQL database dump complete
--

\unrestrict 0ZkdCg4DOGOOdwXp1SuUbnKChTNcHg2pHWZRjc7q1quuJ3fSX26PFwzhHTvQeYU

