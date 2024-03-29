import json
import os
import sys
import time
from tkinter import Button, Entry
from tkinter.filedialog import asksaveasfilename, askopenfile
import pygame
import ButtonClass
import InputClass
from Projekt_Bedienungsanleitung import *
from backend import Game


class Display:  # Zu Display ändern
    """Display Klasse.

    Klasse erstellt ein Pygame Display und ersellt eine Instanz von dem aus
    backend.py importiertem game.
    """

    def __init__(self, windowX: int, windowY: int, nodes=None):
        """Init Klasse.

        Kommentar: Konstrukter der Klasse Display()
        Input: Name der Klasse, x-Größe des Bildschirms, y-Größe des
               Bildschirms, optional: knotenliste
        Output: Kein Output
        Besonders: Erstellt ein pygame Display, erstellt eine Instanz der
                   game() klasse
        """
        pygame.font.init()
        self.curr_num_premade = 0
        self.curr_place_mode = "Zelle"
        self.place_modes = ["Zelle", "Spur", "Radieren", "Form"]
        nodes = nodes or []
        self.window_x = windowX
        self.window_y = windowY
        self.display_x = windowX + 300
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.grey = (173, 173, 173)
        self.green = (46, 218, 53)
        self.red = (255, 0, 0)
        self.curr_rotation = 0
        board_size_x = self.window_x // 10
        board_size_y = self.window_y // 10
        self.verschiebung_ges = [0, 0]
        self.game = Game(nodes=nodes, board_x=board_size_x, board_y=board_size_y)  # noqa: E501
        self.display = pygame.display.set_mode((self.display_x, self.window_y))
        self.play_but = ButtonClass.ButtonPy(self.window_x + 10, 500, ['play', 'pause'])
        self.input_iterations = InputClass.Input(self.window_x + 10, 600, 100, 40, self.display, mode='int')

    def weltformnamefenster(self):
        """Fragt Name für benutzerdefiniertes Objekt ab.

        Kommentar: Öffnet Fenster mit tkinter.
        Input: Kein Input
        Output: Kein Output
        Besonders: Keine Besonderheiten
        """
        fenster = Tk()
        fenster.focus_force()

        fensterBreite = fenster.winfo_reqwidth()
        fensterHoehe = fenster.winfo_reqheight()
        positionRechts = int(fenster.winfo_screenwidth() / 2 - fensterBreite / 2)
        positionUnten = int(fenster.winfo_screenheight() / 2 - fensterHoehe / 0.75)

        fenster.geometry("+{}+{}".format(positionRechts, positionUnten))

        fenster.geometry("300x300")
        fenster.title("")

        frage = Label(fenster, text="Wie soll der Name der Form sein?")
        namefeld = Entry(fenster, bg="goldenrod", fg="black")
        weiterbutton = Button(fenster, bg="goldenrod", fg="black", text="In Datei Speichern", command=lambda: [
            Display.weltalsformspeichern(self.game.deepcopy_nodes(), namefeld.get()), fenster.destroy()])
        frage.grid(row=0, column=0, sticky="nesw")
        namefeld.grid(row=1, column=0, padx=5, pady=5, sticky="nesw")
        weiterbutton.grid(row=2, column=0, padx=5, pady=5, sticky="nesw")

        fenster.grid_columnconfigure(0, weight=1)
        fenster.grid_rowconfigure(0, weight=1)
        fenster.grid_rowconfigure(1, weight=1)
        fenster.grid_rowconfigure(2, weight=1)

    @classmethod
    def is_file(cls, fname):
        return os.path.isfile(fname)

    @classmethod
    def ask_file(cls):
        # ask_window = Tk()
        # ask_window.mainloop()
        return asksaveasfilename(filetypes=[('JSON files', '.json')], initialfile='',
                                 defaultextension=".json")

    @classmethod
    def weltalsformspeichern(cls, nodes, name):
        """Welt als form speichern.

        Kommentar: Passt Weltpunkte an und speichert diese als json.
        Input: Weltpunkte, Name des Objektes
        Output: Kein Output
        Besonders: Keine Besonderheiten
        """
        if len(nodes) == 0:
            return
        pth = cls.ask_file()
        if pth is None or name is None:
            return
        minx = nodes[0][1]
        miny = nodes[0][0]
        for i in range(len(nodes)):
            if nodes[i][1] < minx:
                minx = nodes[i][1]
            if nodes[i][0] < miny:
                miny = nodes[i][0]
        for i in range(len(nodes)):
            nodes[i][1] = nodes[i][1]
            nodes[i][0] = nodes[i][0]

        file_exist = cls.is_file(pth)
        config = dict()
        if file_exist:
            with open(pth, 'r') as f:
                config = json.load(f)
        config[name] = nodes
        with open(pth, 'w') as f:
            json.dump(config, f)

    def change_rotatation(self):
        self.curr_rotation += 90
        while self.curr_rotation >= 360:
            self.curr_rotation -= 360

    def clear_board(self):
        """Entfernt alle Objekte vom Bord.

        Kommentar: leert das Bord und erzeugt ein Gitter.
        Input: Name der Instanz
        Output: Kein Output
        Besonders: Keine Besonderheiten
        """
        pygame.draw.rect(self.display, self.white, pygame.Rect(0, 0, self.window_x, self.window_y))
        self.draw_grid()

    def clear_menu(self):
        """Übermalt den Sidebar bereich weiß.

        Kommentar:Malt ein weißes Rechteck über den sidebar bereich und setzt
                  diesen dadurch zurück.
        Input: Name der Instanz
        Output: Kein Output
        Besonders: Keine Besonderheiten
        """
        pygame.draw.rect(self.display, self.white, pygame.Rect(self.window_x, 0, 300, self.window_y))

    def import_premade(self):
        # TODO: fucking unübersichtlich
        new_premade = self.open_file()
        if new_premade and isinstance(new_premade, dict):
            for key in list(new_premade.keys()):
                if isinstance(new_premade[key], list):
                    for kobject in new_premade[key]:
                        if isinstance(kobject, list) and len(kobject) == 2 and isinstance(kobject[0],
                                                                                          (int, float)) and isinstance(
                            kobject[1], (int, float)):
                            old_premade = self.game.premade
                            merged = self.game.merge_dict(old_premade, new_premade)
                            self.game.premade = merged

    def next_premade(self):
        """Geht zum nächsten Vorgefertigten Objekt.

        Kommentar: rotiert in der Premade liste zum nächsten
        Input: Name der Instanz
        Output: Kein Output
        Besonders: Verändert self.curr_num_premade, nutzt Walrus operator.
        """
        self.curr_num_premade += 1
        if self.curr_num_premade >= (len_premade := (len(self.game.list_premade()))):
            self.curr_num_premade -= len_premade

    def previous_premade(self):
        """Wechselt zum vorherigen vorgefertigten Objekt.

        Kommentar: rotiert in der Premade liste zum vorherigen
        Input: Name der Instanz
        Output: Kein Output
        Besonders: Verändert self.curr_num_premade
        """
        self.curr_num_premade -= 1
        if self.curr_num_premade < 0:
            self.curr_num_premade += len(self.game.list_premade())

    def change_place_mode(self):
        """Wechselt den Place mode.

        Kommentar: Wechselt den Place mode zwischen 'Zelle' und 'premade'
        Input: Name der Instanz
        Output: Kein Output
        Besonders: Verändert self.curr_place_mode
        """
        place_index = self.place_modes.index(self.curr_place_mode) + 1
        if place_index >= len(self.place_modes):
            place_index -= len(self.place_modes)
        self.curr_place_mode = self.place_modes[place_index]

    def open_menu(self):
        """Öffnet ein TKinter Menü.
        Kommentar: Erstelt ein TKInter Menü und öffnet dieses
        Input: Name der Instanz
        Output: Kein Output
        Besonders: Keine Besonderheiten
        """
        self.fenster = Tk()

        self.fensterBreite = self.fenster.winfo_reqwidth()
        self.fensterHoehe = self.fenster.winfo_reqheight()
        positionRechts = int(self.fenster.winfo_screenwidth() / 2 - self.fensterBreite / 2)
        positionUnten = int(self.fenster.winfo_screenheight() / 2 - self.fensterHoehe / 0.75)

        self.fenster.geometry("+{}+{}".format(positionRechts, positionUnten))

        self.fenster.geometry("200x300")
        self.fenster.resizable(0, 0)

        self.fenster.title("CGoL")

        self.title_label = Label(self.fenster, text="Spielmenü")
        self.title_label.grid(row=0, sticky='nesw', padx=5, pady=5)

        self.fortsetzen = Button(self.fenster, bg="goldenrod", fg="black", text="Spiel fortsetzen",
                                 command=lambda: self.fenster.destroy())
        self.fortsetzen.grid(row=1, sticky=' nesw', padx=5, pady=5)

        self.save_button = Button(self.fenster, bg="goldenrod", fg="black", text="Welt speichern",
                                  command=lambda: [self.save_file(self.game.get_nodes(), False)])
        self.save_button.grid(row=2, sticky=' nesw', padx=5, pady=5)

        self.save_as_premade_button = Button(self.fenster, bg="goldenrod", fg="black", text="Welt als Form speichern",
                                             command=lambda: [self.fenster.destroy(), self.weltformnamefenster()])
        self.save_as_premade_button.grid(row=3, sticky=' nesw', padx=5, pady=5)

        self.load_button = Button(self.fenster, bg="goldenrod", fg="black", text="Welt laden",
                                  command=lambda: [self.open_saved_board()])
        self.load_button.grid(row=4, sticky=' nesw', padx=5, pady=5)

        self.import_button = Button(self.fenster, bg="goldenrod", fg="black", text="Objekte laden",
                                    command=lambda: [self.import_premade()])
        self.import_button.grid(row=5, sticky="nesw", padx=5, pady=5)

        self.manual_button = Button(self.fenster, bg="goldenrod", fg="black", text="Anleitung",
                                    command=lambda: [self.fenster.destroy(), anleitung()])
        self.manual_button.grid(row=6, sticky=' nesw', padx=5, pady=5)

        self.quit_button = Button(self.fenster, bg="goldenrod", fg="black", text="Spiel verlassen",
                                  command=lambda: self.spiel_verlassen())
        self.quit_button.grid(row=7, sticky=' nesw', padx=5, pady=5)

        self.fenster.grid_columnconfigure(0, weight=1)
        self.fenster.grid_rowconfigure(0, weight=1)
        self.fenster.grid_rowconfigure(1, weight=1)
        self.fenster.grid_rowconfigure(2, weight=1)
        self.fenster.grid_rowconfigure(3, weight=1)
        self.fenster.grid_rowconfigure(4, weight=1)
        self.fenster.grid_rowconfigure(5, weight=1)
        self.fenster.grid_rowconfigure(6, weight=1)
        self.fenster.grid_rowconfigure(7, weight=1)

        self.fenster.mainloop()

    def draw_grid(self):
        """Zeichnet ein Gitter.

        Kommentar: erzeugt ein Gitter auf der GUI
        Input: Name der Instanz
        Output: Kein Output
        Besonders: Keine Besonderheiten
        """
        for x_koord in range(0, self.window_x, 10):
            start_x = x_koord
            start_y = 0
            end_x = x_koord
            end_y = self.window_y
            start = (start_x, start_y)
            end = (end_x, end_y)
            pygame.draw.line(self.display, self.grey, start, end, width=1)
        for y_koord in range(0, self.window_y, 10):
            start_x = 0
            start_y = y_koord
            end_x = self.window_x
            end_y = y_koord
            start = (start_x, start_y)
            end = (end_x, end_y)
            pygame.draw.line(self.display, self.grey, start, end, width=1)

    def show_board(self, points=None):
        """Zeigt das Bord an.

        Kommentar: Erzeugt die Punkte auf dem Bord
        Input: Name der Instanz, punkte
        Output: Kein Output
        Besonders: Aktualisiert das Bord
        """
        points = points or self.game.get_nodes()
        self.clear_board()
        for point in points:
            x_koord = (point[0] * 10) + 1
            y_koord = (point[1] * 10) + 1
            if y_koord < self.window_y:
                pygame.draw.rect(self.display, self.black, pygame.Rect(y_koord, x_koord, 9, 9))  # noqa: E501
        null = [(self.verschiebung_ges[1] * 10) + 1, (self.verschiebung_ges[0] * 10) + 1]
        mid_x = (((self.window_x // 20) + -1) * 10) + 1
        mid_y = (((self.window_x // 20) + -1) * 10) + 1
        pygame.draw.rect(self.display, self.red, pygame.Rect(null[0], null[1], 4.5, 5))
        pygame.draw.rect(self.display, self.green, pygame.Rect((mid_x, mid_y + 4.5, 4.5, 5)))
        Display.update_board()

    def manipulate_point(self, pos_x: int, pos_y: int):
        """Manipulierung eines Punktes.

        Kommentar: Manipuliert einen Punkt (hinzufuegen wenn keiner vorhanden,
                   entfernen wenn Punhkt vorhanden)
        Input: Name der Instanz, x-Position des Klicks, y-Position des Klicks
        Output: Kein Output
        Besonders: Keine Besonderheiten
        """
        node_x = pos_x // 10
        node_y = pos_y // 10
        point_x = (node_x * 10) + 1
        point_y = (node_y * 10) + 1
        if self.curr_place_mode == "Zelle":
            exist = self.game.manipulate_node(node_x, node_y)
            if exist:
                pygame.draw.rect(self.display, self.black, pygame.Rect(point_y, point_x, 9, 9))  # noqa: E501
            else:
                pygame.draw.rect(self.display, self.white, pygame.Rect(point_y, point_x, 9, 9))  # noqa: E501
        elif self.curr_place_mode == "Form":
            name = self.game.list_premade()[self.curr_num_premade]
            obj_select = self.game.add_premade(name, node_x, node_y, self.curr_rotation // 90)
            to_draw = (cell for cell in self.game.add_premade(name, node_x, node_y, self.curr_rotation // 90) if
                       cell[1] * 10 < self.window_x)
            for point in to_draw:
                point_x = (point[0] * 10) + 1
                point_y = (point[1] * 10) + 1
                pygame.draw.rect(self.display, self.black, pygame.Rect(point_y, point_x, 9, 9))  # noqa: E501

    def draw_menu(self):
        """Zeichnet ein Seitenmenü.

        Kommentar: Zeichneet ein Seitenmenü, dass auch variablen anzeigt
        Input: greift auf self.game.iterations , self.curr_place_mode und
               self.curr_num_premade zu
        Output: Kein Output
        Besonders: Keine Besonderheiten
        """
        self.clear_menu()
        # pygame.draw.rect(self.Display, self.white, pygame.Rect(self.window_x, self.window_y, self.display_x-self.window_x, self.window_y))
        pygame.draw.line(self.display, self.black, (self.window_x, 0), (self.window_x, self.window_y), width=2)
        pygame.draw.line(self.display, self.black, (self.window_x + 3, 0), (self.window_x + 3, self.window_y), width=2)
        pygame.draw.line(self.display, self.black, (self.window_x, 325), (self.display_x, 325), width=1)

        myfont = pygame.font.SysFont('Comic Sans MS', 15)
        instructions = ['Esc - Programm beenden', 'M - Menü öffnen', 'F - Nächste Iteration', '-> - Nächste Form',
                        '<- - Vorherige Form', 'P - Modus Zelle/Spur/Radieren/Form', '      platzieren',
                        'Linksklick - Interaktion', 'Rechtsklick - Zelle zentrieren',
                        "R - rotieren (im Uhrzeigersinn 90°)", '',
                        f'Iterationen :  {self.game.iterations}', f'Modus :  {self.curr_place_mode}',
                        f'Form :  {self.game.list_premade()[self.curr_num_premade]}',
                        f"Rotation : {self.curr_rotation}"]
        for counter, text in enumerate(instructions):
            textsurface = myfont.render(text, False, (0, 0, 0))
            self.display.blit(textsurface, (self.window_x + 10, 10 + 30 * counter))

        self.display.blit(self.play_but.surface, (self.play_but.x, self.play_but.y))
        self.input_iterations.update()
        self.update_board()

    def wait_keypress(self):
        """Wartet auf einen Tastendruck.

        Kommentar: wartet auf einen Tastendruck und führt entsprechende Befehle
                   aus
        Input: Name der Instanz
        Output: Kein Output
        Besonders: Keine Besonderheiten
        """
        while self.play_but.state == 'play':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.spiel_verlassen()
                    # pygame.quit()
                    # sys.exit()
                if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0] is True and \
                        pygame.mouse.get_pos()[0] < self.window_x:
                    mouse_pos = pygame.mouse.get_pos()
                    pos_x = mouse_pos[0] // 10
                    pos_y = mouse_pos[1] // 10
                    if self.curr_place_mode == "Spur":
                        self.game.add_node(pos_y, pos_x)
                        pygame.draw.rect(self.display, self.black,
                                         pygame.Rect((pos_x * 10) + 1, (pos_y * 10) + 1, 9, 9))  # noqa: E501
                        self.update_board()
                    elif self.curr_place_mode == "Radieren":
                        self.game.remove_node(pos_y, pos_x)
                        pygame.draw.rect(self.display, self.white,
                                         pygame.Rect((pos_x * 10) + 1, (pos_y * 10) + 1, 9, 9))  # noqa: E501
                        self.update_board()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    pos_x = pos[1]
                    pos_y = pos[0]
                    if pos_y < self.window_x:
                        if event.button == 1:
                            self.manipulate_point(pos_x, pos_y)
                            self.show_board()
                            # self.game.add_node(nodeX, nodeY)
                        if event.button == 3:
                            mid_x = self.window_x // 2
                            mid_y = self.window_y // 2
                            verschiebung_x = (mid_x - pos_x) // 10
                            verschiebung_y = (mid_y - pos_y) // 10
                            self.show_board_verschoben(verschiebung_x, verschiebung_y)
                    else:
                        if self.play_but.rect.collidepoint(pos_y, pos_x):
                            self.play_but.change_state()
                            self.draw_menu()
                        if self.input_iterations.rect.collidepoint(pos_y, pos_x):
                            if self.input_iterations.change_state():
                                iterations = int(self.input_iterations.text)
                                self.play_but.change_state()
                                self.draw_menu()
                                for iteration in reversed(range(iterations)):
                                    if self.autoplay():
                                        return
                                    self.game.next_board()
                                    self.input_iterations.change_text(str(iteration))
                                    self.draw_menu()
                                    points = self.game.get_nodes()
                                    self.show_board(points)
                                self.input_iterations.change_text('')
                                self.play_but.change_state()
                                self.draw_menu()
                if event.type == pygame.KEYDOWN:
                    # Keypress event listener
                    if event.key == pygame.K_f:
                        # TODO: entfernen, geht zur nächsten Generation
                        return
                    if event.key == pygame.K_ESCAPE:
                        self.spiel_verlassen()
                        # Escape -> Close
                        # pygame.quit()
                        # sys.exit()
                    if event.key == pygame.K_m:
                        self.open_menu()
                    if event.key == pygame.K_RIGHT:
                        self.next_premade()
                        # points = self.game.get_nodes()
                        # self.show_board(points)
                        self.draw_menu()
                    if event.key == pygame.K_LEFT:
                        self.previous_premade()
                        points = self.game.get_nodes()
                        self.show_board(points)
                        self.draw_menu()
                    if event.key == pygame.K_p:
                        self.change_place_mode()
                        # points = self.game.get_nodes()
                        # self.show_board(points)
                        self.draw_menu()
                    if event.key == pygame.K_0 or event.key == pygame.K_KP0:
                        # points = self.game.get_nodes()
                        # for point in points:
                        #     point[0] -= self.verschiebung_ges[0]
                        #     point[1] -= self.verschiebung_ges[1]
                        verschiebung_x = -int(self.verschiebung_ges[0])
                        verschiebung_y = -int(self.verschiebung_ges[1])
                        self.show_board_verschoben(verschiebung_x, verschiebung_y)
                        self.verschiebung_ges = [0, 0]
                    if event.key == pygame.K_w:
                        self.show_board_verschoben(10, 0)
                    if event.key == pygame.K_a:
                        self.show_board_verschoben(0, 10)
                    if event.key == pygame.K_s:
                        self.show_board_verschoben(-10, 0)
                    if event.key == pygame.K_d:
                        self.show_board_verschoben(0, -10)
                    if event.key == pygame.K_r:
                        self.change_rotatation()
                        self.draw_menu()

    def show_board_verschoben(self, verschiebung_x, verschiebung_y):
        """Verschobenes Anzeigen des Boards in Funktion gebündelt.

        Kommentar:
        Input: Name der Instanz, verschiebung x, verschiebung y
        Output: Kein return, visuelles Feedback
        Besonders: Keine Besonderheiten
        """
        self.verschiebung_ges[0] += verschiebung_x
        self.verschiebung_ges[1] += verschiebung_y
        points = self.game.get_nodes()
        for point in points:
            point[0] += verschiebung_x
            point[1] += verschiebung_y
        self.show_board(points)

    def autoplay(self):
        self.check_close()
        start_time = time.time()
        while time.time() - start_time < 0.6:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.spiel_verlassen()
                if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0] is True and \
                        pygame.mouse.get_pos()[0] < self.window_x:
                    mouse_pos = pygame.mouse.get_pos()
                    pos_x = mouse_pos[0] // 10
                    pos_y = mouse_pos[1] // 10
                    if self.curr_place_mode == "draw":
                        self.game.add_node(pos_y, pos_x)
                        pygame.draw.rect(self.display, self.black,
                                         pygame.Rect((pos_x * 10) + 1, (pos_y * 10) + 1, 9, 9))  # noqa: E501
                        self.update_board()
                    elif self.curr_place_mode == "erase":
                        self.game.remove_node(pos_y, pos_x)
                        pygame.draw.rect(self.display, self.white,
                                         pygame.Rect((pos_x * 10) + 1, (pos_y * 10) + 1, 9, 9))  # noqa: E501
                        self.update_board()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    pos_x = pos[1]
                    pos_y = pos[0]
                    if event.button == 1:
                        if self.play_but.rect.collidepoint(pos_y, pos_x):
                            self.play_but.change_state()
                            self.draw_menu()
                            return True
                        if pos_y < self.window_x:
                            if event.button == 1:
                                self.manipulate_point(pos_x, pos_y)
                                self.show_board()
                    if event.button == 3:
                        mid_x = self.window_x // 2
                        mid_y = self.window_y // 2
                        verschiebung_x = (mid_x - pos_x) // 10
                        verschiebung_y = (mid_y - pos_y) // 10
                        self.show_board_verschoben(verschiebung_x, verschiebung_y)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.spiel_verlassen()
                    if event.key == pygame.K_0 or event.key == pygame.K_KP0:
                        # points = self.game.get_nodes()
                        # for point in points:
                        #     point[0] -= self.verschiebung_ges[0]
                        #     point[1] -= self.verschiebung_ges[1]
                        verschiebung_x = -int(self.verschiebung_ges[0])
                        verschiebung_y = -int(self.verschiebung_ges[1])
                        self.show_board_verschoben(verschiebung_x, verschiebung_y)
                        self.verschiebung_ges = [0, 0]
                    if event.key == pygame.K_w:
                        self.show_board_verschoben(10, 0)
                    if event.key == pygame.K_a:
                        self.show_board_verschoben(0, 10)
                    if event.key == pygame.K_s:
                        self.show_board_verschoben(-10, 0)
                    if event.key == pygame.K_d:
                        self.show_board_verschoben(0, -10)
                    if event.key == pygame.K_RIGHT:
                        self.next_premade()
                        # points = self.game.get_nodes()
                        # self.show_board(points)
                        self.draw_menu()
                    if event.key == pygame.K_LEFT:
                        self.previous_premade()
                        points = self.game.get_nodes()
                        self.show_board(points)
                        self.draw_menu()
                    if event.key == pygame.K_p:
                        self.change_place_mode()
                    if event.key == pygame.K_r:
                        self.change_rotatation()
                        self.draw_menu()
        return False

    def mainloop(self):
        """Mainloop, läuft bis beendet.

        Kommentar: Mainloop, läuft bis programm beendet wird
        Input: Name der Instanz
        Output: Kein Output
        Besonders: Keine Besonderheiten
        """
        while True:
            stop = False
            points = self.game.get_nodes()
            self.show_board(points)
            self.draw_menu()
            self.update_board()
            if self.play_but.state == 'play':
                self.wait_keypress()
            if self.play_but.state == 'pause':
                stop = self.autoplay()
            if stop is False:
                self.game.next_board()
            self.check_close()
            #self.check_close()

    def spiel_verlassen(self):
        quit_box = Tk()
        quit_box.focus_force()

        fensterBreite = quit_box.winfo_reqwidth()
        fensterHoehe = quit_box.winfo_reqheight()
        positionRechts = int(quit_box.winfo_screenwidth() / 2 - fensterBreite / 2)
        positionUnten = int(quit_box.winfo_screenheight() / 2 - fensterHoehe / 0.75)

        quit_box.geometry("+{}+{}".format(positionRechts, positionUnten))

        quit_box.geometry("250x90")
        quit_box.title("")

        self.frage = Label(quit_box, text="Willst Du deinen Fortschritt\n vor dem Schließen speichern?")
        self.frage.grid(row=0, column=0, columnspan="2")

        self.quit_button_yes = Button(quit_box, text="Ja", bg="goldenrod", fg="black",
                                      command=lambda: [self.save_file(self.game.get_nodes(), True)])
        self.quit_button_yes.grid(row=1, column=0, sticky='nesw', padx=5, pady=5)
        self.quit_button_no = Button(quit_box, bg="goldenrod", fg="black", text="Nein",
                                     command=lambda: [pygame.quit(), sys.exit()])
        self.quit_button_no.grid(row=1, column=1, sticky='nesw', padx=5, pady=5)
        quit_box.grid_rowconfigure(0, weight=1)
        quit_box.grid_rowconfigure(1, weight=3)
        quit_box.grid_columnconfigure(0, weight=1, uniform="commi")
        quit_box.grid_columnconfigure(1, weight=1, uniform="commi")
        quit_box.mainloop()

    def check_close(self):
        """Prüft, ob Close Button aktiviert wurde.

        Kommentar: Überprüft, ob der Close button aktiviert wurde
        Input: Name der Instanz
        Output: Kein Output
        Besonders: Keine Besonderheiten
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.spiel_verlassen()

    @classmethod
    def update_board(cls):
        """Aktualisiert das Bord.

        Kommentar: Bord wird durch den Flip befehl aktualisiert
        Input: Name der Instanz
        Output: Keine Output
        Besonders: Keine Besonderheiten
        """
        pygame.display.flip()

    @classmethod
    def open_file(cls):
        """Lädt Daten aus einer Datei mit file browser.

        Kommentar: Lädt daten aus einer Datei
        Input: Name der Klasse
        Output: Geladene Daten
        Besonders: Nutzt tkinter lade-Modul, beliebiger Speicherort.
        """
        filename = askopenfile(mode='r', filetypes=[('Json files', '*.json')])
        if filename is not None:
            inhalt = json.load(filename)
            return inhalt
        else:
            return False

    def open_saved_board(self):
        """Importiert eine Welt aus einer .json Datei.

        Kommentar: Öffnet eine Welt aus einer Datei
        Input: Name der Instanz
        Output: Kein direktes Output
        Besonders: Nutzt self.open_file()
        """
        nodes = self.open_file()
        if nodes is not False:
            nodes.sort()
            # to_load = list(nodes for nodes, _ in itertools.groupby(nodes))
            to_load = [[node[0] + self.verschiebung_ges[0], node[1] + self.verschiebung_ges[1]] for node in nodes]
            self.game.replace_nodes(to_load)
        self.show_board(to_load)

    def save_file(self, inhalt, schliessfrage):
        """Speichert gegebene Daten in eine Datei mit file browser.

        Kommentar: Speichert Daten in eine Datei
        Input: Name der Klasse, Daten, True - speichern und schließen oder False - nur speichern
        Output: Kein Output
        Besonders: Nutzt tkinter speicher-Modul, beliebiger Dateiort.
        """
        res = list()
        for node in inhalt:
            res.append([node[0] - self.verschiebung_ges[0], node[1] - self.verschiebung_ges[1]])
        filename = asksaveasfilename(
            filetypes=[('JSON files', '.json')], initialfile='',
            defaultextension=".json"
        )
        if filename:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(res, file)

        if schliessfrage == True:
            pygame.quit()
            sys.exit()
