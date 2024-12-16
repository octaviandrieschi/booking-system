# Model pentru gestionarea programărilor
# Oferă funcționalități pentru crearea, citirea, anularea și verificarea disponibilității programărilor

from app.utils.db import get_db
from datetime import datetime, timedelta
import pytz
from app.models.business_hours import BusinessHours

class Appointment:
    @staticmethod
    def create(user_id, service_id, date_time, db=None):
        """
        Creează o programare nouă
        
        Args:
            user_id (int): ID-ul utilizatorului
            service_id (int): ID-ul serviciului
            date_time (str): Data și ora programării (format: YYYY-MM-DD HH:MM)
            db: Conexiunea la baza de date (opțional)
            
        Returns:
            int: ID-ul programării create
            
        Raises:
            ValueError: Dacă datele nu sunt valide sau intervalul nu este disponibil
        """
        try:
            if db is None:
                db = get_db()
            cursor = db.cursor()
            
            # Verificăm dacă serviciul există și obținem intervalul
            cursor.execute('''
                SELECT id, interval, start_time, end_time
                FROM services 
                WHERE id = ?
            ''', (service_id,))
            
            service = cursor.fetchone()
            if not service:
                raise ValueError('Serviciul selectat nu există')
            
            # Convertim data_time la datetime pentru verificări
            try:
                appointment_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M")
            except ValueError:
                raise ValueError('Format dată invalid. Folosiți formatul: YYYY-MM-DD HH:MM')
            
            current_time = datetime.now()
            
            # Verificăm dacă data este în trecut
            if appointment_time <= current_time:
                raise ValueError('Nu se pot face programări în trecut')
            
            # Verificăm dacă ora este în intervalul de lucru al serviciului
            appointment_hour = appointment_time.strftime("%H:%M")
            if appointment_hour < service['start_time'] or appointment_hour >= service['end_time']:
                raise ValueError(f"Ora selectată ({appointment_hour}) este în afara programului de lucru ({service['start_time']}-{service['end_time']})")
            
            # Verificăm dacă data și ora sunt disponibile
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM appointments 
                WHERE service_id = ? 
                AND date_time = ? 
                AND status IS NULL
            ''', (service_id, date_time))
            
            if cursor.fetchone()['count'] > 0:
                raise ValueError('Intervalul selectat nu este disponibil')
            
            # Inserăm programarea
            cursor.execute('''
                INSERT INTO appointments (user_id, service_id, date_time)
                VALUES (?, ?, ?)
            ''', (user_id, service_id, date_time))
            
            return cursor.lastrowid
            
        except ValueError as e:
            raise
        except Exception as e:
            print(f"Eroare la crearea programării: {str(e)}")
            raise

    @staticmethod
    def get_user_appointments(user_id):
        """
        Preia toate programările unui utilizator
        
        Args:
            user_id (int): ID-ul utilizatorului
            
        Returns:
            list: Lista programărilor utilizatorului, cu detalii despre serviciu
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT a.*, s.name as service_name, s.price 
            FROM appointments a
            JOIN services s ON a.service_id = s.id
            WHERE a.user_id = ?
            ORDER BY a.date_time DESC
        ''', (user_id,))
        appointments = cursor.fetchall()
        return [dict(appointment) for appointment in appointments]

    @staticmethod
    def get_available_slots(date, service_id):
        """
        Calculează intervalele disponibile pentru o dată și un serviciu
        
        Args:
            date (str): Data pentru care se caută intervale (YYYY-MM-DD)
            service_id (int): ID-ul serviciului
            
        Returns:
            list: Lista orelor disponibile pentru programare
        """
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Obține programul serviciului
            cursor.execute('''
                SELECT start_time, end_time, interval
                FROM services
                WHERE id = ?
            ''', (service_id,))
            
            service = cursor.fetchone()
            if not service:
                return []
                
            # Verifică dacă data este în trecut
            today = datetime.now()
            check_date = datetime.strptime(date, "%Y-%m-%d")
            if check_date.date() < today.date():
                return []
                
            # Preia programările existente pentru data selectată
            cursor.execute('''
                SELECT strftime('%H:%M', date_time) as time
                FROM appointments
                WHERE service_id = ? 
                AND date(date_time) = ?
                AND status IS NULL
            ''', (service_id, date))
            
            booked_times = {row['time'] for row in cursor.fetchall()}
            
            # Generează toate intervalele posibile
            slots = []
            current_time = datetime.strptime(f"{date} {service['start_time']}", "%Y-%m-%d %H:%M")
            end_time = datetime.strptime(f"{date} {service['end_time']}", "%Y-%m-%d %H:%M")
            interval = timedelta(minutes=int(service['interval']))
            
            while current_time < end_time:
                current_datetime = current_time
                time_str = current_time.strftime("%H:%M")
                
                # Pentru data curentă, exclude orele trecute
                if check_date.date() == today.date() and current_datetime <= today:
                    current_time += interval
                    continue
                
                if time_str not in booked_times:
                    slots.append(time_str)
                current_time += interval
            
            return slots
            
        except Exception as e:
            print(f"Eroare la generarea intervalelor disponibile: {str(e)}")
            return []

    @staticmethod
    def cancel(appointment_id, user_id):
        """
        Anulează o programare existentă
        
        Args:
            appointment_id (int): ID-ul programării de anulat
            user_id (int): ID-ul utilizatorului care anulează
            
        Returns:
            tuple: (succes: bool, mesaj: str)
        """
        db = get_db()
        cursor = db.cursor()
        
        # Verifică existența și proprietatea programării
        cursor.execute('''
            SELECT * FROM appointments 
            WHERE id = ? AND user_id = ?
        ''', (appointment_id, user_id))
        
        appointment = cursor.fetchone()
        if not appointment:
            return False, "Programarea nu a fost găsită"
            
        # Verifică limita de timp pentru anulare (24h)
        utc = pytz.UTC
        appointment_time = datetime.fromisoformat(appointment['date_time'].replace('Z', '+00:00'))
        if not appointment_time.tzinfo:
            appointment_time = utc.localize(appointment_time)
            
        if datetime.now(utc) > appointment_time - timedelta(hours=24):
            return False, "Programările pot fi anulate doar cu cel puțin 24 de ore înainte"
            
        # Actualizează statusul programării
        cursor.execute('''
            UPDATE appointments 
            SET status = 'cancelled' 
            WHERE id = ?
        ''', (appointment_id,))
        
        db.commit()
        return True, "Programarea a fost anulată cu succes"

    @staticmethod
    def get_all():
        """
        Preia toate programările din sistem (pentru admin)
        
        Returns:
            list: Lista tuturor programărilor cu detalii despre client și serviciu
        """
        try:
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute('''
                SELECT 
                    a.id,
                    u.username as client_name,
                    u.email as client_email,
                    s.name as service_name,
                    a.date_time,
                    a.status
                FROM appointments a
                JOIN users u ON a.user_id = u.id
                JOIN services s ON a.service_id = s.id
                ORDER BY a.date_time DESC
            ''')
            
            appointments = cursor.fetchall()
            return [dict(row) for row in appointments]
        except Exception as e:
            print(f"Eroare la preluarea tuturor programărilor: {str(e)}")
            return [] 
        