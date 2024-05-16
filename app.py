import tkinter as tk
import psycopg2
import bcrypt
from datetime import datetime, timedelta
from tkcalendar import DateEntry



conn = psycopg2.connect(
    dbname="movie_rental",
    user="postgres",
    password="1234")
cursor = conn.cursor()


def login_user(username, password, error_label):
    password_encoded = password.encode("utf-8")

    if not username:
        error_label.config(text="Username cannot be empty")
        return False

    if not password:
        error_label.config(text="Password cannot be empty")
        return False

    cursor.execute("SELECT * FROM client WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user:
        stored_password = user[4]
        if bcrypt.checkpw(password_encoded, stored_password.encode("utf-8")):
            try:
                current_timestamp = datetime.now()
                cursor.execute("INSERT INTO activity_logs (client_id, activity_type, date) VALUES (%s, %s, CURRENT_TIMESTAMP)", (user[0], 'login'))
                conn.commit()
            except Exception as e:
                print("Error logging login information:", e)
            return True
        else:
            error_label.config(text="Invalid username or password")
            return False
    else:
        error_label.config(text="Invalid username or password")
        return False

def is_user_admin(username, password, error_label):
    password_encoded = password.encode("utf-8")

    if not username:
        error_label.config(text="Username cannot be empty")
        return False

    if not password:
        error_label.config(text="Password cannot be empty")
        return False

    cursor.execute("SELECT * FROM client WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user:
        stored_password = user[4]
        if bcrypt.checkpw(password_encoded, stored_password.encode("utf-8")):
            if user[5] == "admin":
                return True
            else:
                return False
        else:
            error_label.config(text="Invalid username or password")
            return False
    else:
        error_label.config(text="Invalid username or password")
        return False

def register_user(
    username, password, name, surname, error_label
):
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

    cursor.execute("SELECT * FROM client WHERE name = %s", (username,))
    if cursor.fetchone() is not None:
        error_label.config(text="Username already exists")
        return False

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode('utf-8')
    cursor.execute(
        "INSERT INTO client (username, password, name, surname, last_logged_in) VALUES (%s,%s,%s,%s,%s)",
        (username, hashed_password, name, surname, None),
    )
    conn.commit()
    return True

def get_user_reservations(username):
    try:
        query = """
        SELECT 
            rental_title, 
            rental_start_date, 
            rental_end_date, 
            rental_price, 
            client_name, 
            client_surname, 
            rental_id
        FROM 
            Active_Rental_Details
        WHERE 
        client_username = %s;
    """
        cursor.execute(query, (username,))

        reservations = []
        for row in cursor.fetchall():
            reservation = {
                "movie_title": row[0],
                "start_date": row[1],
                "end_date": row[2],
                "price": row[3],
                "name": row[4],
                "surname": row[5],
                "id": row[6]
            }
            reservations.append(reservation)
        return reservations
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def get_user_archived_reservations(username):
    try:
        query = """
        SELECT 
            rental_title, 
            rental_start_date, 
            rental_end_date, 
            rental_price, 
            client_name, 
            client_surname, 
            rental_id
        FROM 
            Archived_Rental_Details
        WHERE 
        client_username = %s;
    """
        cursor.execute(query, (username,))

        reservations = []
        for row in cursor.fetchall():
            reservation = {
                "movie_title": row[0],
                "start_date": row[1],
                "end_date": row[2],
                "price": row[3],
                "name": row[4],
                "surname": row[5],
                "id": row[6]
            }
            reservations.append(reservation)
        return reservations
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def get_users_activity():
    try:
        cursor.execute(
            """
            SELECT * FROM Users_Activity
            """
        )
        rows = cursor.fetchall()
        activity_list = []
        for row in rows:
            activity_time, client_id, client_name, client_surname, client_username, action_type, last_logged_in, client_role = row
            activity_list.append({
                "activity_time": activity_time,
                "client_id": client_id,
                "client_name": client_name,
                "client_surname": client_surname,
                "client_username": client_username,
                "action_type": action_type,
                "last_logged_in": last_logged_in,
                "client_role": client_role
            })
        return activity_list
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def get_movies(
    title_filter=None,
    producer_filter=None,
    director_name_filter=None,
    year_filter=None,
    actors_filter=None,
):
    try:
        where_clause = []
        params = []

        query = "SELECT * FROM AvailableMovies"

        # Build WHERE clause based on provided filters
        if title_filter:
            where_clause.append("title LIKE %s")
            params.append("%" + title_filter + "%")
        if producer_filter:
            where_clause.append("producer_name LIKE %s")
            params.append("%" + producer_filter + "%")
        if director_name_filter:
            where_clause.append("(director_name LIKE %s OR director_surname LIKE %s)")
            params.append("%" + director_name_filter + "%")
            params.append("%" + director_name_filter + "%")
        if year_filter:
            where_clause.append("CAST(year AS VARCHAR) LIKE %s")
            params.append("%" + year_filter + "%")
        if actors_filter:
            where_clause.append("(actor_name LIKE %s OR actor_surname LIKE %s)")
            params.append("%" + actors_filter + "%")
            params.append("%" + actors_filter + "%")

        if where_clause:
            query += " WHERE " + " AND ".join(where_clause)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        movies = {}
        for row in rows:
            (
                movie_id,
                title,
                count,
                year,
                producer_id,
                producer_name,
                director_id,
                director_name,
                director_surname,
                actor_id,
                actor_name,
                actor_surname,
            ) = row
            if movie_id not in movies:
                movies[movie_id] = {
                    "id": movie_id,
                    "title": title,
                    "count": count,
                    "year": year,
                    "producer_id": producer_id,
                    "producer_name": producer_name,
                    "director_id": director_id,
                    "director_name": director_name,
                    "director_surname": director_surname,
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

def add_movie(title, year, producer_name, director_name, director_surname, count, genre_list, actor_list):
    try:
        cursor.execute("SELECT id FROM producer WHERE producer_name = %s", (producer_name,))
        producer_id = cursor.fetchone()
        if producer_id is None:
            # Dodanie nowego producenta, jeśli nie istnieje
            cursor.execute("INSERT INTO producer (producer_name) VALUES (%s) RETURNING id", (producer_name,))
            producer_id = cursor.fetchone()[0]
        else:
            producer_id = producer_id[0]

        # Sprawdzenie istnienia reżysera w bazie danych
        cursor.execute("SELECT id FROM director WHERE name = %s AND surname = %s", (director_name, director_surname))
        director_id = cursor.fetchone()
        if director_id is None:
            # Dodanie nowego reżysera, jeśli nie istnieje
            cursor.execute("INSERT INTO director (name, surname) VALUES (%s, %s) RETURNING id", (director_name, director_surname))
            director_id = cursor.fetchone()[0]
        else:
            director_id = director_id[0]

        cursor.execute("SELECT id FROM movie WHERE title = %s", (title,))
        existing_movie_id = cursor.fetchone()
        if existing_movie_id:
            movie_id = existing_movie_id
        else:
            cursor.execute("""
                INSERT INTO movie (title, year, producer_id, director_id, count)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (title, year, producer_id, director_id, count))
            row = cursor.fetchone()
            movie_id = row[0] if row else None

        for genre in genre_list:
            # Sprawdzenie istnienia gatunku w bazie danych
            cursor.execute("SELECT id FROM gener WHERE gener_name = %s", (genre,))
            genre_id = cursor.fetchone()
            if genre_id is None:
                cursor.execute("INSERT INTO gener (gener_name) VALUES (%s) RETURNING id", (genre,))
                genre_id = cursor.fetchone()[0]

            else:
                genre_id = genre_id[0]
            cursor.execute("INSERT INTO movie_gener (movie_id, gener_id) VALUES (%s, %s)", (movie_id, genre_id))

        for actor in actor_list:
            actor_name, actor_surname = actor
            cursor.execute("SELECT id FROM actor WHERE name = %s AND surname = %s", (actor_name, actor_surname))
            actor_id = cursor.fetchone()
            if actor_id is None:
                cursor.execute("INSERT INTO actor (name, surname) VALUES (%s, %s) RETURNING id", (actor_name, actor_surname))
                actor_id = cursor.fetchone()[0]
            else:
                actor_id = actor_id[0]
            cursor.execute("INSERT INTO movie_actor (movie_id, actor_id) VALUES (%s, %s)", (movie_id, actor_id))

        conn.commit()
    except Exception as e:
        print("Wystąpił błąd podczas dodawania filmu:", str(e))
    
def rent_movie(
    username, movie_id, start_date, end_date, price
    ):
    cursor.execute("SELECT id FROM client WHERE username = %s", (username,))
    result = cursor.fetchone()
    client_id = result[0]

    if not movie_id:
        return False

    if not start_date:
        return False

    if not end_date:
        return False

    if not price:
        return False

    cursor.execute("INSERT INTO rent (client_id, movie_id, start_date, end_date, price, is_active) VALUES (%s, %s, %s, %s, %s, %s)",
                   (client_id, movie_id, start_date, end_date, price, True))
    cursor.execute("UPDATE movie SET count = count - 1 WHERE id = %s", (movie_id,))
    conn.commit()
    return True

def finish_selected_rents(user_rents):
    try:
        for rent in user_rents:
            rent_id = rent.get("id")
            if rent_id is not None:
                cursor.execute("UPDATE rent SET is_active = %s WHERE id = %s", (False, rent_id))
                conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")

class SimpleGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Movie Rental")
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        self.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.state("zoomed")

        self.switch_to_login()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.logged_user = None
        self.admin_logged_in = False

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

        self.logout_button = tk.Button(
            self, text="Logout", command=self.logout
        )
        self.logout_button.pack()
        self.back_to_main_button = tk.Button(
            self, text="Back to Main Page", command=self.switch_to_main_page
        )
        self.back_to_main_button.pack()

        self.my_rents_label = tk.Label(self, text="My Rents")
        self.my_rents_label.pack()
    
    def my_archived_rents_screen_setup(self):
        self.title("My Archived Rents")

        self.logout_button = tk.Button(
            self, text="Logout", command=self.logout
        )
        self.logout_button.pack()
        self.back_to_main_button = tk.Button(
            self, text="Back to Main Page", command=self.switch_to_main_page
        )
        self.back_to_main_button.pack()

        self.my_rents_label = tk.Label(self, text="My Archived Rents")
        self.my_rents_label.pack()

    def find_movie_screen_setup(self):
        self.title("Find Movie")
        self.logout_button = tk.Button(
            self, text="Logout", command=self.logout
        )
        self.logout_button.pack()

        self.back_to_main_button = tk.Button(
            self, text="Back to Main Page", command=self.switch_to_main_page
        )
        self.back_to_main_button.pack()

        self.find_movie_label = tk.Label(self, text="Find Movie")
        self.find_movie_label.pack()

    def create_rent_setup(self):
        self.title("Create Rent")
        self.logout_button = tk.Button(
            self, text="Logout", command=self.logout
        )
        self.logout_button.pack()
        self.back_to_main_button = tk.Button(
            self, text="Back to Main Page", command=self.switch_to_main_page
        )
        self.back_to_main_button.pack()

    def add_movie_setup(self):
        self.title("Add movie")
        self.logout_button = tk.Button(
            self, text="Logout", command=self.logout
        )
        self.logout_button.pack()
        self.back_to_main_button = tk.Button(
            self, text="Back to Main Page", command=self.switch_to_main_page
        )
        self.back_to_main_button.pack()

    def finish_rent_search_setup(self):
        self.title("Finish Rent")
        self.logout_button = tk.Button(
            self, text="Logout", command=self.logout
        )
        self.logout_button.pack()
        self.back_to_main_button = tk.Button(
            self, text="Back to Main Page", command=self.switch_to_main_page
        )
        self.back_to_main_button.pack()
        self.label_find_username = tk.Label(self, text="Username:")
        self.label_find_username.pack()
        self.entry_username = tk.Entry()
        self.entry_username.pack()
        self.fetch_rents_by_username_button = tk.Button(self, text="Find reservations", command=lambda: self.fetch_rents_by_username(self.entry_username.get()))
        self.fetch_rents_by_username_button.pack()

    def finish_rent_setup(self):
        self.title("Finish Rent")
        self.logout_button = tk.Button(
            self, text="Logout", command=self.logout
        )
        self.logout_button.pack()
        self.back_to_main_button = tk.Button(
            self, text="Back to Main Page", command=self.switch_to_main_page
        )
        self.back_to_main_button.pack()

    def view_logs_setup(self):
        self.title("Logs")

        self.logout_button = tk.Button(
            self, text="Logout", command=self.logout
        )
        self.logout_button.pack()
        self.back_to_main_button = tk.Button(
            self, text="Back to Main Page", command=self.switch_to_main_page
        )
        self.back_to_main_button.pack()

        self.my_rents_label = tk.Label(self, text="Users Activity")
        self.my_rents_label.pack()


    def main_page_setup(self):
        self.title("Main Page")
        self.logout_button = tk.Button(
            self, text="Logout", command=self.logout
        )
        self.logout_button.pack()

        self.my_rents_button = tk.Button(
            self, text="My Rents", command=self.switch_to_my_rents
        )
        self.my_rents_button.pack()

        self.my_archived_rents_button = tk.Button(
            self, text="My Archived Rents", command=self.switch_to_my_archived_rents
        )
        self.my_archived_rents_button.pack()

        self.find_movie_button = tk.Button(
            self, text="Find Movie", command=self.switch_to_find_movie
        )
        self.find_movie_button.pack()
        if self.admin_logged_in:
            self.finish_rent_button = tk.Button(
            self, text="Finish Rent", command=self.switch_to_finish_rent_search
            )
            self.finish_rent_button.pack()
            self.activity_view_button = tk.Button(
            self, text="View Activity", command=self.switch_to_view_logs
            )
            self.activity_view_button.pack()
            self.add_movie_button = tk.Button(
            self, text="Add movie", command=self.switch_to_add_movie
            )
            self.add_movie_button.pack()

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

    def switch_to_my_archived_rents(self):
        self.close_all_windows()
        self.my_archived_rents_screen_setup()
        self.fetch_archived_rents()

    def switch_to_find_movie(self):
        self.close_all_windows()
        self.find_movie_screen_setup()
        self.fetch_movies()

    def switch_to_main_page(self):
        self.close_all_windows()
        self.main_page_setup()

    def switch_to_finish_rent_search(self):
        self.close_all_windows()
        self.finish_rent_search_setup()

    def switch_to_finish_rent(self):
        self.close_all_windows()
        self.finish_rent_setup()

    def switch_to_add_movie(self):
        self.close_all_windows()
        self.add_movie_setup()
        self.add_movie()

    def switch_to_view_logs(self):
        self.close_all_windows()
        self.view_logs_setup()
        self.fetch_logs()

    def switch_to_create_rent(self, selected_movies):
        self.close_all_windows()
        self.create_rent_setup()
        self.create_rent(selected_movies)

    def close_all_windows(self):
        for widget in self.winfo_children():
            widget.destroy()

    ## Calls ##
    def login_user(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        error_label = self.error_label

        result = login_user(username, password, error_label)
        if result:
            self.logged_user = username
            self.admin_logged_in =  is_user_admin(username, password, error_label)
            self.switch_to_main_page()
            

    def register_user(self):
        username = self.register_entry_username.get()
        password = self.register_entry_password.get()
        name = self.register_entry_name.get()
        surname = self.register_entry_surname.get()

        error_label = self.error_label

        result = register_user(
            username, password, name, surname, error_label
        )
        if result:
            self.register_entry_username.delete(0, tk.END)
            self.register_entry_password.delete(0, tk.END)
            self.register_entry_name.delete(0, tk.END)
            self.register_entry_surname.delete(0, tk.END)
            self.switch_to_login()

    def fetch_rents(self):
        reservations = get_user_reservations(self.logged_user)
        listbox = tk.Listbox(self, width=100, height=20)
        if reservations:
            for i, reservation in enumerate(reservations):
                listbox.insert(tk.END, f"Movie: {reservation['movie_title']} | Start Date: {reservation['start_date']} | End Date: {reservation['end_date']} | Price: {reservation['price']}")
        else:
            listbox.insert(tk.END, "No reservations found.")
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)
    
    def fetch_archived_rents(self):
        reservations = get_user_archived_reservations(self.logged_user)
        listbox = tk.Listbox(self, width=100, height=20)
        if reservations:
            for i, reservation in enumerate(reservations):
                listbox.insert(tk.END, f"Movie: {reservation['movie_title']} | Start Date: {reservation['start_date']} | End Date: {reservation['end_date']} | Price: {reservation['price']}")
        else:
            listbox.insert(tk.END, "No reservations found.")
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)

    def fetch_logs(self):
        activities = get_users_activity()
        listbox = tk.Listbox(self, width=100, height=20)
        if activities:
            for i, activity in enumerate(activities):
                listbox.insert(tk.END, f"Activity {i+1}: Time: {activity['activity_time']} Client Name: {activity['client_name']} {activity['client_surname']} Username: {activity['client_username']} Action Type: {activity['action_type']} Client Role: {activity['client_role']}")
        else:
            listbox.insert(tk.END, "No activity found.")
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)


    def fetch_movies(self):
        def update_movies_list(*args):
            title_search_text = self.entry_fields[0].get()
            producer_search_text = self.entry_fields[1].get()
            director_search_text = self.entry_fields[2].get()
            year_search_text = self.entry_fields[3].get()
            actor_search_text = self.entry_fields[4].get()

            self.movies = get_movies(
                title_search_text,
                producer_search_text,
                director_search_text,
                year_search_text,
                actor_search_text,
            )
            self.listbox.delete(0, tk.END)
            
            if self.movies:
                columns = ["Title", "Count", "Producer", "Director", "Year", "Actors"]
                header = "{:<100} | {:<50} | {:<50} | {:<10} | {:<100}".format(*columns)
                self.listbox.insert(tk.END, header)
                self.listbox.insert(tk.END, "-" * len(header))

                for movie in self.movies:
                    title = movie['title']
                    count = movie['count']
                    year = movie['year']
                    producer = movie['producer_name']
                    director = movie['director_name'] + " " + movie['director_surname']
                    actors = ", ".join([f"{actor['name']} {actor['surname']}" for actor in movie["actors"]])
                    row = "{:<100} | {:<5} | {:<50} | {:<50} | {:<10} | {:<100}".format(title, count, producer, director, year, actors)
                    self.listbox.insert(tk.END, row)
            else:
                self.listbox.insert(tk.END, "No movies found.")

        def on_search_change(*args):
            update_movies_list()
            
        column_labels = ["Title:", "Producer:", "Director:", "Year:", "Actor:"]
        self.entry_fields = []
        for label_text in column_labels:
            label = tk.Label(self, text=label_text, width=20, anchor=tk.W)
            label.pack()
            entry = tk.Entry(self, width=20)
            entry.pack()
            entry.bind("<KeyRelease>", on_search_change)
            self.entry_fields.append(entry)
    
        self.create_rent_button = tk.Button(
            self, text="Create Rent", command=self.select_movies_to_create_rent
        )
        self.create_rent_button.pack()
        self.listbox = tk.Listbox(self, selectmode=tk.MULTIPLE, width=1000, height=600)
        self.listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        update_movies_list()

        
    def create_rent(self, selected_movies):
        self.start_date_label = tk.Label(self, text="Start Date:")
        self.start_date_label.pack()

        # Field populated with current date
        self.start_date_var = tk.StringVar()
        self.start_date_var.set(datetime.today().strftime('%Y-%m-%d'))  # Populate with current date
        self.start_date_label = tk.Label(textvariable=self.start_date_var)
        self.start_date_label.pack()

        self.end_date_label = tk.Label(self, text="End Date:")
        self.end_date_label.pack()

        # Field where date can be chosen from a calendar
        self.end_date_var = DateEntry(date_pattern='yyyy-mm-dd')
        self.end_date_var.pack()
        self.end_date_var.bind("<<DateEntrySelected>>", self.update_rental_price)

        self.price_label = tk.Label(self, text="Rental Price: $0")
        self.price_label.pack()
        self.update_rental_price()

        # Display selected movie titles
        selected_movies_text = "\n".join([movie["title"] for movie in selected_movies])
        self.selected_movies_label = tk.Label(self, text="Selected Movies:")
        self.selected_movies_label.pack()
        self.selected_movies_text = tk.Text(self, width=50, height=5)
        self.selected_movies_text.insert(tk.END, selected_movies_text)
        self.selected_movies_text.pack()

        # Button to create rent
        self.create_rent_button = tk.Button(self, text="Create Rent", command=lambda: self.create_rent_action(selected_movies))
        self.create_rent_button.pack()

    def update_rental_price(self, event=None):
        start_date = datetime.strptime(self.start_date_var.get(), '%Y-%m-%d')
        end_date = datetime.strptime(self.end_date_var.get(), '%Y-%m-%d')
        difference = (end_date - start_date).days
        price = 2 * difference
        if price <= 0:
            price = 1
        self.price_label.config(text=f"Rental Price: ${price}")

    def create_rent_action(self, selected_movies):
        # Retrieve start and end dates
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        current_time = datetime.now().time()
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        start_datetime = start_datetime.replace(hour=current_time.hour, minute=current_time.minute, second=current_time.second)
        end_datetime = end_datetime.replace(hour=current_time.hour, minute=current_time.minute+1, second=current_time.second)
        formatted_start_date = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
        formatted_end_date = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        days_rented = (end_datetime - start_datetime).days
        price = days_rented * 2
        if price == 0:
            price = 1
        username = self.logged_user
        for movie in selected_movies:
            movie_id = movie['id']
            rent_movie(username, movie_id, formatted_start_date, formatted_end_date, price)
        self.switch_to_my_rents()

    def fetch_rents_by_username(self, username):
        self.switch_to_finish_rent()
        self.users_rents = get_user_reservations(username)
        self.finish_rent_button = tk.Button(self, text="Finish Selected Rents", command=self.finish_rent_action)
        self.finish_rent_button.pack()
        self.listbox = tk.Listbox(self, selectmode=tk.MULTIPLE, width=1000, height=600)
        if self.users_rents:
            columns = ["Name", "Surname", "Movie Title", "Start Date", "End Date", "Price", "Delayed"]
            header = "{:<50} | {:<50} | {:<100} | {:<50} | {:<50} | {:<5} | {:<15}".format(*columns)
            self.listbox.insert(tk.END, header)
            self.listbox.insert(tk.END, "-" * len(header))

            for rent in self.users_rents:
                name = rent['name']
                surname = rent['surname']
                start_date = rent['start_date']
                start_date_display = start_date.strftime('%Y-%m-%d %H:%M:%S')
                end_date = rent['end_date']
                end_date_display = end_date.strftime('%Y-%m-%d %H:%M:%S')
                title = rent['movie_title']
                price = rent['price']
                current_datetime = datetime.now()
                if end_date < current_datetime:
                    delayed = "Delayed"
                else:
                    delayed = "On time"
                row = "{:<50} | {:<50} | {:<100} | {:<50} | {:<50} | {:<5} | {:<15}".format(name, surname, title, start_date_display, end_date_display, price, delayed)
                self.listbox.insert(tk.END, row)
        else:
            self.listbox.insert(tk.END, "No rents found.")
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        
    def add_movie(self):
        labels = [
            "title", "year", "producer name", "director name", "director surname", "count",
            "genre 1", "genre 2", "genre 3", "actor name 1", "actor surname 1",
            "actor name 2", "actor surname 2", "actor name 3", "actor surname 3"
        ]
        self.entry_fields = []

        for label_text in labels:
            label = tk.Label(self, text=label_text, width=20, anchor=tk.W)
            label.pack()
            entry = tk.Entry(self, width=20)
            entry.pack()
            self.entry_fields.append(entry)

        def add_movie_click():
            title = self.entry_fields[0].get()
            year = self.entry_fields[1].get()
            producer_name = self.entry_fields[2].get()
            director_name = self.entry_fields[3].get()
            director_surname = self.entry_fields[4].get()
            count = self.entry_fields[5].get()

            genre_list = [entry.get() for entry in self.entry_fields[6:9] if entry.get()]

            actors = [(self.entry_fields[i].get(), self.entry_fields[i+1].get()) for i in range(9, 15, 2) if self.entry_fields[i].get()]

            add_movie(title, year, producer_name, director_name, director_surname, count, genre_list, actors)
            self.switch_to_main_page()

        add_movie_button = tk.Button(self, text="Dodaj film", command=add_movie_click)
        add_movie_button.pack()

    # Other
    def select_movies_to_create_rent(self):
        selected_indices = self.listbox.curselection()
        selected_movies = [self.movies[i-2] for i in selected_indices]
        self.switch_to_create_rent(selected_movies)

    def finish_rent_action(self):
        selected_indices = self.listbox.curselection()
        selected_rents = [self.users_rents[i-2] for i in selected_indices]
        finish_selected_rents(selected_rents)
        self.switch_to_main_page()


    def on_closing(self):
        try:
            conn.close()
        finally:
            self.destroy()

    def logout(self):
        try:
            self.logged_user = None
        finally:
            self.switch_to_login()



if __name__ == "__main__":
    app = SimpleGUI()
    app.mainloop()
