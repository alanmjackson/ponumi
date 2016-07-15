import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import StringProperty
from kivy.properties import ListProperty

import OSC

import ponumi
import ponumi_osc

ponumi_osc._osc_destination = ['192.168.0.8', 8000]

_ancestor = ['po', 'nu', 'mi', 'a', 'mu', 'nu', 'ma', 'ki']

class PoemDisplay(GridLayout):

    syllables = ListProperty([])     #expects a 4 x 12 array of syllables

    def __init__(self, **kwargs):
        super(PoemDisplay, self).__init__(**kwargs)

        self.cols = 12
        self.padding = [100, 20]

        self.display_syllables = []


        for i in range(4):
            display_row = []
            for j in range(12):
                syllable_widget = Label(text='')
                display_row.append(syllable_widget)
                self.add_widget(syllable_widget)

            self.display_syllables.append(display_row)


    def on_syllables(self, instance, value):
        for i in range(4):
            for j in range(12):
                self.display_syllables[i][j].text = self.syllables[i][j]



class NameInputScreen(BoxLayout):

    def __init__(self, **kwargs):
        super(NameInputScreen, self).__init__(**kwargs)

        titleLayout = BoxLayout(size_hint_y=0.05)

        self.poemTitle = Label(size_hint_x=0.9, font_size='28sp')
        self.poem = None

        titleLayout.add_widget(self.poemTitle)
        titleLayout.add_widget(Button(
            text='play',
            size_hint_x=0.1, 
            on_release=self.play_pressed))

        self.add_widget(titleLayout)


        self.poemDisplay = PoemDisplay(size_hint_y=0.2)
        self.add_widget(self.poemDisplay)

        self.add_widget(SyllableKeyboard(size_hint_y=0.7, key_handler=self.syllable_btn_pressed))

        self.syllableEntryBox = SyllableEntryBox(size_hint_y=0.1, enter_handler=self.enter_pressed)
        self.add_widget(self.syllableEntryBox)


    def syllable_btn_pressed(self, *args):
        key = args[0]
        self.syllableEntryBox.append_syllable(key.value)

    def enter_pressed(self, *args):
        global _ancestor

        if len(self.syllableEntryBox.syllables) > 0:
            self.poem = ponumi.create_poem(self.syllableEntryBox.syllables, [_ancestor])        
            self.poemDisplay.syllables = self.poem.syllables
            self.poemTitle.text = ' '.join(self.poem.root_name)
            new_ancestor = []
            for marked_syllable in self.poem.root:
                new_ancestor.append(marked_syllable[0])
            _ancestor = new_ancestor

    def play_pressed(self, *args):
        if self.poem:
            try:
                osc_data = ponumi_osc.send_via_osc(self.poem)

                print "\nsent:" 
                print osc_data
                print "\nto: ", ponumi_osc._osc_destination, ponumi_osc._osc_address
            except OSC.OSCClientError, e:
                print "OSC error: "
                print e    



class SyllableKey(Button):
    value = StringProperty()


class SyllableKeyboard(GridLayout):

    def __init__(self, **kwargs):
        super(SyllableKeyboard, self).__init__(**kwargs)

        key_handler = kwargs['key_handler']

        i = 0
        for syllable in ponumi.syllable_list:
            btn = SyllableKey(text=syllable, value=syllable)
            btn.bind(on_release=key_handler)
            self.add_widget(btn)

            if i == 4 or i == 9:
                self.add_widget(Label(text=''))                
            i += 1

            if i == 15:
                i = 0




class SyllableEntryBox(BoxLayout):
    syllables = ListProperty([])

    def __init__(self, **kwargs):
        super(SyllableEntryBox, self).__init__(**kwargs)

        enter_handler = kwargs['enter_handler']

        self.textWidget = Label(text='', size_hint_x=15, font_size='30sp')
        self.add_widget(self.textWidget)
        self.add_widget(Button(text='del', size_hint_x=1, on_release=self.delete))
        self.add_widget(Button(text='clear', size_hint_x=1, on_release=self.clear))
        self.add_widget(Button(text='enter', size_hint_x=1, on_release=enter_handler))

    def on_syllables(self, instance, value):
        self.textWidget.text = ' '.join(self.syllables)

    def append_syllable(self, syllable):
        self.syllables.append(syllable)

    def delete(self, *args):
        if len(self.syllables) > 0:
            self.syllables.pop()

    def clear(self, *args):
        self.syllables = []




class PonumiPerformer(App):

    def build(self):
        return NameInputScreen(orientation='vertical')


if __name__ == '__main__':
    PonumiPerformer().run()