from app.utils.db import get_db
import bcrypt

class User:
    @staticmethod
    def create(username, email, password):
        db = get_db()
        cursor = db.cursor()
        
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute(
            'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
            (username, email, hashed.decode('utf-8'))
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_by_email(email):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        if user:
            print(f"Found user in DB: {dict(user)}")  # Debug print
        return user

    @staticmethod
    def verify_password(stored_password, provided_password):
        print(f"Verifying password: {provided_password}")  # Debug print
        try:
            result = bcrypt.checkpw(
                provided_password.encode('utf-8'),
                stored_password.encode('utf-8')
            )
            print(f"Password verification result: {result}")  # Debug print
            return result
        except Exception as e:
            print(f"Password verification error: {str(e)}")  # Debug print
            return False