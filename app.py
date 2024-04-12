import tkinter as tk
import sqlite3
import bcrypt

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
      INNER JOIN movies m ON r.movie_id = m.id
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
        SELECT m.id, m.title, m.category, m.year, m.producer_id, m.director_id, m.count, 
            a.id AS actor_id, a.name AS actor_name, a.surname AS actor_surname
        FROM movies m
        LEFT JOIN movies_actors ma ON m.id = ma.movie_id
        LEFT JOIN actors a ON ma.actor_id = a.id
        ORDER BY m.title
        """
        )
        rows = cursor.fetchall()
        movies = {}
        for row in rows:
            (
                movie_id,
                title,
                category,
                year,
                producer_id,
                director_id,
                count,
                actor_id,
                actor_name,
                actor_surname,
            ) = row
            if movie_id not in movies:
                movies[movie_id] = {
                    "id": movie_id,
                    "title": title,
                    "category": category,
                    "year": year,
                    "producer_id": producer_id,
                    "director_id": director_id,
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
        if movies:
            for i, movie in enumerate(movies):
                label_text = f"Title: {movie['title']} | Category: {movie['category']} | Year: {movie['year']} | Actors: "
                actors_text = ", ".join(
                    [f"{actor['name']} {actor['surname']}" for actor in movie["actors"]]
                )
                label_text += actors_text
                tk.Label(self, text=label_text).pack()
        else:
            tk.Label(self, text="No movies found.").pack()

    # Other
    def on_closing(self):
        try:
            conn.close()
        finally:
            self.destroy()


if __name__ == "__main__":
    app = SimpleGUI()
    app.mainloop()
