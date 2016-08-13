"""
ponumi, from Names to Poems

Can be called from the command line to convert poems to midi files.

usage: python ponumi.py POEM_FILE MIDI_FILE

POEM_FILE is the input file. Each syllable must be separated by whitespace. 
MIDI_FILE is the name of the output midi file to be created. 

ponumi requires installation of the miditime package.
The unit test requires installation of the midi package. 

These can be installed using pip:

    $ pip install miditime midi

On Ubuntu 12.04 pip failed to install midi. To install it download it from:
https://github.com/vishnubob/python-midi/archive/v0.2.3.zip

then I had to comment out the following line near the bottom of setup.py:

#setup_alsa(ns)


@author: Alan M Jackson & Jake Harper
"""


import sys
import random
import collections



POEM_ROOT_LENGTH = 8

ANCHOR = "a"
RHYME = "o"
OFF_RHYME = "x"


a = ANCHOR
o = RHYME
x = OFF_RHYME

RHYMING_SCHEME = ((o, x, o, o, x, x, a, o, x, o, o, x),
                  (o, o, x, x, x, o, a, o, o, x, x, a),
                  (o, o, x, x, o, o, x, x, o, o, x, x),
                  (o, x, o, o, x, x, a, o, x, x, o, a))

null_syllables = ['-']
ending_syllables = ["n"]

syllable_left_roots = ["b", "ch", "d", "f", "g", "h", "j", "k", "m", "n", 
                       "p", "r", "s", "sh", "t", "v", "w", "y", "z"]

syllable_right_roots = ["a", "e", "i", "o", "u"]

syllable_table = [null_syllables]
syllable_table.append(syllable_right_roots)
for left_root in syllable_left_roots:
    syllable_row = []
    for right_root in syllable_right_roots:
        syllable_row.append(left_root + right_root)
    syllable_table.append(syllable_row)

syllable_table.append(ending_syllables)

syllable_list = []
for row in syllable_table:
    syllable_list = syllable_list + row

# the list of syllables with corresponding note numbers
syllables = dict( zip(syllable_list, range(0, len(syllable_list)) ) )


'''
The constructed syllable list with note numbers.
This list can be generated using note_table_to_string().

 :      0
a:      1
e:      2
i:      3
o:      4
u:      5
ba:     6
be:     7
bi:     8
bo:     9
bu:    10
cha:   11
che:   12
chi:   13
cho:   14
chu:   15
da:    16
de:    17
di:    18
do:    19
du:    20
fa:    21
fe:    22
fi:    23
fo:    24
fu:    25
ga:    26
ge:    27
gi:    28
go:    29
gu:    30
ha:    31
he:    32
hi:    33
ho:    34
hu:    35
ja:    36
je:    37
ji:    38
jo:    39
ju:    40
ka:    41
ke:    42
ki:    43
ko:    44
ku:    45
ma:    46
me:    47
mi:    48
mo:    49
mu:    50
na:    51
ne:    52
ni:    53
no:    54
nu:    55
pa:    56
pe:    57
pi:    58
po:    59
pu:    60
ra:    61
re:    62
ri:    63
ro:    64
ru:    65
sa:    66
se:    67
si:    68
so:    69
su:    70
sha:   71
she:   72
shi:   73
sho:   74
shu:   75
ta:    76
te:    77
ti:    78
to:    79
tu:    80
va:    81
ve:    82
vi:    83
vo:    84
vu:    85
wa:    86
we:    87
wi:    88
wo:    89
wu:    90
ya:    91
ye:    92
yi:    93
yo:    94
yu:    95
za:    96
ze:    97
zi:    98
zo:    99
zu:   100
n:    101
'''

usage = "ponumi.py POEM_FILE MIDI_FILE"


class Poem:
    def __init__(self, syllables, root_name=None, ancestors=None, 
                 root=None, rhyming_scheme=None):

        self.syllables = syllables
        self.root_name = root_name
        self.ancestors = ancestors
        self.root = root
        self.rhyming_scheme = rhyming_scheme
    
    def to_string(self):
        """
        Create a string representation of a poem. 
        """

        poem_str = ""
        for line in self.syllables:
            line_str = ""
            for syllable in line:
                line_str = line_str + syllable + " "
            poem_str = poem_str + line_str.strip() + "\n"

        return poem_str.strip()


def note_table_to_string():
    """
    Creates a string representation of the list of syllables with associated
    note numbers. 
    """
    table_str = ""

    sorted_syllable_list = sorted(syllables.items(), key=lambda syl: syl[1])
    for syllable in sorted_syllable_list:
        syllable_str = syllable[0] + ":"
        note_str = str(syllable[1])
        table_str = table_str + syllable_str.ljust(5) + note_str.rjust(4) + "\n"

    return table_str


def poem_list_to_notes(poem_list):
    """Takes a list of syllables as an argument and 
       returns a list of note numbers. """
    notes = []
    for item in poem_list:
        #if a poem has a nested list then recursively convert that to notes. 
        if isinstance(item, list):
            notes.append(poem_list_to_notes(item))
        else:
            notes.append(syllables[item])
        
    return notes


