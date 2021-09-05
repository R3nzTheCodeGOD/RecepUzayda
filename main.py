from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from random import choice, randint
from json import dump, load

Config.set('graphics', 'width', '650')
Config.set('graphics', 'height', '400')
Builder.load_file("menu.kv")

class BestScore:
    filename = "./score"

    def get_best_score(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                return load(file)[0]
        except FileNotFoundError:
            with open(self.filename, "w", encoding="utf-8") as file:
                dump([ 0 ], file)
                return 0

    def update_best_score(self, current_score):
        with open(self.filename, "w", encoding="utf-8") as file:
            dump([ current_score ], file)
            
    def score_control(self, current_score):
        best_score = self.get_best_score()
        
        if current_score > best_score:
            self.update_best_score(current_score)
            return True
        else:
            return False


class MainWidget(RelativeLayout):
    from user_actions import keyboard_closed, on_keyboard_up, on_keyboard_down, on_touch_down, on_touch_up
    
    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 8
    V_LINES_SPACING = .25
    vertical_lines = []

    H_NB_LINES = 15
    H_LINES_SPACING = .1
    horizontal_lines = []

    SPEED = .85
    current_offset_y = 0
    current_y_loop = 0

    SPEED_X = 2.25
    current_speed_x = 0
    current_offset_x = 0

    NB_TILES = 15
    tiles = []
    tiles_coordinates = []

    SHIP_WIDTH = .04
    SHIP_HEIGHT = .025
    SHIP_BASE_Y = .04
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    state_game_over = False
    state_game_has_started = False

    score_class = BestScore()
    menu_title = StringProperty("R E C E P  U Z A Y D A")
    menu_button_title = StringProperty("HOHOHOYT")
    score_text = StringProperty()
    best_score_text = StringProperty("BEST SCORE: " + str(score_class.get_best_score()))

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.reset_game()

        if platform in ("linux", "win", "macosx"):
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0 / 144.0)
        Clock.schedule_interval(lambda dt: choice(self.sound_random).play(), 6)
        Clock.schedule_once(lambda dt: self.sound_welcome.play())
        Clock.schedule_interval(lambda dt: self.sound_music.play() if self.sound_music.state == "stop" and not self.state_game_over else None, 1)
        Clock.schedule_once(lambda dt: self.sound_hohoyt.play(), 3.5)
                
    def init_audio(self):
        self.sound_welcome = SoundLoader.load("audio/welcome.wav")
        self.sound_gameover_impact = SoundLoader.load("audio/fart.wav")
        self.sound_music = SoundLoader.load("audio/tema.wav")
        self.sound_hohoyt = SoundLoader.load("audio/hohoyt.wav")
        self.sound_random = (
            SoundLoader.load("audio/recep1.wav"),
            SoundLoader.load("audio/recep2.wav"),
            SoundLoader.load("audio/recep3.wav"),
            SoundLoader.load("audio/recep4.wav"),
            SoundLoader.load("audio/recep5.wav"),
            SoundLoader.load("audio/recep6.wav"),
            self.sound_hohoyt
        )

        self.sound_music.volume = .25

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def init_tiles(self):
        with self.canvas:
            Color(1, .52, .15)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, .52, .15)
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, .52, .15)
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def reset_game(self):
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        self.tiles_coordinates = []
        self.score_text = "SCORE: " + str(self.current_y_loop)
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()
        self.state_game_over = False

    def transform(self, x, y):
        lin_y = y * self.perspective_point_y / self.height
        if lin_y > self.perspective_point_y:
            lin_y = self.perspective_point_y

        diff_x = x - self.perspective_point_x
        diff_y = self.perspective_point_y - lin_y
        factor_y = diff_y / self.perspective_point_y
        factor_y = pow(factor_y, 4)

        tr_x = self.perspective_point_x + diff_x * factor_y
        tr_y = self.perspective_point_y - factor_y * self.perspective_point_y

        return int(tr_x), int(tr_y)

    def transform_2D(self, x, y):
        return int(x), int(y)

    def update_ship(self):
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGHT * self.height
        self.ship_coordinates[0] = (center_x-ship_half_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y + ship_height)
        self.ship_coordinates[2] = (center_x + ship_half_width, base_y)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])

        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def update_tiles(self):
        for i in range(0, self.NB_TILES):
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0]+1, tile_coordinates[1]+1)
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_lines(self):
        start_index = -int(self.V_NB_LINES/2)+1
        for i in range(start_index, start_index+self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def update_horizontal_lines(self):
        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index+self.V_NB_LINES-1

        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)
        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def check_ship_collision(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)
        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    def pre_fill_tiles_coordinates(self):
        for i in range(0, 10):
            self.tiles_coordinates.append((0, i))

    def generate_tiles_coordinates(self):
        last_x = 0
        last_y = 0

        for i in range(len(self.tiles_coordinates)-1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_x = last_coordinates[0]
            last_y = last_coordinates[1] + 1

        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            r = randint(0, 2)
            start_index = -int(self.V_NB_LINES / 2) + 1
            end_index = start_index + self.V_NB_LINES - 1
            if last_x <= start_index:
                r = 1
            if last_x >= end_index:
                r = 2

            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            if r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))

            last_y += 1

    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        line_x = central_line_x + offset*spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING*self.height
        line_y = index*spacing_y-self.current_offset_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def on_menu_button_pressed(self):
        if not self.state_game_over:
            self.sound_hohoyt.play()

        self.sound_music.stop()
        self.sound_music.play()
        self.reset_game()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0

    def update(self, dt):
        time_factor = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()

        if not self.state_game_over and self.state_game_has_started:
            speed_y = self.SPEED * self.height / 100
            self.current_offset_y += speed_y * time_factor
            spacing_y = self.H_LINES_SPACING * self.height
            
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score_text = "SCORE: " + str(self.current_y_loop)
                self.generate_tiles_coordinates()

            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor

        if not self.check_ship_collision() and not self.state_game_over:
            self.state_game_over = True
            self.menu_title = "R E C E P L E N D I N"
            self.menu_button_title = "TEKRAR OYNA"
            self.menu_widget.opacity = 1
            Clock.schedule_once(lambda dt: self.sound_gameover_impact.play())
            
            if self.score_class.score_control(self.current_y_loop):
                self.best_score_text = "BEST SCORE: " + str(self.score_class.get_best_score())


class R3nzApp(App):
    pass


if __name__ == "__main__":
    R3nzApp().run()