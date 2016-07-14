''' 
unit test for ponumi.py
@author: Alan M Jackson & Jake Harper
'''

import unittest
import os

import midi

import ponumi
import ponumi_midi
import ponumi_osc
from ponumi import a as a
from ponumi import o as o
from ponumi import x as x


class Test(unittest.TestCase):
    
    def test_poem_to_note(self):
        poem = [["po", "nu", "mi", "po", "nu", "mi", "po", "nu", "mi", "po", "nu", "mi"],
                ["po", "nu", "mi", "po", "nu", "mi", "po", "nu", "mi", "po", "nu", "mi"],
                ["po", "nu", "mi", "po", "nu", "mi", "po", "nu", "mi", "po", "nu", "mi"],
                ["po", "nu", "mi", "po", "nu", "mi", "po", "nu", "mi", "po", "nu", "mi"]
               ]

        notes = [[59, 55, 48, 59, 55, 48, 59, 55, 48, 59, 55, 48],
                 [59, 55, 48, 59, 55, 48, 59, 55, 48, 59, 55, 48],
                 [59, 55, 48, 59, 55, 48, 59, 55, 48, 59, 55, 48],
                 [59, 55, 48, 59, 55, 48, 59, 55, 48, 59, 55, 48]
                ]

        self.assertTrue(ponumi.poem_list_to_notes(poem) == notes)

    
    def test_flat_poem_list_to_notes(self):
        poem = ["po", "nu", "mi", "po", "nu", "mi", "po", "nu", "mi", "po", "nu", "mi"]

        notes = [59, 55, 48, 59, 55, 48, 59, 55, 48, 59, 55, 48]

        self.assertTrue(ponumi.poem_list_to_notes(poem) == notes)    


    def test_load_poem_file(self):
        poem_list = ponumi.load_poem_file("test/test_poem.txt")
        self.assertTrue(poem_list == [["po", "nu", "mi"], ["po", "nu", "mi"], ["po", "nu", "mi"]])


    def test_load_rhyming_scheme(self):
        expected_scheme = ((x, o, x, x, o, o, x, a, o, x, x, o),
                           (x, x, o, o, o, a, x, x, o, o, a, x),
                           (x, x, o, o, x, x, o, o, x, x, o, o),
                           (x, o, x, x, o, x, o, a, x, o, a, x))

        rhyming_scheme = ponumi.load_rhyming_scheme("test/test_rhyming_scheme.txt")
        self.assertTrue(rhyming_scheme == expected_scheme)
 

    def test_notes_to_midi_file(self):
        test_filename = "test/test.mid"
        
        test_notes = [1, 1, 2, 3, 5]
        ponumi_midi.notes_to_midi_file(test_notes, test_filename)

        pattern = midi.read_midifile(test_filename)
        
        notes = []
        for event in pattern[0]:
            if isinstance(event, midi.NoteOnEvent):
                #if the note is a note_on event, get its note number
                notes.append(event.data[0])

        self.assertTrue(notes == test_notes)
        os.remove(test_filename)    #delete the test file
        

    def test_convert_poem_to_midi_file(self):
        test_filename = "test/test2.mid"
        ponumi_midi.convert_poem_file_to_midi_file("test/test_poem.txt", test_filename)
        
        pattern = midi.read_midifile(test_filename)
        
        notes = []
        for event in pattern[0]:
            if isinstance(event, midi.NoteOnEvent):
                #if the note is a note_on event, get its note number
                notes.append(event.data[0])

        print "notes", notes

        self.assertTrue(notes == [59, 55, 48, 59, 55, 48, 59, 55, 48])
        os.remove(test_filename)    #delete the test file

    def test_create_syllable_list(self):
        root_name = ["po", "nu", "mi"]
        parent1_name = ["ka", "ki", "ku"]
        parent2_name = ["ga", "gi", "gu"]
        poem_root = ponumi.create_syllable_list([root_name, parent1_name, parent2_name], 8)
        self.assertTrue(poem_root == ["po", "nu", "mi", "ka", "ki", "ku", "ga", "gi"])

        root_name = ["po", "nu", "mi", "ka", "ki", "ku", "ga", "gi", "gu"]
        poem_root = ponumi.create_syllable_list([root_name, parent1_name, parent2_name], 8)
        self.assertTrue(poem_root == ["po", "nu", "mi", "ka", "ki", "ku", "ga", "gi"])

        root_name = ["po", "nu", "mi"]
        parent1_name = ["ka", "ki", "ku", "ga", "gi", "gu"]
        parent2_name = []
        poem_root = ponumi.create_syllable_list([root_name, parent1_name, parent2_name], 8)
        self.assertTrue(poem_root == ["po", "nu", "mi", "ka", "ki", "ku", "ga", "gi"])

        root_name = ["po", "nu", "mi"]
        parent1_name = []
        parent2_name = []
        poem_root = ponumi.create_syllable_list([root_name, parent1_name, parent2_name], 8)
        self.assertTrue(poem_root == ["po", "nu", "mi", "po", "nu", "mi", "po", "nu"])

        root_name = []
        parent1_name = []
        parent2_name = []
        poem_root = ponumi.create_syllable_list([root_name, parent1_name, parent2_name], 8)
        self.assertTrue(poem_root == None)

        root_name = ["po", "nu", "mi"]
        parent1_name = ["ki", "ko"]
        parent2_name = ["ku"]
        poem_root = ponumi.create_syllable_list([root_name, parent1_name, parent2_name], 6)
        self.assertTrue(poem_root == ["po", "nu", "mi", "ki", "ko", "ku"])


    def test_mark_root_syllables(self):
        root_syllables = ["po", "nu", "mi", "ka", "ki", "ku", "ga", "gi"]
        poem_root = ponumi.mark_root_syllables(root_syllables)

        first_syllable_attribute = poem_root[0][1]
        self.assertTrue(len(poem_root) == 8)
        self.assertTrue(first_syllable_attribute == ponumi.ANCHOR)

        rhyming_syllables = 0
        off_rhyme_syllables = 0
        for syllable in poem_root:
            if syllable[1] == ponumi.RHYME:
                rhyming_syllables += 1
            elif syllable[1] == ponumi.OFF_RHYME:
                off_rhyme_syllables += 1

        self.assertTrue(rhyming_syllables == 2)
        self.assertTrue(off_rhyme_syllables == 5)


    def test_create_poem_root(self):
        root_name = ["po", "nu", "mi"]
        parent1_name = ["ka", "ki", "ku"]
        parent2_name = ["ga", "gi", "gu"]
        poem_root = ponumi.create_poem_root([root_name, parent1_name, parent2_name])

        self.assertTrue(len(poem_root) == 8)
        first_syllable = poem_root[0][0]
        self.assertTrue(first_syllable == "po")
        first_syllable_attribute = poem_root[0][1]
        self.assertTrue(first_syllable_attribute == ponumi.ANCHOR)


    def test_apply_rhyming_scheme(self):
        poem_root = [["i", "a"], ["vi", "o"], ["ja", "x"], ["ka", "x"], 
                     ["so", "x"], ["n", "o"], ["a", "x"], ["ra", "x"]]
        poem_syllables = ponumi.apply_rhyming_scheme(poem_root, ponumi.RHYMING_SCHEME)

        self.assertTrue(len(poem_syllables) == 4)
        for line in poem_syllables:
            self.assertTrue(len(line) == 12)

        expected_poem = "vi ja n vi ka so i n a vi n ra\n" + \
                        "vi n ja ka so vi i n vi a ra i\n" + \
                        "vi n ja ka vi n so a vi n ra ja\n" + \
                        "vi ja n vi ka so i n a ra vi i"

        self.assertTrue(ponumi.Poem(poem_syllables).to_string() == expected_poem)


    def test_resize_rhyming_scheme(self):
        x = ponumi.x
        a = ponumi.a
        o = ponumi.o
        rhyming_scheme = ((a, x, o),
                          (o, x, x))

        resized_scheme = ponumi.resize_rhyming_scheme(rhyming_scheme, 4)
        expected_scheme = ((a, x, o),
                           (o, x, x),
                           (a, x, o),
                           (o, x, x))

        self.assertTrue(expected_scheme == resized_scheme)


        resized_scheme = ponumi.resize_rhyming_scheme(rhyming_scheme, 7)
        expected_scheme = ((a, x, o),
                           (o, x, x),
                           (a, x, o),
                           (o, x, x),
                           (a, x, o),
                           (o, x, x),
                           (a, x, o))

        self.assertTrue(expected_scheme == resized_scheme)


        resized_scheme = ponumi.resize_rhyming_scheme(rhyming_scheme, 1)
        expected_scheme = ((a, x, o),)
        self.assertTrue(expected_scheme == resized_scheme)


        resized_scheme = ponumi.resize_rhyming_scheme(rhyming_scheme, columns=2)
        expected_scheme = ((a, x),
                           (o, x))

        self.assertTrue(expected_scheme == resized_scheme)


        resized_scheme = ponumi.resize_rhyming_scheme(rhyming_scheme, 3, 5)
        expected_scheme = ((a, x, o, a, x),
                           (o, x, x, o, x),
                           (a, x, o, a, x))

        self.assertTrue(expected_scheme == resized_scheme)



    def test_create_poem(self):
        root_name = ["po", "nu", "mi"]
        parent1_name = ["ka", "ki", "ku"]
        parent2_name = ["ga", "gi", "gu"]
        poem = ponumi.create_poem(root_name, [parent1_name, parent2_name])        

        self.assertTrue(len(poem.syllables) == 4)
        for line in poem.syllables:
            self.assertTrue(len(line) == 12)


    def test_note_list_to_kyma_osc(self):
        s = ponumi_osc.osc_scaling
        self.assertTrue(type(ponumi_osc.notelist_to_kyma_osc([1])[0]) is float )
        self.assertTrue(ponumi_osc.notelist_to_kyma_osc([1, 2, 3, 4]) == [1/s, 2/s, 3/s, 4/s])

        notelist = [[ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12],
                    [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
                    [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
                    [37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48]
                   ]

        expected_osc = [ 1/s,  2/s,  3/s,  4/s,  5/s,  6/s,  7/s,  8/s,  9/s, 10/s, 11/s, 12/s,
                        13/s, 14/s, 15/s, 16/s, 17/s, 18/s, 19/s, 20/s, 21/s, 22/s, 23/s, 24/s,
                        25/s, 26/s, 27/s, 28/s, 29/s, 30/s, 31/s, 32/s, 33/s, 34/s, 35/s, 36/s,
                        37/s, 38/s, 39/s, 40/s, 41/s, 42/s, 43/s, 44/s, 45/s, 46/s, 47/s, 48/s
                       ]

        osc = ponumi_osc.notelist_to_kyma_osc(notelist)
        self.assertTrue(expected_osc == osc)


    def test_split_syllable(self):
        consonant, vowel = ponumi.split_syllable("ku")
        self.assertTrue(consonant == "k")
        self.assertTrue(vowel == "u")

        consonant, vowel = ponumi.split_syllable("a")
        self.assertTrue(consonant == "")
        self.assertTrue(vowel == "a")

        consonant, vowel = ponumi.split_syllable("n")
        self.assertTrue(consonant == "n")
        self.assertTrue(vowel == "")



    def test_force_rhyme(self):
        self.assertTrue(ponumi.force_rhyme("ku", "mi") == "ki")
        self.assertTrue(ponumi.force_rhyme("po", "nu") == "pu")
        self.assertTrue(ponumi.force_rhyme("ku", "a") == "ka")
        self.assertTrue(ponumi.force_rhyme("n", "pa") == "na")
        self.assertTrue(ponumi.force_rhyme("ku", "n") == "n")
        self.assertTrue(ponumi.force_rhyme("a", "pu") == "u")


    def test_simple_convolve(self):

        #simple case with no rhyming or convolving scheme and a one syllable convolver
        source = [["po", "nu", "mi"],
                  ["mi", "po", "nu"],
                  ["nu", "mi", "po"]]

        poem = ponumi.Poem(source)

        convolver = ["ja"]

        expected_poem = [["pa", "na", "ma"],
                         ["ma", "pa", "na"],
                         ["na", "ma", "pa"]]
  

        convoled_poem = ponumi.convolve(poem, convolver)
        self.assertTrue(convoled_poem.syllables == expected_poem)

    def test_convolve_with_rhyming_scheme(self):
        #using a rhyming scheme
        source = [["po", "nu", "mi"],
                  ["mi", "po", "nu"],
                  ["nu", "mi", "po"]]

        rhyming_scheme = (("a", "o", "x"),
                          ("x", "a", "o"),
                          ("o", "x", "a"))

        poem = ponumi.Poem(source, rhyming_scheme=rhyming_scheme)

        convolver = ["ja"]


        expected_poem = [["pa", "na", "mi"],
                         ["mi", "pa", "na"],
                         ["na", "mi", "pa"]]

        convoled_poem = ponumi.convolve(poem, convolver)
        self.assertTrue(convoled_poem.syllables == expected_poem)


    def test_multi_syllable_convolve(self):
        #using a rhyming scheme with a multi-syllable convolver
        source = [["po", "nu", "mi"],
                  ["mi", "po", "nu"],
                  ["nu", "mi", "po"]]

        rhyming_scheme = (("a", "o", "x"),
                          ("x", "a", "o"),
                          ("o", "x", "a"))

        poem = ponumi.Poem(source, rhyming_scheme=rhyming_scheme)
        
        convolver = ["ja", "ku", "ha", "ru", "pe", "ru"]


        expected_poem = [["pa", "nu", "mi"],
                         ["mi", "pe", "nu"],
                         ["na", "mi", "pa"]]

        convoled_poem = ponumi.convolve(poem, convolver)
        self.assertTrue(convoled_poem.syllables == expected_poem)


    def test_convolve(self):

        #using a rhyming scheme and a convolving scheme
        source = [["po", "nu", "mi"],
                  ["mi", "po", "nu"],
                  ["nu", "mi", "po"]]

        rhyming_scheme = (("a", "o", "x"),
                          ("x", "a", "o"),
                          ("o", "x", "a"))

        poem = ponumi.Poem(source, rhyming_scheme=rhyming_scheme)

        convolver = ["ja", "ku", "ha", "ru", "pe", "ru"]
        
        convolving_scheme = (1, 2)

        expected_poem = [["pa", "nu", "mi"],
                         ["mi", "pu", "nu"],
                         ["ne", "mi", "pu"]]

        convoled_poem = ponumi.convolve(poem, convolver, convolving_scheme)

        self.assertTrue(convoled_poem.syllables == expected_poem)


    def test_root_scheme(self):
        root = ["ja", "ku", "ha", "ru", "pe", "ru"]
        root_scheme = (x, o, a, o, x, o)

        poem_root = ponumi.mark_root_syllables(root, root_scheme)
        expected_root = [["ja", x], ["ku", o], ["ha", a], ["ru", o], ["pe", x], ["ru", o]]

        self.assertTrue(poem_root == expected_root)


    def test_create_poem_with_root_scheme(self):
        root_name = ["ja", "ku", "ha", "ru", "pe", "ru"]
        ancestors = []
        root_scheme = (a, o, x, o, x, o)
        root_size = 6
        rhyming_scheme = ((a, o, x, o, x, o),
                          (a, o, o, o, x, x),
                          (a, x, x, x, x, o))

        expected_poem = [["ja", "ku", "ha", "ru", "pe", "ru"],
                         ["ja", "ku", "ru", "ru", "ha", "pe"],
                         ["ja", "ha", "pe", "ha", "pe", "ku"]]

        poem = ponumi.create_poem(root_name, ancestors, root_scheme, root_size, rhyming_scheme)

        self.assertTrue(poem.syllables == expected_poem)






if __name__ == "__main__":
    unittest.main()
    


