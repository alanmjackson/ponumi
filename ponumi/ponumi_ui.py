import re
import curses
import os
import Tkinter
import tkFileDialog
import pickle

import OSC

import ponumi
import ponumi_midi
import ponumi_osc



ponumi_osc._osc_destination = ['192.168.0.8', 8000]

_default_name = ['po', 'nu', 'mi', 'ki', 'ma', 'pa', 'ka', 'ra', 'na', 'za', 'cha']

root_scheme = None
rhyming_scheme = ponumi.RHYMING_SCHEME


def format_syllable_table(syllable_table, column_width=4, columns=3):
    
    column_space = "       "
    rows = len(syllable_table)
    rows_in_column = int(float(rows) / float(columns) + 0.5)        #round up

    table_str = ""
    for row_index in range(rows_in_column):
        
        row_string = ""

        for column in range(columns):

            table_row_index = row_index + column * rows_in_column

            if table_row_index < rows:
                row = syllable_table[table_row_index]
                for item in row:
                    row_string = row_string + item.ljust(column_width, " ")

                row_string = row_string + column_space

        table_str += row_string.strip() + "\n"
    return table_str



def get_names():
    print("\nSyllables:")
    print(format_syllable_table(ponumi.syllable_table))
    name = get_name("\nenter your name in syllables:          ")
    syllable_count = len(name)
    
    ancestor_names = []
    while syllable_count < ponumi.POEM_ROOT_LENGTH:
        ancestor_name = get_name("enter an ancestor's name in syllables: ")
        syllable_count += len(ancestor_name)
        ancestor_names.append(ancestor_name)

    return name, ancestor_names


def get_name(prompt):
    name = []
    while name == []:
        name_str = name_str = raw_input(prompt)
        name = name_str.split()

        #check the name is made up of allowed syllables
        for syllable in name:
            if syllable not in ponumi.syllables:
                print("\n================ ERROR ================" + \
                      "\nName contains an unsupported syllable." + \
                      "\nUse only syllables from the table below separated by a space." + \
                      "\n=======================================\n")
                print("Syllables:")
                print(format_syllable_table(ponumi.syllable_table))
                name = []

    return name


def convolving_scheme_validator(scheme):
    #Validation function, returns True if scheme is valid
    for item in scheme:
        if not(item.isdigit()) or int(item) < 1:
            raise ValueError("Scheme can only contain numbers greater than 0")

    return True


def root_scheme_validator(scheme):
    #Validation function, returns True if scheme is valid
    anchors = 0
    rhymes = 0
    off_rhymes = 0

    for item in scheme:
        if item == ponumi.a:
            anchors += 1
        elif item == ponumi.o:
            rhymes += 1
        elif item == ponumi.x:
            off_rhymes += 1
        else:
            raise ValueError("Scheme can only contain " + ponumi.a + " or " + \
                              ponumi.o + " or " + ponumi.x)

    if anchors == 0 or rhymes == 0 or off_rhymes == 0:
        raise ValueError("Scheme must have at least 1 anchor, rhyme and off rhyme.")

    return True


def get_convolving_scheme(prompt):
    return input_scheme(prompt, convolving_scheme_validator)

def get_root_scheme(prompt):
    return input_scheme(prompt, root_scheme_validator)


def input_scheme(prompt, validator):
    scheme = None
    while scheme == None:
        scheme_str = scheme_str = raw_input(prompt)
        scheme = scheme_str.split()

        #check the scheme is made up of allowed items 
        if scheme != []:
            try:
                validator(scheme)
            except ValueError as e:
                print "\n================ ERROR ================" + \
                      "\nScheme contains an unsupported item." + \
                      "\n" + str(e) + \
                      "\nItems must be separated by spaces." + \
                      "\n=======================================\n"

                scheme = None
            except:
                raise

    return tuple(scheme)



def format_as_table(table_str, column_width=3):
    """
    Formats multi-line strings as tables by padding words with spaces to create 
    fixed width columns.
    """
    lines = table_str.split("\n")
    formatted_str = ""
    for line in lines:
        
        line_str = format_table_line(line, column_width)        
        formatted_str = formatted_str + line_str.strip() + "\n"    

    return formatted_str.strip()


