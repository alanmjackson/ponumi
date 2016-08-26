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
from kivy.uix.actionbar import ActionBar
from kivy.uix.actionbar import ActionButton
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.behaviors import ToggleButtonBehavior

from kivy.properties import StringProperty
from kivy.properties import ListProperty
from kivy.properties import DictProperty
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore

import kivy.lib.osc.oscAPI as oscAPI

from os.path import join
from functools import partial

import ponumi
import ponumi_osc

#Config:
_DEBUG = False

_default_osc_ip_address = '127.0.0.1'
_default_osc_port = '8000'
_default_osc_data_address = '/notelist' 
_default_osc_go_address = '/go'
_default_osc_syllable_address = '/syllable'
_default_osc_syllable_gate_address = '/syllablegate'
_default_osc_rhythm_address = '/rhythm'


_osc_go_delay = 0.01     #seconds

_ancestor = ['po', 'nu', 'mi', 'a', 'mu', 'nu', 'ma', 'ki']

_poem_length = 48

def make_rhythm(root):

    #create an 8 item rhythm_root by truncating or repeating the given root
    q, r = divmod(8, len(root))
    rhythm_root = root * q + root[:r]

    return ponumi.create_poem(root, [])


_default_rhythm = make_rhythm(['1'])

#mac 169.254.211.66
#kyma 169.254.157.100
#ipad 169.254.163.159
#touchosc discovered 169.254.9.91



#Screens


class RootScreen(BoxLayout):

    def __init__(self, **kwargs):
        super(RootScreen, self).__init__(**kwargs)

        self.orientation = 'vertical'



class NameInputScreen(BoxLayout):

    def __init__(self, **kwargs):
        super(NameInputScreen, self).__init__(**kwargs)

        self.poem = None
        
        self.orientation = 'vertical'
        self.spacing = 10

        top = BoxLayout(
            orientation='horizontal', 
            spacing=2, 
            size_hint_y=0.5)
        
        top_left = BoxLayout(
            orientation='vertical', 
            size_hint_x=0.9)

        titleLayout = BoxLayout(size_hint_y=0.05)

        self.poemTitle = Label(size_hint_x=0.9, font_size='24sp')

        titleLayout.add_widget(self.poemTitle)
        top_left.add_widget(titleLayout)


        self.poemDisplay = PoemDisplay(size_hint_y=0.35)
        top_left.add_widget(self.poemDisplay)


        poem_controls = BoxLayout(size_hint_y=0.1, spacing=2)

        self.entryBox = EntryBox(size_hint_x=14)
        poem_controls.add_widget(self.entryBox)

        poem_controls.add_widget(IconButton(
            #text='enter',
            size_hint=[None, None],
            size=['48dp', '48dp'],
            up_image='images/ret-no-alpha.png',
            down_image='images/ret-no-alpha-glitch-inv.png',
            on_release=self.enter_pressed))



        play_controls = BoxLayout(
            orientation='vertical', 
            size_hint_x=None,
            size=['48dp', 0],
            spacing=2)

        play_controls.add_widget(IconButton(
            #text='play',
            size_hint=[None, None],
            size=['48dp', '48dp'],
            up_image='images/play-no-alpha.png',
            down_image='images/play-no-alpha-glitch-inv.png', 
            on_release=self.play_pressed))

        play_controls.add_widget(VCSButton(
            #text='stop',
            osc_address='/stop',
            size_hint=[None, None],
            size=['48dp', '48dp'],
            up_image='images/stop-no-alpha.png',
            down_image='images/stop-no-alpha-glitch-inv.png'))

        play_controls.add_widget(VCSToggleButton(
            #text='loop',
            osc_address='/loop',
            size_hint=[None, None],
            size=['48dp', '48dp'],
            up_image='images/loop-no-alpha.png',
            down_image='images/loop-no-alpha-glitch-inv.png'))

        self.hear_button = IconToggleButton(
            #text='hear',
            size_hint=[None, None],
            size=['48dp', '48dp'],
            up_image='images/hear-no-alpha.png',
            down_image='images/hear-no-alpha-glitch-inv.png')

        play_controls.add_widget(self.hear_button)


        top_left.add_widget(poem_controls)

        top.add_widget(top_left)
        top.add_widget(play_controls)

        self.add_widget(top)
        self.add_widget(SyllableKeyboard(
            size_hint_y=0.7, 
            on_keyboard_down=self.syllable_btn_pressed,
            on_keyboard_up=self.syllable_btn_released))


    def generate_and_show_poem(self, root_name, ancestor):
        self.poem = ponumi.create_poem(root_name, [ancestor])        
        self.poemDisplay.syllables = self.poem.syllables
        self.poemTitle.text = ' '.join(self.poem.root_name)
        

    def syllable_btn_pressed(self, *args):
        key = args[1]
        if self.hear_button.state == 'down':
            play_syllable_via_osc(key.value)
            Clock.schedule_once(send_osc_syllable_gate_on, _osc_go_delay)

    def syllable_btn_released(self, *args):
        key = args[1]
        self.entryBox.append_syllable(key.value)
        if self.hear_button.state == 'down':
            send_osc_syllable_gate_off()




    def enter_pressed(self, *args):
        global _ancestor

        if len(self.entryBox.syllables) > 0:
            self.generate_and_show_poem(self.entryBox.syllables, _ancestor)

            new_ancestor = []
            for marked_syllable in self.poem.root:
                new_ancestor.append(marked_syllable[0])
            _ancestor = new_ancestor
            
            #clear the entry box
            self.entryBox.syllables = []
        else:
            if self.poem:
                self.generate_and_show_poem(self.poem.root_name, _ancestor)
            else:
                self.generate_and_show_poem(_ancestor, _ancestor)

    def play_pressed(self, *args):
        if self.poem:
            play_poem_via_osc(self.poem)



