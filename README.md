#PONUMI

PONUMI creates poems from names. 

Names are entered using Japanese style syllables. A syllabic rhyming scheme is used based on traditional Chinese rhyming schemes. 

PONUMI can create, save and load poems as well as send them as data over OSC.

PONUMI was developed to work in conjunction with the kyma music production system from Symbolic Sound to play the poems. 

PONUMI was originally a command-line tool written in Python. 


#prioritised TODO list

* Port to ipad for real-time performance of poems with Kyma.

* real-time parsing of typed syllables

* check rhyming scheme and poem text files are well formed when loading

* improve admin UI using a static curses layout and instant key detect for menu

* port the UI to pygame

* add a help function

* create a self-service "gallery" UI

----
* Make a file dialog that can run on cloud9?
(http://pythondialog.sourceforge.net/doc/index.html)


* add resizing rhyming schemes to the UI

* (Hard rhyme syllables (convolving with a single syllable on anchor points))

----

# Completed Tasks

    /* Load prototype kyma "sound"

    /* elongating poems (elongating rhyming schemes by repeating lines)


    /* create and use other rhyming schemes
        UI let's you select another file. 

    /* Make it so you can do someone's name ahead of time, save it to disk (not send via OSC) and then when they arrive read it back in and send over OSC. 
        Load a saved poem


    /* convolution: convolving a poem against a list of syllables on poem anchors, (ons, offs and all?)

    /* what if you don't want the poem root randomly created?

    /* save and load the whole poem object (including names, root and rhyming scheme)

    /* re-implement loading a text file











#unprioritised bucket

Get gallery_ui working

work out input method
play sample for each typed syllable
allow editing of name



----


#Implementation Notes

1. Specifying the number of lines to stretch the poem to (so it can be only one line, or two, or 20)
2. A hard rhyme - specifying a syllable that all of the 'on rhyme' syllables are forced to..

For example taking the line:

E ma za CHA me ri hi N  (capitals are on rhyme)  

force it to rhyme with 'A'

and it becomes:

A ma za CHA me ri hi NA

This is useful because it allows us to take a stream of names and force them to rhyme with a particular name, so we can use a particular subject's name as a modifier for all the names.


Further, it would be advanced feature if the 'hard rhyme' could change every 1st and 8th place in a line of poem, and cycle through each letter of a selected 8-syllable name - - this would be actually like convolution where the syllables of one name become like 8 impulse responses filtered through the poem based off another name. 

For example:

Subject: "SHA ka mu NI shu do DA na"
Object: "MA ka ka SHO sha ka MU ni" 

-Each name is exactly 8 syllables

-Convolution shifts through 2nd gen name by 1 syllable  at 1st and 8th syllables (after the O resolve points)

nu
    

o"mu"
    

na
    

o"Sha"
    

da
    

o"ka"
    

da
    

o "Ma"

she
    

x
    

da
    

o
    

na
    

o
    

ni
    

x

du
    

o
    

ki
    

x
    

mu
    

x
    

na
    

o

nu
    

o
    

mu
    

x
    

ki
    

x
    

na
    

o

na
    

x
    

na
    

o
    

shu
    

x
    

shu
    

x

she
    

x
    

na
    

o
    

na
    

o
    

ki
    

x

shu
    

O
    

da
    

x
    

sha
    

O
    

sha
    

O

ni
    

o"ni"
    

mu
    

x"ka"
    

do
    

o"shou"
    

da
    

o "ka"

ka
    

x
    

da
    

o
    

no
    

o
    

mu
    

x

mu
    

x
    

na
    

o
    

na
    

x
    

na
    

o

di
    

o
    

ki
    

x
    

shu
    

x
    

na
    

o

shi
    

o
    

shu
    

x
    

sho
    

o
    

do
    

x