def format_table_line(line, column_width=3):
    """
    Formats single-line strings as table columns by padding words with spaces to create 
    fixed width columns.
    """
    elements = line.split()
    line_str = ""
    for element in elements:
        line_str = line_str + element.ljust(column_width) + " "

    return line_str.strip()


def print_poem(poem):

    if poem == None:
        print("NO CURRENT POEM")
    else:
        print("\n--------------------POEM------------------------")
        
        if poem.root_name != None:
            print "root name:      " + " ".join(poem.root_name)

        if poem.ancestors != None:    
            for ancestor_name in poem.ancestors:
                print "ancestor name:  " + " ".join(ancestor_name)

        if poem.root != None:
            print("\nPoem Root:")
            print_poem_root(poem.root)

        if poem.rhyming_scheme != None:
            print("\nRhyming Scheme:")
            print_rhyming_scheme(poem.rhyming_scheme)

        if poem.syllables != None:
            print("\nPoem Text:")
            print_poem_text(poem.to_string())



def print_poem_root(root):

    top_line_str = ""
    bottom_line_str = ""
    for syllable, mark in root:
            top_line_str = top_line_str + syllable.ljust(3) + " "
            bottom_line_str = bottom_line_str + mark.ljust(3) + " "

    print(top_line_str.strip())
    print(bottom_line_str.strip())


def print_rhyming_scheme(scheme):
    print(format_as_table(ponumi.rhyming_scheme_to_string(scheme)))

def print_poem_text(text):
    print("------------------------------------------------")
    print(format_as_table(text))
    print("------------------------------------------------\n")


def print_root_scheme(scheme):
    if scheme == None:
        print("Built-in Default")
    else:
        print(format_table_line(ponumi.rhyming_scheme_to_string(scheme)))





def save_file(data, extension=""):
    filename = raw_input("enter file name:")
    f = open(filename + extension, "w")
    f.write(data)
    f.close()

def save_poem(poem):
    filename = raw_input("enter file name:")
    f = open(filename + ".pnm", "wb")
    pickle.dump(poem, f)
    f.close()

def load_poem(filename):
    f = open(filename, "rb")
    loaded_poem = pickle.load(f)
    f.close()
    return loaded_poem


def send_via_osc(poem):

    try:
        osc_data = ponumi_osc.send_via_osc(poem)

        print "\nsent:" 
        print osc_data
        print "\nto: ", ponumi_osc._osc_destination, ponumi_osc._osc_address
    except OSC.OSCClientError, e:
        print "OSC error: "
        print e    


def configure_osc():

    print "current osc network destination: ", ponumi_osc._osc_destination[0]
    while True :
        new_osc_destination_IP = raw_input("enter IP address: ")

        if new_osc_destination_IP == "":
            break   #if nothing is entered leave the IP address as it is.
        elif valid_ip_address(new_osc_destination_IP):
            ponumi_osc._osc_destination[0] = new_osc_destination_IP
            break
        else:
            print "invalid IP address"

    print "current osc data address: ", ponumi_osc._osc_address
    while True :
        new_osc_address = raw_input("enter OSC address: ")

        if new_osc_address == "":
            break   #if nothing is entered leave the IP address as it is.
        elif valid_osc_address(new_osc_address):
            ponumi_osc._osc_address = new_osc_address
            break
        else:
            print "invalid OSC address"
    

def valid_ip_address(address_string):
    m = re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', address_string)
    return m != None


def valid_osc_address(address_string):
    m = re.match(r'^/[/a-zA-Z0-9_]+$', address_string)
    return m != None


