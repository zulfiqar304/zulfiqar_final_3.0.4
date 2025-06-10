
from main import app, db, User
from flask import session
import sqlite3

def make_user_admin():
    # Get all users to see who to make admin
    db_path = 'instance/users.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Current users:")
    cursor.execute("SELECT id, username, email, is_admin FROM user")
    users = cursor.fetchall()
    
    for user in users:
        print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Is Admin: {user[3]}")
    
    user_id = input("\nEnter the ID of the user you want to make admin: ")
    
    try:
        cursor.execute("UPDATE user SET is_admin = 1 WHERE id = ?", (user_id,))
        conn.commit()
        print(f"User with ID {user_id} is now an admin!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    make_user_admin()
