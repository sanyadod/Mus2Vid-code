import pretty_midi as pm
import matplotlib.pyplot as plt
# Env variables
chrom_notes = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'] # A list of all the notes/pitch classes with
                                                                                # indices corresponding to 
                                                                                # MIDI note values mod 12

offsets = { # A list of chord intervals with their corresponding MIDI note value offset
    '1': 0, 
    '2': 2,
    '3': 4,
    '4': 5,
    '5': 7,
    '6': 9,
    '7': 11,
    '8': 12,
    '9': 14,
    '10': 16,
    '11': 17,
    '12': 19,
    '13': 21
}

# Returns the first note by time in a list of notes
def first_note(notes):
    if notes == []:
        return None
    f_note = notes[0]
    for i in range(1, len(notes)):
        if notes[i].start < f_note.start:
            f_note = notes[i]
    return f_note

# Returns the last note by time in a list of notes
def last_note(notes):
    if notes == []:
        return None
    l_note = notes[0]
    for i in range(1, len(notes)):
        if notes[i].start > l_note.start:
            l_note = notes[i]
    return l_note

# Returns a list of all the non-drum notes in a song regardless of instrument
def consolidate_notes(song):
    notes = []
    for instrument in song.instruments:
        if not instrument.is_drum:
            for note in instrument.notes:
                notes.append(note)
    return notes

# Returns a note name based on its MIDI note number
def get_note(note_n):
    return chrom_notes[note_n % 12]

# Returns the note corresponding to a particular degree in a scale defined by the root note
def parse_chord(root, number_string):
    note_num = chrom_notes.index(root)
    out = ""
    num = ""
    scale_num = 0
    parentheses = False
    for char in number_string:
        if char == '(':
            parentheses = True
        if char == 'b':
            scale_num -= 1
        if char == '#':
            scale_num += 1
        if char >= '0' and char <= '9':
            num += char
    scale_num += offsets.get(num)
    if (parentheses):
        out = "("
    out += str(get_note(note_num + scale_num))
    if (parentheses):
        out += ")"
    return out

# Outputs the master chord list (dict version)
def generate_chord_list(filepath = "chords without names.txt"):
    chord_list = []
    for note in chrom_notes:
        f = open(filepath)
        lines = f.readlines()
        for line in lines:
            parts = line.split()
            chord_name = ''
            note_list = []
            for i in range(len(parts)):
                part = parts[i]
                if i == 0:
                    chord_name = part.replace('_', note, 1)
                elif part[0] == 'b' or part[0] == '#' or \
                   (part[0] >= '0' and part[0] <= '9') or \
                   part[0] == '(':
                    note_list.append(parse_chord(note, part))
                else: continue
            chord_list.append([chord_name, note_list])
    return chord_list

# Gets the chords in a song
def get_chords(notes, 
               offset = 0.01):
    start_times = []
    for note in notes:
        if not (note.start in start_times):
            start_times.append(note.start)
    chords = []
    for time in start_times:
        playing_notes = []
        actual = time + offset # Offset is a parameter shifting the time selected for to allow chords to be picked up
        for note in notes:
            if note.start < actual and note.end >= time:
                song.instruments[0].notes
                playing_notes.append(note)
        chords.append(playing_notes)
    return chords

# Gets the chords in a song
def get_chords_window(notes, 
                      offset = 0.01,
                      window = 0.5):
    start_times = []
    for note in notes:
        if not (note.start in start_times):
            start_times.append(note.start)
    chords = []
    for time in start_times:
        playing_notes = []
        # Offset is a parameter shifting the time selected for to allow chords to be picked up
        # Window is a parameter allowing notes behind the current to be picked up
        for note in notes:
            if note.start < time + offset and note.end >= time - window:
                song.instruments[0].notes
                playing_notes.append(note)
        chords.append(playing_notes)
    return chords

