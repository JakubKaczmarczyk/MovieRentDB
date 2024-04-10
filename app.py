import tkinter as tk
import sqlite3

# Database connection (replace with your database path)
conn = sqlite3.connect("movie_rental.db")
cursor = conn.cursor()


def login_user(username_entry, password_entry, error_label):
    username = username_entry.get()
    password = password_entry.get()

    if not username:
        error_label.config(text="Username cannot be empty")
        return False

    if not password:
        error_label.config(text="Password cannot be empty")
        return False

    # Check username and password in database
    cursor.execute(
        f"SELECT * FROM client WHERE username = ? AND password = ?",
        (username, password)
    )
    user = cursor.fetchone()

    if user:
        return True
    else:
        error_label.config(text="Invalid username or password")
        return False

def register_user(username_entry, password_entry, name_entry, surname_entry, error_label):
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

    cursor.execute(
        f"INSERT INTO client (username, password, name, surname, last_logged_in) VALUES ('{username}', '{password}', '{name}', '{surname}', NULL)"
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
          "price": row[3]
      }
      reservations.append(reservation)
    return reservations
  except Exception as e:
    print(f"An error occurred: {e}")
    return []
  
def get_movies():
    try:
        cursor.execute("""
        SELECT m.id, m.title, m.category, m.year, m.producer_id, m.director_id, m.count, 
            a.id AS actor_id, a.name AS actor_name, a.surname AS actor_surname
        FROM movies m
        LEFT JOIN movies_actors ma ON m.id = ma.movie_id
        LEFT JOIN actors a ON ma.actor_id = a.id
        ORDER BY m.title
        """)
        rows = cursor.fetchall()
        movies = {}
        for row in rows:
            movie_id, title, category, year, producer_id, director_id, count, actor_id, actor_name, actor_surname = row
            if movie_id not in movies:
                movies[movie_id] = {
                    "id": movie_id,
                    "title": title,
                    "category": category,
                    "year": year,
                    "producer_id": producer_id,
                    "director_id": director_id,
                    "count": count,
                    "actors": []
                }
            if actor_id:
                movies[movie_id]["actors"].append({"id": actor_id, "name": actor_name, "surname": actor_surname})
        movie_list = list(movies.values())
        return movie_list
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

class SimpleGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.width = 1200
        self.height = 600
        self.title("Movie Rental")
        self.geometry(f"{self.width}x{self.height}+0+0")

        self.login_screen_setup()
        self.register_screen_setup()
        self.my_rents_screen_setup()
        self.find_movie_screen_setup()
        self.main_page_setup()
        self.main_page_screen.withdraw()
        self.my_rents_screen.withdraw()
        self.find_movie_screen.withdraw()

        self.switch_to_login()
        self.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.logged_user = None

    ## Screens ##
    def login_screen_setup(self):
        self.login_screen = tk.Toplevel(self)
        self.login_screen.title("Movie Rental Login")
        self.login_screen.geometry(f"{self.width}x{self.height}+0+0")

        self.login_label_username = tk.Label(self.login_screen, text="Username:")
        self.login_label_username.pack()

        self.entry_username = tk.Entry(self.login_screen)
        self.entry_username.pack()

        self.login_label_password = tk.Label(self.login_screen, text="Password:")
        self.login_label_password.pack()

        self.entry_password = tk.Entry(self.login_screen, show="*")
        self.entry_password.pack()

        self.login_button = tk.Button(self.login_screen, text="Login", command=self.login_user)
        self.login_button.pack()

        self.register_button = tk.Button(self.login_screen, text="Register", command=self.switch_to_register)
        self.register_button.pack()

        self.error_label = tk.Label(self.login_screen, text="")
        self.error_label.pack()
        self.login_screen.protocol("WM_DELETE_WINDOW", self.on_closing)

    def register_screen_setup(self):
        self.register_screen = tk.Toplevel(self)
        self.register_screen.title("Movie Rental Register")
        self.register_screen.geometry(f"{self.width}x{self.height}+0+0")

        self.register_label_username = tk.Label(self.register_screen, text="Username:")
        self.register_label_username.pack()

        self.register_entry_username = tk.Entry(self.register_screen)
        self.register_entry_username.pack()

        self.register_label_password = tk.Label(self.register_screen, text="Password:")
        self.register_label_password.pack()

        self.register_entry_password = tk.Entry(self.register_screen, show="*")
        self.register_entry_password.pack()

        self.register_label_name = tk.Label(self.register_screen, text="Name:")
        self.register_label_name.pack()

        self.register_entry_name = tk.Entry(self.register_screen)
        self.register_entry_name.pack()

        self.register_label_surname = tk.Label(self.register_screen, text="Surname:")
        self.register_label_surname.pack()

        self.register_entry_surname = tk.Entry(self.register_screen)
        self.register_entry_surname.pack()

        self.register_button = tk.Button(self.register_screen, text="Register", command=self.register_user)
        self.register_button.pack()

        self.back_to_login_button = tk.Button(self.register_screen, text="Back to Login", command=self.switch_to_login)
        self.back_to_login_button.pack()
        self.register_screen.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def my_rents_screen_setup(self):
        self.my_rents_screen = tk.Toplevel(self)
        self.my_rents_screen.title("My Rents")
        self.my_rents_screen.geometry(f"{self.width}x{self.height}+0+0")

        self.back_to_main_button = tk.Button(self.my_rents_screen, text="Back to Main Page", command=self.switch_to_main_page)
        self.back_to_main_button.pack()

        self.my_rents_label = tk.Label(self.my_rents_screen, text="My Rents")
        self.my_rents_label.pack()
        self.my_rents_screen.protocol("WM_DELETE_WINDOW", self.on_closing)

    def find_movie_screen_setup(self):
        self.find_movie_screen = tk.Toplevel(self)
        self.find_movie_screen.title("Find Movie")
        self.find_movie_screen.geometry(f"{self.width}x{self.height}+0+0")

        self.back_to_main_button = tk.Button(self.find_movie_screen, text="Back to Main Page", command=self.switch_to_main_page)
        self.back_to_main_button.pack()

        self.find_movie_label = tk.Label(self.find_movie_screen, text="Find Movie")
        self.find_movie_label.pack()
        self.find_movie_screen.protocol("WM_DELETE_WINDOW", self.on_closing)

    def main_page_setup(self):
        self.main_page_screen = tk.Toplevel(self)
        self.main_page_screen.title("Main Page")
        self.main_page_screen.geometry(f"{self.width}x{self.height}+0+0")

        self.my_rents_button = tk.Button(self.main_page_screen, text="My Rents", command=self.show_my_rents)
        self.my_rents_button.pack()

        self.find_movie_button = tk.Button(self.main_page_screen, text="Find Movie", command=self.show_find_movie)
        self.find_movie_button.pack()
        self.main_page_screen.protocol("WM_DELETE_WINDOW", self.on_closing)

    ## Switches ##
    def switch_to_register(self):
        self.close_all_windows()
        self.register_screen.deiconify()

    def switch_to_login(self):
        self.close_all_windows()
        self.login_screen.deiconify()
    
    def show_my_rents(self):
        self.close_all_windows()
        self.my_rents_screen.deiconify()
        for widget in self.my_rents_screen.winfo_children():
            if widget.cget("text") != "Back to Main Page":
                widget.destroy()
        self.fetch_rents()

    def show_find_movie(self):
        self.close_all_windows()
        self.find_movie_screen.deiconify()
        for widget in self.find_movie_screen.winfo_children():
            if widget.cget("text") != "Back to Main Page":
                widget.destroy()
        self.fetch_movies()

    def switch_to_main_page(self):
        self.close_all_windows()
        self.main_page_screen.deiconify()

    def close_all_windows(self):
        if self.login_screen.winfo_exists():
            self.login_screen.withdraw()
        if self.register_screen.winfo_exists():
            self.register_screen.withdraw()
        if self.main_page_screen.winfo_exists():
            self.main_page_screen.withdraw()
        if self.find_movie_screen.winfo_exists():
            self.find_movie_screen.withdraw()
        if self.my_rents_screen.winfo_exists():
            self.my_rents_screen.withdraw()

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

        result = register_user(username_entry, password_entry, name_entry, surname_entry, error_label)
        if result:
            # If registration successful, hide the register screen and switch to login screen
            self.register_screen.withdraw()
            self.switch_to_login()

    def fetch_rents(self):
        reservations = get_user_reservations(self.logged_user)
        if reservations:
            for i, reservation in enumerate(reservations):
                label_text = f"Movie: {reservation['movie_title']} | Start Date: {reservation['start_date']} | End Date: {reservation['end_date']} | Price: {reservation['price']}"
                tk.Label(self.my_rents_screen, text=label_text).pack()
        else:
            tk.Label(self.my_rents_screen, text="No reservations found.").pack()
    
    def fetch_movies(self):
        movies = get_movies()
        if movies:
            for i, movie in enumerate(movies):
                label_text = f"Title: {movie['title']} | Category: {movie['category']} | Year: {movie['year']} | Actors: "
                actors_text = ", ".join([f"{actor['name']} {actor['surname']}" for actor in movie['actors']])
                label_text += actors_text
                tk.Label(self.find_movie_screen, text=label_text).pack()
        else:
            tk.Label(self.find_movie_screen, text="No movies found.").pack()

    # Other
    def on_closing(self):
        try:
            conn.close()
        finally:
            self.destroy()


if __name__ == "__main__":
    app = SimpleGUI()
    app.mainloop()