class ConfigScreen(BoxLayout):

    osc_ip_address = ObjectProperty(None)
    osc_port = ObjectProperty(None)
    osc_data_address = ObjectProperty(None)
    osc_go_address = ObjectProperty(None)
    osc_syllable_address = ObjectProperty(None)
    osc_syllable_gate_address = ObjectProperty(None)
    osc_rhythm_address = ObjectProperty(None)


    def __init__(self, **kwargs):
        super(ConfigScreen, self).__init__(**kwargs)


    def refresh_form(self, *args):
        app = kivy.app.App.get_running_app()

        self.osc_ip_address.text = app.osc_ip_address
        self.osc_port.text = app.osc_port
        self.osc_data_address.text = app.osc_data_address
        self.osc_go_address.text = app.osc_go_address
        self.osc_syllable_address.text = app.osc_syllable_address
        self.osc_syllable_gate_address.text = app.osc_syllable_gate_address
        self.osc_rhythm_address.text = app.osc_rhythm_address



    def save_pressed(self, *args):
        app = kivy.app.App.get_running_app()

        app.osc_ip_address = self.osc_ip_address.text
        app.osc_port = self.osc_port.text
        app.osc_data_address = self.osc_data_address.text
        app.osc_go_address = self.osc_go_address.text
        app.osc_syllable_address = self.osc_syllable_address.text
        app.osc_syllable_gate_address = self.osc_syllable_gate_address.text
        app.osc_rhythm_address = self.osc_rhythm_address.text

        app.save_config()


