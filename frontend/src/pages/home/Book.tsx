import React from 'react';
import BookingForm from '../../components/BookingForm';
import Modal from '../../components/modal/Modal';

interface BookProps {
    onClose: () => void;
}

/**
 * Book component that displays a booking form in a modal.
 * @component
 * @param {BookProps} props - The properties for the Book component.
 * @param {() => void} props.onClose - Function to close the modal.
 */
const Book: React.FC<BookProps> = ({ onClose }) => {
    return (
        <Modal onClose={onClose}>
            <BookingForm />
        </Modal>
    );
};

export default Book;
