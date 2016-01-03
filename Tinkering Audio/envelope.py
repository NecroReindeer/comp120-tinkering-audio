
from enum import Enum

import time

class Envelope(object):
    def __init__(self, type, attack_length, decay_length, sustain_level, sustain_length, release_length):
        """Initialise the fields.

        Arguments:
        type: the type of the envelope (frequency or amplitude) as an EnvelopeType
        attack_length: the length of the attack as a float representing the proportion of the sound
        decay_length: the length of the decay as a float representing the proportion of the sound
        sustain level: the sustain level. Use the absolute value for amplitude, or the number of
        semitones difference for frequency
        sustain_length: the length of the sustain as a float representing the proportion of the sound
        release_length: the length of the release as a float representing the proportion of the sound
        """
        self.type = type
        self.attack_length = attack_length
        self.decay_length = decay_length
        self.sustain_level = sustain_level
        self.sustain_length = sustain_length
        self.release_length = release_length

    def get_value(self, default_value, sample_index, number_of_samples):
        """Return the appropriate amplitude value according to the envelope  phase times
        Arguments:
        default value -- the default amplitude or frequency of the tone
        sample_index -- the index of the sample the envelope will be applied to
        number_of_samples -- the total number of samples in the tone
        """
        attack_length = self.attack_length * number_of_samples
        decay_length = self.decay_length * number_of_samples
        sustain_length =  self.sustain_length * number_of_samples
        release_length =  self.release_length * number_of_samples

        decay_start = attack_length
        release_start = attack_length + decay_length + sustain_length

        phase = self.get_phase(sample_index, number_of_samples)

        if self.type == EnvelopeType.amplitude:
            if self.sustain_level == 0:
                sustain_level = default_value
            else:
                sustain_level = self.sustain_level
        else:
            sustain_level = self.get_frequency_sustain_level(default_value)

        if phase == EnvelopePhase.attack:
            envelope = float(sample_index / float(attack_length))
            new_value = default_value * envelope
            if self.type == EnvelopeType.frequency and new_value == 0:
                return 1
            else:
                return new_value

        if phase == EnvelopePhase.decay:
            envelope = 1.0 - (float(sample_index - decay_start) / float(decay_length))
            new_value = default_value * envelope
            if new_value < sustain_level:
                return sustain_level
            else:
                return new_value

        if phase == EnvelopePhase.sustain:
            new_value = sustain_level
            return new_value

        if phase == EnvelopePhase.release:
            envelope = 1.0 - (float(sample_index - release_start) / float(release_length))
            new_value = envelope * sustain_level
            return new_value

    def get_frequency_sustain_level(self, default_frequency):
        if self.sustain_level == 0:
            return default_frequency
        else:
            INTERVAL = 2.0**(1.0/12.0)
            frequency = default_frequency * INTERVAL ** self.sustain_level
            return frequency

    def get_phase(self, sample_index, number_of_samples):
        """Return the phase of the given sample number"""
        attack_end = self.attack_length * number_of_samples
        decay_end = attack_end + self.decay_length * number_of_samples
        sustain_end = decay_end + self.sustain_length * number_of_samples
        release_end = sustain_end + self.release_length * number_of_samples

        if sample_index < attack_end:
            return EnvelopePhase.attack

        if sample_index < decay_end:
            return EnvelopePhase.decay

        if sample_index < sustain_end:
            return EnvelopePhase.sustain

        if sample_index < release_end:
            return EnvelopePhase.release


class EnvelopePhase(Enum):
    """Enum for different envelope phases"""
    attack = 0
    decay = 1
    sustain = 2
    release = 3

class EnvelopeType(Enum):
    """Enum for different envelope types"""
    amplitude = 0
    frequency = 1
