--
-- PostgreSQL database dump
--

\restrict EPNUFRZDSTb23IxsqpWseMndbAy5VCWnJgPAoivVrBRf8d6NZmjWn0hUy6CvI6S

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, password, last_login, is_superuser, username, first_name, last_name, is_staff, is_active, date_joined, phone_number, email, created_at, updated_at, is_verified) FROM stdin;
4	pbkdf2_sha256$1200000$xoBbDfV0dKv6jA7OjuDdSB$d85gCyBf1L1/ddKikjqMQBsacR5yvWvIc+ctOsm0EUE=	\N	f	pranay			f	t	2026-05-18 11:26:51.731569+05:30	9284246391	pranayisgreat11@gmail.com	2026-05-18 11:26:53.618527+05:30	2026-05-18 11:26:53.618539+05:30	t
5	pbkdf2_sha256$1200000$p3YKi657KDGkJsQVeEnqoy$545GIEw2n6EUNH+rUaqKUScEcevwC9c2Q2q+4CP+SvU=	\N	f	vedant			f	t	2026-05-18 15:53:12.798267+05:30	6789012345	chorawalavedant@gmail.com	2026-05-18 15:53:15.090169+05:30	2026-05-18 15:53:15.090192+05:30	t
7	pbkdf2_sha256$1200000$iINN988ZeZDCFJzPJwtddG$ttxaO6RXkQDDw7WRQU63rSA9revDJz3sXTCtW16BBYw=	\N	f	pranayth			f	t	2026-05-23 14:06:07.148669+05:30	9284246392	thakurpranayyy@gmail.com	2026-05-23 14:06:09.182489+05:30	2026-05-23 14:06:09.182513+05:30	t
\.


--
-- Data for Name: labels; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.labels (id, title, created_at, updated_at, created_by_id) FROM stdin;
1	Mentor	2026-05-18 15:56:31.301784+05:30	2026-05-18 15:56:31.301813+05:30	5
2	Important	2026-05-18 16:11:23.022804+05:30	2026-05-18 16:11:23.022851+05:30	5
3	Work	2026-05-18 16:34:01.190664+05:30	2026-05-18 16:34:01.190673+05:30	5
4	Personal	2026-05-18 16:34:01.361949+05:30	2026-05-18 16:34:01.361955+05:30	5
5	Ideas	2026-05-18 16:34:01.420544+05:30	2026-05-18 16:34:01.42055+05:30	5
6	Shopping	2026-05-18 16:34:01.471661+05:30	2026-05-18 16:34:01.471668+05:30	5
7	Travel	2026-05-18 16:34:01.530641+05:30	2026-05-18 16:34:01.53065+05:30	5
8	Health	2026-05-18 16:34:01.602715+05:30	2026-05-18 16:34:01.602723+05:30	5
9	Finance	2026-05-18 16:34:01.657034+05:30	2026-05-18 16:34:01.657041+05:30	5
10	Learning	2026-05-18 16:34:01.70947+05:30	2026-05-18 16:34:01.709476+05:30	5
11	Urgent	2026-05-18 16:34:01.882799+05:30	2026-05-18 16:34:01.882807+05:30	5
12	Someday	2026-05-18 16:34:01.943005+05:30	2026-05-18 16:34:01.943012+05:30	5
13	test	2026-05-23 14:27:45.081173+05:30	2026-05-23 14:27:45.081207+05:30	7
14	Work	2026-05-25 10:28:29.834978+05:30	2026-05-25 10:28:29.834999+05:30	7
15	Apexon	2026-05-25 10:28:42.46096+05:30	2026-05-25 10:28:42.460984+05:30	7
16	Personal	2026-05-26 22:00:16.852382+05:30	2026-05-26 22:00:16.852395+05:30	7
17	Ideas	2026-05-26 22:00:16.865567+05:30	2026-05-26 22:00:16.865576+05:30	7
18	Shopping	2026-05-26 22:00:16.867374+05:30	2026-05-26 22:00:16.867383+05:30	7
19	Travel	2026-05-26 22:00:16.869419+05:30	2026-05-26 22:00:16.869428+05:30	7
20	Health	2026-05-26 22:00:16.871374+05:30	2026-05-26 22:00:16.871382+05:30	7
21	Finance	2026-05-26 22:00:16.873533+05:30	2026-05-26 22:00:16.873541+05:30	7
22	Learning	2026-05-26 22:00:16.875955+05:30	2026-05-26 22:00:16.875965+05:30	7
23	Urgent	2026-05-26 22:00:16.8781+05:30	2026-05-26 22:00:16.878108+05:30	7
24	Someday	2026-05-26 22:00:16.880154+05:30	2026-05-26 22:00:16.880162+05:30	7
25	Idea	2026-06-02 12:23:08.817808+05:30	2026-06-02 12:23:08.817839+05:30	4
\.


