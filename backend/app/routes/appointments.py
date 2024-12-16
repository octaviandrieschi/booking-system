from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import pytz
from app.models.appointment import Appointment
from app.models.receipt import Receipt
from app.utils.db import get_db, transaction
from app.utils.auth import token_required, admin_required, get_token_data

bp = Blueprint('appointments', __name__, url_prefix='/api')

@bp.route('/appointments', methods=['POST'])
@token_required
def create_appointment(current_user_id):
    """
    Endpoint pentru crearea unei noi programări
    
    Args:
        current_user_id: ID-ul utilizatorului care face programarea
        
    Request body:
        - service_id: ID-ul serviciului
        - date_time: data și ora programării (format: YYYY-MM-DD HH:MM sau ISO)
        
    Returns:
        - appointment_id: ID-ul programării create
        - receipt: detaliile chitanței generate
    """
    token_data = get_token_data()
    if token_data.get('role') == 'admin':
        return jsonify({'message': 'Administratorii nu pot face programări'}), 403

    try:
        data = request.get_json()
        
        if not data or 'service_id' not in data or 'date_time' not in data:
            return jsonify({'message': 'Date incomplete pentru programare'}), 400
            
        # Validăm formatul datei
        date_time = data['date_time']
        if 'T' in date_time:
            dt = datetime.fromisoformat(date_time.replace('Z', '+00:00'))
            date_time = dt.strftime("%Y-%m-%d %H:%M")
        
        db = get_db()
        cursor = db.cursor()
        
        # Verificăm dacă serviciul există
        cursor.execute('SELECT * FROM services WHERE id = ?', (data['service_id'],))
        service = cursor.fetchone()
        if not service:
            return jsonify({'message': 'Serviciul selectat nu există'}), 400
            
        # Verificăm dacă utilizatorul există
        cursor.execute('SELECT * FROM users WHERE id = ?', (current_user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'message': 'Utilizatorul nu există'}), 400
            
        # Folosim context manager-ul pentru tranzacții
        with transaction(db) as trans_db:
            # Create the appointment
            appointment_id = Appointment.create(
                user_id=current_user_id,
                service_id=data['service_id'],
                date_time=date_time,
                db=trans_db
            )
            
            if not appointment_id:
                raise ValueError('Nu s-a putut crea programarea')
                
            # Create a receipt for the appointment
            receipt = Receipt.create(appointment_id, trans_db)
            
            if not receipt:
                raise ValueError('Eroare la generarea chitanței')
            
            return jsonify({
                'message': 'Programare creată cu succes',
                'appointment_id': appointment_id,
                'receipt': receipt
            }), 201
            
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        print(f"Eroare la crearea programării: {str(e)}")
        return jsonify({'message': 'Eroare internă la crearea programării'}), 500

@bp.route('/appointments/my', methods=['GET'])
@token_required
def get_user_appointments(current_user_id):
    """
    Endpoint pentru preluarea programărilor unui utilizator
    Returnează toate programările utilizatorului autentificat
    
    Args:
        current_user_id: ID-ul utilizatorului
        
    Returns:
        Lista de programări cu detaliile complete
    """
    appointments = Appointment.get_user_appointments(current_user_id)
    return jsonify(appointments)

@bp.route('/appointments/all', methods=['GET'])
@admin_required
def get_all_appointments(current_user_id):
    """
    Endpoint pentru preluarea tuturor programărilor
    Accesibil doar administratorilor
    """
    try:
        appointments = Appointment.get_all()
        return jsonify(appointments)
    except Exception as e:
        print(f"Eroare la preluarea programărilor: {str(e)}")
        return jsonify({'message': 'Eroare la încărcarea programărilor'}), 500

@bp.route('/appointments/available-slots', methods=['GET'])
def get_available_slots():
    """
    Endpoint pentru obținerea intervalelor disponibile pentru o dată și un serviciu
    
    Query params:
        - date: Data pentru care se caută intervale (format: YYYY-MM-DD)
        - service_id: ID-ul serviciului
        
    Returns:
        - slots: Lista de intervale orare disponibile pentru programare
    """
    date = request.args.get('date')
    service_id = request.args.get('service_id')
    
    if not date or not service_id:
        return jsonify({
            'message': 'Data și serviciul sunt obligatorii',
            'slots': []
        }), 400
    
    try:
        # Validează formatul datei
        datetime.strptime(date, '%Y-%m-%d')
        
        # Obține intervalele disponibile
        available_slots = Appointment.get_available_slots(date, service_id)
        
        return jsonify({
            'slots': available_slots
        })
    except ValueError:
        return jsonify({
            'message': 'Format dată invalid',
            'slots': []
        }), 400
    except Exception as e:
        print(f"Eroare la obținerea intervalelor: {str(e)}")
        return jsonify({
            'message': 'Eroare la încărcarea intervalelor disponibile',
            'slots': []
        }), 500

@bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@token_required
def cancel_appointment(current_user_id, appointment_id):
    """
    Endpoint pentru anularea unei programări
    Verifică dacă anularea este permisă (cu cel puțin 24h înainte)
    
    Parametri:
    - appointment_id: ID-ul programării de anulat
    """
    success, message = Appointment.cancel(appointment_id, current_user_id)
    if success:
        return jsonify({'message': message})
    return jsonify({'message': message}), 400 

@bp.route('/services', methods=['GET'])
def get_services():
    """
    Endpoint pentru obținerea listei de servicii disponibile
    """
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT 
                s.id, s.name, s.description, s.price, 
                s.start_time, s.end_time, s.interval,
                c.id as category_id, c.name as category_name, 
                c.description as category_description,
                c.icon as category_icon
            FROM services s
            JOIN categories c ON s.category_id = c.id
            ORDER BY c.name, s.price ASC
        ''')
        
        services = [dict(row) for row in cursor.fetchall()]
        return jsonify(services)
        
    except Exception as e:
        print(f"Eroare la obținerea serviciilor: {str(e)}")
        return jsonify({'message': 'Eroare la încărcarea serviciilor'}), 500

@bp.route('/user/current', methods=['GET'])
@token_required
def get_current_user(current_user_id):
    """
    Endpoint pentru obținerea detaliilor utilizatorului curent
    """
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT id, username, email, role
            FROM users
            WHERE id = ?
        ''', (current_user_id,))
        
        user = cursor.fetchone()
        if not user:
            return jsonify({'message': 'Utilizatorul nu există'}), 404
            
        return jsonify(dict(user))
        
    except Exception as e:
        print(f"Eroare la obținerea detaliilor utilizatorului: {str(e)}")
        return jsonify({'message': 'Eroare internă'}), 500