def main():
    global root_scheme, rhyming_scheme

    #command = "r"   #start by generating a poem from scratch
    command = None
    poem = None

    root = Tkinter.Tk()
    root.withdraw()


    while command != "q":
        if command == "p":      #Restart - make a poem from scratch
            name, ancestor_names = get_names()
            poem = ponumi.create_poem(name, ancestor_names, 
                   root_scheme=root_scheme, rhyming_scheme=rhyming_scheme)

            print_poem(poem)
            

        elif command == "d":    #Use the default poem, for testing
            poem = ponumi.create_poem(_default_name, [], 
                   root_scheme=root_scheme, rhyming_scheme=rhyming_scheme)

            print_poem(poem)

        elif command == "s":    #Save poem file
            save_poem(poem)

        elif command == "l":    #Load poem file
            file_path = tkFileDialog.askopenfilename()
    
            if file_path != "" and file_path != None:
                poem = load_poem(file_path)
                print("loading: " + file_path)
                print_poem(poem)


        elif command == "x":    #Load poem from a text file
            file_path = tkFileDialog.askopenfilename()
    
            if file_path != "" and file_path != None:
                syllables = ponumi.load_poem_file(file_path)
                poem = ponumi.Poem(syllables)
                print("loading: " + file_path)
                print_poem(poem)

                
        elif command == "t":    #Save poem text file 
            save_file(poem.to_string(), ".txt")

        elif command == "n":    #Save note number file
            notes = ponumi.poem_list_to_notes(poem.syllables)
            save_file(ponumi.notes_to_csv(notes), ".csv")

        elif command == "m":    #Save midi file
            filename = raw_input("enter file name:")
            notes = ponumi.poem_list_to_notes(poem.syllables)
            ponumi_midi.notes_to_midi_file(notes, filename + ".mid")

        elif command == "o":    #Send poem over OSC to a paca(rana)
            send_via_osc(poem)

        elif command == "c":    #configure OSC settings
            configure_osc()

        elif command == "i":    #print out information on config etc
            print "\nOSC Destination: ", ponumi_osc._osc_destination[0]
            print "OSC Address:     ", ponumi_osc._osc_address
            print "OSC Gate Address:     ", ponumi_osc._osc_go_address
            print("\nDefault Rhyming Scheme:")
            print_rhyming_scheme(rhyming_scheme)
            print("\nDefault Root Scheme:")
            print_root_scheme(root_scheme)            
            print_poem(poem)

        elif command == "r":    #load another rhyming scheme
            file_path = tkFileDialog.askopenfilename()
    
            if file_path != "" and file_path != None:
                scheme = ponumi.load_rhyming_scheme(file_path)
                rhyming_scheme = scheme
                print("loading: " + file_path)
                print_rhyming_scheme(rhyming_scheme)

        elif command == "v":    #convolve current poem with a name
            if poem != None:    
                print "\nSyllables:"
                print(format_syllable_table(ponumi.syllable_table))
                name = get_name("\nenter your name in syllables:          ")

                convolving_scheme = get_convolving_scheme(
                                "\nenter convolving scheme (leave blank for default - '7 5'):  ")
                if convolving_scheme == ():
                    convolving_scheme = (7, 5)

                poem = ponumi.convolve(poem, name, convolving_scheme)
                print_poem(poem)
            else:
                print("\nNo current poem to convolve.\n")

        elif command == "e":     #edit the root scheme
            root_scheme = get_root_scheme(
                          "\nenter root scheme (leave blank for default random scheme):  ")

            if root_scheme == ():
                root_scheme = None

            print("Root Scheme:")
            print_root_scheme(root_scheme)

        elif command == "":     #Regenerate poem with current names
            if poem != None and poem.root_name != None:

                poem = ponumi.create_poem(poem.root_name, poem.ancestors, 
                       root_scheme=root_scheme, rhyming_scheme=rhyming_scheme)

            print_poem(poem)

        command = raw_input(
            "\nCOMMANDS:\n" + \
            "'p' new Poem               'enter' regenerate poem    'i' show confIguration\n" + \
            "'s' Save poem              'l' Load poem              'x' load teXt file\n" + \
            "'t' save as Text           'r' load Rhyming scheme    'e' Edit root scheme\n" + \
            "'m' save as Midi           'o' send via OSC           'v' conVolve\n" + \
            "'n' save as Notes          'c' Configure OSC          'q' Quit\n" + \
            "'d' Default poem \n" + \
            ":")


if __name__ == '__main__':
    main()