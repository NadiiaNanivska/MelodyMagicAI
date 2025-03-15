import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import Soundfont from 'soundfont-player';

const SoundfontProvider = ({
  instrumentName,
  hostname,
  format = 'mp3',
  soundfont = 'MusyngKite',
  audioContext,
  render,
  onNoteSelect
}) => {
  const [instrument, setInstrument] = useState(null);
  const [activeAudioNodes, setActiveAudioNodes] = useState({});
  const [noteDurations, setNoteDurations] = useState({});

  const loadInstrument = useCallback((instrumentName) => {
    setInstrument(null);
    Soundfont.instrument(audioContext, instrumentName, {
      format,
      soundfont,
      nameToUrl: (name, soundfont, format) => {
        return `${hostname}/${soundfont}/${name}-${format}.js`;
      },
    }).then((instrument) => {
      setInstrument(instrument);
    });
  }, [audioContext, format, soundfont, hostname]);

  useEffect(() => {
    loadInstrument(instrumentName);
  }, [instrumentName, loadInstrument]);

  const playNote = (midiNumber) => {
    audioContext.resume().then(() => {
      const audioNode = instrument.play(midiNumber);
      const startTime = Date.now();

      setActiveAudioNodes((prevNodes) => ({
        ...prevNodes,
        [midiNumber]: audioNode,
      }));

      setNoteDurations((prevDurations) => ({
        ...prevDurations,
        [midiNumber]: { startTime, duration: null },
      }));
    });
  };

  const stopNote = (midiNumber) => {
    audioContext.resume().then(() => {
      const audioNode = activeAudioNodes[midiNumber];
      if (!audioNode) return;

      audioNode.stop();

      const endTime = Date.now();
      const duration = endTime - noteDurations[midiNumber].startTime;
      console.log(`Note ${midiNumber} duration: ${duration}ms`);

      onNoteSelect({
        pitch: midiNumber,
        duration: duration / 1000,
        velocity: 100,
      });

      setActiveAudioNodes((prevNodes) => ({
        ...prevNodes,
        [midiNumber]: null,
      }));

      setNoteDurations((prevDurations) => ({
        ...prevDurations,
        [midiNumber]: {
          ...prevDurations[midiNumber],
          duration,
        },
      }));
    });
  };

  const stopAllNotes = () => {
    audioContext.resume().then(() => {
      Object.values(activeAudioNodes).forEach((node) => {
        if (node) {
          node.stop();
        }
      });

      setActiveAudioNodes({});
      setNoteDurations({});
    });
  };

  return render({
    isLoading: !instrument,
    playNote,
    stopNote,
    stopAllNotes,
    noteDurations,
  });
};

SoundfontProvider.propTypes = {
  instrumentName: PropTypes.string.isRequired,
  hostname: PropTypes.string.isRequired,
  format: PropTypes.oneOf(['mp3', 'ogg']),
  soundfont: PropTypes.oneOf(['MusyngKite', 'FluidR3_GM']),
  audioContext: PropTypes.instanceOf(window.AudioContext),
  render: PropTypes.func.isRequired,
};

export default SoundfontProvider;