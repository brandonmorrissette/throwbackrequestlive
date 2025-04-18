import React, { useState } from 'react';
import { toast } from 'react-toastify';
import { useAuth } from '../../contexts/AuthContext';
import { useError } from '../../contexts/ErrorContext';
import { default as DataService } from '../../services/data';

/**
 * ShowCreation component that renders the form for creating a show.
 * @component
 */
const ShowCreation: React.FC = ({}) => {
    const [formData, setFormData] = useState({
        start_time: '',
        end_time: '',
        name: '',
        venue: '',
        street: '',
        city: '',
        state: '',
    });

    const { token } = useAuth();
    const { setError } = useError();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        console.log('Form submitted:', formData);
        DataService.postRows('shows', token, [formData])
            .then(() => {
                toast.success('Show created successfully:');
            })
            .catch((error) => {
                setError(error);
            });
    };

    return (
        <>
            <h1 className="text-center">Create a Show</h1>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>Start Time:</label>
                    <input
                        type="datetime-local"
                        name="start_time"
                        value={formData.start_time}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>End Time:</label>
                    <input
                        type="datetime-local"
                        name="end_time"
                        value={formData.end_time}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Name:</label>
                    <input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Venue:</label>
                    <input
                        type="text"
                        name="venue"
                        value={formData.venue}
                        onChange={handleChange}
                    />
                </div>
                <div className="form-group">
                    <label>Street:</label>
                    <input
                        type="text"
                        name="street"
                        value={formData.street}
                        onChange={handleChange}
                    />
                </div>
                <div className="form-group">
                    <label>City:</label>
                    <input
                        type="text"
                        name="city"
                        value={formData.city}
                        onChange={handleChange}
                    />
                </div>
                <div className="form-group">
                    <label>State:</label>
                    <input
                        type="text"
                        name="state"
                        value={formData.state}
                        onChange={handleChange}
                    />
                </div>
                <div className="form-group text-center">
                    <button type="submit">Submit</button>
                </div>
            </form>
        </>
    );
};

export default ShowCreation;