--
-- Data for Name: notes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.notes (id, title, content, is_archived, is_trashed, created_at, updated_at, created_by_id, color) FROM stdin;
1	string	string	t	t	2026-05-18 11:42:32.248597+05:30	2026-05-18 11:42:32.248625+05:30	4	default
2	BL	Sam sir	f	f	2026-05-18 15:56:52.940946+05:30	2026-05-18 15:56:52.940974+05:30	5	default
3	Meeting notes — Q3 planning	Discussed roadmap priorities for Q3.\nAction items:\n- Finalize API design by Friday\n- Review infra costs with DevOps\n- Schedule follow-up for next Monday	f	f	2026-05-18 16:34:02.043035+05:30	2026-05-18 16:34:02.043041+05:30	5	default
4	Book recommendations	1. Designing Data-Intensive Applications — Kleppmann\n2. Clean Architecture — Robert C. Martin\n3. The Pragmatic Programmer — Hunt & Thomas\n4. Staff Engineer — Will Larson	f	f	2026-05-18 16:34:02.103665+05:30	2026-05-18 16:34:02.103672+05:30	5	default
6	Trip to Goa — packing list	Clothes: 3 t-shirts, 2 shorts, swimwear\nDocuments: ID, hotel booking, flight tickets\nGadgets: charger, earphones, power bank\nMisc: sunscreen, sunglasses, flip-flops	f	f	2026-05-18 16:34:02.231351+05:30	2026-05-18 16:34:02.231357+05:30	5	default
7	Startup idea — AI recipe generator	Core concept: user inputs available ingredients, AI suggests recipes with step-by-step instructions.\nMonetisation: freemium + premium meal-plan subscriptions.\nTech stack: FastAPI backend, React frontend, OpenAI API.	f	f	2026-05-18 16:34:02.291437+05:30	2026-05-18 16:34:02.291442+05:30	5	default
8	Monthly budget — May 2026	Income:  ₹85,000\nRent:    ₹18,000\nFood:    ₹8,000\nTravel:  ₹3,500\nSavings: ₹20,000\nMisc:    ₹5,000	f	f	2026-05-18 16:34:02.358143+05:30	2026-05-18 16:34:02.358149+05:30	5	default
9	Workout plan — this week	Mon: chest + triceps\nTue: back + biceps\nWed: rest / walk\nThu: legs\nFri: shoulders + core\nSat: cardio 30 min\nSun: rest	f	f	2026-05-18 16:34:02.528548+05:30	2026-05-18 16:34:02.528555+05:30	5	default
10	Django REST Framework — study notes	Key concepts:\n- Serializers: validation + representation\n- ViewSets vs FBVs — project uses FBVs with @api_view\n- JWT auth via simplejwt\n- Throttling: AnonRateThrottle + UserRateThrottle\n- drf-spectacular for OpenAPI docs	f	f	2026-05-18 16:34:02.704303+05:30	2026-05-18 16:34:02.704308+05:30	5	default
12	Archived — old project tasks	Legacy tasks from the previous sprint.\nKept for reference only — no action needed.	t	f	2026-05-18 16:34:02.833555+05:30	2026-05-18 16:34:02.833561+05:30	5	default
27	Meeting Notes	Discussed Q3 strategy. Action items: Email client, Review budget.	f	f	2026-06-02 12:22:26.870432+05:30	2026-06-02 12:24:19.736538+05:30	4	red
25	Random Ideas	Here are some random thoughts: 1. Do yoga. 2. Read a book. 3. Take a walk.	t	f	2026-06-02 12:22:22.350777+05:30	2026-06-02 12:41:27.552994+05:30	4	blue
26	Project Plan	Draft outline: 1. Set goals. 2. Assign tasks. 3. Set deadlines.	f	f	2026-06-02 12:22:24.585999+05:30	2026-06-02 12:43:43.818391+05:30	4	green
14	Bridgelabz	Finish frontend topics	f	f	2026-05-25 10:28:55.821049+05:30	2026-05-25 10:28:55.821067+05:30	7	red
28	Schoolwork Tasks	Math homework: Chapter 5 problems 1-20, English essay due Friday, Science project proposal draft.	f	f	2026-06-02 12:29:43.827692+05:30	2026-06-04 12:22:12.96494+05:30	4	default
5	Grocery list	- Milk\n- Eggs\n- Bread\n- Olive oil\n- Spinach\n- Chicken breast\n- Greek yogurt	f	f	2026-05-18 16:34:02.168613+05:30	2026-05-25 10:31:27.569859+05:30	5	default
15	Meeting notes — Q3 planning	Discussed roadmap priorities for Q3.\nAction items:\n- Finalize API design by Friday\n- Review infra costs with DevOps\n- Schedule follow-up for next Monday	f	f	2026-05-26 22:00:16.885203+05:30	2026-05-26 22:00:16.885213+05:30	7	yellow
16	Book recommendations	1. Designing Data-Intensive Applications — Kleppmann\n2. Clean Architecture — Robert C. Martin\n3. The Pragmatic Programmer — Hunt & Thomas\n4. Staff Engineer — Will Larson	f	f	2026-05-26 22:00:16.892884+05:30	2026-05-26 22:00:16.892893+05:30	7	blue
17	Grocery list	- Milk\n- Eggs\n- Bread\n- Olive oil\n- Spinach\n- Chicken breast\n- Greek yogurt	f	f	2026-05-26 22:00:16.89766+05:30	2026-05-26 22:00:16.897668+05:30	7	green
18	Trip to Goa — packing list	Clothes: 3 t-shirts, 2 shorts, swimwear\nDocuments: ID, hotel booking, flight tickets\nGadgets: charger, earphones, power bank\nMisc: sunscreen, sunglasses, flip-flops	f	f	2026-05-26 22:00:16.901125+05:30	2026-05-26 22:00:16.901134+05:30	7	teal
19	Startup idea — AI recipe generator	Core concept: user inputs available ingredients, AI suggests recipes with step-by-step instructions.\nMonetisation: freemium + premium meal-plan subscriptions.\nTech stack: FastAPI backend, React frontend, OpenAI API.	f	f	2026-05-26 22:00:16.905389+05:30	2026-05-26 22:00:16.905397+05:30	7	purple
20	Monthly budget — May 2026	Income:  85,000\nRent:    18,000\nFood:     8,000\nTravel:   3,500\nSavings: 20,000\nMisc:     5,000	f	f	2026-05-26 22:00:16.90839+05:30	2026-05-26 22:00:16.908398+05:30	7	orange
21	Workout plan — this week	Mon: chest + triceps\nTue: back + biceps\nWed: rest / walk\nThu: legs\nFri: shoulders + core\nSat: cardio 30 min\nSun: rest	f	f	2026-05-26 22:00:16.911198+05:30	2026-05-26 22:00:16.911207+05:30	7	red
22	Django REST Framework — study notes	Key concepts:\n- Serializers: validation + representation\n- ViewSets vs FBVs — project uses FBVs with @api_view\n- JWT auth via simplejwt\n- Throttling: AnonRateThrottle + UserRateThrottle\n- drf-spectacular for OpenAPI docs	f	f	2026-05-26 22:00:16.914229+05:30	2026-05-26 22:00:16.914237+05:30	7	default
23	Random thoughts	Sometimes the best ideas come when you least expect them.\nKeep a note of everything — you never know what will be useful.\nThe key is to review your notes regularly.	f	f	2026-05-26 22:00:16.918933+05:30	2026-05-26 22:00:16.918943+05:30	7	pink
24	Archived — old project tasks	Legacy tasks from the previous sprint.\nKept for reference only — no action needed.	t	f	2026-05-26 22:00:16.922647+05:30	2026-05-26 22:00:16.922655+05:30	7	gray
29	test	1234	f	f	2026-06-04 12:31:54.233679+05:30	2026-06-04 12:31:54.233698+05:30	4	default
13	Example	This is a note description	f	f	2026-05-23 14:27:21.511761+05:30	2026-06-04 15:48:09.440302+05:30	7	green
30	Testing	This is a test note.	t	f	2026-06-04 17:09:43.445789+05:30	2026-06-04 17:10:01.962405+05:30	7	default
31	Collaborative note	This note is shared with chorawalavedant@gmail.com.	f	f	2026-06-04 17:10:35.269253+05:30	2026-06-04 17:10:35.26926+05:30	7	default
11	Random thoughts	Reflecting on recent thoughts, I identified actionable insights:\n1. Prioritize self-value activities to improve motivation.\n2. Engage in one new activity weekly that aligns with personal interests.\n3. Create a structure for viewing progress in personal projects.	f	f	2026-05-18 16:34:02.76934+05:30	2026-06-04 17:12:48.146217+05:30	5	default
\.


