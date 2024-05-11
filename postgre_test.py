import psycopg2

# Połącz się z bazą danych
conn = psycopg2.connect(
    dbname="moja_baza_danych",
    user="postgres",
    password="1234",
    host="localhost"
)

# Utwórz kursor do wykonywania operacji SQL
cur = conn.cursor()

# Utwórz nową tabelę
cur.execute("CREATE TABLE customers (id SERIAL PRIMARY KEY, name VARCHAR, address VARCHAR)")

# Dodaj wpis do tabeli
cur.execute("INSERT INTO customers (name, address) VALUES (%s, %s)", ("John", "Highway 21"))

# Zatwierdź zmiany
conn.commit()

print("1 record inserted.")

# Zamknij połączenie
cur.close()
conn.close()