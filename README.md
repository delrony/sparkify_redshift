# Introduction
In this project, we use data from a music streaming app. The app collects the songs and user activity information in JSON format. The data resides in S3. Our task in this project is to build an ETL pipeline to extract the data from S3 and load them in the staging tables of Redshift. Then we will transform the data into a set of dimensional tables.

# Database schema design
We collected information from two datasets.

1. Song Dataset: Provides song and artist information.
2. Log Dataset: Provides user activities information. This dataset also has a corresponding JSON metadata.

From this information, we created staging tables and dimentional tables (Star schema).

## Staging Tables
### staging_events

    CREATE TABLE IF NOT EXISTS staging_events
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
    
### staging_songs

    CREATE TABLE IF NOT EXISTS staging_songs
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
    
## Dimentional Tables
### Fact Table
#### songplays

    CREATE TABLE IF NOT EXISTS songplays
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
    
### Dimension Tables
#### users

    CREATE TABLE IF NOT EXISTS users
    (
        user_id int SORTKEY PRIMARY KEY, 
        first_name varchar, 
        last_name varchar, 
        gender varchar, 
        level varchar NOT NULL
    )
    
#### songs

    CREATE TABLE IF NOT EXISTS songs
    (
        song_id varchar SORTKEY PRIMARY KEY, 
        title varchar NOT NULL, 
        artist_id varchar NOT NULL, 
        year int, 
        duration float8 NOT NULL
    )
    
#### artists

    CREATE TABLE IF NOT EXISTS artists
    (
        artist_id varchar SORTKEY PRIMARY KEY, 
        name varchar NOT NULL, 
        location varchar, 
        latitude varchar, 
        longitude varchar
    )
    
#### time

    CREATE TABLE IF NOT EXISTS time
    (
        start_time timestamp DISTKEY SORTKEY PRIMARY KEY, 
        hour smallint, 
        day smallint, 
        week smallint, 
        month smallint, 
        year smallint, 
        weekday varchar
    )
    
# Amazon Redshift clusters
We used the following configurations to create the Amazon Redshift clusters.

## Node Type
4 dc2.large Nodes

## Database Configuration
Name: dev

Port: 5439

Username and Password were also provided.

## Cluster Permission
The IAM Role was added to access S3 bucket.

## Network and security
VPC: Default VPC

VPC Security Groups: Security group was added to access the database from outside.

Subnet group: By default, there was no subnet group. We created a subnet group for the default VPC and added it here.

Publicly Accessible: Yes

# ETL pipeline
In this project, we created an ETL pipeline (etl.py) that reads the song and log datasets from S3 and loads them into the above tables. It loads first the staging tables from S3 by using COPY command. Then it inserts the dimenational tables from the staging tables. The COPY and INSERT queries are defined in sql_queries.py file.

Befor executing the ETL pipeline script, we reset the tables by using the create_tables.py script.

    python create_tables.py

Then we execute the ETL pipeline script

    python etl.py

To check the data in tables, we used the query editor from Amazon Redshift. After executing the ETL pipeline, we queried for the number of rows in each table.

| Table Name     | Nr. of rows |
| :---:          |:---:        |
| staging_events | 8056        |
| staging_songs  | 14896       |
| songplays      | 319         |
| users          | 97          |
| songs          | 14896       |
| artists        | 10025       |
| time           | 319         |

# Purpose of the database
The database can be used to answer various business queries. Here are some examples:

- What are the top 3/10/100 songs for a specific day/week/month? This information can be used to advertise the top songs.
- Which songs a free user frequently plays, and how many times? These can be used to recommend the songs to the users.
- After a specific song, which song is played? The recommendation system can also use this.
- Which artist's songs are listened to by the paid users? This may help to provide incentive payments to the artists.
- What is the peak time of listening musing? It can be analyzed daily, weekly and monthly basis.
- What songs are users currently listening to? If we execute the ETL pipeline more frequently, it will be possible to get this information in real time. However, it is still a batch process. So, the data cannot be live and depends on the execution time of the last batch.

Here are some purposes of the database:

- To advertise songs and artists to the users.
- To recommend the songs to the user.
- To determine the peak usage of the application.