class ManualScreen(BoxLayout):

    syllables = ListProperty([])

    def __init__(self, **kwargs):
        super(ManualScreen, self).__init__(**kwargs)

        self.orientation = 'vertical'
        self.spacing=15

        self.poem_display = PoemDisplay(size_hint_y=0.4)
        self.add_widget(self.poem_display)

        controls = BoxLayout(size_hint_y=0.1, spacing=15)

        controls.add_widget(Label(size_hint_x=12))
        controls.add_widget(IconButton(
            #text='del',
            size_hint=[None, None],
            size=['48dp', '48dp'],
            up_image='images/del-no-alpha.png',
            down_image='images/del-no-alpha-glitch-inv.png',
            on_release=self.del_pressed))

        controls.add_widget(IconButton(
            #text='clear',
            size_hint=[None, None],
            size=['48dp', '48dp'],
            up_image='images/clear-no-alpha.png',
            down_image='images/clear-no-alpha-glitch-inv.png',
            on_release=self.clear_pressed))

        controls.add_widget(IconButton(
            #text='play',
            size_hint=[None, None],
            size=['48dp', '48dp'],
            up_image='images/play-no-alpha.png',
            down_image='images/play-no-alpha-glitch-inv.png', 
            on_release=self.play_pressed))

        self.hear_button = IconToggleButton(
            #text='hear',
            size_hint=[None, None],
            size=['48dp', '48dp'],
            up_image='images/hear-no-alpha.png',
            down_image='images/hear-no-alpha-glitch-inv.png')

        controls.add_widget(self.hear_button)

        self.add_widget(controls)


        self.add_widget(SyllableKeyboard(
            size_hint_y = 0.7,
            on_keyboard_down=self.syllable_btn_pressed,
            on_keyboard_up=self.syllable_btn_released))


    def del_pressed(self, *args):
        if len(self.syllables) > 0:
            self.syllables.pop()


    def clear_pressed(self, *args):
        self.syllables = []


    def play_pressed(self, *args):
        #pad the end of the poem with silence
        syllables = self.syllables + ['-'] * (_poem_length - len(self.syllables))
        poem = ponumi.Poem(syllables)
        if poem:
            play_poem_via_osc(poem)


    def syllable_btn_pressed(self, *args):
        key = args[1]
        if self.hear_button.state == 'down':
            play_syllable_via_osc(key.value)
            Clock.schedule_once(send_osc_syllable_gate_on, _osc_go_delay)


    def syllable_btn_released(self, *args):
        key = args[1]
        self.syllables.append(key.value)
        if self.hear_button.state == 'down':
            send_osc_syllable_gate_off()

    def on_syllables(self, instance, value):
        if len(self.syllables) > _poem_length:
            self.syllables = self.syllables[:_poem_length]

        #PoemDisplay expects a 2D array
        poem = [['' for x in range(12)] for y in range(4)]
        for i in range(min(_poem_length, len(self.syllables))):
            poem[int(i/12)][i % 12] = self.syllables[i]

        self.poem_display.syllables = poem


class KeyboardScreen(BoxLayout):

    def __init__(self, **kwargs):
        super(KeyboardScreen, self).__init__(**kwargs)
        self.add_widget(SyllableKeyboard(
            size_hint_y = 0.9,
            on_keyboard_down=self.syllable_btn_pressed,
            on_keyboard_up=self.syllable_btn_released))


    def syllable_btn_pressed(self, *args):
        play_syllable_via_osc(args[1].value)
        Clock.schedule_once(send_osc_syllable_gate_on, _osc_go_delay)

    def syllable_btn_released(self, *args):
        send_osc_syllable_gate_off()



class RhythmScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(RhythmScreen, self).__init__(**kwargs)

        self.poem = None
        
        self.orientation = 'vertical'
        self.spacing = 10

        titleLayout = BoxLayout(size_hint_y=0.05)

        self.poemTitle = Label(size_hint_x=0.9, font_size='24sp')

        titleLayout.add_widget(self.poemTitle)
        self.add_widget(titleLayout)


        self.poemDisplay = PoemDisplay(size_hint_y=0.35)
        self.add_widget(self.poemDisplay)


        poem_controls = BoxLayout(size_hint_y=0.1, spacing=15)

        self.entryBox = EntryBox(size_hint_x=14)
        poem_controls.add_widget(self.entryBox)

        poem_controls.add_widget(IconButton(
            #text='enter',
            size_hint=[None, None],
            size=['48dp', '48dp'],
            up_image='images/ret-no-alpha.png',
            down_image='images/ret-no-alpha-glitch-inv.png',
            on_release=self.enter_pressed))

        self.add_widget(poem_controls)

        self.add_widget(RhythmKeyboard(
            size_hint_y=0.7, 
            on_keyboard_up=self.keyboard_btn_released))


    def generate_and_show_rhythm(self, rhythm_root):
        self.poem = make_rhythm(rhythm_root)
        self.display_rhythm()        
        
    def refresh_form(self, *args):
        app = kivy.app.App.get_running_app()
        self.poem = app.rhythm
        self.display_rhythm()

    def display_rhythm(self):
        self.poemDisplay.syllables = self.poem.syllables
        self.poemTitle.text = ' '.join(self.poem.root_name)


    def keyboard_btn_released(self, *args):
        key = args[1]
        self.entryBox.append_syllable(key.value)


    def enter_pressed(self, *args):

        if len(self.entryBox.syllables) > 0:

            self.generate_and_show_rhythm(self.entryBox.syllables)

            #clear the entry box
            self.entryBox.syllables = []
        else:
            if self.poem:
                self.generate_and_show_rhythm(self.poem.root_name)
            else:
                self.generate_and_show_rhythm(['1'])

        app = kivy.app.App.get_running_app()
        app.rhythm = self.poem


class VCSScreen(BoxLayout):

    def __init__(self, **kwargs):
        super(VCSScreen, self).__init__(**kwargs)

        self.orientation='horizontal'
        slider = VCSSlider('/vol')
        #slider.bind(osc_value=self.vcs_slider_moved)
        self.add_widget(slider)

        slider = VCSSlider('/bpm')
        #slider.bind(osc_value=self.vcs_slider_moved)
        self.add_widget(slider)

        self.add_widget(Label())

        slider = VCSSlider('/poem_dur')
        #slider.bind(osc_value=self.vcs_slider_moved)
        self.add_widget(slider)

        slider = VCSSlider('/poem_var')
        #slider.bind(osc_value=self.vcs_slider_moved)
        self.add_widget(slider)

        self.add_widget(Label())

        slider = VCSSlider('/key_dur')
        #slider.bind(osc_value=self.vcs_slider_moved)
        self.add_widget(slider)

        slider = VCSSlider('/key_var')
        #slider.bind(osc_value=self.vcs_slider_moved)
        self.add_widget(slider)


    #def vcs_slider_moved(self, instance, value):
    #    send_osc_message(value['osc_address'], [value['value']])


###############################################################
# Parts of screens
###############################################################


class IconButton(ButtonBehavior, Image):

    def __init__(self, down_image=None, up_image=None, **kwargs):
        super(IconButton, self).__init__(**kwargs)

        self.allow_stretch = True

        self.up_image = up_image
        if up_image:
            self.source = up_image

        if down_image:
            self.down_image = down_image
        else:
            self.down_image = up_image

    def on_press(self):
        if self.down_image:
            self.source = self.down_image

    def on_release(self):
        if self.up_image:
            self.source = self.up_image


class IconToggleButton(ToggleButtonBehavior, Image):

    def __init__(self, down_image=None, up_image=None, **kwargs):
        super(IconToggleButton, self).__init__(**kwargs)

        self.allow_stretch = True

        self.up_image = up_image
        if up_image:
            self.source = up_image

        if down_image:
            self.down_image = down_image
        else:
            self.down_image = up_image

    def on_state(self, widget, value):
        if value == 'down':
            if self.down_image:
                self.source = self.down_image
        else:
            if self.up_image:
                self.source = self.up_image


