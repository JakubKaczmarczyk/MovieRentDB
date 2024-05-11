import json
import psycopg2
import random
import bcrypt
from datetime import datetime, timedelta

# Connect to the database (or create it if it doesn't exist)
conn = psycopg2.connect(
    dbname="movie_rental",
    user="postgres",
    password="1234",
    host="localhost"
)

# Create a cursor object
cursor = conn.cursor()

## SIMPLE TABLES ##
# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS client (
   id SERIAL PRIMARY KEY,
   name VARCHAR,
   surname VARCHAR,
   username VARCHAR,
   password VARCHAR,
   role VARCHAR,
   last_logged_in TIMESTAMP NULL
)
"""
)

# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS director (
   id SERIAL PRIMARY KEY,
   name VARCHAR,
   surname VARCHAR
)
"""
)

# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS actor (
   id SERIAL PRIMARY KEY,
   name VARCHAR,
   surname VARCHAR
)
"""
)

# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS producer (
   id SERIAL PRIMARY KEY,
   producer_name VARCHAR
)
"""
)

# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS gener (
   id SERIAL PRIMARY KEY,
   gener_name VARCHAR
)
"""
)

## Advanced Tables ##
# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS movie (
   id SERIAL PRIMARY KEY,
   title VARCHAR,
   year INTEGER,
   producer_id INTEGER,
   director_id INTEGER,
   count INTEGER,
   FOREIGN KEY (producer_id) REFERENCES producer(id),
   FOREIGN KEY (director_id) REFERENCES director(id)
)
"""
)

# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS rent (
   id SERIAL PRIMARY KEY,
   client_id INTEGER,
   movie_id INTEGER,
   start_date TIMESTAMP,
   end_date TIMESTAMP,
   price INTEGER,
   FOREIGN KEY (client_id) REFERENCES client(id),
   FOREIGN KEY (movie_id) REFERENCES movie(id)
)
"""
)

## Join Tables ##
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS movie_actor (
   actor_id INTEGER,
   movie_id INTEGER,
   FOREIGN KEY (actor_id) REFERENCES actor(id),
   FOREIGN KEY (movie_id) REFERENCES movie(id)
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS movie_gener (
   gener_id INTEGER,
   movie_id INTEGER,
   FOREIGN KEY (gener_id) REFERENCES gener(id),
   FOREIGN KEY (movie_id) REFERENCES movie(id)
)
"""
)

cursor.execute("""
CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    client_id INTEGER,
    activity_type TEXT,
    login_date TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES client(id)
);
""")



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
         INSERT INTO client (name, surname, username, password)
         VALUES (%s, %s, %s, %s)
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

        num_actors = random.randint(3, 8)  # Random number of actors from 3 to 8
        actor_ids = random.sample(
            range(1, 101), num_actors
        )  # Assuming actor IDs range from 1 to 100
        for actor_id in actor_ids:
            cursor.execute(
                """
            INSERT INTO movie_actor (actor_id, movie_id)
            VALUES (%s, %s)
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
            VALUES (%s, %s)
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
    # price = days_rented * price_multiplier
    price = days_rented * 2

    cursor.execute(
        """
      INSERT INTO rent (client_id, movie_id, start_date, end_date, price)
      VALUES (%s, %s, %s, %s, %s)
   """,
        (client_id, movie_id, start_time, end_time, price),
    )


# Commit the changes and close the connection
conn.commit()

# Trigger
cursor.execute("""
    CREATE TRIGGER prevent_zero_count_rent
    BEFORE INSERT ON rent
    FOR EACH ROW
    BEGIN
        SELECT RAISE(ABORT, 'Cannot rent a movie with count 0') 
        WHERE (SELECT count FROM movie WHERE id = NEW.movie_id) = 0;
    END;
""")

# Define the trigger to log activity
cursor.execute("""
    CREATE TRIGGER log_registration
    AFTER INSERT ON client
    FOR EACH ROW
    BEGIN
        INSERT INTO activity_logs (client_id, activity_type, login_date) VALUES (NEW.id, 'register', CURRENT_TIMESTAMP);
    END;
""")

# Trigger to increase price by 5 for each day of delay when an activity log is inserted
cursor.execute("""
    CREATE TRIGGER increase_price_for_delayed_rentals
    AFTER INSERT ON activity_logs
    FOR EACH ROW
    BEGIN
        UPDATE rent
        SET price = price + (5 * (julianday('now') - julianday(end_date)))
        WHERE end_date < CURRENT_TIMESTAMP;
    END;
""")

cursor.execute("""
CREATE TRIGGER prevent_delete_rent
BEFORE DELETE ON rent
FOR EACH ROW
WHEN (
    SELECT role
    FROM client
    WHERE username = CURRENT_USER
) != 'admin'
BEGIN
    SELECT RAISE(ABORT, 'Only administrators can delete rentals');
END;

""")

# Views
cursor.execute("""
    CREATE VIEW Rental_Details AS
    SELECT 
        rent.id AS rental_id,
        client.name AS user_name,
        client.surname AS user_surname,
        movie.title AS movie_title,
        movie.year AS movie_year,
        rent.start_date AS rental_start_date,
        rent.end_date AS rental_end_date,
        rent.price AS rental_price
    FROM 
        rent
    JOIN 
        client ON rent.client_id = client.id
    JOIN 
        movie ON rent.movie_id = movie.id;
""")


# Commit the changes to save the trigger
conn.commit()


conn.close()
