# Model pentru gestionarea programului de funcționare
# Oferă funcționalități pentru citirea și actualizarea programului general al clinicii

from app.utils.db import get_db

class BusinessHours:
    @staticmethod
    def get():
        """
        Preia programul de funcționare curent
        
        Returns:
            dict: Dicționar cu orele de funcționare:
                - start_time: ora de început (format: HH:MM)
                - end_time: ora de sfârșit (format: HH:MM)
                - interval: durata unei programări în minute
        """
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''
                SELECT start_time, end_time, interval
                FROM business_hours
                LIMIT 1
            ''')
            
            hours = cursor.fetchone()
            return dict(hours) if hours else {
                'start_time': '09:00',
                'end_time': '17:00',
                'interval': 30
            }
        except Exception as e:
            print(f"Eroare la preluarea programului: {str(e)}")
            # Returnează valori implicite în caz de eroare
            return {
                'start_time': '09:00',
                'end_time': '17:00',
                'interval': 30
            }

    @staticmethod
    def update(start_time, end_time, interval):
        """
        Actualizează programul de funcționare
        
        Args:
            start_time (str): Ora de început (format: HH:MM)
            end_time (str): Ora de sfârșit (format: HH:MM)
            interval (int): Durata unei programări în minute
            
        Returns:
            bool: True dacă actualizarea a reușit, False în caz contrar
        """
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Verifică dacă există deja un program setat
            cursor.execute('SELECT COUNT(*) as count FROM business_hours')
            count = cursor.fetchone()['count']
            
            if count > 0:
                # Actualizează programul existent
                cursor.execute('''
                    UPDATE business_hours 
                    SET start_time = ?, end_time = ?, interval = ?
                ''', (start_time, end_time, interval))
            else:
                # Inserează program nou
                cursor.execute('''
                    INSERT INTO business_hours (start_time, end_time, interval)
                    VALUES (?, ?, ?)
                ''', (start_time, end_time, interval))
            
            db.commit()
            return True
        except Exception as e:
            print(f"Eroare la actualizarea programului: {str(e)}")
            db.rollback()
            return False 