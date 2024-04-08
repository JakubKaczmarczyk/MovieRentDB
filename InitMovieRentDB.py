import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect("movie_rental.db")

# Create a cursor object
cursor = conn.cursor()

# Create the tables with appropriate data types and constraints
cursor.execute("""
CREATE TABLE IF NOT EXISTS client (
   id INTEGER PRIMARY KEY,
   name VARCHAR,
   surname VARCHAR,
   username VARCHAR,
   password VARCHAR,
   last_logged_in TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS movies (
   id INTEGER PRIMARY KEY,
   title VARCHAR,
   category VARCHAR,
   year TIMESTAMP,
   producer_id INTEGER,
   director_id INTEGER,
   count INTEGER,
   FOREIGN KEY (producer_id) REFERENCES producers(id),
   FOREIGN KEY (director_id) REFERENCES directors(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS actors (
   id INTEGER PRIMARY KEY,
   name VARCHAR,
   surname VARCHAR
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS directors (
   id INTEGER PRIMARY KEY,
   name VARCHAR,
   surname VARCHAR
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS producers (
   id INTEGER PRIMARY KEY,
   studio_name VARCHAR
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS rents (
   id INTEGER PRIMARY KEY,
   user_id INTEGER,
   movie_id INTEGER,
   start_date TIMESTAMP,
   end_date TIMESTAMP,
   price INTEGER,
   FOREIGN KEY (user_id) REFERENCES client(id),
   FOREIGN KEY (movie_id) REFERENCES movies(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS movies_actors (
   actor_id INTEGER,
   movie_id INTEGER,
   FOREIGN KEY (actor_id) REFERENCES actors(id),
   FOREIGN KEY (movie_id) REFERENCES movies(id)
)
""")

# Commit the changes and close the connection
conn.commit()
conn.close()