def load_poem_file(filename):
    """Open a poem file and return a list of its syllables"""
    f = open(filename, "r")
    lines = []
    for line in f:
        lines.append(line.split())

    return lines


def load_rhyming_scheme(filename):
    """Open a rhyming scheme file and return it as a tuple of tuples.
    The whole poem is a tuple of lines and each line is a tuple of 
    syllable markers: ponumi.a, ponumi.o or ponumi.x."""
    f = open(filename, "r")
    lines = []
    for line in f:
        lines.append(tuple(line.split()))

    return tuple(lines)


def flatten(in_list):
    """
    Flattens lists so that a list of lists becomes just a flat list of all the 
    items of all the contained lists.
    For example:

    [[1,2], [3,4]]  ->   [1, 2, 3, 4]
    """
    for element in in_list:
        if isinstance(element, collections.Iterable) and not isinstance(element, basestring):
            for sub in flatten(element):
                yield sub
        else:
            yield element


def create_syllable_list(syllable_lists, size):
    """
    Takes a list of syllable lists and creates a single syllable list, the length is 
    determined by the size argument. 

    Syllables are taken from each list, in order, until the length specified by the size
    argument is reached. 
    
    The result is a list of syllables.

    eg.
    >>> create_syllable_list([["po", "nu", "mi"], ["ka", "ki", "ku"], ["ga", "gi", "gu"]], 8)
    ["po", "nu", "mi", "ka", "ki", "ku", "ga", "gi"]

    If there are less than the required number of syllables in the list arguments
    then syllables are repeated.

    Returns None if there are no syllables in any of the given arguments 
    """

    syllable_list = []
    while len(syllable_list) < size:
        for s_list in syllable_lists:
            syllable_list = syllable_list + s_list[:size - len(syllable_list)]

        #if there are no syllables in any of the given arguments then return None
        if len(syllable_list) == 0:
            return None

    return syllable_list


def mark_root_syllables(root_syllables, root_scheme=None):
    """
    Takes a list of root syllables and returns a poem root, which is a marked
    up list of syllables. If no marking scheme is given, a default random marking 
    scheme is used. 
    """
    if root_scheme == None:
        return mark_root_randomly(root_syllables)

    poem_root = []
    for i in range(len(root_syllables)):
        
        if i < len(root_scheme):
            marking = root_scheme[i]
        else:
            marking = x

        poem_root.append([root_syllables[i], marking])

    return poem_root


def mark_root_randomly(root_syllables):
    """
    Implements the default random root marking scheme.
    """
    assert len(root_syllables) == POEM_ROOT_LENGTH, "argument is not " + POEM_ROOT_LENGTH + " syllables."
    poem_root = [ [root_syllables[0], ANCHOR] ]
    
    root_syllables = root_syllables[1:]

    rhyme_positions = random.sample(range(1, len(root_syllables) + 1), 2)

    for syllable in root_syllables:
        poem_root.append([syllable, OFF_RHYME])

    for rhyme_position in rhyme_positions:
        poem_root[rhyme_position][1] = RHYME

    return poem_root


def create_poem_root(names, root_scheme=None, size=POEM_ROOT_LENGTH):
    """
    Takes a name and a list of ancestors names and creates a poem root. 
    The name argument is a list of syllables.
    The ancestors argument is a list of names, each of which is a list of syllables.
    The result is a poem root, which is list of marked syllables 
    of the form ["po", a], where 'a' is ponumi.ANCHOR. 

    eg:

    [["po", a], ["nu", o], ["mi", x], ["ka", o], ["ki", x], ["ku", x], ["ga", x], ["gi", x]]
    """
    root_syllables = create_syllable_list(names, size)
    poem_root = mark_root_syllables(root_syllables, root_scheme)

    return poem_root


def apply_rhyming_scheme(poem_root, rhyming_scheme):
    """
    Create a poem by applying a rhyming scheme to a poem root. 
    """
    anchors = []
    rhymes = []
    off_rhymes = []
    for syllable in poem_root:
        if syllable[1] == ANCHOR:
            anchors.append(syllable[0])
        elif syllable[1] == RHYME:
            rhymes.append(syllable[0])
        else:
            off_rhymes.append(syllable[0])

    if len(anchors) == 0 or len(rhymes) == 0 or len(off_rhymes) == 0:
        raise ValueError("Bad root scheme. Root scheme must have at least 1 anchor," + \
                         "rhyme and off rhyme.")

    poem = []
    for line in rhyming_scheme:
        anchor_index = 0
        rhyme_index = 0
        off_rhyme_index = 0
        poem_line = []
        for syllable in line:
            if syllable == ANCHOR:
                poem_line.append(anchors[anchor_index])
                anchor_index = (anchor_index + 1) % len(anchors)
            if syllable == RHYME:
                poem_line.append(rhymes[rhyme_index])
                rhyme_index = (rhyme_index + 1) % len(rhymes)
            if syllable == OFF_RHYME:
                poem_line.append(off_rhymes[off_rhyme_index])
                off_rhyme_index = (off_rhyme_index + 1) % len(off_rhymes)
        poem.append(poem_line)

    return poem


