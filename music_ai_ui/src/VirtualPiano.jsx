import React, { useState } from 'react';
import { Piano, KeyboardShortcuts, MidiNumbers } from 'react-piano';
import 'react-piano/dist/styles.css';
import SoundfontProvider from './SoundfontProvider';

const VirtualPiano =  React.memo(({ onNoteSelect, parentWidth }) => {
  const [activeNotes, setActiveNotes] = useState([]);
  const audioContext = new (window.AudioContext || window.webkitAudioContext)();
  const soundfontHostname = 'https://d1pzp51pvbm36p.cloudfront.net';

  const firstNote = MidiNumbers.fromNote('c0');
  const lastNote = MidiNumbers.fromNote('g9');

  const keyboardShortcuts = KeyboardShortcuts.create({
    firstNote: firstNote,
    lastNote: lastNote,
    keyboardConfig: KeyboardShortcuts.HOME_ROW,
  });

  return (
    <SoundfontProvider
      instrumentName="acoustic_grand_piano"
      audioContext={audioContext}
      hostname={soundfontHostname}
      onNoteSelect={onNoteSelect}
      render={({ isLoading, playNote, stopNote }) => (
        <Piano
          noteRange={{ first: firstNote, last: lastNote }}
          width={parentWidth}
          playNote={playNote}
          stopNote={stopNote}
          disabled={isLoading}
        />
      )}
    />
  );
});

export default VirtualPiano;
