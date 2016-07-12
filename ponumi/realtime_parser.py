'''This is just a first experiment or spike. 
It's not part of the ponumi application yet.'''

import curses

import ponumi



def valid_next_char(context):

    valid_next_chars = []
    for syllable in ponumi.syllable_list:

        if syllable.startswith(context):
            next_char_index = len(context)
            if len(syllable) > next_char_index:
                valid_next_chars.append(syllable[next_char_index])

    return valid_next_chars


def get_possible_syllables(context):

    possible_syllables = []
    for syllable in ponumi.syllable_list:

        if syllable.startswith(context):
            possible_syllables.append(syllable)   

    return possible_syllables 




def main(stdscr):
    stdscr.addstr("hello world\n")

    syllable_so_far = ""

    key = ""
    while key != "q": 

        key = chr(stdscr.getch())

        valid_next_chars = valid_next_char(syllable_so_far)
        
        if key in valid_next_chars:
            stdscr.addstr(key + "\n")
            syllable_so_far += key
            possible_syllables = get_possible_syllables(syllable_so_far)
            stdscr.addstr(str(possible_syllables) + "\n")
            if len(possible_syllables) == 1:
                stdscr.addstr(syllable_so_far + "\n")
                syllable_so_far = ""




if __name__ == "__main__":
    curses.wrapper(main)
