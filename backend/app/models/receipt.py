# Model pentru gestionarea chitanțelor
# Oferă funcționalități pentru crearea și preluarea chitanțelor asociate programărilor

from app.utils.db import get_db
from datetime import datetime
import random
import string

class Receipt:
    @staticmethod
    def create(appointment_id, db=None):
        """
        Creează o chitanță nouă pentru o programare
        
        Args:
            appointment_id (int): ID-ul programării pentru care se creează chitanța
            db: Conexiunea la baza de date (opțional)
            
        Returns:
            dict: Datele chitanței create sau None în caz de eroare
        """
        try:
            if db is None:
                db = get_db()
            cursor = db.cursor()
            
            # Verificăm dacă programarea există și obținem toate datele necesare
            cursor.execute('''
                SELECT 
                    a.id, a.user_id, a.service_id, a.date_time, a.status,
                    u.username, u.email,
                    s.name as service_name, s.price
                FROM appointments a
                JOIN users u ON a.user_id = u.id
                JOIN services s ON a.service_id = s.id
                WHERE a.id = ?
            ''', (appointment_id,))
            
            appointment = cursor.fetchone()
            if not appointment:
                print(f"No appointment found with id {appointment_id}")
                return None
            
            # Generăm un număr unic pentru chitanță
            receipt_number = f"REC-{datetime.now().strftime('%Y%m%d')}-{appointment_id}"
            date_issued = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Inserăm chitanța în baza de date
            cursor.execute('''
                INSERT INTO receipts (appointment_id, receipt_number, date_issued)
                VALUES (?, ?, ?)
            ''', (appointment_id, receipt_number, date_issued))
            
            # Returnăm datele complete ale chitanței
            return {
                'receipt_number': receipt_number,
                'date_issued': date_issued,
                'date_time': appointment['date_time'],
                'service_name': appointment['service_name'],
                'total': float(appointment['price']),
                'client_name': appointment['username'],
                'client_email': appointment['email'],
                'status': appointment['status'] or 'confirmat'
            }
            
        except Exception as e:
            print(f"Eroare la crearea chitanței: {str(e)}")
            raise

    @staticmethod
    def get_by_appointment(appointment_id, user_id):
        """
        Obține sau creează o chitanță pentru o programare
        
        Args:
            appointment_id (int): ID-ul programării
            user_id (int): ID-ul utilizatorului care solicită chitanța
            
        Returns:
            dict: Datele chitanței sau None în caz de eroare
        """
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Verificăm dacă programarea există și aparține utilizatorului
            cursor.execute('''
                SELECT 
                    a.id, a.user_id, a.service_id, a.date_time, a.status,
                    u.username, u.email,
                    s.name as service_name, s.price
                FROM appointments a
                JOIN users u ON a.user_id = u.id
                JOIN services s ON a.service_id = s.id
                WHERE a.id = ? AND a.user_id = ?
            ''', (appointment_id, user_id))
            
            appointment = cursor.fetchone()
            if not appointment:
                print(f"No appointment found for id {appointment_id} and user {user_id}")
                return None
            
            # Verificăm dacă există o chitanță
            cursor.execute('''
                SELECT 
                    r.receipt_number,
                    r.date_issued,
                    a.date_time,
                    s.name as service_name,
                    s.price as total,
                    u.username as client_name,
                    u.email as client_email,
                    a.status
                FROM receipts r
                JOIN appointments a ON r.appointment_id = a.id
                JOIN services s ON a.service_id = s.id
                JOIN users u ON a.user_id = u.id
                WHERE r.appointment_id = ?
            ''', (appointment_id,))
            
            result = cursor.fetchone()
            if result:
                receipt_data = dict(result)
                receipt_data['total'] = float(receipt_data['total'])
                receipt_data['status'] = receipt_data['status'] or 'confirmat'
                return receipt_data
            
            # Dacă nu există chitanță, o creăm
            receipt_number = f"REC-{datetime.now().strftime('%Y%m%d')}-{appointment_id}"
            date_issued = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
                INSERT INTO receipts (appointment_id, receipt_number, date_issued)
                VALUES (?, ?, ?)
            ''', (appointment_id, receipt_number, date_issued))
            
            db.commit()
            
            # Returnăm datele chitanței nou create
            return {
                'receipt_number': receipt_number,
                'date_issued': date_issued,
                'date_time': appointment['date_time'],
                'service_name': appointment['service_name'],
                'total': float(appointment['price']),
                'client_name': appointment['username'],
                'client_email': appointment['email'],
                'status': appointment['status'] or 'confirmat'
            }
            
        except Exception as e:
            print(f"Error in get_by_appointment: {str(e)}")
            if 'db' in locals():
                db.rollback()
            return None 