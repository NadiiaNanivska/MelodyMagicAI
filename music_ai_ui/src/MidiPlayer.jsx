import React from 'react';
import 'html-midi-player';
const MidiPlayer = () => {
    return (
        <section id="section1">
            {/* <midi-visualizer 
                type="staff" 
                src="http://localhost:8000/output.mid">
            </midi-visualizer> */}

            <midi-player 
                src="http://localhost:8000/output.mid" 
                sound-font >
                // visualizer="#section1 midi-visualizer"
            </midi-player>
        </section>
    );
};

export default MidiPlayer;