class VCSToggleButton(IconToggleButton):

    def __init__(self, osc_address, down_value=1, up_value=0, **kwargs):
        super(VCSToggleButton, self).__init__(**kwargs)
        self.osc_address = osc_address
        self.down_value = down_value
        self.up_value = up_value

    def on_state(self, widget, value):
        super(VCSToggleButton, self).on_state(widget, value)
        if value == 'down':
            send_osc_message(self.osc_address, [self.down_value])
        else:
            send_osc_message(self.osc_address, [self.up_value])


class VCSButton(IconButton):

    def __init__(self, osc_address, down_value=1, up_value=0, **kwargs):
        super(VCSButton, self).__init__(**kwargs)
        self.osc_address = osc_address
        self.down_value = down_value
        self.up_value = up_value

    def on_press(self):
        super(VCSButton, self).on_press()
        send_osc_message(self.osc_address, [self.down_value])

    def on_release(self):
        super(VCSButton, self).on_release()
        send_osc_message(self.osc_address, [self.up_value])


class VCSSlider(BoxLayout):


    def __init__(self, osc_address, **kwargs):
        super(VCSSlider, self).__init__(**kwargs)

        self.osc_address = osc_address

        self.orientation = 'vertical'
        self.slider = Slider(
            orientation='vertical',
            size_hint_y=0.8)

        self.slider.bind(value=self.slider_moved)

        label = Label(
            text=self.osc_address.replace('_', ' ').lstrip('/'),
            size_hint_y=0.2)
            
        self.add_widget(self.slider)
        self.add_widget(label)

    def slider_moved(self, instance, value):
        send_osc_message(self.osc_address, [self.slider.value_normalized])



class NavBar(ActionBar):

    osc_indicator = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(NavBar, self).__init__(**kwargs)

    def entry_pressed(self, *args):
        kivy.app.App.get_running_app().screen_manager.current = 'entry_screen'

    def manual_pressed(self, *args):
        kivy.app.App.get_running_app().screen_manager.current = 'manual_screen'

    def keyboard_pressed(self, *args):
        kivy.app.App.get_running_app().screen_manager.current = 'keyboard_screen'

    def rhythm_pressed(self, *args):
        kivy.app.App.get_running_app().screen_manager.current = 'rhythm_screen'
        kivy.app.App.get_running_app().screen_manager.current_screen.children[0].refresh_form()

    def vcs_pressed(self, *args):
        kivy.app.App.get_running_app().screen_manager.current = 'vcs_screen'

    def config_pressed(self, *args):
        kivy.app.App.get_running_app().screen_manager.current = 'config_screen'

        #This next line seems hacky, but I couldn't get this to work triggering from the
        #on_enter event of the Screen. The function would get run but would have no
        #effect on the text input widgets on the screen. 
        kivy.app.App.get_running_app().screen_manager.current_screen.children[0].refresh_form()



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
        #truncate array to 4 x 12
        truncated_syllables = self.syllables[:4]
        for k in range(len(truncated_syllables)):
            truncated_syllables[k] = truncated_syllables[k][:12]
        self.syllables = truncated_syllables

        for i in range(4):
            for j in range(12):
                if i < len(self.syllables) and j < len(self.syllables[i]):
                    self.display_syllables[i][j].text = self.syllables[i][j]
                else:
                    self.display_syllables[i][j].text = ''




class Key(Button):
    value = StringProperty()

    def __init__(self, **kwargs):
        super(Key, self).__init__(**kwargs)

        #self.background_color = (127,127,127,1.0)
        self.color = (0,0,0,1.0)
        self.bold = True
        self.background_normal = 'images/button_texture_white.png'


class Keyboard(BoxLayout):
    #Base class for keyboards, eg. SyllableKeyboard

    def __init__(self, **kwargs):
        self.register_event_type('on_keyboard_down')
        self.register_event_type('on_keyboard_up')

        super(Keyboard, self).__init__(**kwargs)


    def key_press_handler(self, *args):
        self.dispatch('on_keyboard_down', args[0])

    def key_release_handler(self, *args):
        self.dispatch('on_keyboard_up', args[0])

    def on_keyboard_down(self, *args):
        pass

    def on_keyboard_up(self, *args):
        pass


