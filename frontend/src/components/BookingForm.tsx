import React from 'react';

/**
 * BookingForm component that displays a contact form for booking inquiries.
 * @component
 */
const BookingForm: React.FC = () => {
    return (
        <div>
            <h3>Booking</h3>
            <p>
                For questions regarding booking us for your next event, please
                fill out this form and we will gladly get back to you as soon as
                we can. Thank you, have a great day!
            </p>
            <form
                action="mailto:ThrowbackRequestLive@proton.me"
                method="post"
                encType="text/plain"
                className="contact-form"
            >
                <div className="form-group">
                    <label htmlFor="name">Your Name:</label>
                    <input type="text" id="name" name="name" required />
                </div>
                <div className="form-group">
                    <label htmlFor="email">Your Email:</label>
                    <input type="email" id="email" name="email" required />
                </div>
                <div className="form-group">
                    <label htmlFor="phone">Your Phone:</label>
                    <input type="phone" id="phone" name="phone" required />
                </div>
                <div className="form-group">
                    <label htmlFor="message">Your Message:</label>
                    <textarea
                        id="message"
                        name="message"
                        rows={4}
                        required
                    ></textarea>
                </div>
                <div className="form-group text-center">
                    <button type="submit">Send Message</button>
                </div>
            </form>
        </div>
    );
};

export default BookingForm;
