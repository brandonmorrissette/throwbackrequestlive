import React from 'react';
import Modal from '../../components/modal/Modal';

interface BookProps {
    onClose: () => void;
}

const Book: React.FC<BookProps> = ({ onClose }) => {
    return (
        <Modal onClose={onClose}>
            <h2>Booking</h2>
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
        </Modal>
    );
};

export default Book;
