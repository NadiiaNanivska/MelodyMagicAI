import numpy as np
import tensorflow as tf


def predict_next_note(
    notes: np.ndarray,
    model: tf.keras.Model,
    temperature: float = 1.0) -> tuple[int, float, float]:
  """Generates a note as a tuple of (pitch, step, duration), using a trained sequence model."""

  assert temperature > 0

  # Add batch dimension
  inputs = tf.expand_dims(notes, 0)

  predictions = model.predict(inputs)
  pitch_logits = predictions['pitch']
  step = predictions['step']
  duration = predictions['duration']
  interval = predictions['interval']
  velocity = predictions['velocity']
  polyphony_logits = predictions['polyphony']

  # Process pitch with temperature scaling and categorical sampling
  pitch_logits /= temperature
  pitch = tf.random.categorical(pitch_logits, num_samples=1)
  pitch = tf.squeeze(pitch, axis=-1)

  # Extract and squeeze other predictions
  duration = tf.squeeze(duration, axis=-1)
  step = tf.squeeze(step, axis=-1)
  interval = tf.squeeze(interval, axis=-1)
  velocity = tf.squeeze(velocity, axis=-1)

  # Polyphony is treated as classification Problem
  polyphony_logits = predictions['polyphony']
  polyphony = tf.random.categorical(polyphony_logits, num_samples=1)
  polyphony = tf.squeeze(polyphony, axis=-1)

  # `step` and `duration` values should be non-negative
  step = tf.maximum(0, step)
  duration = tf.maximum(0, duration)
  velocity = tf.maximum(0, velocity)
  polyphony = tf.maximum(0, polyphony)


  return int(pitch), float(step), float(duration), float(interval), float(velocity), int(polyphony)


#Generate Polyphony
def extend_scale(scale, octaves=2):
    """Extends the scale by repeating it across multiple octaves."""
    extended_scale = scale.copy()
    for octave in range(1, octaves):
        # Add the scale shifted by 12 semitones per octave
        extended_scale = np.concatenate((extended_scale, scale + 12 * octave))
    return extended_scale

def generate_chord_tones(root_pitch, num_notes, scale):
    """
    Generates a list of pitches that form a chord based on the given scale.
    """
    # Make sure we don't try to sample more notes than are available in the scale
    num_notes = min(num_notes, len(scale))

    chord_tones = np.random.choice(scale, num_notes, replace=False)
    chord_tones = np.sort(chord_tones)  # Sort to maintain harmonic structure

    return [int((root_pitch + interval) % 128) for interval in chord_tones]

def generate_harmonic_intervals(root_pitch, num_intervals):
    """
    Generates a list of pitches based on harmonic intervals from the root pitch.
    Could be improved to fit within a specific scale or mode.
    """
    # Define common intervals for simplicity: major third, perfect fifth, and octave
    intervals = [4, 7, 12]
    return [(root_pitch + interval) % 128 for interval in np.random.choice(intervals, num_intervals)]


