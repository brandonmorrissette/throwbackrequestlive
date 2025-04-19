import React from 'react';

interface ThankYouProps {
    songName: string;
}

/**
 * ThankYou component that displays a thank you message with the requested song.
 * @component
 * @param {ThankYouProps} props - The properties for the ThankYou component.
 * @param {string} props.song - The requested song.
 */
const ThankYou: React.FC<ThankYouProps> = ({ songName }) => {
    return (
        <div>
            <p>
                We’re thrilled to have you here to make the night unforgettable!
                Your request for <strong>{songName}</strong> is in, and the energy
                is building. The 10 songs with the most requests will close out
                the set, so don’t stop now — bring your buds, text your crew, DM
                your crush and get them down here. Let’s make this a night to
                remember!
            </p>
            <p>Thanks for being part of this, we hope you enjoy the show!</p>
        </div>
    );
};

export default ThankYou;