def create_poem(root_name, ancestors, root_scheme=None, root_size=POEM_ROOT_LENGTH, 
                rhyming_scheme=None):
    """
    Takes a name, a list of ancestors names and a rhyming scheme. 
    The name argument is a list of syllables.
    The ancestors argument is a list of names, each of which is a list of syllables.
    The result is a Poem object.
    """
    #if no rhyming scheme is given use the default one
    if rhyming_scheme == None:
        rhyming_scheme = RHYMING_SCHEME

    names = [root_name] + ancestors
    poem_root = create_poem_root(names, root_scheme, root_size)
    syllables = apply_rhyming_scheme(poem_root, rhyming_scheme)
    
    poem = Poem(syllables, root_name, ancestors, poem_root, rhyming_scheme)

    return poem


def rhyming_scheme_to_string(scheme):
    """
    Create a string representation of a rhyming scheme
    """

    #This function would be identical to the poem_to_string function
    return Poem(scheme).to_string()


def notes_to_string(notes, separator=" "):
    """
    Create a string representation of a note list.
    """
    note_str = ""
    for item in notes:
        if isinstance(item, list):
            if note_str != "":
                note_str = note_str + "\n"
            note_str = note_str + notes_to_string(item, separator)
        else:
            if note_str != "":
                note_str = note_str + separator
            note_str = note_str + str(item)

    return note_str


def resize_rhyming_scheme(rhyming_scheme, lines=None, columns=None):
    resized_scheme = rhyming_scheme

    if lines != None:
        resized_scheme_list = []
        for i in range(lines):
            resized_scheme_list.append(rhyming_scheme[i % len(rhyming_scheme)])

        resized_scheme = tuple(resized_scheme_list)

    if columns != None:
        resized_scheme_list = []
        for line in resized_scheme:
            resized_line = []
            for j in range(columns):
                resized_line.append(line[j % len(line)])

            resized_scheme_list.append(tuple(resized_line))

        resized_scheme = tuple(resized_scheme_list)

    return resized_scheme


def notes_to_csv(notes):
    """
    Create a CSV (comma separated values) string from a note list.
    """
    note_str = notes_to_string(notes, ", ")
    return note_str




def force_rhyme(forced_syllable, forcing_syllable):
    """
    Forces the first syllable argument to rhyme with the second. 
    Returns the resulting forced syllable.
    In other words, returns the consonant root of the first syllable 
    and the vowel of the second.
    """

    consonant1, vowel1 = split_syllable(forced_syllable)
    consonant2, vowel2 = split_syllable(forcing_syllable)

    #if the forcing syllable is just a consonant (eg. "n"), then force rhyme to "n"
    if vowel2 == "" and consonant2 != "":
        syllable = consonant2
    else:
        syllable = consonant1 + vowel2

    return syllable
    

def split_syllable(syllable):
    """
    Splits a syllable into the consonant and vowels parts.
    Assumes a syllable is formed of:
        just a vowel
        just a consonant
        a consonant followed by a vowel
    """

    vowel = ""
    consonant = syllable

    vowels = syllable_table[0]

    for v in vowels:
        i = syllable.rfind(v)
        if i > -1:
            consonant = syllable[:i]
            vowel = syllable[i:]
            break

    return (consonant, vowel)


def convolve(source_poem, convolver, convolving_scheme=(1,)):
    """
    Convolves a list of syllables, the source, against another
    list of syllables, the convolver and returns the result. 
    The result will be the same shape as the convolve source. 
    Convolve uses the rhyming_scheme to determine which syllables in the source to force
    to rhyme with the appropriate syllable from the convolver. 
    The convolving_scheme determines which syllable from the convolver to use. 

    If no rhyming_scheme is given then all syllables in the source will be forced to rhyme. 

    If not convolving_scheme is given then syllables from the convolver will be matched one 
    to one with syllables from the source.
    """

    i = 0   #poem line index
    j = 0   #syllable index
    c = 0   #convolver syllable index
    d = 0   #span index - position within the span of poem syllables 
            #covered by the current convolver syllable.

    output_poem_syllables = []

    syllables = source_poem.syllables
    rhyming_scheme = source_poem.rhyming_scheme

    for i in range(len(syllables)):

        output_line = []
        for j in range(len(syllables[i])):

            if rhyming_scheme != None:
                if rhyming_scheme[i][j] == a or rhyming_scheme[i][j] == o:
                    output_line.append(force_rhyme(syllables[i][j], convolver[c % len(convolver)]))
                else:
                    output_line.append(syllables[i][j])    
            else:
                output_line.append(force_rhyme(syllables[i][j], convolver[c % len(convolver)]))
            
            d += 1
     
            if d >= convolving_scheme[c % len(convolving_scheme)]:
                c += 1
                d = 0


        output_poem_syllables.append(output_line)
        convolved_poem = Poem(output_poem_syllables, rhyming_scheme=rhyming_scheme)

    return convolved_poem


