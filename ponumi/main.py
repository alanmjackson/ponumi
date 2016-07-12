import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout

import ponumi

class NameInputScreen(BoxLayout):

    def __init__(self, **kwargs):
        super(NameInputScreen, self).__init__(**kwargs)

        self.add_widget(SyllableKeyboard(size_hint_y=0.7))
        self.add_widget(TextEntryBox(size_hint_y=0.1))



class SyllableKeyboard(GridLayout):

    def __init__(self, **kwargs):
        super(SyllableKeyboard, self).__init__(**kwargs)


        self.cols = 17

        i = 0
        for syllable in ponumi.syllable_list:
            self.add_widget(Button(text=syllable))

            if i == 4 or i == 9:
                self.add_widget(Label(text='-'))                
            i += 1

            if i == 15:
                i = 0


class TextEntryBox(BoxLayout):

    def __init__(self, **kwargs):
        super(TextEntryBox, self).__init__(**kwargs)

        self.add_widget(Label(text='1234567890', size_hint_x=15))
        self.add_widget(Button(text='del', size_hint_x=1))
        self.add_widget(Button(text='enter', size_hint_x=1))




class MyApp(App):

    def build(self):
        return NameInputScreen(orientation='vertical')


if __name__ == '__main__':
    MyApp().run()