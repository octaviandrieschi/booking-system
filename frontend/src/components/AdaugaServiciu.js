import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL } from '../config';

function AdaugaServiciu() {
    const navigate = useNavigate();
    const [categories, setCategories] = useState([]);
    const [formData, setFormData] = useState({
        category_id: '',
        name: '',
        description: '',
        price: '',
        start_time: '09:00',
        end_time: '17:00',
        interval: '30'
    });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        // Încărcăm categoriile la montarea componentei
        fetch(`${API_URL}/categories`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        })
        .then(response => response.json())
        .then(data => setCategories(data))
        .catch(error => console.error('Eroare la încărcarea categoriilor:', error));
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        try {
            const response = await fetch(`${API_URL}/services`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    ...formData,
                    price: parseFloat(formData.price),
                    interval: parseInt(formData.interval),
                    category_id: parseInt(formData.category_id)
                })
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess('Serviciu adăugat cu succes!');
                setTimeout(() => navigate('/services'), 2000);
            } else {
                setError(data.message || 'Eroare la adăugarea serviciului');
            }
        } catch (error) {
            setError('Eroare la comunicarea cu serverul');
        }
    };

    return (
        <div className="container mt-4">
            <h2>Adaugă Serviciu Nou</h2>
            {error && <div className="alert alert-danger">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}
            
            <form onSubmit={handleSubmit} className="mt-4">
                <div className="mb-3">
                    <label className="form-label">Categorie:</label>
                    <select 
                        name="category_id"
                        value={formData.category_id}
                        onChange={handleChange}
                        className="form-select"
                        required
                    >
                        <option value="">Selectează categoria</option>
                        {categories.map(category => (
                            <option key={category.id} value={category.id}>
                                {category.name}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="mb-3">
                    <label className="form-label">Nume serviciu:</label>
                    <input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        className="form-control"
                        required
                    />
                </div>

                <div className="mb-3">
                    <label className="form-label">Descriere:</label>
                    <textarea
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        className="form-control"
                        required
                    />
                </div>

                <div className="mb-3">
                    <label className="form-label">Preț (RON):</label>
                    <input
                        type="number"
                        name="price"
                        value={formData.price}
                        onChange={handleChange}
                        className="form-control"
                        min="0"
                        step="0.01"
                        required
                    />
                </div>

                <div className="row">
                    <div className="col-md-4 mb-3">
                        <label className="form-label">Ora începerii:</label>
                        <input
                            type="time"
                            name="start_time"
                            value={formData.start_time}
                            onChange={handleChange}
                            className="form-control"
                            required
                        />
                    </div>

                    <div className="col-md-4 mb-3">
                        <label className="form-label">Ora închiderii:</label>
                        <input
                            type="time"
                            name="end_time"
                            value={formData.end_time}
                            onChange={handleChange}
                            className="form-control"
                            required
                        />
                    </div>

                    <div className="col-md-4 mb-3">
                        <label className="form-label">Interval (minute):</label>
                        <input
                            type="number"
                            name="interval"
                            value={formData.interval}
                            onChange={handleChange}
                            className="form-control"
                            min="15"
                            step="15"
                            required
                        />
                    </div>
                </div>

                <button type="submit" className="btn btn-primary">
                    Adaugă Serviciu
                </button>
            </form>
        </div>
    );
}

export default AdaugaServiciu; 