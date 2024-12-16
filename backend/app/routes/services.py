# Rute pentru gestionarea serviciilor
# Oferă endpoint-uri pentru CRUD (Create, Read, Update, Delete) pe serviciile disponibile

from flask import Blueprint, jsonify, request
from app.models.service import Service
from app.utils.auth import admin_required
from app.utils.db import get_db

bp = Blueprint('services', __name__, url_prefix='/api')

@bp.route('/services', methods=['GET'])
def get_services():
    """
    Endpoint pentru listarea tuturor serviciilor disponibile
    Accesibil public - oricine poate vedea lista de servicii
    
    Returns:
        JSON cu lista de servicii, fiecare conținând:
        - id: identificator unic
        - name: numele serviciului
        - description: descrierea
        - price: prețul
        - start_time: ora de început
        - end_time: ora de sfârșit
        - interval: durata în minute
        - category_id: id-ul categoriei
        - category_name: numele categoriei
    """
    try:
        services = Service.get_all()
        return jsonify(services)
    except Exception as e:
        print(f"Eroare la preluarea serviciilor: {str(e)}")
        return jsonify({'message': 'Eroare la încărcarea serviciilor'}), 500

@bp.route('/services', methods=['POST'])
@admin_required
def add_service(current_user_id):
    """
    Endpoint pentru adăugarea unui serviciu nou
    Doar administratorii pot adăuga servicii
    
    Args:
        current_user_id: ID-ul utilizatorului admin
        
    Request body:
        - category_id: ID-ul categoriei
        - name: numele serviciului
        - description: descrierea serviciului
        - price: prețul serviciului
        - start_time: ora de început (format HH:MM)
        - end_time: ora de sfârșit (format HH:MM)
        - interval: durata în minute
    """
    try:
        data = request.get_json()
        print("\n=== Service Creation Debug ===")
        print("Raw request data:", data)
        
        # Validate required fields
        required_fields = ['category_id', 'name', 'description', 'price', 'start_time', 'end_time', 'interval']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print("Missing fields:", missing_fields)
            return jsonify({'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400
            
        # Convert data types
        try:
            category_id = int(data['category_id'])
            price = float(data['price'])
            interval = int(data['interval'])
        except (ValueError, TypeError) as e:
            print(f"Data conversion error: {str(e)}")
            return jsonify({'message': f'Invalid data format: {str(e)}'}), 400
            
        service_id = Service.create(
            name=data['name'],
            description=data['description'],
            price=price,
            category_id=category_id,
            start_time=data['start_time'],
            end_time=data['end_time'],
            interval=interval
        )
        
        if service_id:
            # Get the created service
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''
                SELECT s.*, c.name as category_name 
                FROM services s
                JOIN categories c ON s.category_id = c.id
                WHERE s.id = ?
            ''', (service_id,))
            new_service = cursor.fetchone()
            
            return jsonify({
                'message': 'Service created successfully',
                'service': dict(new_service)
            }), 201
            
        return jsonify({'message': 'Nu s-a putut adăuga serviciul'}), 400
        
    except Exception as e:
        print(f"Eroare la crearea serviciului: {str(e)}")
        return jsonify({'message': 'Eroare la crearea serviciului'}), 500

@bp.route('/services/<int:service_id>', methods=['PUT'])
@admin_required
def update_service(current_user_id, service_id):
    """
    Endpoint pentru actualizarea unui serviciu existent
    Doar administratorii pot modifica servicii
    """
    try:
        data = request.get_json()
        print("\n=== Service Update Debug ===")
        print("Raw request data:", data)
        
        # Validate required fields
        required_fields = ['category_id', 'name', 'description', 'price', 'start_time', 'end_time', 'interval']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print("Missing fields:", missing_fields)
            return jsonify({'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400
            
        # Convert data types
        try:
            category_id = int(data['category_id'])
            price = float(data['price'])
            interval = int(data['interval'])
        except (ValueError, TypeError) as e:
            print(f"Data conversion error: {str(e)}")
            return jsonify({'message': f'Invalid data format: {str(e)}'}), 400
            
        success = Service.update(
            service_id=service_id,
            name=data['name'],
            description=data['description'],
            price=price,
            category_id=category_id,
            start_time=data['start_time'],
            end_time=data['end_time'],
            interval=interval
        )
        
        if success:
            # Get the updated service
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''
                SELECT s.*, c.name as category_name 
                FROM services s
                JOIN categories c ON s.category_id = c.id
                WHERE s.id = ?
            ''', (service_id,))
            updated_service = cursor.fetchone()
            
            return jsonify({
                'message': 'Service updated successfully',
                'service': dict(updated_service)
            })
            
        return jsonify({'message': 'Nu s-a putut actualiza serviciul'}), 400
        
    except Exception as e:
        print(f"Error updating service: {str(e)}")
        return jsonify({'message': f'Error: {str(e)}'}), 500

@bp.route('/services/<int:service_id>', methods=['DELETE'])
@admin_required
def delete_service(current_user_id, service_id):
    """
    Endpoint pentru ștergerea unui serviciu
    Doar administratorii pot șterge servicii
    
    Parametri:
    - service_id: ID-ul serviciului de șters
    """
    try:
        success = Service.delete(service_id)
        if success:
            return jsonify({'message': 'Serviciu șters cu succes'})
        return jsonify({'message': 'Nu s-a putut șterge serviciul'}), 400
    except Exception as e:
        print(f"Eroare la ștergerea serviciului: {str(e)}")
        return jsonify({'message': 'Eroare la ștergerea serviciului'}), 500 