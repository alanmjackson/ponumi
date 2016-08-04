import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from kivy.properties import ListProperty
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore

import kivy.lib.osc.oscAPI as oscAPI

from os.path import join

import ponumi
import ponumi_osc

#Config:
_default_osc_ip_address = '169.254.9.91'
_default_osc_port = '8000'
_default_osc_data_address = '/notelist' 
_default_osc_go_address = '/go'
_default_osc_syllable_address = '/syllable'
_default_osc_syllable_gate_address = '/syllablegate'

_osc_go_delay = 0.01     #seconds

_ancestor = ['po', 'nu', 'mi', 'a', 'mu', 'nu', 'ma', 'ki']

#mac 169.254.211.66
#kyma 169.254.157.100
#ipad 169.254.163.159
#touchosc discovered 169.254.9.91



#Screens

class NameInputScreen(BoxLayout):

    def __init__(self, **kwargs):
        super(NameInputScreen, self).__init__(**kwargs)

        self.poem = None
        
        self.spacing = 10

        screen_nav = BoxLayout(size_hint_y=0.08)

        screen_nav.add_widget(Button(
            size_hint_x=None,
            size=['100dp', 1],
            text='cfg',
            on_release=self.config_pressed))

        self.add_widget(screen_nav)

        titleLayout = BoxLayout(size_hint_y=0.05)

        self.poemTitle = Label(size_hint_x=0.9, font_size='24sp')

        titleLayout.add_widget(self.poemTitle)
        self.add_widget(titleLayout)


        self.poemDisplay = PoemDisplay(size_hint_y=0.35)
        self.add_widget(self.poemDisplay)


        poem_controls = BoxLayout(size_hint_y=0.1)

        self.syllableEntryBox = SyllableEntryBox(size_hint_x=14)
        poem_controls.add_widget(self.syllableEntryBox)

        poem_controls.add_widget(Button(
            text='enter',
            size_hint_x=1,
            on_release=self.enter_pressed))

        poem_controls.add_widget(Button(
            text='play',
            size_hint_x=1, 
            on_release=self.play_pressed))

        self.hear_button = ToggleButton(
            text='hear',
            size_hint_x=1)

        poem_controls.add_widget(self.hear_button)


        self.add_widget(poem_controls)

        self.add_widget(SyllableKeyboard(
            size_hint_y=0.7, 
            key_release_handler=self.syllable_btn_released,
            key_press_handler=self.syllable_btn_pressed))


    def generate_and_show_poem(self, root_name, ancestor):
        self.poem = ponumi.create_poem(root_name, [ancestor])        
        self.poemDisplay.syllables = self.poem.syllables
        self.poemTitle.text = ' '.join(self.poem.root_name)
        

    def syllable_btn_released(self, *args):
        key = args[0]
        self.syllableEntryBox.append_syllable(key.value)
        if self.hear_button.state == 'down':
            send_osc_syllable_gate_off()


    def syllable_btn_pressed(self, *args):
        key = args[0]
        if self.hear_button.state == 'down':
            play_syllable_via_osc(key.value)
            Clock.schedule_once(send_osc_syllable_gate_on, _osc_go_delay)


    def enter_pressed(self, *args):
        global _ancestor

        if len(self.syllableEntryBox.syllables) > 0:
            self.generate_and_show_poem(self.syllableEntryBox.syllables, _ancestor)

            new_ancestor = []
            for marked_syllable in self.poem.root:
                new_ancestor.append(marked_syllable[0])
            _ancestor = new_ancestor
            
            #clear the entry box
            self.syllableEntryBox.syllables = []
        else:
            if self.poem:
                self.generate_and_show_poem(self.poem.root_name, _ancestor)
            else:
                self.generate_and_show_poem(_ancestor, _ancestor)


    def play_pressed(self, *args):
        if self.poem:
            osc_data = play_poem_via_osc(self.poem)
        
    def config_pressed(self, *args):
        app = kivy.app.App.get_running_app()
        
        app.previous_screen = app.screen_manager.current
        app.screen_manager.current = 'config_screen'



