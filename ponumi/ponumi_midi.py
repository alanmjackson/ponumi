"""Functions for converting Ponumi poems to midi."""

from ponumi import flatten
from ponumi import load_poem_file
from ponumi import poem_list_to_notes

from miditime.MIDITime import MIDITime

_default_tempo = 120    #BPM


def notes_to_midi_file(note_list, filename, tempo=_default_tempo):
    """Creates a midi file from a list of notes."""
    midifile = MIDITime(_default_tempo, filename)
    
    time = 0
    midi_event_list = []

    note_list = flatten(note_list)      #flatten the note list
    for note in note_list:
        midi_event_list.append([time, note, 200, 1])
        time += 1
    
    midifile.add_track(midi_event_list)
    midifile.save_midi()


def convert_poem_file_to_midi_file(poem_file, midi_file):
    """
    Converts a poem file to a list of notes and then writes a midi file
    consisting of those notes. 
    """
    poem = load_poem_file(poem_file)
    notes = poem_list_to_notes(poem)
    notes_to_midi_file(notes, midi_file)


def main():
    print "ponumi!"

    args = sys.argv[1:]
    if len(args) != 2: 
        print usage
        sys.exit("incorrect arguments")
    else:
        convert_poem_file_to_midi_file(args[0], args[1])


if __name__ == '__main__':
    main()

