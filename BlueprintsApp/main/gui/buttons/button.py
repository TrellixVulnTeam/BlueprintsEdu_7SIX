from abc import ABC, abstractmethod
import pygame as pg
from utils import gui_utils
from utils import app_utils
import os

class Button(ABC):

    def __init__(self, text, theme, pos):
        font = pg.font.Font(theme.get("button_font_style"), int(app_utils.BOARD_HEGHT * .05))
        self.__text = font.render(text, True, theme.get("font"))
        self.__width = int(app_utils.BOARD_HEGHT * gui_utils.BUTTON_PRIMARY[0])
        self.__height = int(app_utils.BOARD_HEGHT * gui_utils.BUTTON_PRIMARY[1])
        self.color = theme.get("button")
        self.set_coordinates(pos)

    @abstractmethod
    def on_click(self, board):
        pass

    def get_text(self):
        return self.__text

    def get_color(self):
        return self.color

    def set_coordinates(self, pos):
        self.__x = int(app_utils.BOARD_WIDTH * .5)
        start = int(app_utils.BOARD_HEGHT * .6)
        if pos > 0:
            self.__y = int(start + (self.__height + int(gui_utils.BUTTON_MARGIN * app_utils.BOARD_HEGHT)) * pos)
        else:
            self.__y = start

    def set_custom_coordinates(self, pos):
        self.__x, self.__y = pos

    def set_custom_size(self, size):
        self.__width = int(app_utils.BOARD_WIDTH * size[0])
        self.__height = int(app_utils.BOARD_HEGHT * size[1])

    def get_topleft(self):
        x = self.__x - int(self.__width * .5)
        y = self.__y - int(self.__height * .5)
        return (x, y)

    def is_hovered(self, coords):
        r = self.get_rect()
        return (coords[0] >= r.x and coords[0] <= (r.x + r.width) and
            coords[1] >= r.y and coords[1] <= (r.y + r.height))


    def get_rect(self):
        return pg.Rect(self.get_topleft(), (self.__width, self.__height))

    def get_text_rect(self):
        text_rect = self.__text.get_rect()
        text_rect.center = self.get_rect().center
        return text_rect