class SyllableKeyboard(Keyboard):

    def __init__(self, **kwargs):
        super(SyllableKeyboard, self).__init__(**kwargs)

        self.spacing = 33

        columns = 3
        keys_per_row = 5

        q, r = divmod(len(ponumi.syllable_list), keys_per_row)
        total_rows = q + (r > 0)

        q, r = divmod(total_rows, columns)
        rows_per_column = q + (r > 0)

        down_colours = [
            'images/button_pressed_red.png',
            'images/button_pressed_orange.png',
            'images/button_pressed_yellow.png',
            'images/button_pressed_green.png',
            'images/button_pressed_turquoise.png',
            'images/button_pressed_purple.png',
            'images/button_pressed_magenta.png'
        ]

        for col in range(columns):
            col_layout = GridLayout(cols=keys_per_row)
            for i in range(rows_per_column):
                down_colour = down_colours[i]
                for j in range(keys_per_row):
                    #Adding 1 on to the index so the silent syllable is initially skipped... 
                    index = (col * rows_per_column * keys_per_row) + (i * keys_per_row) + j + 1
                    if index <= len(ponumi.syllable_list):
                        if index < len(ponumi.syllable_list):
                            syllable = ponumi.syllable_list[index]
                        #...and then append the silent syllable button at the end
                        else:
                            syllable = ponumi.syllable_list[0]

                        button = Key(
                            text=syllable, 
                            value=syllable, 
                            background_down=down_colour)
                        button.bind(
                            on_release=self.key_release_handler, 
                            on_press=self.key_press_handler)
                        col_layout.add_widget(button)


            self.add_widget(col_layout)


class RhythmKeyboard(Keyboard):

    def __init__(self, **kwargs):
        super(RhythmKeyboard, self).__init__(**kwargs)

        self.spacing = 40

        button = Key(
            text='0', 
            value='0',
            background_down='images/button_pressed_magenta.png')
        button.bind(
            on_release=self.key_release_handler, 
            on_press=self.key_press_handler)

        self.add_widget(button)

        button = Key(
            text='1', 
            value='1',
            background_down='images/button_pressed_magenta.png')
        button.bind(
            on_release=self.key_release_handler, 
            on_press=self.key_press_handler)

        self.add_widget(button)


class EntryBox(BoxLayout):
    syllables = ListProperty([])

    def __init__(self, **kwargs):
        super(EntryBox, self).__init__(**kwargs)

        self.textWidget = Label(text='', size_hint_x=13, font_size='30sp')
        self.add_widget(self.textWidget)
        self.add_widget(IconButton(
            #text='del', 
            size_hint_x=None,
            size_hint_y=None,
            size=['48dp', '48dp'],
            background_color=[127,127,127,1.0],
            up_image='images/del-no-alpha.png',
            down_image='images/del-no-alpha-glitch-inv.png', 
            on_release=self.delete))

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


def send_rhythm_via_osc():
    app = kivy.app.App.get_running_app()
    osc_address = app.osc_rhythm_address
    rhythm = kivy.app.App.get_running_app().rhythm.syllables
    rhythm = ponumi.flatten(rhythm)

    msg = []
    for beat in rhythm:
        msg.append(float(beat))

    send_osc_message(osc_address, msg)


def play_poem_via_osc(poem):
    send_rhythm_via_osc()

    osc_address = kivy.app.App.get_running_app().osc_data_address
    msg = ponumi_osc.poem_to_kyma_osc(poem)
    send_osc_message(osc_address, msg)

    #queue up the gate signal
    Clock.schedule_once(send_osc_go_on_signal, _osc_go_delay)


