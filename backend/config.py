# Configurații pentru aplicație
# Definește variabilele de configurare globale

import os

class Config:
    # Cheie secretă pentru semnarea token-urilor JWT și alte operații criptografice
    SECRET_KEY = 'your-secret-key'  # Trebuie înlocuită cu o cheie sigură în producție
    
    # Calea către baza de date SQLite
    DATABASE = os.path.join(os.path.dirname(__file__), 'instance', 'bookings.db') 