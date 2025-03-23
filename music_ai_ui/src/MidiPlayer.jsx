import React from 'react';
import 'html-midi-player';

const MidiPlayer = ({ harmonizedMidiUrl }) => {
    console.log(harmonizedMidiUrl)
    return (
        <midi-player
            src={harmonizedMidiUrl}
            sound-font></midi-player>
    );
};

export default MidiPlayer;