def send_osc_go_on_signal(*args):
    osc_address = kivy.app.App.get_running_app().osc_go_address

    #send the gate on signal (ie the rising edge of the gate signal)
    send_osc_message(osc_address, [1.0])
    #queue up the gate off signal (ie the falling edge)
    Clock.schedule_once(send_osc_go_off_signal, _osc_go_delay)

def send_osc_go_off_signal(*args):
    osc_address = kivy.app.App.get_running_app().osc_go_address

    send_osc_message(osc_address, [0.0])


def send_osc_syllable_gate_on(*args):
    osc_address = kivy.app.App.get_running_app().osc_syllable_gate_address

    send_osc_message(osc_address, [1.0])

def send_osc_syllable_gate_off(*args):
    osc_address = kivy.app.App.get_running_app().osc_syllable_gate_address

    send_osc_message(osc_address, [0.0])



def play_syllable_via_osc(syllable):
    osc_address = kivy.app.App.get_running_app().osc_syllable_address
    msg = ponumi_osc.syllables_to_kyma_osc([syllable])

    send_osc_message(osc_address, msg)


def short_flash_osc_indicator(*args):
    flash_osc_indicator(1)

def long_flash_osc_indicator(*args):
    flash_osc_indicator(3)

short_flash_osc_indicator_trigger = Clock.create_trigger(short_flash_osc_indicator)
long_flash_osc_indicator_trigger = Clock.create_trigger(long_flash_osc_indicator)


def flash_osc_indicator(repeats, *args):
    for i in range(repeats):
        Clock.schedule_once(partial(set_osc_indicator, 1),i)
        Clock.schedule_once(partial(set_osc_indicator, 2), i + 0.25)
        Clock.schedule_once(partial(set_osc_indicator, 3), i + 0.5)
        Clock.schedule_once(partial(set_osc_indicator, 0), i + 0.75)


def set_osc_indicator(state, *args):
    app = kivy.app.App.get_running_app()


    if state == 3:
        path = 'images/audio-volume-high.png'
    elif state == 2:
        path = 'images/audio-volume-medium.png'
    elif state == 1:
        path = 'images/audio-volume-low.png'
    elif state == -1:
        path = 'images/audio-volume-muted.png'
    else:
        path = 'images/audio-volume-none-glitch-inv.png'

    app.osc_indicator.icon = path


def send_osc_message(osc_address, msg):

    app = kivy.app.App.get_running_app()
    ip_address = app.osc_ip_address
    port = int(app.osc_port)

    try:
        oscAPI.sendMsg(
            osc_address, 
            dataArray=msg, 
            ipAddr=ip_address, 
            port=port, 
            typehint=None)

        print "\nsent:"
        print msg
        print "\nto: ", ip_address, port, osc_address

        if len(msg) > 12:
            long_flash_osc_indicator_trigger()
        else:
            short_flash_osc_indicator_trigger()
  


    except Exception as e:
        print "Problem sending OSC message"
        print e

        #The oscAPI creates a threading lock when sending an OSC message.
        #If there is an exception this lock isn't released and the application will hang
        #the next time an OSC message is sent because oscAPI will attempt to acquire a lock
        #and threading.Lock() will block. 
        oscAPI.oscLock.release()

        for i in range(2):
            Clock.schedule_once(partial(set_osc_indicator, -1), i)
            Clock.schedule_once(partial(set_osc_indicator, 0), (i + 0.5))

        if _DEBUG:
            raise(e)


###############################################################
# Top Level Widgets
###############################################################


