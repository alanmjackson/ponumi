import curses

import ponumi
import ponumi_ui


def main(stdscr):
    #while True:
    syllable_border_scr = stdscr.derwin(10,78,2,2)
    syllable_scr = syllable_border_scr.derwin(9,76,1,2)
    syllable_scr.addstr("SYLLABLES:\n")
    syllable_scr.addstr(ponumi_ui.format_syllable_table(ponumi.syllable_table))
    syllable_border_scr.border()
    syllable_border_scr.refresh()
    stdscr.addstr(13, 2, "Enter your name using only the syllables above.")
    stdscr.addstr(14, 2, "For example:")
    stdscr.addstr(15, 10, "Alan -> a ra n")
    stdscr.addstr(16, 10, "Jane -> ja i n")
    stdscr.addstr(17, 10, "James -> ja mu su")
    stdscr.addstr(18, 10, "Elizabeth -> e ri za be tu")
    stdscr.addstr(20, 2, "Enter your name: ")
    stdscr.getstr()

if __name__ == "__main__":
    curses.wrapper(main)
