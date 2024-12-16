-- Ștergerea tabelelor existente pentru a evita conflictele
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS receipts;

-- Tabel pentru utilizatori
-- Stochează datele de autentificare și rolul utilizatorilor
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,          -- Numele de utilizator
    email TEXT UNIQUE NOT NULL,      -- Email-ul (unic) pentru autentificare
    password TEXT NOT NULL,          -- Parola hash-uită
    role TEXT DEFAULT 'user'         -- Rolul: 'user' sau 'admin'
);

-- Tabel pentru categorii de servicii
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,              -- Numele categoriei
    description TEXT,                -- Descrierea categoriei
    icon TEXT                        -- Numele icon-ului pentru UI (optional)
);

-- Tabel pentru serviciile disponibile
CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,    -- ID-ul categoriei
    name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    start_time TIME NOT NULL DEFAULT '09:00',
    end_time TIME NOT NULL DEFAULT '17:00',
    interval INTEGER NOT NULL DEFAULT 30,  -- intervalul între programări în minute
    FOREIGN KEY (category_id) REFERENCES categories (id)
);

-- Tabel pentru programări
-- Stochează programările făcute de utilizatori
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,        -- ID-ul utilizatorului care face programarea
    service_id INTEGER NOT NULL,     -- ID-ul serviciului ales
    date_time TEXT NOT NULL,         -- Data și ora programării
    status TEXT DEFAULT NULL,        -- Statusul programării (null=activă, 'cancelled'=anulată)
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (service_id) REFERENCES services (id)
);

-- Tabel pentru chitanțe
-- Stochează chitanțele generate pentru programări
CREATE TABLE receipts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id INTEGER NOT NULL,  -- ID-ul programării asociate
    receipt_number TEXT NOT NULL,     -- Numărul unic al chitanței
    date_issued TEXT NOT NULL,        -- Data emiterii chitanței
    FOREIGN KEY (appointment_id) REFERENCES appointments (id)
);

-- Inserare utilizatori de test
INSERT INTO users (username, email, password, role) VALUES 
('admin', 'admin@example.com', '$2b$12$8i7ixYJr5apGbqUFyExmAOktl80fmMoaqFqu9LFUCSUZWRasgO9vK', 'admin'),
('john.doe', 'john@example.com', '$2b$12$fg0F6DsvQJbrWqooOjce.O1dzeXQggtiq/ygd/5g1p1Gh8ct9mCya', 'user'),
('jane.doe', 'jane@example.com', '$2b$12$fg0F6DsvQJbrWqooOjce.O1dzeXQggtiq/ygd/5g1p1Gh8ct9mCya', 'user'),
('test.user', 'test@example.com', '$2b$12$fg0F6DsvQJbrWqooOjce.O1dzeXQggtiq/ygd/5g1p1Gh8ct9mCya', 'user');

-- Inserare categorii
INSERT INTO categories (name, description, icon) VALUES
('Salon', 'Servicii de înfrumusețare și îngrijire personală', 'cut'),
('Medical', 'Servicii medicale și consultații', 'medical'),
('IT', 'Servicii IT și consultanță tehnică', 'computer'),
('Sport', 'Fitness și activități sportive', 'dumbbell'),
('Auto', 'Servicii auto și întreținere', 'car'),
('Legal', 'Servicii juridice și consultanță', 'balance-scale'),
('Imobiliare', 'Servicii imobiliare și evaluări', 'home'),
('Educație', 'Servicii educaționale și coaching', 'graduation-cap'),
('Evenimente', 'Organizare și servicii pentru evenimente', 'calendar');

-- Inserare servicii cu categorii
INSERT INTO services (category_id, name, description, price, start_time, end_time, interval) VALUES
    -- Salon (1)
    (1, 'Tuns bărbați', 'Tuns, spălat și coafat', 40.00, '09:00', '17:00', 30),
    (1, 'Tuns femei', 'Tuns, spălat și coafat', 60.00, '09:00', '17:00', 45),
    (1, 'Vopsit', 'Vopsit și coafat', 150.00, '09:00', '17:00', 120),
    (1, 'Coafat', 'Coafat și styling', 50.00, '09:00', '17:00', 45),
    (1, 'Tratament păr', 'Tratament pentru păr deteriorat', 80.00, '09:00', '17:00', 60),
    
    -- Medical (2)
    (2, 'Consultație Generală', 'Evaluare completă a stării de sănătate', 200.00, '08:00', '16:00', 20),
    (2, 'Ecografie', 'Investigație imagistică prin ultrasunete', 300.00, '09:00', '14:00', 30),
    (2, 'Analize de Sânge', 'Set complet de analize sangvine', 150.00, '07:30', '11:00', 15),
    
    -- IT (3)
    (3, 'Consultanță IT', 'Asistență tehnică și soluții IT', 120.00, '10:00', '18:00', 60),
    (3, 'Service Laptop', 'Diagnosticare și reparații laptop', 100.00, '09:00', '17:00', 90),
    (3, 'Dezvoltare Website', 'Consultanță pentru dezvoltare web', 200.00, '10:00', '19:00', 60),
    
    -- Sport (4)
    (4, 'Antrenament Personal', 'Sesiune individuală de fitness', 80.00, '07:00', '21:00', 60),
    (4, 'Yoga', 'Clasă privată de yoga', 60.00, '08:00', '20:00', 45),
    (4, 'Masaj Sportiv', 'Masaj terapeutic pentru sportivi', 100.00, '10:00', '20:00', 45),
    
    -- Auto (5)
    (5, 'Diagnosticare Auto', 'Verificare completă a autovehiculului', 150.00, '08:00', '16:00', 45),
    (5, 'Schimb Ulei', 'Schimb ulei și filtre', 200.00, '08:00', '16:00', 30),
    
    -- Legal (6)
    (6, 'Consultanță Juridică', 'Consiliere juridică personalizată', 250.00, '09:00', '17:00', 30),
    (6, 'Consultanță Financiară', 'Planificare financiară personală', 200.00, '10:00', '18:00', 45),
    
    -- Imobiliare (7)
    (7, 'Evaluare Proprietate', 'Evaluare imobiliară la fața locului', 300.00, '10:00', '16:00', 60),
    (7, 'Consultanță Imobiliară', 'Consiliere pentru tranzacții imobiliare', 150.00, '09:00', '18:00', 45),
    
    -- Educație (8)
    (8, 'Meditație Matematică', 'Pregătire individuală matematică', 80.00, '14:00', '20:00', 60),
    (8, 'Coaching Carieră', 'Consiliere pentru dezvoltare profesională', 180.00, '11:00', '19:00', 90),
    (8, 'Curs Limba Engleză', 'Lecții private de limba engleză', 70.00, '09:00', '20:00', 45),
    
    -- Evenimente (9)
    (9, 'Fotografie Eveniment', 'Servicii foto pentru evenimente', 300.00, '10:00', '22:00', 120),
    (9, 'Consultanță Evenimente', 'Planificare și organizare evenimente', 150.00, '10:00', '18:00', 60);

-- Verifică datele din tabela categories
SELECT * FROM categories;

-- Verifică structura tabelei services
.schema services

-- Verifică structura tabelei categories
.schema categories