from flask import Flask
from flask_cors import CORS
from config import Config
from app.utils.db import init_app

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)

    init_app(app)

    from app.routes import auth, services, appointments, receipts, business_hours
    app.register_blueprint(auth.bp)
    app.register_blueprint(services.bp)
    app.register_blueprint(appointments.bp)
    app.register_blueprint(receipts.bp)
    app.register_blueprint(business_hours.bp)

    return app 