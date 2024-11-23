import React from 'react';

interface ThankYouProps {
    song: string;
}

const ThankYou: React.FC<ThankYouProps> = ({ song }) => {
    return (
        <div>
            <p>
                We’re thrilled to have you here to make the night unforgettable!
                Your vote for <strong>{song}</strong> is in, and the energy is
                building. The 10 songs with the most votes will close out the
                set, so don’t stop now — bring your buds, text your crew, DM
                your crush and get them down here. Let’s make this a night to
                remember!
            </p>
            <p>Thanks for being part of this, we hope you enjoy the show!</p>
        </div>
    );
};

export default ThankYou;