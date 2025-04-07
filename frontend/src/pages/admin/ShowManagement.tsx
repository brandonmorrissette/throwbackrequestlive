import { useState } from 'react';
import { default as DataService } from '../../services/data';
import { AdminComponent } from './Admin';

/**
 * ShowManagement component that allows managing show tables.
 * @component
 */
const ShowManagement: AdminComponent = () => {
    const [formData, setFormData] = useState({
        start_time: '',
        end_time: '',
        name: '',
        venue: '',
        street: '',
        city: '',
        state: '',
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        console.log('Form submitted:', formData);
        DataService.postRows('shows', [formData])
            .then((response) => {
                console.log('Show created successfully:', response);
            })
            .catch((error) => {
                console.error('Error creating show:', error);
            });
    };

    return (
        <div>
            <h1>Create a Show</h1>
            <form onSubmit={handleSubmit}>
                <label>
                    Start Time:
                    <input
                        type="datetime-local"
                        name="start_time"
                        value={formData.start_time}
                        onChange={handleChange}
                        required
                    />
                </label>
                <br />
                <label>
                    End Time:
                    <input
                        type="datetime-local"
                        name="end_time"
                        value={formData.end_time}
                        onChange={handleChange}
                        required
                    />
                </label>
                <br />
                <label>
                    Name:
                    <input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        required
                    />
                </label>
                <br />
                <label>
                    Venue:
                    <input
                        type="text"
                        name="venue"
                        value={formData.venue}
                        onChange={handleChange}
                    />
                </label>
                <br />
                <label>
                    Street:
                    <input
                        type="text"
                        name="street"
                        value={formData.street}
                        onChange={handleChange}
                    />
                </label>
                <br />
                <label>
                    City:
                    <input
                        type="text"
                        name="city"
                        value={formData.city}
                        onChange={handleChange}
                    />
                </label>
                <br />
                <label>
                    State:
                    <input
                        type="text"
                        name="state"
                        value={formData.state}
                        onChange={handleChange}
                    />
                </label>
                <br />
                <button type="submit">Submit</button>
            </form>
        </div>
    );
};

ShowManagement.allowed_groups = ['superuser'];

export default ShowManagement;