class ConfigScreen(BoxLayout):

    osc_ip_address = ObjectProperty(None)
    osc_port = ObjectProperty(None)
    osc_data_address = ObjectProperty(None)
    osc_go_address = ObjectProperty(None)
    osc_syllable_address = ObjectProperty(None)
    osc_syllable_gate_address = ObjectProperty(None)


    def ok_pressed(self, *args):
        app = kivy.app.App.get_running_app()

        app.osc_ip_address = self.osc_ip_address.text
        app.osc_port = self.osc_port.text
        app.osc_data_address = self.osc_data_address.text
        app.osc_go_address = self.osc_go_address.text
        app.osc_syllable_address = self.osc_syllable_address.text
        app.osc_syllable_gate_address = self.osc_syllable_gate_address.text

        app.screen_manager.current = app.previous_screen
        app.save_config()


    def cancel_pressed(self, *args):
        app = kivy.app.App.get_running_app()

        self.osc_ip_address.text = app.osc_ip_address
        self.osc_port.text = app.osc_port
        self.osc_data_address.text = app.osc_data_address
        self.osc_go_address.text = app.osc_go_address
        self.osc_syllable_address.text = app.osc_syllable_address
        self.osc_syllable_gate_address.text = app.osc_syllable_gate_address

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
                syllable_widget = Label(text='', font_size='20sp')
                display_row.append(syllable_widget)
                self.add_widget(syllable_widget)

            self.display_syllables.append(display_row)


    def on_syllables(self, instance, value):
        for i in range(4):
            for j in range(12):
                self.display_syllables[i][j].text = self.syllables[i][j]





class SyllableKey(Button):
    value = StringProperty()


class SyllableKeyboard(BoxLayout):

    def __init__(self, **kwargs):
        super(SyllableKeyboard, self).__init__(**kwargs)

        key_release_handler = kwargs['key_release_handler']
        key_press_handler = kwargs['key_press_handler']
        
        self.spacing = 40

        columns = 3
        keys_per_row = 5

        q, r = divmod(len(ponumi.syllable_list), keys_per_row)
        total_rows = q + (r > 0)

        q, r = divmod(total_rows, columns)
        rows_per_column = q + (r > 0)

        for col in range(columns):
            col_layout = GridLayout(cols=keys_per_row)
            for i in range(rows_per_column):
                for j in range(keys_per_row):
                    index = (col * rows_per_column * keys_per_row) + (i * keys_per_row) + j
                    if index < len(ponumi.syllable_list):
                        syllable = ponumi.syllable_list[index]
                        btn = SyllableKey(text=syllable, value=syllable)
                        btn.bind(on_release=key_release_handler, on_press=key_press_handler)
                        col_layout.add_widget(btn)

            self.add_widget(col_layout)



class SyllableEntryBox(BoxLayout):
    syllables = ListProperty([])

    def __init__(self, **kwargs):
        super(SyllableEntryBox, self).__init__(**kwargs)

        self.textWidget = Label(text='', size_hint_x=13, font_size='30sp')
        self.add_widget(self.textWidget)
        self.add_widget(Button(text='del', size_hint_x=1, on_release=self.delete))

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


def play_poem_via_osc(poem):
    app = kivy.app.App.get_running_app()

    ip_address = app.osc_ip_address
    port = int(app.osc_port)
    data_address = app.osc_data_address

    msg = ponumi_osc.poem_to_kyma_osc(poem)

    #send poem array
    oscAPI.sendMsg(data_address, dataArray=msg, ipAddr=ip_address, port=port, typehint=None)

    print("\nsent:")
    print(msg)
    print "\nto: ", ip_address, port, data_address

    Clock.schedule_once(send_osc_go_on_signal, _osc_go_delay)


def send_osc_go_on_signal(*args):
    app = kivy.app.App.get_running_app()

    #send the go gate on signal (ie the rising edge of the gate signal)
    oscAPI.sendMsg(
        app.osc_go_address, 
        ipAddr=app.osc_ip_address, 
        port=int(app.osc_port), 
        typehint=None,
        dataArray=[1.0]) 
    
    print "sent go signal to: ", app.osc_ip_address, app.osc_port, app.osc_go_address
    Clock.schedule_once(send_osc_go_off_signal, _osc_go_delay)