# Generates note scores for the piece
def get_note_scores(notes, 
                    octave_multiplier_on = False,
                    end_multiplier_on = False):
    note_scores_octave_agn = []
    note_scores_octave_agn_dict = dict()
    last_start = last_note(notes).start
    first_start = first_note(notes).start
    last_end = last_note(notes).start
    overall_dur = last_end - first_start
    overall_dur_minus_last = last_start - first_start
    for i in range(0, 12):
        note_scores_octave_agn.append(0) # Create bins for each note
    for note in notes:
        duration = note.end - note.start
        score = duration * note.velocity / 127
        octave_multiplier = 1
        end_multiplier = 1
        if octave_multiplier_on: # Reduce the score of the note the higher up in pitch it is
            octave_multiplier = max(0, 1 - (max(0, (round(note.pitch / 12) - 2) / 8.0)))
        if end_multiplier_on: # Reduce the score of the note the farther away it is from the last note
            end_multiplier = (note.start - first_start) / overall_dur_minus_last
        score *= octave_multiplier
        score *= end_multiplier
        note_scores_octave_agn[note.pitch % 12] += score # Add the note scores by pitch class
    for i in range(0, 12):
        if note_scores_octave_agn[i] != 0:
            note_scores_octave_agn_dict[i] = note_scores_octave_agn[i]

    return note_scores_octave_agn_dict, overall_dur, last_end, first_start
    
# Generates chord scores based on note scores
def get_chord_scores(chord_list, 
                     note_scores_octave_agn_dict, 
                     overall_dur,
                     parentheses_multiplier = 1,
                     min_note_threshold = 0.1, 
                     missing_deweight = 0.5, 
                     root_note_multiplier = 2):
    chord_scores_dict = {}
    for chord_tuple in chord_list:
        chord_name = chord_tuple[0]
        chord_notes = chord_tuple[1]
        chord_score = 0.0
        for i in range(0, len(chord_notes)):
            note = chord_notes[i]
            multiplier = 1 # A multiplier for the note score when calculating chord matchups
            actual_note = note
            if note[0] == '(':
                multiplier = parentheses_multiplier
                actual_note = note[1 : (len(note) - 1)]
            if i == 0: # If the note is the root note, weight that pitch specifically
                multiplier *= root_note_multiplier
            note_val = chrom_notes.index(actual_note)
            note_score = note_scores_octave_agn_dict.get(note_val, 0) # Grab the actual note score
            if note_score <= min_note_threshold: # Deweight chords with missing notes
                note_score = -1 * missing_deweight
            chord_score += note_score * multiplier # Multiply by the multiplier and sum to the chord score
        if chord_score > 0.0:
            chord_scores_dict[chord_name] = chord_score
    chord_scores_dict_sorted = sorted(chord_scores_dict.items(), key=lambda x:x[1], reverse = True) # Sort the chords
                                                                                                    # by score
    return chord_scores_dict_sorted

# Makes a list of all the chords in a song
def calculate_song_chords(song):
    all_chords = generate_chord_list()
    chord_list = []
    for chord in get_chords(song.instruments[0].notes):
        note_dict, overall_dur, last_end, first_start = get_note_scores(chord)
        
        chord_scores = get_chord_scores(all_chords, note_dict, last_end)
        if chord_scores != []:
            chord = chord_scores[:1][0][0] # Grab the top detected chord for each chord event
            if chord != "":
                chord_list.append(chord)
    return chord_list

# Returns n-grams of the items of a list (used in this case to make chord-grams)
def n_grams(my_list, n):
    items = []
    for i in range(0, len(my_list) - n):
        n_gram = []
        for j in range(i, i + n):
            n_gram.append(my_list[j])
        items.append(n_gram)
    return items

# Returns the number of chord changes per second on average of a song
def chord_changes(chord_list, song):
    notes = song.instruments[0].notes
    duration = last_note(notes).end - first_note(notes).start
    chord_changes_per_time = (len(chord_list) - 1) / duration
    return chord_changes_per_time