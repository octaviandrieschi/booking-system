from flask import Blueprint, jsonify, request
from app.models.business_hours import BusinessHours
from app.utils.auth import admin_required

bp = Blueprint('business_hours', __name__, url_prefix='/api')

@bp.route('/business-hours', methods=['GET'])
def get_business_hours():
    """
    Endpoint pentru preluarea programului de funcționare
    Accesibil public - oricine poate vedea programul
    
    Returns:
        JSON cu orele de funcționare:
        - start_time: ora de început (format HH:MM)
        - end_time: ora de sfârșit (format HH:MM)
        - interval: durata unei programări în minute
    """
    try:
        hours = BusinessHours.get()
        return jsonify(hours)
    except Exception as e:
        print(f"Eroare la preluarea programului: {str(e)}")
        return jsonify({'message': 'Eroare la preluarea programului'}), 500

@bp.route('/business-hours', methods=['PUT'])
@admin_required
def update_business_hours(current_user_id):
    """
    Endpoint pentru actualizarea programului de funcționare
    Doar administratorii pot modifica programul
    
    Args:
        current_user_id: ID-ul administratorului
        
    Request body:
        - start_time: ora de început (format: HH:MM)
        - end_time: ora de sfârșit (format: HH:MM)
        - interval: durata în minute
    """
    try:
        data = request.get_json()
        success = BusinessHours.update(
            start_time=data['start_time'],
            end_time=data['end_time'],
            interval=data['interval']
        )
        
        if success:
            return jsonify({'message': 'Programul a fost actualizat cu succes'})
        else:
            return jsonify({'message': 'Nu s-a putut actualiza programul'}), 500
    except Exception as e:
        print(f"Eroare la actualizarea programului: {str(e)}")
        return jsonify({'message': 'Eroare la actualizarea programului'}), 500 