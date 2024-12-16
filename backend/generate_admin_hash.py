# Script pentru generarea hash-ului parolei administrative
# Folosit pentru crearea contului de admin implicit în baza de date

import bcrypt

password = "admin123"  # Parola implicită pentru admin
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print(f"Generated hash for admin password: {hashed.decode('utf-8')}") 