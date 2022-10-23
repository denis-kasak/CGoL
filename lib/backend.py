# -*- coding: utf-8 -*-
"""Docstring beenden."""
import json
import os
import time


class Game:
    """Game Klasse, für Backend benutzt."""

    def __init__(self, nodes=None, board_x=30, board_y=30, premade=None) -> None:  # noqa: E501
        """Init Methode.

        Kommentar: Standard init Methode
        Input: Name der Instanz, optional: nodes--(siehe docs), boardX--Breite
               der Simulation, boardY--höhe der Simulation
        Output: Kein Output
        Besonders: Standard init, nichts Besonderes
        """
        nodes = nodes or list()
        premade = premade or dict()
        self.iterations = 0
        self.nodes = nodes
        self.board_x = board_x
        self.board_y = board_y
        if premade:
            self.premade = premade
        else:
            self.premade = {}
            self.premade = self.import_premade()

    def get_num_neighbours(self, x_koord: int, y_koord: int) -> int:
        # NOTE: Aufruf 5403x in denis.json welt. Optimierung?
        """Gibt die Anzahl der Nachbarn zurück.

        Kommentar: gibt die Anzahl der Nachbarn als int aus
        Input: Name der Instanz, x-Koordinate, y-Koordinate
        Output: Int mit anzahl der Nachbarn
        Besonders: keine Besonderheiten
        """
        nachbar_zellen = [[x_koord - 1, y_koord - 1], [x_koord - 1, y_koord],
                          [x_koord - 1, y_koord + 1], [x_koord, y_koord - 1],
                          [x_koord, y_koord + 1], [x_koord + 1, y_koord - 1],
                          [x_koord + 1, y_koord], [x_koord + 1, y_koord + 1]]
        # setzen der Nachbarn zur länge der Überschneidung von nachbar_zellen
        #  und self.nodes (Knotenliste)
        num_nachbarn = len(Game.get_list_intersection(nachbar_zellen, self.nodes))  # noqa: E501
        return num_nachbarn

    def next_board(self) -> list:
        # OPTIMIZE: Aufruf von self.check_regeln optimieren
        """Erzeugt das nächste Bord und gibt dieses zurück.

        Kommentar:erzeugt das neue board und ersetzt das Aktuelle mit dem neuen
        Input: name der Instanz
        Output: aktualisierte Knotenliste
        Besonders: nutzt check_regeln
        """
        new_board = []
        nachbarn = []
        nodes = self.get_points()
        for node in nodes:
            x_koord = node[0]
            y_koord = node[1]
            numneighbors = self.get_num_neighbours(x_koord, y_koord)

            nachbar_zellen = [[x_koord - 1, y_koord - 1], [x_koord - 1, y_koord],
                              [x_koord - 1, y_koord + 1], [x_koord, y_koord - 1],
                              [x_koord, y_koord + 1], [x_koord + 1, y_koord - 1],
                              [x_koord + 1, y_koord], [x_koord + 1, y_koord + 1]]
            for zelle in nachbar_zellen:
                if zelle not in nachbarn + nodes:
                    nachbarn.append(zelle)
            if node not in new_board and numneighbors in [2, 3]:
                new_board.append(node)
        for nachbar in nachbarn:  # loop durch nachbarn
            if nachbar not in new_board and self.get_num_neighbours(nachbar[0], nachbar[1]) == 3:
                new_board.append(nachbar)
        self.replace_points(new_board)
        self.iterations += 1
        return new_board

    def replace_points(self, nodes) -> list:
        """ Ersetzt self.nodes durch nodes

        Kommentar: Erstzen der self.nodes durch nodes
        Input: Name der Instanz, nodes als Knotenliste
        Output: Kein Output
        Besonders: Keine Besonderheiten
        """
        # TODO: doku beenden
        self.nodes = Game.remove_duplicates(nodes)
        return self.nodes

    def get_points(self) -> list:
        """Gibt die Knotenliste zurück.

        Kommentar: gibt die aktuelle Knotenliste aus
        Input: Name der Instanz
        Output: Knotenliste self.node
        Besonders: Rückgabe mittels return
        """
        return self.nodes

    def deepcopy_points(self):
        res = []
        for node in self.nodes:
            res.append([int(node[0]), int(node[1])])
        return res

    def add_point(self, x_koord: int, y_koord: int) -> list:
        """Fügt einen Punkt zur Knotenliste hinzu.

        Kommentar: Fuegt einen Punkt zur Knotenliste self.nodes hinzu
        Input: name der Instanz, x-Koordinate als int, y-Koordinate als int
        Output: Aktualisierte Knotenliste self.nodes
        Besonders: Weitere Optimierung der Laufzeit
        """
        # OPTIMIZE: Laufzeit optimieren (add, append oder operator?)
        if [x_koord, y_koord] not in self.nodes:
            self.nodes.append([x_koord, y_koord])
        return self.nodes

    def remove_point(self, x_koord, y_koord):
        """Entfernt einen Punkt aus der Knotenliste.

        Kommentar: Entfernt einen Punkt aus der Knotenliste
        Input: Name der Instanz, x-Koordinate als int, y-Koordinate als int
        Output: Aktualisierte Knotenliste self.nodes
        Besonders: Falls Punkt nicht in Knotenliste erfolgt Error
        """
        # OPTIMIZE: Laufzeit?
        # DEBUG: Try except pruefen
        while [x_koord, y_koord] in self.nodes:
            self.nodes.remove([x_koord, y_koord])
        return self.nodes

    def manipulate_point(self, x_koord: int, y_koord: int) -> bool:

        """Siehe Kommentar.

        Kommentar: Fuegt Punkt hinzu, wenn nicht vorhanden, entfernt wenn
                   vorhanden
        Input: Name der Instanz, x-Koordinate als int, y-Koordinate als int
        Output: Aktualisierte Knotenliste
        Besonders: Prueft ob Punkt in Knotenliste
        """
        if [x_koord, y_koord] in self.nodes:
            # TODO ist in Coverage nicht eingetreten
            self.remove_point(x_koord, y_koord)
            res = False
        else:
            self.add_point(x_koord, y_koord)
            res = True
        return res

    def list_premade(self) -> list:
        """Listet alle vorgefertigten Objekte auf.

        Kommentar: listet alle vorgefertigten Objekte mit deren Namen auf
        Input: Name der Instanz
        Output: Liste mit allen Namen
        Besonders: Keine Besonderheiten
        """
        res = list()
        for name in list(self.premade.keys()):
            res.append(name)
        return res

    def import_premade(self, filename=None) -> dict:
        """Importiert vorgefertigte Elemente aus einer Datei.

        Kommentar: Importiert vorgefertigte Objekte aus einer Json datei
        Input: Name der Instanz, Optional: Dateiname
        Output: vorgefertigte Dateien, werden aber automatisch zu self.premade
                hinzugefügt
        Besonders: Wenn kein Dateiname gegeben, wird die standard datei genutzt
        """
        if filename:
            data = Game.load_premade(filename)
        else:
            pth = os.path.join(os.path.dirname(__file__),"..", "premade", "premade.json")
            data = Game.load_premade(pth)
        self.premade = Game.merge_dict(self.premade, data)
        return data

    def add_premade(self, name: str, pos_x: int, pos_y: int, rotation=None) -> list:
        """Fügt ein vorgefertigtes Element zur Knotenliste hinzu.

        Kommentar: fuegt an einer gegebenen Position ein vorgefertigtes Objekt
                   anhand dessen Namen hinzu
        Input: Name der Instanz, Name des Objekts, x-Koordinate, y-Koordinate
        Output: Kein Output, Knoten werden an Knotenliste angehängt
        Besonders: Kein Output, anfügen an Knotenliste
        """
        rotation = rotation or 0
        select = self.premade[name]
        to_add = self.multirotate(rotation, select)
        new_point = []
        for point in to_add:
            new_point.append([point[0] + pos_x, point[1] + pos_y])
        for point in new_point:
            self.add_point(point[0], point[1])
        return new_point

    @classmethod
    def merge_dict(cls, dict1: dict, dict2: dict) -> dict:
        """Merge zweiter Dicts.

        Kommentar: kombiniert zwei Dictionaries, dict2 hat höhere Priorität
        Input: Name der Klasse, Dict1 und Dict2
        Output: Kombinitere Dictionaries
        Besonders: dict2 hat höhere Priorität (dict1 wird bei dopplung
                   überschrieben)
        """
        dict1.update(dict2)
        return dict1

    @classmethod
    def load_premade(cls, path: str) -> dict:
        """Lädt vorgefertigte Elemente aus einem Pfad.

        Kommentar: lädt eine json Datei aus einem Pfad
        Input: Name der Klasse, Pfad zur Datei
        Output: Daten der Datei
        Besonders: Keine Besonderheiten
        """
        data = json.load(open(path, "r"))
        return data

    @classmethod
    def get_list_intersection(cls, list_a: list, list_b: list) -> list:
        # TODO: NICHT ENTFERNEN, essenziell
        # OPTIMIZE: Optimierung der Laufzeit? (alternative zur Iteration)
        # NOTE: Wird bei testwelt denis.json 5403x aufgerufen in der ersten Iteration
        """Gibt die Überschneidung zweier Listen zurück.

        Kommentar: erzeugt die überschneidung zweier listen
        Input: Name der Klasse, erste Liste, zweite Liste
        Output: Überschneidung der Listen
        Besonders: Keine Besonderheiten
        """
        if len(list_a) > len(list_b):
            intersect = [item for item in list_b if item in list_a]
        else:
            intersect = [item for item in list_a if item in list_b]
        return intersect

    @classmethod
    def remove_duplicates(cls, liste):
        res = set()
        for punkt in liste:
            res.add((punkt[0], punkt[1]))
        res = list(res)
        out = [[punkt[0], punkt[1]] for punkt in res]
        return out

    @classmethod
    def find_center(cls, nodes):
        x_vals = list()
        y_vals = list()
        for node in nodes:
            x_vals.append(node[1])
            y_vals.append(node[0])
        extreme = [max(y_vals), max(x_vals)]
        mid = [int((extreme[0] / float(2)) + 0.49), int((extreme[1] / float(2)) + .049)]
        return mid

    @classmethod
    def rotate_point(cls, mid, point):
        """Vektoroperationen um Punkt um 90° mit dem Uhrzeigersin zu rotieren."""
        v_mid_point = [point[0] - mid[0], point[1] - mid[1]]
        v_mid_res = [v_mid_point[1], -v_mid_point[0]]
        v_res = [mid[0] + v_mid_res[0], mid[1] + v_mid_res[1]]
        return v_res

    @classmethod
    def rotate_obj(cls, nodes):
        mid = cls.find_center(nodes)
        res = []
        for node in nodes:
            rot = cls.rotate_point(mid, node)
            res.append([int(rot[0]), int(rot[1])])
        return res

    @classmethod
    def multirotate(cls, iterable, nodes):
        curr_nodes = nodes
        for i in range(iterable):
            curr_nodes = cls.rotate_obj(nodes=curr_nodes)
        return curr_nodes


def debug():
    """Debug Funktion."""


if __name__ == '__main__':
    debug()
