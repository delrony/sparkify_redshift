import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

IAM_ROLE = config['IAM_ROLE']['ARN']
LOG_DATA = config['S3']['LOG_DATA']
LOG_JSONPATH = config['S3']['LOG_JSONPATH']
SONG_DATA = config['S3']['SONG_DATA']

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create= ("""CREATE TABLE IF NOT EXISTS staging_events
(
    artist varchar,
    auth varchar,
    firstName varchar,
    gender varchar,
    itemInSession int,
    lastName varchar,
    length float8,
    level varchar,
    location varchar,
    method varchar,
    page varchar,
    registration bigint,
    sessionid int,
    song varchar,
    status int,
    ts timestamp,
    userAgent varchar,
    userId int
)
""")

staging_songs_table_create = ("""CREATE TABLE IF NOT EXISTS staging_songs
(
    song_id varchar,
    num_songs bigint,
    artist_id varchar,
    artist_latitude varchar,
    artist_longitude varchar,
    artist_location varchar,
    artist_name varchar,
    title varchar,
    duration float8,
    year int
)
""")

songplay_table_create = ("""CREATE TABLE IF NOT EXISTS songplays
(
    songplay_id bigint IDENTITY(0,1) PRIMARY KEY, 
    start_time timestamp NOT NULL DISTKEY SORTKEY, 
    user_id int NOT NULL, 
    level varchar NOT NULL, 
    song_id varchar NOT NULL, 
    artist_id varchar NOT NULL, 
    session_id int NOT NULL, 
    location varchar, 
    user_agent varchar
)
""")

user_table_create = ("""CREATE TABLE IF NOT EXISTS users
(
    user_id int SORTKEY PRIMARY KEY, 
    first_name varchar, 
    last_name varchar, 
    gender varchar, 
    level varchar NOT NULL
)
""")

song_table_create = ("""CREATE TABLE IF NOT EXISTS songs
(
    song_id varchar SORTKEY PRIMARY KEY, 
    title varchar NOT NULL, 
    artist_id varchar NOT NULL, 
    year int, 
    duration float8 NOT NULL
)
""")

artist_table_create = ("""CREATE TABLE IF NOT EXISTS artists
(
    artist_id varchar SORTKEY PRIMARY KEY, 
    name varchar NOT NULL, 
    location varchar, 
    latitude varchar, 
    longitude varchar
)
""")

time_table_create = ("""CREATE TABLE IF NOT EXISTS time
(
    start_time timestamp DISTKEY SORTKEY PRIMARY KEY, 
    hour smallint, 
    day smallint, 
    week smallint, 
    month smallint, 
    year smallint, 
    weekday varchar
)
""")

# STAGING TABLES

staging_events_copy = ("""COPY staging_events
FROM {}
IAM_ROLE {}
REGION 'us-west-2'
JSON {}
TIMEFORMAT 'epochmillisecs'
""").format(LOG_DATA, IAM_ROLE, LOG_JSONPATH)

staging_songs_copy = ("""COPY staging_songs
FROM {}
IAM_ROLE {}
REGION 'us-west-2'
JSON 'auto'
""").format(SONG_DATA, IAM_ROLE)

# FINAL TABLES

songplay_table_insert = ("""INSERT INTO songplays
(start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
SELECT  DISTINCT(se.ts), se.userId, se.level, ss.song_id, ss.artist_id, se.sessionid, se.location, se.userAgent
FROM staging_events se
JOIN staging_songs ss ON se.song = ss.title AND se.artist = ss.artist_name AND se.length = ss.duration
WHERE se.page = 'NextSong' AND se.userId IS NOT NULL
""")

user_table_insert = ("""INSERT INTO users
(user_id, first_name, last_name, gender, level)
SELECT DISTINCT(userId) as user_id, firstName, lastName, gender, level
FROM staging_events se1
WHERE se1.userId IS NOT NULL
AND se1.ts = (SELECT MAX(ts) FROM staging_events se2 WHERE se1.userId = se2.userId)
ORDER BY se1.userId
""")

song_table_insert = ("""INSERT INTO songs
(song_id, title, artist_id, year, duration)
SELECT DISTINCT(song_id), title, artist_id, year, duration FROM staging_songs
WHERE song_id IS NOT NULL
""")

artist_table_insert = ("""INSERT INTO artists
(artist_id, name, location, latitude, longitude)
SELECT DISTINCT(artist_id) as artist_id, artist_name, artist_location, artist_latitude, artist_longitude
FROM staging_songs
WHERE artist_id IS NOT NULL
""")

time_table_insert = ("""INSERT INTO time (start_time, hour, day, week, month, year, weekday)
SELECT DISTINCT(start_time),
EXTRACT (HOUR FROM start_time), EXTRACT (DAY FROM start_time),
EXTRACT (WEEK FROM start_time), EXTRACT (MONTH FROM start_time),
EXTRACT (YEAR FROM start_time), EXTRACT (WEEKDAY FROM start_time) FROM songplays
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
