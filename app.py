import tkinter as tk
import sqlite3
import bcrypt
import json
import random
from datetime import datetime, timedelta


## Start of Feeding data and creating DB
def feed_database():
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
        return random.randint(1, 50)  # Assuming director IDs range from 1 to 64


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


# Main
# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect("movie_rental.db", detect_types=sqlite3.PARSE_DECLTYPES)

# Create a cursor object
cursor = conn.cursor()

table_exists = cursor.fetchone() is not None
if not table_exists:
    feed_database()
conn.close()
## End of Feeding data and creating DB


conn = sqlite3.connect("movie_rental.db")
cursor = conn.cursor()


def login_user(username_entry, password_entry, error_label):
    username = username_entry.get()
    password = password_entry.get()
    password = password.encode("utf-8")

    if not username:
        error_label.config(text="Username cannot be empty")
        return False

    if not password:
        error_label.config(text="Password cannot be empty")
        return False

    cursor.execute("SELECT * FROM client WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        stored_password = user[4]
        if bcrypt.checkpw(password, stored_password):
            return True
        else:
            error_label.config(text="Invalid username or password")
            return False
    else:
        error_label.config(text="Invalid username or password")
        return False


def register_user(
    username_entry, password_entry, name_entry, surname_entry, error_label
):
    username = username_entry.get()
    password = password_entry.get()
    name = name_entry.get()
    surname = surname_entry.get()

    if not username:
        error_label.config(text="Username cannot be empty")
        return False

    if not password:
        error_label.config(text="Password cannot be empty")
        return False

    if not name:
        error_label.config(text="Name cannot be empty")
        return False

    if not surname:
        error_label.config(text="Surname cannot be empty")
        return False

    cursor.execute(f"SELECT * FROM client WHERE name = ?", (username,))
    if cursor.fetchone() is not None:
        error_label.config(text="Username already exists")
        return False

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    cursor.execute(
        "INSERT INTO client (username, password, name, surname, last_logged_in) VALUES (?,?,?,?,?)",
        (username, hashed_password, name, surname, None),
    )
    conn.commit()
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    surname_entry.delete(0, tk.END)
    return True


def get_user_reservations(username):
    try:
        query = """
      SELECT m.title, r.start_date, r.end_date, r.price
      FROM rents r
      INNER JOIN movie m ON r.movie_id = m.id
      INNER JOIN client c ON r.user_id = c.id
      WHERE c.username = ?
    """
        cursor.execute(query, (username,))

        reservations = []
        for row in cursor.fetchall():
            reservation = {
                "movie_title": row[0],
                "start_date": row[1],
                "end_date": row[2],
                "price": row[3],
            }
            reservations.append(reservation)
        return reservations
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def get_movies():
    try:
        cursor.execute(
            """
        SELECT m.id, m.title, m.year, p.id AS producer_id, p.producer_name, 
        d.id AS director_id, d.name AS director_name, d.surname AS director_surname, m.count, 
            a.id AS actor_id, a.name AS actor_name, a.surname AS actor_surname
        FROM movie m
        LEFT JOIN movie_actor ma ON m.id = ma.movie_id
        LEFT JOIN actor a ON ma.actor_id = a.id
        LEFT JOIN producer p ON m.producer_id = p.id
        LEFT JOIN director d ON m.director_id = d.id
        ORDER BY m.title
        """
        )
        rows = cursor.fetchall()
        movies = {}
        for row in rows:
            (
                movie_id,
                title,
                year,
                producer_id,
                producer_name,
                director_id,
                director_name,
                director_surname,
                count,
                actor_id,
                actor_name,
                actor_surname,
            ) = row
            if movie_id not in movies:
                movies[movie_id] = {
                    "id": movie_id,
                    "title": title,
                    "year": year,
                    "producer_id": producer_id,
                    "producer_name": producer_name,
                    "director_id": director_id,
                    "director_name": director_name,
                    "director_surname": director_surname,
                    "count": count,
                    "actors": [],
                }
            if actor_id:
                movies[movie_id]["actors"].append(
                    {"id": actor_id, "name": actor_name, "surname": actor_surname}
                )
        movie_list = list(movies.values())
        return movie_list
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


class SimpleGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Movie Rental")
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        self.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.state("zoomed")

        self.login_screen_setup()
        self.register_screen_setup()
        self.my_rents_screen_setup()
        self.find_movie_screen_setup()
        self.main_page_setup()

        self.switch_to_login()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.logged_user = None

    ## Screens ##
    def login_screen_setup(self):
        self.title("Movie Rental Login")

        self.login_label_username = tk.Label(self, text="Username:")
        self.login_label_username.pack()

        self.entry_username = tk.Entry()
        self.entry_username.pack()

        self.login_label_password = tk.Label(self, text="Password:")
        self.login_label_password.pack()

        self.entry_password = tk.Entry(self, show="*")
        self.entry_password.pack()

        self.login_button = tk.Button(self, text="Login", command=self.login_user)
        self.login_button.pack()

        self.register_button = tk.Button(
            self, text="Register", command=self.switch_to_register
        )
        self.register_button.pack()

        self.error_label = tk.Label(self, text="")
        self.error_label.pack()

    def register_screen_setup(self):

        self.title("Movie Rental Register")

        self.register_label_username = tk.Label(self, text="Username:")
        self.register_label_username.pack()

        self.register_entry_username = tk.Entry(self)
        self.register_entry_username.pack()

        self.register_label_password = tk.Label(self, text="Password:")
        self.register_label_password.pack()

        self.register_entry_password = tk.Entry(self, show="*")
        self.register_entry_password.pack()

        self.register_label_name = tk.Label(self, text="Name:")
        self.register_label_name.pack()

        self.register_entry_name = tk.Entry(self)
        self.register_entry_name.pack()

        self.register_label_surname = tk.Label(self, text="Surname:")
        self.register_label_surname.pack()

        self.register_entry_surname = tk.Entry(self)
        self.register_entry_surname.pack()

        self.register_button = tk.Button(
            self, text="Register", command=self.register_user
        )
        self.register_button.pack()

        self.back_to_login_button = tk.Button(
            self, text="Back to Login", command=self.switch_to_login
        )
        self.back_to_login_button.pack()

    def my_rents_screen_setup(self):
        self.title("My Rents")

        self.back_to_main_button = tk.Button(
            self, text="Back to Main Page", command=self.switch_to_main_page
        )
        self.back_to_main_button.pack()

        self.my_rents_label = tk.Label(self, text="My Rents")
        self.my_rents_label.pack()

    def find_movie_screen_setup(self):
        self.title("Find Movie")

        self.back_to_main_button = tk.Button(
            self, text="Back to Main Page", command=self.switch_to_main_page
        )
        self.back_to_main_button.pack()

        self.find_movie_label = tk.Label(self, text="Find Movie")
        self.find_movie_label.pack()

    def main_page_setup(self):
        self.title("Main Page")

        self.my_rents_button = tk.Button(
            self, text="My Rents", command=self.switch_to_my_rents
        )
        self.my_rents_button.pack()

        self.find_movie_button = tk.Button(
            self, text="Find Movie", command=self.switch_to_find_movie
        )
        self.find_movie_button.pack()

    ## Switches ##
    def switch_to_register(self):
        self.close_all_windows()
        self.register_screen_setup()

    def switch_to_login(self):
        self.close_all_windows()
        self.login_screen_setup()

    def switch_to_my_rents(self):
        self.close_all_windows()
        self.my_rents_screen_setup()
        self.fetch_rents()

    def switch_to_find_movie(self):
        self.close_all_windows()
        self.find_movie_screen_setup()
        self.fetch_movies()

    def switch_to_main_page(self):
        self.close_all_windows()
        self.main_page_setup()

    def close_all_windows(self):
        for widget in self.winfo_children():
            widget.destroy()

    ## Calls ##
    def login_user(self):
        username_entry = self.entry_username
        password_entry = self.entry_password
        error_label = self.error_label

        result = login_user(username_entry, password_entry, error_label)
        if result:
            self.logged_user = username_entry.get()
            self.switch_to_main_page()

    def register_user(self):
        username_entry = self.register_entry_username
        password_entry = self.register_entry_password
        name_entry = self.register_entry_name
        surname_entry = self.register_entry_surname
        error_label = self.error_label

        result = register_user(
            username_entry, password_entry, name_entry, surname_entry, error_label
        )
        if result:
            self.switch_to_login()

    def fetch_rents(self):
        reservations = get_user_reservations(self.logged_user)
        if reservations:
            for i, reservation in enumerate(reservations):
                label_text = f"Movie: {reservation['movie_title']} | Start Date: {reservation['start_date']} | End Date: {reservation['end_date']} | Price: {reservation['price']}"
                tk.Label(self, text=label_text).pack()
        else:
            tk.Label(self, text="No reservations found.").pack()

    def fetch_movies(self):
        movies = get_movies()
        listbox = tk.Listbox(self, selectmode=tk.MULTIPLE, width=1000, height=600)
        if movies:
            columns = ["Title", "Producer", "Director", "Year", "Actors"]
            header = "{:<100} | {:<50} | {:<50} | {:<10} | {:<100}".format(*columns)
            listbox.insert(tk.END, header)
            listbox.insert(tk.END, "-" * len(header))

            for movie in movies:
                title = movie['title']
                year = movie['year']
                producer = movie['producer_name']
                director = movie['director_name'] + " " + movie['director_surname']
                actors = ", ".join([f"{actor['name']} {actor['surname']}" for actor in movie["actors"]])
                row = "{:<100} | {:<50} | {:<50} | {:<10} | {:<100}".format(title, producer, director, year, actors)
                listbox.insert(tk.END, row)
        else:
            listbox.insert(tk.END, "No movies found.")

        listbox.pack()


    # Other
    def on_closing(self):
        try:
            conn.close()
        finally:
            self.destroy()


if __name__ == "__main__":
    app = SimpleGUI()
    app.mainloop()
