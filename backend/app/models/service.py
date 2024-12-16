# Model pentru gestionarea serviciilor
# Oferă funcționalități CRUD pentru serviciile disponibile în aplicație

from app.utils.db import get_db

class Service:
    @staticmethod
    def get_all():
        """
        Preia toate serviciile din baza de date
        
        Returns:
            list: Lista de servicii, fiecare serviciu fiind un dicționar
                  cu proprietățile: id, name, description, price, etc.
                  și category_name din join-ul cu tabelul categories
        """
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''
                SELECT s.*, c.name as category_name 
                FROM services s
                JOIN categories c ON s.category_id = c.id
            ''')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Eroare la preluarea serviciilor: {str(e)}")
            return []

    @staticmethod
    def get_by_id(service_id):
        """
        Preia un serviciu specific după ID
        
        Args:
            service_id (int): ID-ul serviciului căutat
            
        Returns:
            dict: Datele serviciului sau None dacă nu este găsit
        """
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''
                SELECT s.*, c.name as category_name 
                FROM services s
                JOIN categories c ON s.category_id = c.id
                WHERE s.id = ?
            ''', (service_id,))
            service = cursor.fetchone()
            return dict(service) if service else None
        except Exception as e:
            print(f"Eroare la preluarea serviciului: {str(e)}")
            return None

    @staticmethod
    def create(name, description, price, category_id, start_time='09:00', end_time='17:00', interval=30):
        """
        Creează un serviciu nou
        
        Args:
            name (str): Numele serviciului
            description (str): Descrierea serviciului
            price (float): Prețul serviciului
            category_id (int): ID-ul categoriei
            start_time (str): Ora de început a programului (format: HH:MM)
            end_time (str): Ora de sfârșit a programului (format: HH:MM)
            interval (int): Durata serviciului în minute
            
        Returns:
            int: ID-ul serviciului creat sau None în caz de eroare
        """
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Verify category exists
            cursor.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
            if not cursor.fetchone():
                print(f"Category {category_id} not found")
                return None
            
            cursor.execute('''
                INSERT INTO services 
                (category_id, name, description, price, start_time, end_time, interval)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (category_id, name, description, price, start_time, end_time, interval))
            
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating service: {str(e)}")
            db.rollback()
            return None

    @staticmethod
    def delete(service_id):
        """
        Șterge un serviciu din baza de date
        
        Args:
            service_id (int): ID-ul serviciului de șters
            
        Returns:
            bool: True dacă ștergerea a reușit, False în caz contrar
        """
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('DELETE FROM services WHERE id = ?', (service_id,))
            db.commit()
            return True
        except Exception as e:
            print(f"Eroare la ștergerea serviciului: {str(e)}")
            db.rollback()
            return False

    @staticmethod
    def update(service_id, name, description, price, category_id, start_time, end_time, interval):
        """
        Actualizează datele unui serviciu existent
        
        Args:
            service_id (int): ID-ul serviciului de actualizat
            name (str): Noul nume
            description (str): Noua descriere
            price (float): Noul preț
            category_id (int): ID-ul noii categorii
            start_time (str): Noua oră de început
            end_time (str): Noua oră de sfârșit
            interval (int): Noul interval în minute
            
        Returns:
            bool: True dacă actualizarea a reușit, False în caz contrar
        """
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Verify category exists
            cursor.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
            if not cursor.fetchone():
                print(f"Category {category_id} not found")
                return False
            
            cursor.execute('''
                UPDATE services 
                SET category_id = ?, name = ?, description = ?, price = ?, 
                    start_time = ?, end_time = ?, interval = ?
                WHERE id = ?
            ''', (category_id, name, description, price, start_time, end_time, interval, service_id))
            
            db.commit()
            return True
        except Exception as e:
            print(f"Error updating service: {str(e)}")
            db.rollback()
            return False