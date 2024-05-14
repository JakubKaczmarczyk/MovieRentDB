import json
import psycopg2
import random
import bcrypt
from datetime import datetime, timedelta

# Connect to the database (or create it if it doesn't exist)
conn = psycopg2.connect(
    dbname="movie_rental",
    user="postgres",
    password="1234")

# Create a cursor object
cursor = conn.cursor()

# Randoms
def get_random_director_id():
    return random.randint(1, 50)  # Assuming director IDs range from 1 to 50


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
            INSERT INTO client (name, surname, username, password, role)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                client["name"],
                client["surname"],
                client["username"],
                hashed_password,
                client["role"]
            ),
        )


    for actor in data["actor"]:
        cursor.execute(
            """
            INSERT INTO actor (name, surname)
            VALUES (%s, %s)
            """,
            (actor["name"], actor["surname"]),
        )


    for director in data["director"]:
        cursor.execute(
            """
            INSERT INTO director (name, surname)
            VALUES (%s, %s)
            """,
            (director["name"], director["surname"]),
        )


    for producer in data["producer"]:
        cursor.execute(
            """
            INSERT INTO producer (producer_name)
            VALUES (%s)
            """,
            (producer["producer_name"],),
        )


    for gener in data["gener"]:
        cursor.execute(
            """
            INSERT INTO gener (gener_name)
            VALUES (%s)
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
            VALUES (%s, %s, %s, %s, %s)
            """,
            (title, year, producer_id, director_id, count),
        )


        # Pobierz movie_id ostatnio dodanego filmu
        cursor.execute("SELECT MAX(id) FROM movie")
        movie_id = cursor.fetchone()[0]  # Pobierz wartość pierwszej kolumny z wyniku zapytania


        # Dodawanie aktorów do filmu
        num_actors = random.randint(3, 8)  # Random number of actors from 3 to 8
        actor_ids = random.sample(range(1, 101), num_actors)  # Assuming actor IDs range from 1 to 100
        for actor_id in actor_ids:
            cursor.execute(
                """
                INSERT INTO movie_actor (actor_id, movie_id)
                VALUES (%s, %s)
                """,
                (actor_id, movie_id),
            )

        # Add random genres to the movie_gener table
        num_genres = random.randint(1, 3)  # Random number of genres from 1 to 3
        genre_ids = random.sample(range(1, 18), num_genres)  # Assuming genre IDs range from 1 to 17
        for genre_id in genre_ids:
            cursor.execute(
                """
                INSERT INTO movie_gener (gener_id, movie_id)
                VALUES (%s, %s)
                """,
                (genre_id, movie_id),
            ) 


    # Add rentals to the rent table
for rental in data["rent"]:
    start_time, end_time = add_random_time(rental["start_date"], rental["end_date"])
    client_id = random.randint(1, 10)
    movie_id = random.randint(1, 300)
    days_rented = (end_time - start_time).days
    price_multiplier = random.randint(1, 5)  # Random multiplier for price
    # price = days_rented * price_multiplier
    price = days_rented * 2
    is_active = True

    cursor.execute(
        """
        INSERT INTO rent (client_id, movie_id, start_date, end_date, price, is_active)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (client_id, movie_id, start_time, end_time, price, is_active),
    )


# Commit the changes to save the trigger
conn.commit()


conn.close()