import React from 'react';
import 'html-midi-player';

const MidiPlayer = ({ showMidiPlayer, harmonizedMidiUrl }) => {
    return (
        <section style={{ margin: '35px 0 0 0' }} id="section1">
            <midi-visualizer
                type="staff"
                src="https://cdn.jsdelivr.net/gh/cifkao/html-midi-player@2b12128/twinkle_twinkle.mid">
            </midi-visualizer>
            {showMidiPlayer &&
                (<midi-player
                    src="https://www.mfiles.co.uk/downloads/fur-elise.mid"
                    sound-font></midi-player>)}
        </section>
    );
};

export default MidiPlayer;
