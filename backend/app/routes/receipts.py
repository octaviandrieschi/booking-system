# Rute pentru gestionarea chitanțelor
# Oferă endpoint-uri pentru vizualizarea chitanțelor asociate programărilor

from flask import Blueprint, jsonify, send_file
from app.models.receipt import Receipt
from app.utils.auth import token_required
import os
from app.utils.pdf import generate_receipt_pdf

bp = Blueprint('receipts', __name__, url_prefix='/api')

@bp.route('/receipts/<int:appointment_id>', methods=['GET'])
@token_required
def get_receipt(current_user_id, appointment_id):
    """
    Endpoint pentru obținerea chitanței unei programări
    
    Args:
        current_user_id: ID-ul utilizatorului care solicită chitanța
        appointment_id: ID-ul programării
        
    Returns:
        Detaliile chitanței în format JSON sau mesaj de eroare
    """
    receipt = Receipt.get_by_appointment(appointment_id, current_user_id)
    
    if receipt:
        return jsonify(receipt)
    return jsonify({'message': 'Chitanța nu a fost găsită'}), 404

@bp.route('/receipts/<int:appointment_id>/pdf', methods=['GET'])
@token_required
def get_receipt_pdf(current_user_id, appointment_id):
    """
    Endpoint pentru descărcarea chitanței în format PDF
    
    Args:
        current_user_id: ID-ul utilizatorului care solicită PDF-ul
        appointment_id: ID-ul programării
        
    Returns:
        Fișierul PDF al chitanței sau mesaj de eroare
    """
    try:
        receipt = Receipt.get_by_appointment(appointment_id, current_user_id)
        
        if not receipt:
            return jsonify({'message': 'Chitanța nu a fost găsită'}), 404

        # Creează directorul pentru PDF-uri temporare dacă nu există
        pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp')
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Generează calea pentru PDF
        pdf_path = os.path.join(pdf_dir, f'receipt_{appointment_id}.pdf')
        
        # Generează PDF-ul
        generate_receipt_pdf(receipt, pdf_path)
        
        # Trimite fișierul și șterge-l după
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'receipt_{receipt["receipt_number"]}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"Eroare la generarea PDF: {str(e)}")
        return jsonify({'message': 'Eroare la generarea PDF'}), 500