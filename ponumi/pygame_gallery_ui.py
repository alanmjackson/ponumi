import os
import math
import random
import pygame
import ponumi



from pygame.locals import *


_image_path = os.path.join('..', 'data')

buttons = []

# set up the colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
LIGHT_GREEN = (128, 255, 128)

grid = 75
columns = 3
text_box_horizontal_margin = 10
text_box_vertical_margin = 10

#Set up pygame etc...
pygame.init()
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
textInputFont = pygame.font.SysFont(name="Balker", size=48, bold=False, italic=False)




class Button:

    def __init__(self, name, image, x, y, action=None, action_args=[], action_kwargs={}):
        self.name = name
        self.image = image
        self.x = x
        self.y = y
        self.width = image.get_width()
        self.height = image.get_height()
        self.action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs


    def is_in(self, co_ords):

        #test x
        if co_ords[0] < self.x or co_ords[0] > self.x + self.width:
            return False

        #test y
        if co_ords[1] < self.y or co_ords[1] > self.y + self.height:
            return False

        return True


    def do_action(self):
        if self.action != None:
            return self.action(*self.action_args, **self.action_kwargs)



def get_clicked_button(position, buttons):

    for button in buttons:
        if button.is_in(position):
            return button


# Button Actions
def enter_syllable(syllable, syllable_list):
    syllable_list.append(syllable)

def backspace_syllable(syllable_list):
    if len(syllable_list) > 0:
        syllable_list.pop()

# END OF Button Actions


def draw_rounded_rect(surface, color, rect, radius=0, width=1):

    radius = min(radius, abs(rect.right - rect.left)/2, abs(rect.bottom - rect.top)/2)
    width = min(width, radius)
    width = max(width, 1)

    #top line
    pygame.draw.line(surface, color, (rect.left + radius, rect.top), 
                    (rect.right - radius + 1, rect.top), width)

    #bottom line
    pygame.draw.line(surface, color, (rect.left + radius - 1, rect.bottom), 
                    (rect.right - radius, rect.bottom), width)

    #left line
    pygame.draw.line(surface, color, (rect.left, rect.top + radius - 1), 
                    (rect.left, rect.bottom - radius - 1), width)

    #right line
    pygame.draw.line(surface, color, (rect.right, rect.top + radius), 
                    (rect.right, rect.bottom - radius + 1), width)


    if radius > 0:
        pygame.draw.arc(surface, color, 
            Rect(rect.left - (width-1)/2, rect.top - (width-1)/2, 
            2*radius + width, 2*radius + width), 
            0.5 * math.pi, math.pi,  width)

        pygame.draw.arc(surface, color, 
            Rect(rect.left - (width-1)/2, rect.bottom - 2*radius - (width-1)/2, 
            2*radius + width, 2*radius + width), 
            math.pi, 1.5*math.pi,  width)

        pygame.draw.arc(surface, color, 
            Rect(rect.right - 2*radius - (width-1)/2, rect.bottom - 2*radius - (width-1)/2, 
            2*radius + width, 2*radius + width), 
            1.5*math.pi, 2*math.pi,  width)

        pygame.draw.arc(surface, color, 
            Rect(rect.right - 2*radius - (width-1)/2, rect.top-(width-1)/2, 
            2*radius + width, 2*radius + width), 
            0, 0.5*math.pi,  width)



def show_entered_syllables(entered_syllables):
    
    syllable_string = ""
    for syllable in entered_syllables:
        syllable_string += syllable + " "

    text_x = 2 * grid + text_box_horizontal_margin
    text_y = 9 * grid + text_box_vertical_margin
    text_width = (13 - 2) * grid - 2 * text_box_horizontal_margin
    text_height = (10 - 9) * grid - 2 * text_box_vertical_margin

    text = textInputFont.render(syllable_string, True, LIGHT_GREEN)

    #clear any text that's there already
    pygame.draw.rect(screen, BLACK, (text_x, text_y, text_width, text_height))

    screen.blit(text, (text_x, text_y))
    pygame.display.flip()


def main():


    draw_rounded_rect(screen, (0,200,50), pygame.Rect(100,200,65,65), 10, 2)



    pygame.display.flip()

    pygame.event.set_allowed(pygame.KEYDOWN)
    pygame.event.set_allowed(pygame.MOUSEBUTTONUP)
    while True:
        event = pygame.event.wait()
        if event.type == pygame.KEYDOWN:
            break


    entered_syllables = []

    #create the buttons

    rows = len(ponumi.syllable_table)
    rows_in_column = int(float(rows) / float(3) + 0.5)        #round up

    for row_index in range(rows_in_column):
        
        for column in range(columns):

            table_row_index = row_index + column * rows_in_column

            if table_row_index < rows:
                row = ponumi.syllable_table[table_row_index]
                for item_index in range(len(row)):
                    item = row[item_index]
                    img = pygame.image.load(os.path.join(_image_path, item +".png"))
                    buttons.append(Button(
                        name=item, 
                        image=img, 
                        x=item_index * grid + column * 6 * grid, 
                        y=row_index * grid,
                        action=enter_syllable,
                        action_args=[item, entered_syllables]
                        ))
                    

    img = pygame.image.load(os.path.join(_image_path, "enter_your_name.png"))
    buttons.append(Button("enter_your_name", img, 2 * grid, 8 * grid))

    img = pygame.image.load(os.path.join(_image_path, "text_input.png"))
    buttons.append(Button("text_input", img, 2 * grid, 9 * grid))

    img = pygame.image.load(os.path.join(_image_path, "backspace.png"))
    buttons.append(Button(
        name="backspace", 
        image=img, 
        x=13 * grid, 
        y=9 * grid, 
        action=backspace_syllable, 
        action_args=[entered_syllables]))

    img = pygame.image.load(os.path.join(_image_path, "enter.png"))
    buttons.append(Button("enter", img, 14 * grid, 9 * grid))

    img = pygame.image.load(os.path.join(_image_path, "help.png"))
    buttons.append(Button("help", img, 16 * grid, 9 * grid))



    #render buttons
    for button in buttons:
        screen.blit(button.image, (button.x, button.y))



    pygame.display.flip()

    #pygame.image.save(screen, "screen.png")

    while True:
        event = pygame.event.wait()

        pushed_button = None
        #give visual feedback when clicking the button
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            pushed_button = get_clicked_button(pos, buttons)
            inverted_image = pushed_button.image.copy()
            print(inverted_image.get_palette())
            inverted_image.set_palette([(255,0,0),(0,0,0)])
            screen.blit(inverted_image, (pushed_button.x, pushed_button.y))

        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            button = get_clicked_button(pos, buttons)
            if button != None:
                button.do_action()
                show_entered_syllables(entered_syllables)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                break





if __name__ == '__main__':
    main()

