import React from 'react';
import 'html-midi-player';

const MidiPlayerInner = ({ harmonizedMidiUrl }) => {
    console.log(harmonizedMidiUrl)
    return (
        <midi-player
            src={harmonizedMidiUrl}
            sound-font></midi-player>
    );
};

const MidiPlayer = React.memo(({ harmonizedMidiUrl }) => {
    return (
            <MidiPlayerInner harmonizedMidiUrl={harmonizedMidiUrl} />
    );
});

export default MidiPlayer;
