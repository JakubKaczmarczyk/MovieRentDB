import json
import sqlite3
import psycopg2
import random
import bcrypt
from datetime import datetime, timedelta

# Connect to the database (or create it if it doesn't exist)
#conn = sqlite3.connect("movie_rental.db", detect_types=sqlite3.PARSE_DECLTYPES)
conn = psycopg2.connect(
    dbname="movie_rental",
    user="postgres",
    password="1234",
    host="localhost")

# Create a cursor object
cursor = conn.cursor()

## SIMPLE TABLES ##
# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS client (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    surname VARCHAR(50) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20),
    last_logged_in TIMESTAMP WITHOUT TIME ZONE
);
"""
)

# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS director (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    surname VARCHAR(50) NOT NULL
);
"""
)

# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS actor (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    surname VARCHAR(50) NOT NULL
);
"""
)

# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS producer (
    id SERIAL PRIMARY KEY,
    producer_name VARCHAR(255) NOT NULL
);
"""
)

# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS gener (
  id SERIAL PRIMARY KEY,
  gener_name VARCHAR(255) NOT NULL
);
"""
)

## Advanced Tables ##
# Done
cursor.execute("""
CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    client_id INTEGER,
    activity_type TEXT,
    date TIMESTAMP,
    CONSTRAINT fk_client_id FOREIGN KEY (client_id) REFERENCES client(id)
);
""")


# Done
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS movie (
   id SERIAL PRIMARY KEY,
   title VARCHAR,
   year TIMESTAMP,
   producer_id INTEGER,
   director_id INTEGER,
   count INTEGER,
   CONSTRAINT fk_producer_id FOREIGN KEY (producer_id) REFERENCES producer(id),
   CONSTRAINT fk_director_id FOREIGN KEY (director_id) REFERENCES director(id)
);
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
   is_active BOOLEAN,
   CONSTRAINT fk_client_id FOREIGN KEY (client_id) REFERENCES client(id),
   CONSTRAINT fk_movie_id FOREIGN KEY (movie_id) REFERENCES movie(id)
);
"""
)


## Join Tables ##
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS movie_actor (
   actor_id INTEGER,
   movie_id INTEGER,
   CONSTRAINT fk_actor_id FOREIGN KEY (actor_id) REFERENCES actor(id),
   CONSTRAINT fk_movie_id FOREIGN KEY (movie_id) REFERENCES movie(id)
);
"""
)


cursor.execute(
    """
CREATE TABLE IF NOT EXISTS movie_gener (
   gener_id INTEGER,
   movie_id INTEGER,
   CONSTRAINT fk_gener_id FOREIGN KEY (gener_id) REFERENCES gener(id),
   CONSTRAINT fk_movie_id FOREIGN KEY (movie_id) REFERENCES movie(id)
);
"""
)


# Triggers
cursor.execute("""
    CREATE OR REPLACE FUNCTION check_movie_count() RETURNS TRIGGER AS $$
    BEGIN
        IF (SELECT count FROM movie WHERE id = NEW.movie_id) = 0 THEN
            RAISE EXCEPTION 'Cannot rent a movie with count 0';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER prevent_zero_count_rent
    BEFORE INSERT ON rent
    FOR EACH ROW
    EXECUTE FUNCTION check_movie_count();

""")


# Define the trigger to log activity when registering new user
cursor.execute("""
    CREATE OR REPLACE FUNCTION log_registration_function() RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO activity_logs (client_id, activity_type, date)
        VALUES (NEW.id, 'register', CURRENT_TIMESTAMP);
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER log_registration
    AFTER INSERT ON client
    FOR EACH ROW
    EXECUTE FUNCTION log_registration_function();

""")


# Trigger to increase price by 5 for each day of delay when an activity log is inserted
cursor.execute("""
    CREATE OR REPLACE FUNCTION increase_price_for_delayed_rentals() RETURNS TRIGGER AS $$
    BEGIN
        -- Update price only for active rentals
        UPDATE rent
        SET price = price + (5 * (EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - end_date))/86400))
        WHERE end_date < CURRENT_TIMESTAMP AND is_active = true;
        
        -- Log activity for the price increase
        INSERT INTO activity_logs (client_id, activity_type, date)
        SELECT NEW.client_id, 'price_increase', CURRENT_TIMESTAMP
        FROM rent
        WHERE end_date < CURRENT_TIMESTAMP AND is_active = true;
        
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER increase_price_for_delayed_rentals
    AFTER INSERT ON activity_logs
    FOR EACH ROW
    EXECUTE FUNCTION increase_price_for_delayed_rentals();

""")


# Trigger to log activity when a new row is inserted into the rents table
cursor.execute("""
    CREATE OR REPLACE FUNCTION log_rent_insert_activity_function() RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO activity_logs (client_id, activity_type, date)
        VALUES (NEW.client_id, 'rent_started', CURRENT_TIMESTAMP);
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER log_rent_insert_activity
    AFTER INSERT ON rent
    FOR EACH ROW
    EXECUTE FUNCTION log_rent_insert_activity_function();

""")

# Trigger to log activity when a row is updated in the rents table
cursor.execute("""
    CREATE OR REPLACE FUNCTION log_rent_update_activity()
    RETURNS TRIGGER AS $$
    BEGIN
        -- Insert activity into activity_logs for the update operation
        INSERT INTO activity_logs (client_id, activity_type, date)
        VALUES (NEW.client_id, 
                CASE 
                    WHEN NEW.is_active = TRUE THEN 'rent_started' 
                    ELSE 'rent_finished' 
                END, 
                CURRENT_TIMESTAMP);
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER log_rent_update_activity
    AFTER UPDATE OF is_active ON rent
    FOR EACH ROW
    WHEN (OLD.is_active IS DISTINCT FROM NEW.is_active)
    EXECUTE FUNCTION log_rent_update_activity();

""")

# Views
cursor.execute("""
    CREATE OR REPLACE VIEW Active_Rental_Details AS
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
        rent.is_active = TRUE;

""")

cursor.execute("""
    CREATE OR REPLACE VIEW Archived_Rental_Details AS
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
        rent.is_active = FALSE;

""")

cursor.execute("""
    CREATE OR REPLACE VIEW Users_Activity AS
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
    CREATE OR REPLACE VIEW AvailableMovies AS
    SELECT 
        m.id, 
        m.title, 
        m.count, 
        m.year, 
        p.id AS producer_id, 
        p.producer_name, 
        d.id AS director_id, 
        d.name AS director_name, 
        d.surname AS director_surname, 
        a.id AS actor_id, 
        a.name AS actor_name, 
        a.surname AS actor_surname
    FROM 
        movie m
    LEFT JOIN 
        movie_actor ma ON m.id = ma.movie_id
    LEFT JOIN 
        actor a ON ma.actor_id = a.id
    LEFT JOIN 
        producer p ON m.producer_id = p.id
    LEFT JOIN 
        director d ON m.director_id = d.id
    WHERE 
        m.count > 0
    ORDER BY 
        m.title;

""")


# Commit the changes to save the trigger
conn.commit()


conn.close()
