# Utilitar pentru gestionarea conexiunii la baza de date
# Oferă funcții pentru inițializarea și accesarea bazei de date SQLite

import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext
from contextlib import contextmanager

def get_db():
    """
    Obține o conexiune la baza de date
    Reutilizează conexiunea dacă există deja în contextul aplicației
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        
        # Activăm foreign keys și setăm modul de izolare a tranzacțiilor
        g.db.execute('PRAGMA foreign_keys = ON')
        g.db.isolation_level = None  # Permite control manual al tranzacțiilor
        
    return g.db

def close_db(e=None):
    """
    Închide conexiunea la baza de date dacă există
    """
    db = g.pop('db', None)
    
    if db is not None:
        db.close()

def init_db():
    """
    Inițializează baza de date folosind schema.sql
    """
    db = get_db()
    
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@contextmanager
def transaction(db):
    """Context manager for database transactions"""
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise

@click.command('init-db')
@with_appcontext
def init_db_command():
    """
    Comandă CLI pentru inițializarea bazei de date
    Poate fi rulată cu 'flask init-db'
    """
    init_db()
    click.echo('Baza de date a fost inițializată.')

def init_app(app):
    """
    Înregistrează funcțiile de gestionare a bazei de date în aplicație
    
    Args:
        app: Instanța aplicației Flask
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command) 