@bp.route('/services', methods=['POST'])
@admin_required
def create_service(current_user_id):
    print("\n=== Starting Service Creation ===")
    try:
        print("Getting JSON data...")
        data = request.get_json()
        print("\n=== Service Creation Debug ===")
        print("Raw request data:", data)
        print("Request headers:", dict(request.headers))
        print("Current user ID:", current_user_id)
        
        # Validate required fields
        required_fields = ['category_id', 'name', 'description', 'price', 'start_time', 'end_time', 'interval']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print("Missing fields:", missing_fields)
            return jsonify({'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        # Convert and validate data types
        try:
            category_id = int(data['category_id'])
            price = float(data['price'])
            interval = int(data['interval'])
            
            print("\nConverted values:")
            print(f"category_id: {category_id} ({type(category_id)})")
            print(f"price: {price} ({type(price)})")
            print(f"interval: {interval} ({type(interval)})")
        except (ValueError, TypeError) as e:
            print(f"Eroare la conversia datelor: {str(e)}")
            return jsonify({'message': f'Format de date invalid: {str(e)}'}), 400
        
        db = get_db()
        print("\nGot database connection")
        
        with transaction(db) as trans_db:
            cursor = trans_db.cursor()
            print("\nStarted transaction")
            
            # Verify category exists
            cursor.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
            category = cursor.fetchone()
            print("\nFound category:", category)
            
            if not category:
                print(f"Categoria {category_id} nu există")
                return jsonify({'message': f'Categoria {category_id} nu există'}), 400
            
            # Insert service
            insert_query = '''
                INSERT INTO services 
                (category_id, name, description, price, start_time, end_time, interval)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            insert_values = (
                category_id,
                data['name'].strip(),
                data['description'].strip(),
                price,
                data['start_time'],
                data['end_time'],
                interval
            )
            
            print("\nExecuting INSERT:")
            print("Query:", insert_query)
            print("Values:", insert_values)
            
            try:
                cursor.execute(insert_query, insert_values)
                print("\nInsert successful")
                
                # Get the new service ID
                new_id = cursor.lastrowid
                print("\nNew service ID:", new_id)
                
                # Verify the insert
                verify_query = '''
                    SELECT s.*, c.name as category_name 
                    FROM services s
                    JOIN categories c ON s.category_id = c.id
                    WHERE s.id = ?
                '''
                cursor.execute(verify_query, (new_id,))
                new_service = cursor.fetchone()
                
                if not new_service:
                    print("\nError: Service not found after insert")
                    return jsonify({'message': 'Service creation failed'}), 400
                    
                print("\nCreated service:", dict(new_service))
                
                return jsonify({
                    'message': 'Service created successfully',
                    'service': dict(new_service)
                }), 201
                
            except Exception as e:
                print("\nEroare la operațiunea în baza de date:", str(e))
                print("Tip eroare:", type(e))
                raise
            
    except Exception as e:
        print("\nEroare generală:", str(e))
        print("Tip eroare:", type(e))
        print("Argumente eroare:", getattr(e, 'args', None))
        return jsonify({'message': f'Error: {str(e)}'}), 400

@bp.route('/categories', methods=['GET'])
def get_categories():
    """
    Endpoint pentru obținerea listei de categorii
    """
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT id, name, description, icon
            FROM categories
            ORDER BY name ASC
        ''')
        
        categories = [dict(row) for row in cursor.fetchall()]
        return jsonify(categories)
        
    except Exception as e:
        print(f"Eroare la obținerea categoriilor: {str(e)}")
        return jsonify({'message': 'Eroare la încărcarea categoriilor'}), 500

@bp.route('/services/<int:service_id>', methods=['PUT'])
@admin_required
def update_service(current_user_id, service_id):
    """
    Endpoint pentru actualizarea unui serviciu existent
    Accesibil doar pentru administratori
    """
    try:
        data = request.get_json()
        print("\n=== Service Update Debug ===")
        print("Service ID:", service_id)
        print("Raw request data:", data)
        
        # Validate required fields
        required_fields = ['category_id', 'name', 'description', 'price', 'start_time', 'end_time', 'interval']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print("Missing fields:", missing_fields)
            return jsonify({'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        # Convert and validate data types
        try:
            category_id = int(data['category_id'])
            price = float(data['price'])
            interval = int(data['interval'])
            
            print("\nConverted values:")
            print(f"category_id: {category_id} ({type(category_id)})")
            print(f"price: {price} ({type(price)})")
            print(f"interval: {interval} ({type(interval)})")
        except (ValueError, TypeError) as e:
            print(f"Eroare la conversia datelor: {str(e)}")
            return jsonify({'message': f'Format de date invalid: {str(e)}'}), 400
        
        db = get_db()
        
        with transaction(db) as trans_db:
            cursor = trans_db.cursor()
            
            # Verify service exists
            cursor.execute('SELECT * FROM services WHERE id = ?', (service_id,))
            service = cursor.fetchone()
            if not service:
                print(f"Serviciul {service_id} nu a fost găsit")
                return jsonify({'message': 'Serviciul nu a fost găsit'}), 404
            
            # Verify category exists
            cursor.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
            category = cursor.fetchone()
            if not category:
                print(f"Categoria {category_id} nu există")
                return jsonify({'message': f'Categoria {category_id} nu există'}), 400
            
            # Update service
            update_query = '''
                UPDATE services 
                SET category_id = ?, name = ?, description = ?, 
                    price = ?, start_time = ?, end_time = ?, interval = ?
                WHERE id = ?
            '''
            update_values = (
                category_id,
                data['name'].strip(),
                data['description'].strip(),
                price,
                data['start_time'],
                data['end_time'],
                interval,
                service_id
            )
            
            print("\nExecuting UPDATE:")
            print("Query:", update_query)
            print("Values:", update_values)
            
            cursor.execute(update_query, update_values)
            
            # Verify the update
            verify_query = '''
                SELECT s.*, c.name as category_name 
                FROM services s
                JOIN categories c ON s.category_id = c.id
                WHERE s.id = ?
            '''
            cursor.execute(verify_query, (service_id,))
            updated_service = cursor.fetchone()
            
            if not updated_service:
                print("\nError: Service not found after update")
                return jsonify({'message': 'Service update failed'}), 400
                
            print("\nUpdated service:", dict(updated_service))
            
            return jsonify({
                'message': 'Service updated successfully',
                'service': dict(updated_service)
            }), 200
            
    except Exception as e:
        print("\nEroare generală:", str(e))
        print("Tip eroare:", type(e))
        return jsonify({'message': f'Error: {str(e)}'}), 400