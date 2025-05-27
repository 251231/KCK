import json
import os
import hashlib

# Ścieżka do bazy danych użytkowników
USERS_DB_PATH = "../DataBase/users.json"

def hash_password(password):
    """
    Zwraca SHA256 hash hasła.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """
    Wczytuje dane użytkowników z pliku JSON.
    """
    if os.path.exists(USERS_DB_PATH):
        with open(USERS_DB_PATH, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    """
    Zapisuje dane użytkowników do pliku JSON.
    """
    with open(USERS_DB_PATH, "w") as f:
        json.dump(users, f, indent=4)

def register_user(username, password):
    """
    Rejestruje nowego użytkownika z zahashowanym hasłem.
    Zwraca True, jeśli sukces, False jeśli użytkownik istnieje.
    """
    users = load_users()
    if username in users:
        return False  # użytkownik już istnieje
    users[username] = {
        "password": hash_password(password)
    }
    save_users(users)
    return True

def authenticate_user(username, password):
    """
    Sprawdza poprawność loginu i hasła.
    Zwraca True jeśli dane są poprawne.
    """
    users = load_users()
    hashed = hash_password(password)
    return users.get(username, {}).get("password") == hashed