def send_osc_go_off_signal(*args):
    app = kivy.app.App.get_running_app()

    #send the go gate off signal (ie the falling edge of the gate signal)
    oscAPI.sendMsg(
        app.osc_go_address, 
        ipAddr=app.osc_ip_address, 
        port=int(app.osc_port), 
        typehint=None,
        dataArray=[0.0]) 


def send_osc_syllable_gate_on(*args):
    app = kivy.app.App.get_running_app()

    oscAPI.sendMsg(
        app.osc_syllable_gate_address, 
        ipAddr=app.osc_ip_address, 
        port=int(app.osc_port), 
        typehint=None,
        dataArray=[1.0]) 

    print 'osc syllable gate on'


def send_osc_syllable_gate_off(*args):
    app = kivy.app.App.get_running_app()

    oscAPI.sendMsg(
        app.osc_syllable_gate_address, 
        ipAddr=app.osc_ip_address, 
        port=int(app.osc_port), 
        typehint=None,
        dataArray=[0.0]) 

    print 'osc syllable gate off'



def play_syllable_via_osc(syllable):
    app = kivy.app.App.get_running_app()

    ip_address = app.osc_ip_address
    port = int(app.osc_port)
    osc_address = app.osc_syllable_address

    msg = ponumi_osc.syllables_to_kyma_osc([syllable])

    #send syllables
    oscAPI.sendMsg(osc_address, dataArray=msg, ipAddr=ip_address, port=port, typehint=None)


    print("\nsent:")
    print(msg)
    print "\nto: ", ip_address, port, osc_address





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
    osc_syllable_address = StringProperty(_default_osc_syllable_address)
    osc_syllable_gate_address = StringProperty(_default_osc_syllable_gate_address)

    previous_screen = StringProperty(None)


    def __init__(self, **kwargs):
        super(PonumiPerformer, self).__init__(**kwargs)
        data_dir = getattr(self, 'user_data_dir')
        self.config_store = JsonStore(join(data_dir, 'ponumiperformer.json'))
        oscAPI.init()


    def build(self):
        self.load_config()

        self.screen_manager = PonumiPerformerScreenManager()
        return self.screen_manager


    def save_config(self):

        self.config_store.put('config', 
            osc_ip_address=self.osc_ip_address,
            osc_port=self.osc_port,
            osc_data_address=self.osc_data_address,
            osc_go_address=self.osc_go_address,
            osc_syllable_address=self.osc_syllable_address,
            osc_syllable_gate_address=self.osc_syllable_gate_address)


    def load_config(self):

        if self.config_store.exists('config'):
            config = self.config_store.get('config')

            if 'osc_ip_address' in config: self.osc_ip_address = config['osc_ip_address']
            if 'osc_port' in config: self.osc_port = config['osc_port']
            if 'osc_data_address' in config: self.osc_data_address = config['osc_data_address']
            if 'osc_go_address' in config: self.osc_go_address = config['osc_go_address']
            if 'osc_syllable_address' in config: self.osc_syllable_address = config['osc_syllable_address']
            if 'osc_syllable_gate_address' in config: self.osc_syllable_gate_address = config['osc_syllable_gate_address']


    def load_default_config(self):
        self.osc_ip_address = _default_osc_ip_address
        self.osc_port = _default_osc_port
        self.osc_data_address = _default_osc_data_address
        self.osc_go_address = _default_osc_go_address
        self.osc_syllable_address = _default_osc_syllable_address
        self.osc_syllable_gate_address = _default_osc_syllable_gate_address





if __name__ == '__main__':

    # Temporary tweaking of ponumi syllables to compensate for a couple of anomalies 
    # in the index order of the Steph101.wav file:
    #START
    import copy
    syllable_list = copy.copy(ponumi.syllable_list)
    syllable_list.remove('zu')
    syllable_list.remove('n')
    syllable_list.insert(9, 'zu')
    syllable_list.insert(10, 'n')
    ponumi.syllables = dict( zip(syllable_list, range(0, len(syllable_list) ) ) )
    #END

    PonumiPerformer().run()