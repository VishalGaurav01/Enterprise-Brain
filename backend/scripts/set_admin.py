import os
import sys

# Add the backend directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
import bcrypt

def set_admin():
    db_url = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@db:5432/brain")
    engine = create_engine(db_url)
    
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(b"admin123", salt).decode("utf-8")
    
    with engine.begin() as conn:
        # Check if users table exists
        # Update the first user to be admin@example.com
        result = conn.execute(text("SELECT id FROM users LIMIT 1"))
        first_user = result.fetchone()
        
        if first_user:
            user_id = first_user[0]
            conn.execute(text("""
                UPDATE users 
                SET email = 'admin@example.com', 
                    username = 'Admin User',
                    hashed_password = :pwd,
                    status = 'Active'
                WHERE id = :uid
            """), {"pwd": hashed_pwd, "uid": user_id})
            print("Successfully updated an existing user to admin credentials.")
        else:
            print("No users found in database.")

if __name__ == "__main__":
    set_admin()