--
-- Data for Name: note_collaborators; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.note_collaborators (id, note_id, collaborator_id, access_level, created_at, updated_at) FROM stdin;
1	14	5	read_write	2026-05-25 10:29:34.799478+05:30	\N
\.


--
-- Data for Name: notes_labels; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.notes_labels (id, note_id, label_id) FROM stdin;
1	2	1
2	3	11
3	3	3
4	4	10
5	4	4
6	5	6
7	6	4
8	6	7
9	7	5
10	8	9
11	9	8
12	10	10
13	10	3
14	11	4
15	11	12
16	12	3
17	13	13
18	14	14
19	14	15
20	15	14
21	15	23
22	16	22
23	16	16
24	17	18
25	18	19
26	18	16
27	19	17
28	20	21
29	21	20
30	22	22
31	22	14
32	23	16
33	23	24
34	24	14
\.


--
-- Data for Name: token_blacklist_outstandingtoken; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.token_blacklist_outstandingtoken (id, token, created_at, expires_at, user_id, jti) FROM stdin;
1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3OTY4OTUyNCwiaWF0IjoxNzc5MDg0NzI0LCJqdGkiOiI5MDk0NDcyMTYyYzI0NGUwYWIzNzZkMTA5ZWIxYTA1OSIsInVzZXJfaWQiOiI0In0.5Es-eyArvt-JnnlirZgGQgmEPhrve-VYAJt_AJfRQuo	2026-05-18 11:42:04.277617+05:30	2026-05-25 11:42:04+05:30	4	9094472162c244e0ab376d109eb1a059
2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3OTY5MjMzNywiaWF0IjoxNzc5MDg3NTM3LCJqdGkiOiI0ODU3MGE3MTcyOWM0MjZmODg5YWE0ZTlhZTUyMDE1ZCIsInVzZXJfaWQiOiI0In0.ASJzDr-D3KXDweu79xJjz3Ar9zcOuOIznGyYJ3FlogM	2026-05-18 12:28:57.499084+05:30	2026-05-25 12:28:57+05:30	4	48570a71729c426f889aa4e9ae52015d
3	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3OTY5MjMzOSwiaWF0IjoxNzc5MDg3NTM5LCJqdGkiOiJlMmQxZWI4MDYxN2Y0M2Y3OGI5MzZiNjNhMzE0YjBkNSIsInVzZXJfaWQiOiI0In0.236Jdufe9bJqE3Ze1CezvVBeaHZPEUYQ6Y61VmTlPtg	2026-05-18 12:28:59.284974+05:30	2026-05-25 12:28:59+05:30	4	e2d1eb80617f43f78b936b63a314b0d5
4	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3OTcwNDcyNiwiaWF0IjoxNzc5MDk5OTI2LCJqdGkiOiIwMDc3MjA2YmFiZWU0NmE3YWMzNmNlNjgwMjIzZTcyNSIsInVzZXJfaWQiOiI1In0.iSDpLT2wGo3ZVLIkbqoPlyKqbiR0lnbPWnuFDOx8ZVg	2026-05-18 15:55:26.033203+05:30	2026-05-25 15:55:26+05:30	5	0077206babee46a7ac36ce680223e725
5	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3OTcwOTcxMCwiaWF0IjoxNzc5MTA0OTEwLCJqdGkiOiI3OTgyZmJlNzMyMzI0OGNhODdjODI3OWFiODAxYzUzZSIsInVzZXJfaWQiOiI1In0.fbrJMOp4C45Yd13QXwk7tKUTR3KO_E9C_9FGkjF5NUw	2026-05-18 17:18:30.682525+05:30	2026-05-25 17:18:30+05:30	5	7982fbe7323248ca87c8279ab801c53e
6	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3OTg3NzY3MiwiaWF0IjoxNzc5MjcyODcyLCJqdGkiOiJiNWE5MzZhOTA4ZmE0NGM0OGFhNmVjMTU2YWNhZmM0NSIsInVzZXJfaWQiOiI1In0.mmpQOK4FOJJkS6WX9Lwebp7GMwWUY7HmjglZ_huGqdk	2026-05-20 15:57:52.47905+05:30	2026-05-27 15:57:52+05:30	5	b5a936a908fa44c48aa6ec156acafc45
7	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDEzMDM0MiwiaWF0IjoxNzc5NTI1NTQyLCJqdGkiOiIzNzE0YTI2YTMzY2Q0YmUyYjM3NDVkNTUwMGRjYjY5NCIsInVzZXJfaWQiOiI3In0.-Gn6lpVBWjjUMP_ZBxspuldk3c4L58y1NcCADmv5BFs	2026-05-23 14:09:02.698434+05:30	2026-05-30 14:09:02+05:30	7	3714a26a33cd4be2b3745d5500dcb694
8	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDEzMDU1MiwiaWF0IjoxNzc5NTI1NzUyLCJqdGkiOiJiZWNlNzE5NjNlMWQ0YjY4OTZiNWY0ZDI1ODA2ZWFmZCIsInVzZXJfaWQiOiI3In0.ne7SY05EKP0dhI5G38vBPokAvEgsKQIsqWLSyRr9GQ0	2026-05-23 14:12:32.107928+05:30	2026-05-30 14:12:32+05:30	7	bece71963e1d4b6896b5f4d25806eafd
9	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDEzMDYwOSwiaWF0IjoxNzc5NTI1ODA5LCJqdGkiOiI0NTg3NTBkZDBiM2Y0ZDBiOTBkOWNmNDFhYWIyZGE4MyIsInVzZXJfaWQiOiI3In0.aAm-axrlIV6iT2Pj1qwJFXpeopOwgJP0ApCmE4RgtTo	2026-05-23 14:13:29.097809+05:30	2026-05-30 14:13:29+05:30	7	458750dd0b3f4d0b90d9cf41aab2da83
10	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDEzMDgzOCwiaWF0IjoxNzc5NTI2MDM4LCJqdGkiOiI3OWMyYTFlY2EzNDA0YTk4OTEyZjc0NmNmNDI1YjlkOCIsInVzZXJfaWQiOiI3In0.GFdoseKfTP4p9kuUzkqzP_1o3p4T2V2jY_CcgoJyP9c	2026-05-23 14:17:18.064161+05:30	2026-05-30 14:17:18+05:30	7	79c2a1eca3404a98912f746cf425b9d8
11	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDEzMTA5NSwiaWF0IjoxNzc5NTI2Mjk1LCJqdGkiOiI2ODA2MDIyM2ViYjA0NjgxYmE1Zjg3ZWY5NWJlN2YzZiIsInVzZXJfaWQiOiI3In0.fY4St1Hhi5sHbU9XuPjpneVrLEZ5pXuVx8G99_sjulI	2026-05-23 14:21:35.824444+05:30	2026-05-30 14:21:35+05:30	7	68060223ebb04681ba5f87ef95be7f3f
12	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDEzMTEzOCwiaWF0IjoxNzc5NTI2MzM4LCJqdGkiOiJjODRjNDYzMDA4MmI0NmRkODRlNTE2Y2FjNTc2MjBiMSIsInVzZXJfaWQiOiI3In0.1T2L2zHHTXTg1ZaSJXVZJ-4DLMAxoT-I4A8SDwUY_TE	2026-05-23 14:22:18.742506+05:30	2026-05-30 14:22:18+05:30	7	c84c4630082b46dd84e516cac57620b1
13	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDEzMTM5OSwiaWF0IjoxNzc5NTI2NTk5LCJqdGkiOiJiMjg1NDlkZDY2MzM0ZGI3YjRkMjIzOWU3NGRiMzE0MSIsInVzZXJfaWQiOiI3In0.IeIJudUz-orjYCyUQxSxnZ_hxZ_FtipPGxrB0EPCNM8	2026-05-23 14:26:39.047485+05:30	2026-05-30 14:26:39+05:30	7	b28549dd66334db7b4d2239e74db3141
14	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDEzMTczNSwiaWF0IjoxNzc5NTI2OTM1LCJqdGkiOiI0YWMyZmRiYmQ0MGM0NTgxYWEzMzUzOTBmOGZhNjYzZSIsInVzZXJfaWQiOiI3In0.PN0OihrzuL-hREw7cgig3w2X7QA-cJPE17gN13VUN3g	2026-05-23 14:32:15.560886+05:30	2026-05-30 14:32:15+05:30	7	4ac2fdbbd40c4581aa335390f8fa663e
15	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDEzOTQyMCwiaWF0IjoxNzc5NTM0NjIwLCJqdGkiOiJhNjhhYjg5MmU4OGQ0MzE0OTlmNjA1ZDNiNWY2MjJlMCIsInVzZXJfaWQiOiI3In0.iLIjah3tspZimEtvoJqUHQcXXHbmFIys3_eJJi67H0I	2026-05-23 16:40:20.030459+05:30	2026-05-30 16:40:20+05:30	7	a68ab892e88d431499f605d3b5f622e0
16	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDEzOTYyNiwiaWF0IjoxNzc5NTM0ODI2LCJqdGkiOiI5YzhiYzEwMmNmNDM0NWNhOWMyOWNhMWZmYmU3OTQxMiIsInVzZXJfaWQiOiI3In0.4nUveyhtGeyxHRNayJZ9gwKjDEBiP3DVcNrBNfAHOPI	2026-05-23 16:43:46.193681+05:30	2026-05-30 16:43:46+05:30	7	9c8bc102cf4345ca9c29ca1ffbe79412
17	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDI4OTc5MywiaWF0IjoxNzc5Njg0OTkzLCJqdGkiOiI0MmQwYWM2YjA4YTQ0YTUyODEzZTliZjQxMTA2ODdjZCIsInVzZXJfaWQiOiI3In0.4oUqgMwAzPGqIwFUnOaYbtoJNU0DPjwVqxmTDwwyDZw	2026-05-25 10:26:33.806144+05:30	2026-06-01 10:26:33+05:30	7	42d0ac6b08a44a52813e9bf4110687cd
18	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDI5MDA0OSwiaWF0IjoxNzc5Njg1MjQ5LCJqdGkiOiI2ZTE0YWM3NTFmZGI0MDZiYWYzNzU1YjgyOTg5ZjVmYSIsInVzZXJfaWQiOiI1In0.PqadnU_Y7jKcsqX8Ox94yOPjffzwPDIeyJrGYh8GEd8	2026-05-25 10:30:49.998816+05:30	2026-06-01 10:30:49+05:30	5	6e14ac751fdb406baf3755b82989f5fa
19	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDI5MDQzMCwiaWF0IjoxNzc5Njg1NjMwLCJqdGkiOiI1OGFlYTUwMTM2ZmM0N2I3YmQyM2YyODQxYWM3Y2VhYyIsInVzZXJfaWQiOiI1In0.gUXfdNw1Gl9YC7x2woqOuMPcLKCU3HULrUnbAwfIR_A	2026-05-25 10:37:10.955007+05:30	2026-06-01 10:37:10+05:30	5	58aea50136fc47b7bd23f2841ac7ceac
20	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDMxMzg1MywiaWF0IjoxNzc5NzA5MDUzLCJqdGkiOiJkYzFmZTAwOTkxYmU0ODdiOGJhMjUwZGU1OTdlMmFkYiIsInVzZXJfaWQiOiI1In0.eOW6EGMjCj6Hbo8-iPWv-B2gsIj4FPK18po5ogrSJi4	2026-05-25 17:07:33.633212+05:30	2026-06-01 17:07:33+05:30	5	dc1fe00991be487b8ba250de597e2adb
21	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDQxNzQ4MCwiaWF0IjoxNzc5ODEyNjgwLCJqdGkiOiI3MWUzODMwYTg2YWI0M2NmOGRjNTAxMWJjNGM3YTRlZiIsInVzZXJfaWQiOiI3In0.7w_x-ruelHS0DgpvJDTUBouCecqTfwLhPe1Z61Ov4e0	2026-05-26 21:54:40.192023+05:30	2026-06-02 21:54:40+05:30	7	71e3830a86ab43cf8dc5011bc4c7a4ef
22	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDQxNzYzNCwiaWF0IjoxNzc5ODEyODM0LCJqdGkiOiI5YjA5OWZiYzczMmE0MzFkYThlZWY0YjNjMDM0ZjlkYiIsInVzZXJfaWQiOiI3In0.JUNNlB-k932ff2B9_GT0m1EZohoRc0JOGJMsXiou0aM	2026-05-26 21:57:14.304597+05:30	2026-06-02 21:57:14+05:30	7	9b099fbc732a431da8eef4b3c034f9db
23	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDQxNzY0OSwiaWF0IjoxNzc5ODEyODQ5LCJqdGkiOiI1ZGRjODVhNjcyY2I0OGM1YmVhNzk4ODVhNjdjOGI1MSIsInVzZXJfaWQiOiI3In0.aW4cWaDYO-nP7NelVZHWQDVJqEPQESVrl6XNvDeCFLo	2026-05-26 21:57:29.927692+05:30	2026-06-02 21:57:29+05:30	7	5ddc85a672cb48c5bea79885a67c8b51
24	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDk4NzY2OCwiaWF0IjoxNzgwMzgyODY4LCJqdGkiOiJjYWVhMzkxMGQxN2E0N2RlOGViNDQ5NGYzMTZiZjkzMiIsInVzZXJfaWQiOiI0In0.LtzqgxpP8ERQSQdtLTP_D33SGCPAKFjc9zVBFYeul4E	2026-06-02 12:17:48.922641+05:30	2026-06-09 12:17:48+05:30	4	caea3910d17a47de8eb4494f316bf932
25	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MTA5NjI5MCwiaWF0IjoxNzgwNDkxNDkwLCJqdGkiOiJlMDZkMWJkYmQ1Yjk0NzAzODAyOGMyZTU5OWY5ZjNjNCIsInVzZXJfaWQiOiI0In0.aCPmOzSCGsNw-F2xaKuNG06sakP6EL5nfXcJ-P7e3z0	2026-06-03 18:28:10.198313+05:30	2026-06-10 18:28:10+05:30	4	e06d1bdbd5b947038028c2e599f9f3c4
26	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MTE1OTUzMiwiaWF0IjoxNzgwNTU0NzMyLCJqdGkiOiIxMjhhYTU0ZmZkZjM0YjEyOTE4NjNmMTUzNGI2ZWI4NCIsInVzZXJfaWQiOiI0In0.8bBi95exYq4hzDtBh3wqCgfhzaQ9PXMnqgWGTICtmls	2026-06-04 12:02:12.030334+05:30	2026-06-11 12:02:12+05:30	4	128aa54ffdf34b1291863f1534b6eb84
27	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MTE2MzE4NSwiaWF0IjoxNzgwNTU4Mzg1LCJqdGkiOiIzM2Y1OTQ4OWJjZWI0ZTU2OTM0ODUzNTM1Y2U5N2ViYSIsInVzZXJfaWQiOiI0In0.WWaTvsWJXHr2H0FiBlVGBNxoFLRFMfRgcXhpP3sC5Ys	2026-06-04 13:03:05.262792+05:30	2026-06-11 13:03:05+05:30	4	33f59489bceb4e56934853535ce97eba
28	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MTE3MDM2NSwiaWF0IjoxNzgwNTY1NTY1LCJqdGkiOiJhMWIyNTgzN2VhZDU0MmFhYjRlZDkxMGM1ODg5N2UyOSIsInVzZXJfaWQiOiI3In0.qzUW7L-IfhhMYTWWwy7LUDWO1_Xt_Ci-g2G1yZWBfdM	2026-06-04 15:02:45.867775+05:30	2026-06-11 15:02:45+05:30	7	a1b25837ead542aab4ed910c58897e29
29	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MTE3NzM3NSwiaWF0IjoxNzgwNTcyNTc1LCJqdGkiOiIyZGU4MDhkYzhlZGM0YmFjYTUxMzUzODhkYzVlMmE3MSIsInVzZXJfaWQiOiI3In0.bIHA3eqEb5nudgubYD56Ncg0U_GTHDeM9DzyNVIEKFk	2026-06-04 16:59:35.167278+05:30	2026-06-11 16:59:35+05:30	7	2de808dc8edc4baca5135388dc5e2a71
30	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MTE3ODA4NCwiaWF0IjoxNzgwNTczMjg0LCJqdGkiOiJlODg5NGRmODk3MzA0NDljYTI5MDk2MjI4YjU0YmFlZiIsInVzZXJfaWQiOiI1In0.7VrHWAqZzXrgVZz-jUDxqThfm4c9p7pABPG4Vg1qMVw	2026-06-04 17:11:24.749268+05:30	2026-06-11 17:11:24+05:30	5	e8894df89730449ca29096228b54baef
\.


