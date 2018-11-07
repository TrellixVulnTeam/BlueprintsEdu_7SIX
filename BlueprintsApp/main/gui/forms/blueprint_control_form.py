from gui.forms.form import Form
from utils.gui_utils import Themes
from utils import logger_utils
import pygame as pg
from pygame.locals import *
from gui.blueprints.attribute_blueprint import AttributeBlueprint
from gui.blueprints.character_blueprint import CharacterBlueprint
from gui.blueprints.function_blueprint import FunctionBlueprint
from gui.blueprints.sprite_blueprint import SpriteBlueprint
from blueprints.blueprint import Blueprint
from project_manager import ProjectManager
from blueprint_manager import BlueprintManager


class BlueprintControlForm(Form):

    def __init__(self, control_panel, display, project_info, coords=None, size=None):
        Form.__init__(self, display, coords, size)
        self.__project_info = project_info
        self.__cont_panel = control_panel
        self.__logger = logger_utils.get_logger(__name__)
        self.__bps = list()
        self.__bps_connections = list()

    def draw_form(self):
        pg.draw.rect(self.display, Themes.DEFAULT_THEME.get("panel_disabled"), self.get_rect(), 0)
        if self.get_rect().collidepoint(pg.mouse.get_pos()) == 1:
            pg.draw.rect(self.display, Themes.DEFAULT_THEME.get("selection_background"), self.get_rect(), 2)
        self.draw_connections()
        if len(self.__bps) > 0:
            for bp in self.__bps:
                if not bp.focused:
                    pg.draw.rect(self.display, Themes.DEFAULT_THEME.get("idle_blueprint"), bp.get_rect(), 0)
                else:
                    pg.draw.rect(self.display, Themes.DEFAULT_THEME.get("enabled_blueprint"), bp.get_rect(), 0)
                self.display.blit(bp.get_text(), bp.get_text_rect())
                if bp.is_hovered():
                    pg.draw.rect(self.display, Themes.DEFAULT_THEME.get("selection_background"), bp.get_rect(), 2)

    def draw_connections(self):
        for con in self.__bps_connections:
            c1 = con[0].get_rect().center
            c2 = con[1].get_rect().center
            pg.draw.line(self.display, Themes.DEFAULT_THEME.get("connection_line"), c1, c2, 2)

    def unfocuse_blueprints(self):
        self.__cont_panel.set_blueprint(None)
        if len(self.__bps) > 0:
            for bp in self.__bps:
                bp.focused = False

    def check_form_events(self, event):
        super().check_form_events(event)
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:   # LEFT MOUSE BUTTON
                pos = pg.mouse.get_pos()
                if len(self.__bps) > 0:
                    for bp in self.__bps:
                        if bp.get_rect().collidepoint(pos) == 1:
                            bp.pressed = True
                            bp.set_offset(pos)
                            if not bp.focused:
                                self.unfocuse_blueprints()
                                bp.focused = True
                                self.__cont_panel.set_blueprint(bp)
                            elif bp.focused:
                                self.unfocuse_blueprints()
                            break
            elif event.button == 3:  # RIGHT MOUSE BUTTON
                pos = pg.mouse.get_pos()
                if len(self.__bps) > 0:
                    for bp in self.__bps:
                        if bp.get_rect().collidepoint(pos) == 1:
                            for bp_1 in self.__bps:
                                if bp != bp_1 and bp_1.focused:
                                    self.connect_blueprints(bp_1, bp)

        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:   # LEFT MOUSE BUTTON
                pos = pg.mouse.get_pos()
                if len(self.__bps) > 0:
                    for bp in self.__bps:
                        if bp.get_rect().collidepoint(pos) == 1:
                            bp.pressed = False
                            break
        elif event.type == MOUSEMOTION:
            if len(self.__bps) > 0:
                for bp in self.__bps:
                    if bp.pressed:
                        mx, my = event.pos
                        bp.set_topleft((mx + bp.offset[0], my + bp.offset[1]))
                        self.__check_blueprint_inbound(bp)

    def __check_blueprint_inbound(self, blueprint):
        r = self.get_rect()
        bp = blueprint.get_rect()
        left, top = bp.left, bp.top
        if r.left > bp.left:
            left = r.left
        if r.right < bp.right:
            left = r.right - bp.width
        if r.top > bp.top:
            top = r.top
        if r.bottom < bp.bottom:
            top = r.bottom - bp.height
        blueprint.set_topleft((left, top))

    def add_attribute(self):
        t = AttributeBlueprint(self.get_rect())
        self.__bps.append(t)

    def add_character(self):
        t = CharacterBlueprint(self.get_rect())
        self.__bps.append(t)

    def add_function(self):
        t = FunctionBlueprint(self.get_rect())
        self.__bps.append(t)

    def add_sprite(self):
        t = SpriteBlueprint(self.get_rect())
        self.__bps.append(t)

    def save_project(self):
        """Description: function prepares blueprints in the current development
        panel for further processing
        """
        data = list()
        for bp in self.__bps:
            d = list()

            d.append(bp.get_blueprint())
            r = bp.get_rect()
            d.append([r.topleft, r.size])

            data.append(d)
        ProjectManager.save_project(self.__project_info, data, self.__bps_connections)

    def load_project(self, bp_conn, bps):
        self.__bps = BlueprintManager.reverse_parse_blueprints(self.get_rect(), bps)
        self.__logger.debug(self.__bps)
        self.__bps_connections = BlueprintManager.generate_connections(bp_conn, self.__bps)

    def connect_blueprints(self, bp_1, bp_2):
        valid = True
        if bp_1.get_blueprint().get_type() == Blueprint.TYPES.get("ATTRIBUTE"):
            if (bp_2.get_blueprint().get_type() == Blueprint.TYPES.get("ATTRIBUTE")) or \
                    (bp_2.get_blueprint().get_type() == Blueprint.TYPES.get("FUNCTION")):
                valid = False
        if bp_1.get_blueprint().get_type() == Blueprint.TYPES.get("CHARACTER"):
            if bp_2.get_blueprint().get_type() == Blueprint.TYPES.get("CHARACTER"):
                valid = False
        if bp_1.get_blueprint().get_type() == Blueprint.TYPES.get("FUNCTION"):
            if (bp_2.get_blueprint().get_type() == Blueprint.TYPES.get("FUNCTION")) or \
                    (bp_2.get_blueprint().get_type() == Blueprint.TYPES.get("ATTRIBUTE")):
                valid = False
        if bp_1.get_blueprint().get_type() == Blueprint.TYPES.get("SPRITE"):
            if bp_2.get_blueprint().get_type() == Blueprint.TYPES.get("SPRITE"):
                valid = False
        for con in self.__bps_connections:
            if ((con[0] == bp_1) and (con[1] == bp_2)) or \
                    ((con[0] == bp_2) and (con[1] == bp_1)):
                valid = False
        if valid:
            self.__bps_connections.append([bp_1, bp_2])
            self.__logger.debug("Blueprints connected")
