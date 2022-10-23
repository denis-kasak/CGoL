from tkinter import *


class Display:

    def open_menu(self):
        """Öffnet ein TKinter Menü.
        Kommentar: Erstelt ein TKInter Menü und öffnet dieses
        Input: Name der Instanz
        Output: Kein Output
        Besonders: Keine Besonderheiten
        """
        master = Tk()

        master.geometry("200x100")
        master.resizable(False, False)

        master.title("CgoL")

        title_label = Label(master, text="Spielmenü")
        title_label.grid(row=0, column=0, sticky='ew')

        save_button = Button(master, text="Speichern",
                                  command=lambda: self.save_file(self.game.get_points(), False))
        save_button.grid(row=1, column=0, sticky='ew')

        load_button = Button(master, text="Laden", command=lambda: self.open_saved_board())
        load_button.grid(row=1, column=1, sticky='ew')

        import_button = Button(master, text="Objekte laden", command=lambda: self.import_premade())
        import_button.grid(row=2, column=0, sticky="ew")

        manual_button = Button(master, text="Anleitung")
        manual_button.grid(row=2, column=1, sticky='ew')

        quit_button = Button(master, text="Quit", command=lambda: self.spiel_verlassen())
        quit_button.grid(row=3, column=0, sticky='ew')

        master.columnconfigure(0, weight=5, uniform="commi")
        master.columnconfigure(1, weight=5, uniform="commi")
        master.mainloop()


a = Display()
a.open_menu()