--
-- Data for Name: token_blacklist_blacklistedtoken; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.token_blacklist_blacklistedtoken (id, blacklisted_at, token_id) FROM stdin;
1	2026-05-23 16:40:20.269143+05:30	13
2	2026-05-25 10:30:12.222898+05:30	17
3	2026-05-25 10:34:13.832766+05:30	18
4	2026-05-25 17:07:33.815069+05:30	19
5	2026-06-03 18:28:10.398916+05:30	24
6	2026-06-04 13:03:05.324705+05:30	26
7	2026-06-04 16:59:35.297734+05:30	28
\.


--
-- Name: labels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.labels_id_seq', 25, true);


--
-- Name: note_collaborators_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.note_collaborators_id_seq', 1, true);


--
-- Name: notes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.notes_id_seq', 31, true);


--
-- Name: notes_labels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.notes_labels_id_seq', 34, true);


--
-- Name: token_blacklist_blacklistedtoken_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.token_blacklist_blacklistedtoken_id_seq', 7, true);


--
-- Name: token_blacklist_outstandingtoken_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.token_blacklist_outstandingtoken_id_seq', 30, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 7, true);


--
-- PostgreSQL database dump complete
--

\unrestrict EPNUFRZDSTb23IxsqpWseMndbAy5VCWnJgPAoivVrBRf8d6NZmjWn0hUy6CvI6S