class PonumiPerformerScreenManager(ScreenManager):

    def __init__(self, **kwargs):
        super(PonumiPerformerScreenManager, self).__init__(**kwargs)
        
        entry_screen = Screen(name='entry_screen')
        entry_screen.add_widget(NameInputScreen())

        manual_screen = Screen(name='manual_screen')
        manual_screen.add_widget(ManualScreen())

        keyboard_screen = Screen(name='keyboard_screen')
        keyboard_screen.add_widget(KeyboardScreen())

        rhythm_screen = Screen(name='rhythm_screen')
        rhythm_screen.add_widget(RhythmScreen())

        vcs_screen = Screen(name='vcs_screen')
        vcs_screen.add_widget(VCSScreen())

        config_screen = Screen(name='config_screen')
        config_screen.add_widget(ConfigScreen())

        self.add_widget(entry_screen)
        self.add_widget(manual_screen)
        self.add_widget(keyboard_screen)
        self.add_widget(rhythm_screen)
        self.add_widget(vcs_screen)
        self.add_widget(config_screen)




class PonumiPerformer(App):

    osc_ip_address = StringProperty(_default_osc_ip_address)
    osc_port = StringProperty(_default_osc_port)
    osc_data_address = StringProperty(_default_osc_data_address)
    osc_go_address = StringProperty(_default_osc_go_address)
    osc_syllable_address = StringProperty(_default_osc_syllable_address)
    osc_syllable_gate_address = StringProperty(_default_osc_syllable_gate_address)
    osc_rhythm_address = StringProperty(_default_osc_rhythm_address)


    osc_indicator = ObjectProperty(None)


    def __init__(self, **kwargs):
        super(PonumiPerformer, self).__init__(**kwargs)
        data_dir = getattr(self, 'user_data_dir')
        self.config_store = JsonStore(join(data_dir, 'ponumiperformer.json'))
        self.rhythm = _default_rhythm
        oscAPI.init()


    def build(self):
        self.load_config()

        rootscreen = RootScreen()

        navbar = NavBar()
        self.osc_indicator = navbar.osc_indicator
        rootscreen.add_widget(navbar)
        self.screen_manager = PonumiPerformerScreenManager()
        rootscreen.add_widget(self.screen_manager)

        return rootscreen


    def save_config(self):

        self.config_store.put('config', 
            osc_ip_address=self.osc_ip_address,
            osc_port=self.osc_port,
            osc_data_address=self.osc_data_address,
            osc_go_address=self.osc_go_address,
            osc_syllable_address=self.osc_syllable_address,
            osc_syllable_gate_address=self.osc_syllable_gate_address,
            osc_rhythm_address=self.osc_rhythm_address)            


    def load_config(self):

        if self.config_store.exists('config'):
            config = self.config_store.get('config')

            if 'osc_ip_address' in config: self.osc_ip_address = config['osc_ip_address']
            if 'osc_port' in config: self.osc_port = config['osc_port']
            if 'osc_data_address' in config: self.osc_data_address = config['osc_data_address']
            if 'osc_go_address' in config: self.osc_go_address = config['osc_go_address']
            if 'osc_syllable_address' in config: self.osc_syllable_address = config['osc_syllable_address']
            if 'osc_syllable_gate_address' in config: self.osc_syllable_gate_address = config['osc_syllable_gate_address']
            if 'osc_rhythm_address' in config: self.osc_rhythm_address = config['osc_rhythm_address']


    def load_default_config(self):
        self.osc_ip_address = _default_osc_ip_address
        self.osc_port = _default_osc_port
        self.osc_data_address = _default_osc_data_address
        self.osc_go_address = _default_osc_go_address
        self.osc_syllable_address = _default_osc_syllable_address
        self.osc_syllable_gate_address = _default_osc_syllable_gate_address
        self.osc_rhythm_address = _default_osc_rhythm_address





if __name__ == '__main__':

    # Temporary tweaking of ponumi syllables to compensate for a couple of anomalies 
    # in the index order of the Steph101.wav file:
    #START
    import copy
    syllable_list = copy.copy(ponumi.syllable_list)
    syllable_list.remove('zu')
    syllable_list.remove('n')
    syllable_list.insert(10, 'zu')
    syllable_list.insert(11, 'n')
    ponumi.syllables = dict( zip(syllable_list, range(0, len(syllable_list) ) ) )
    #END

    PonumiPerformer().run()