const HarmonizeMelody = ({ uploadedMidiRef }) => {
    return (
        <div>
            <h2>Harmonize Melody</h2>
            {uploadedMidiRef.current 
                ? <p>🎵 MIDI File Loaded: Ready to Harmonize</p> 
                : <p>No MIDI file uploaded.</p>}
        </div>
    );
};

export default HarmonizeMelody;
