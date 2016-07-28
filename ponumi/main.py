import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from kivy.properties import ListProperty
from kivy.properties import ObjectProperty


import kivy.lib.osc.oscAPI as oscAPI


import ponumi
import ponumi_osc

_ancestor = ['po', 'nu', 'mi', 'a', 'mu', 'nu', 'ma', 'ki']

#mac 169.254.211.66
#kyma 169.254.157.100
#ipad 169.254.163.159
#touchosc discovered 169.254.9.91

_default_osc_ip_address = '169.254.9.91'
_default_osc_port = '55388'
_default_osc_data_address = '/notelist' 
_default_osc_go_address = '/go'


#Screens

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

        titleLayout.add_widget(Button(
            text='config',
            size_hint_x=0.1,
            on_release=self.config_pressed))

        titleLayout.add_widget(Button(
            text='regen',
            size_hint_x=0.1,
            on_release=self.regenerate_pressed))

        self.add_widget(titleLayout)


        self.poemDisplay = PoemDisplay(size_hint_y=0.2)
        self.add_widget(self.poemDisplay)

        self.add_widget(SyllableKeyboard(size_hint_y=0.7, key_handler=self.syllable_btn_pressed))

        self.syllableEntryBox = SyllableEntryBox(size_hint_y=0.1, enter_handler=self.enter_pressed)
        self.add_widget(self.syllableEntryBox)


    def generate_and_show_poem(self, root_name, ancestor=_ancestor):
        self.poem = ponumi.create_poem(root_name, [ancestor])        
        self.poemDisplay.syllables = self.poem.syllables
        self.poemTitle.text = ' '.join(self.poem.root_name)
        

    def syllable_btn_pressed(self, *args):
        key = args[0]
        self.syllableEntryBox.append_syllable(key.value)

    def enter_pressed(self, *args):
        global _ancestor

        if len(self.syllableEntryBox.syllables) > 0:
            self.generate_and_show_poem(self.syllableEntryBox.syllables)

            new_ancestor = []
            for marked_syllable in self.poem.root:
                new_ancestor.append(marked_syllable[0])
            _ancestor = new_ancestor
            
            #clear the entry box
            self.syllableEntryBox.syllables = []

    def regenerate_pressed(self, *args):
        self.generate_and_show_poem(self.poem.root_name)


    def play_pressed(self, *args):
        if self.poem:
            osc_data = send_via_osc(self.poem)
        
    def config_pressed(self, *args):
        app = kivy.app.App.get_running_app()
        
        app.previous_screen = app.screen_manager.current
        app.screen_manager.current = 'config_screen'



class ConfigScreen(BoxLayout):

    osc_ip_address = ObjectProperty(None)
    osc_port = ObjectProperty(None)
    osc_data_address = ObjectProperty(None)
    osc_go_address = ObjectProperty(None)


    def ok_pressed(self, *args):
        app = kivy.app.App.get_running_app()

        app.osc_ip_address = self.osc_ip_address.text
        app.osc_port = self.osc_port.text
        app.osc_data_address = self.osc_data_address.text
        app.osc_go_address = self.osc_go_address.text

        app.screen_manager.current = app.previous_screen

    def cancel_pressed(self, *args):
        app = kivy.app.App.get_running_app()

        self.osc_ip_address.text = app.osc_ip_address
        self.osc_port.text = app.osc_port
        self.osc_data_address.text = app.osc_data_address
        self.osc_go_address.text = app.osc_go_address

        app.screen_manager.current = app.previous_screen




###############################################################
# Parts of screens
###############################################################


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
        self.add_widget(Button(text='enter', size_hint_x=1, on_release=enter_handler))

    def on_syllables(self, instance, value):
        self.textWidget.text = ' '.join(self.syllables)

    def append_syllable(self, syllable):
        self.syllables.append(syllable)

    def delete(self, *args):
        if len(self.syllables) > 0:
            self.syllables.pop()


###############################################################
#Functions
###############################################################


def send_via_osc(poem):
    app = kivy.app.App.get_running_app()

    ip_address = app.osc_ip_address
    port = int(app.osc_port)
    data_address = app.osc_data_address
    go_address = app.osc_go_address

    msg = ponumi_osc.poem_to_kyma_osc(poem)

    #send poem array
    oscAPI.sendMsg(data_address, dataArray=msg, ipAddr=ip_address, port=port, typehint=None)

    #send the go gate signal
    oscAPI.sendMsg(go_address, dataArray=[1.0], ipAddr=ip_address, port=port, typehint=None)

    print "\nsent:" 
    print msg
    print "\nto: ", ip_address, port, data_address 
    print "with go signal to: ", go_address



###############################################################
# Top Level Widgets
###############################################################


class PonumiPerformerScreenManager(ScreenManager):

    def __init__(self, **kwargs):
        super(PonumiPerformerScreenManager, self).__init__(**kwargs)
        
        entry_screen = Screen(name='entry_screen')
        entry_screen.add_widget(NameInputScreen(orientation='vertical'))

        config_screen = Screen(name='config_screen')
        config_screen.add_widget(ConfigScreen())

        self.add_widget(entry_screen)
        self.add_widget(config_screen)



class PonumiPerformer(App):

    osc_ip_address = StringProperty(_default_osc_ip_address)
    osc_port = StringProperty(_default_osc_port)
    osc_data_address = StringProperty(_default_osc_data_address)
    osc_go_address = StringProperty(_default_osc_go_address)

    previous_screen = StringProperty(None)

    def __init__(self, **kwargs):
        super(PonumiPerformer, self).__init__(**kwargs)
        oscAPI.init()


    def build(self):
        self.screen_manager = PonumiPerformerScreenManager()
        return self.screen_manager




if __name__ == '__main__':
    PonumiPerformer().run()