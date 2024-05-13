import json
import sqlite3
import random
import bcrypt
from datetime import datetime, timedelta

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect("movie_rental.db", detect_types=sqlite3.PARSE_DECLTYPES)

# Create a cursor object
cursor = conn.cursor()
cursor.execute(
    """
    PRAGMA time_zone = 'Europe/Warsaw+0200';
    """
)
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
   role VARCHAR,
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
cursor.execute("""
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY,
    client_id INTEGER,
    activity_type TEXT,
    date TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES client(id)
);
""")

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
   is_active BOOLEAN,
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

# Triggers
cursor.execute("""
    CREATE TRIGGER prevent_zero_count_rent
    BEFORE INSERT ON rent
    FOR EACH ROW
    BEGIN
        SELECT RAISE(ABORT, 'Cannot rent a movie with count 0') 
        WHERE (SELECT count FROM movie WHERE id = NEW.movie_id) = 0;
    END;
""")

# Define the trigger to log activity when registering new user
cursor.execute("""
    CREATE TRIGGER log_registration
    AFTER INSERT ON client
    FOR EACH ROW
    BEGIN
        INSERT INTO activity_logs (client_id, activity_type, date) VALUES (NEW.id, 'register', CURRENT_TIMESTAMP);
    END;
""")

# Trigger to increase price by 5 for each day of delay when an activity log is inserted
cursor.execute("""
    CREATE TRIGGER increase_price_for_delayed_rentals
    AFTER INSERT ON activity_logs
    FOR EACH ROW
    BEGIN
        -- Update price only for active rentals
        UPDATE rent
        SET price = price + (5 * (julianday('now') - julianday(end_date)))
        WHERE end_date < CURRENT_TIMESTAMP AND is_active = 1;
        
        -- Log activity for the price increase
        INSERT INTO activity_logs (client_id, activity_type, date)
        SELECT client_id, 'price_increase', CURRENT_TIMESTAMP
        FROM rent
        WHERE end_date < CURRENT_TIMESTAMP AND is_active = 1;
    END;
""")


# Trigger to log activity when a new row is inserted into the rents table
cursor.execute("""
    CREATE TRIGGER log_rent_insert_activity
    AFTER INSERT ON rent
    FOR EACH ROW
    BEGIN
        -- Insert activity into activity_logs for the insert operation
        INSERT INTO activity_logs (client_id, activity_type, date)
        VALUES (NEW.client_id, 'rent_started', CURRENT_TIMESTAMP);
    END;
""")

# Trigger to log activity when a row is updated in the rents table
cursor.execute("""
    CREATE TRIGGER log_rent_update_activity
    AFTER UPDATE OF is_active ON rent
    FOR EACH ROW
    WHEN OLD.is_active <> NEW.is_active
    BEGIN
        -- Insert activity into activity_logs for the update operation
        INSERT INTO activity_logs (client_id, activity_type, date)
        VALUES (NEW.client_id, 
                CASE 
                    WHEN NEW.is_active = 1 THEN 'rent_started' 
                    ELSE 'rent_finished' 
                END, 
                CURRENT_TIMESTAMP);
    END;
""")

# Views
cursor.execute("""
    CREATE VIEW Active_Rental_Details AS
    SELECT 
        rent.id AS rental_id,
        client.name AS client_name,
        client.surname AS client_surname,
        client.username AS client_username,
        movie.title AS rental_title,
        movie.year AS rental_year,
        rent.start_date AS rental_start_date,
        rent.end_date AS rental_end_date,
        rent.price AS rental_price
    FROM 
        rent
    JOIN 
        client ON rent.client_id = client.id
    JOIN 
        movie ON rent.movie_id = movie.id
    WHERE 
        rent.is_active = 1;

""")

cursor.execute("""
    CREATE VIEW Archived_Rental_Details AS
    SELECT 
        rent.id AS rental_id,
        client.name AS client_name,
        client.surname AS client_surname,
        client.username AS client_username,
        movie.title AS rental_title,
        movie.year AS rental_year,
        rent.start_date AS rental_start_date,
        rent.end_date AS rental_end_date,
        rent.price AS rental_price
    FROM 
        rent
    JOIN 
        client ON rent.client_id = client.id
    JOIN 
        movie ON rent.movie_id = movie.id
    WHERE 
        rent.is_active = 0;

""")

cursor.execute("""
    CREATE VIEW Users_Activity AS
    SELECT
        activity_logs.date AS activity_time,
        client.id AS client_id,
        client.name AS client_name,
        client.surname AS client_surname,
        client.username AS client_username,
        activity_logs.activity_type AS action_type,
        client.last_logged_in AS last_logged_in,
        client.role AS client_role
    FROM
        activity_logs
    JOIN
        client ON activity_logs.client_id = client.id
    ORDER BY
        activity_logs.date DESC;

""")

cursor.execute("""
    CREATE VIEW AvailableMovies AS
    SELECT m.id, m.title, m.count, m.year, p.id AS producer_id, p.producer_name, 
        d.id AS director_id, d.name AS director_name, d.surname AS director_surname, m.count, 
            a.id AS actor_id, a.name AS actor_name, a.surname AS actor_surname
        FROM movie m
        LEFT JOIN movie_actor ma ON m.id = ma.movie_id
        LEFT JOIN actor a ON ma.actor_id = a.id
        LEFT JOIN producer p ON m.producer_id = p.id
        LEFT JOIN director d ON m.director_id = d.id
        WHERE m.count > 0
        ORDER BY m.title
""")


# Commit the changes to save the trigger
conn.commit()


conn.close()
