import threading
import psycopg2

lock = threading.Lock()


def reset_db_values():
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute("UPDATE showcase.counters SET value = 0")

    cur.close()
    conn.close()


def print_db_values():
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    conn.autocommit = True

    return_values = []
    print("\nValues in the database:")
    cur = conn.cursor()
    cur.execute("SELECT counter_id, value FROM showcase.counters ORDER BY counter_id")
    for counter_id, value in cur.fetchall():
        print(f"\tCounter id: {counter_id}, value: {value}")
        return_values.append({counter_id: value})
    cur.close()
    conn.close()
    return return_values


def increase_db_values(counter_id):
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute("SELECT value FROM showcase.counters WHERE counter_id = %s", (counter_id,))
    value = cur.fetchone()[0]
    cur.execute("UPDATE showcase.counters SET value = %s WHERE counter_id = %s", (value + 1, counter_id))
    cur.close()
    conn.close()


def increase_db_values_locking(counter_id):
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    conn.autocommit = True

    with lock:
        cur = conn.cursor()
        cur.execute("SELECT value FROM showcase.counters WHERE counter_id = %s", (counter_id,))
        value = cur.fetchone()[0]
        cur.execute("UPDATE showcase.counters SET value = %s WHERE counter_id = %s", (value + 1, counter_id))
        cur.close()
    conn.close()
