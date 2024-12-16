# Punct de intrare pentru aplicația Flask
# Creează și pornește serverul de aplicație

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)  # Pornește serverul în mod debug pentru dezvoltare