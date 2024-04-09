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

class SimpleGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Movie Rental")
        self.geometry("300x200")

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
        self.login_screen.geometry("300x200")

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
        self.register_screen.geometry("300x200")

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
        self.my_rents_screen.geometry("300x200")

        self.my_rents_label = tk.Label(self.my_rents_screen, text="My Rents")
        self.my_rents_label.pack()
        self.my_rents_screen.protocol("WM_DELETE_WINDOW", self.on_closing)

    def find_movie_screen_setup(self):
        self.find_movie_screen = tk.Toplevel(self)
        self.find_movie_screen.title("Find Movie")
        self.find_movie_screen.geometry("300x200")

        self.find_movie_label = tk.Label(self.find_movie_screen, text="Find Movie")
        self.find_movie_label.pack()
        self.find_movie_screen.protocol("WM_DELETE_WINDOW", self.on_closing)

    def main_page_setup(self):
        self.main_page_screen = tk.Toplevel(self)
        self.main_page_screen.title("Main Page")
        self.main_page_screen.geometry("300x200")

        self.my_rents_button = tk.Button(self.main_page_screen, text="My Rents", command=self.show_my_rents)
        self.my_rents_button.pack()

        self.find_movie_button = tk.Button(self.main_page_screen, text="Find Movie", command=self.show_find_movie)
        self.find_movie_button.pack()
        self.main_page_screen.protocol("WM_DELETE_WINDOW", self.on_closing)

    ## Switches ##
    def switch_to_register(self):
        self.login_screen.withdraw()
        self.register_screen.deiconify()

    def switch_to_login(self):
        self.register_screen.withdraw()
        self.login_screen.deiconify()
    
    def show_my_rents(self):
        self.main_page_screen.withdraw()
        self.my_rents_screen.deiconify()

    def show_find_movie(self):
        self.main_page_screen.withdraw()
        self.find_movie_screen.deiconify()

    def switch_to_main_page(self):
        self.login_screen.withdraw()
        self.main_page_screen.deiconify()

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
    
    # Other
    def on_closing(self):
        try:
            conn.close()
        finally:
            self.destroy()


if __name__ == "__main__":
    app = SimpleGUI()
    app.mainloop()


