import json
import sqlite3
import random
import bcrypt
from datetime import datetime, timedelta

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect("movie_rental.db", detect_types=sqlite3.PARSE_DECLTYPES)

# Create a cursor object
cursor = conn.cursor()

## SIMPLE TABLES ##
# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS client (
   id INTEGER PRIMARY KEY,
   name VARCHAR,
   surname VARCHAR,
   username VARCHAR,
   password VARCHAR,
   last_logged_in TIMESTAMP
)
"""
)

# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS director (
   id INTEGER PRIMARY KEY,
   name VARCHAR,
   surname VARCHAR
)
"""
)

# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS actor (
   id INTEGER PRIMARY KEY,
   name VARCHAR,
   surname VARCHAR
)
"""
)

# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS producer (
   id INTEGER PRIMARY KEY,
   producer_name VARCHAR
)
"""
)

# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS gener (
   id INTEGER PRIMARY KEY,
   gener_name VARCHAR
)
"""
)

## Advanced Tables ##
# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS movie (
   id INTEGER PRIMARY KEY,
   title VARCHAR,
   year TIMESTAMP,
   producer_id INTEGER,
   director_id INTEGER,
   count INTEGER,
   FOREIGN KEY (producer_id) REFERENCES producers(id),
   FOREIGN KEY (director_id) REFERENCES directors(id)
)
"""
)

# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS rent (
   id INTEGER PRIMARY KEY,
   client_id INTEGER,
   movie_id INTEGER,
   start_date TIMESTAMP,
   end_date TIMESTAMP,
   price INTEGER,
   FOREIGN KEY (client_id) REFERENCES client(id),
   FOREIGN KEY (movie_id) REFERENCES movies(id)
)
"""
)

## Join Tables ##
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS movie_actor (
   actor_id INTEGER,
   movie_id INTEGER,
   FOREIGN KEY (actor_id) REFERENCES actors(id),
   FOREIGN KEY (movie_id) REFERENCES movies(id)
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS movie_gener (
   gener_id INTEGER,
   movie_id INTEGER,
   FOREIGN KEY (gener_id) REFERENCES gener(id),
   FOREIGN KEY (movie_id) REFERENCES movies(id)
)
"""
)


# Randoms
def get_random_director_id():
    return random.randint(1, 64)  # Assuming director IDs range from 1 to 64


# Function to get a random producer ID
def get_random_producer_id():
    return random.randint(1, 100)


def random_time():
    return timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))


def add_random_time(start_date_str, end_date_str):
    # Parse start and end dates
    start_date = datetime.strptime(start_date_str, "%m/%d/%Y")
    end_date = datetime.strptime(end_date_str, "%m/%d/%Y")

    # Generate random hour and minute
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)

    # Add random time to start and end dates
    start_date += timedelta(hours=random_hour, minutes=random_minute)
    end_date += timedelta(hours=random_hour, minutes=random_minute)

    return start_date, end_date


with open("raw_data.json", "r") as f:
    data = json.load(f)
    for client in data["client"]:
        hashed_password = bcrypt.hashpw(b"1234", bcrypt.gensalt())
        cursor.execute(
            """
         INSERT INTO client (name, surname, username, password)
         VALUES (?, ?, ?, ?)
      """,
            (
                client["name"],
                client["surname"],
                client["username"],
                hashed_password,
            ),
        )

    for actor in data["actor"]:
        cursor.execute(
            """
         INSERT INTO actor (name, surname)
         VALUES (?, ?)
      """,
            (actor["name"], actor["surname"]),
        )

    for director in data["director"]:
        cursor.execute(
            """
         INSERT INTO director (name, surname)
         VALUES (?, ?)
      """,
            (director["name"], director["surname"]),
        )

    for producer in data["producer"]:
        cursor.execute(
            """
         INSERT INTO producer (producer_name)
         VALUES (?)
      """,
            (producer["producer_name"],),
        )

    for gener in data["gener"]:
        cursor.execute(
            """
         INSERT INTO gener (gener_name)
         VALUES (?)
      """,
            (gener["gener_name"],),
        )

    for movie in data["movie"]:
        title = movie["title"]
        year = movie["year"]
        count = movie["count"]
        director_id = get_random_director_id()
        producer_id = get_random_producer_id()

        cursor.execute(
            """
         INSERT INTO movie (title, year, producer_id, director_id, count)
         VALUES (?, ?, ?, ?, ?)
      """,
            (title, year, producer_id, director_id, count),
        )

        num_actors = random.randint(3, 8)  # Random number of actors from 3 to 8
        actor_ids = random.sample(
            range(1, 101), num_actors
        )  # Assuming actor IDs range from 1 to 100
        for actor_id in actor_ids:
            cursor.execute(
                """
            INSERT INTO movie_actor (actor_id, movie_id)
            VALUES (?, ?)
         """,
                (actor_id, cursor.lastrowid),
            )  # cursor.lastrowid gets the ID of the last inserted movie

        # Add random genres to the movie_gener table
        num_genres = random.randint(1, 3)  # Random number of genres from 1 to 3
        genre_ids = random.sample(
            range(1, 18), num_genres
        )  # Assuming genre IDs range from 1 to 17
        for genre_id in genre_ids:
            cursor.execute(
                """
            INSERT INTO movie_gener (gener_id, movie_id)
            VALUES (?, ?)
         """,
                (genre_id, cursor.lastrowid),
            )  # cursor.lastrowid gets the ID of the last inserted movie

    # Add rentals to the rent table
for rental in data["rent"]:
    start_time, end_time = add_random_time(rental["start_date"], rental["end_date"])
    client_id = random.randint(1, 10)
    movie_id = random.randint(1, 300)
    days_rented = (end_time - start_time).days
    price_multiplier = random.randint(1, 5)  # Random multiplier for price
    price = days_rented * price_multiplier

    cursor.execute(
        """
      INSERT INTO rent (client_id, movie_id, start_date, end_date, price)
      VALUES (?, ?, ?, ?, ?)
   """,
        (client_id, movie_id, start_time, end_time, price),
    )


# Commit the changes and close the connection
conn.commit()
conn.close()
