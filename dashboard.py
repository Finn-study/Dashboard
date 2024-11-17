from models import Fortschritt, VergangeneZeit, Notenschnitt, LernzeitTracker
from database import Datenbank

# Klasse Dashboard mit allen anderen Klassen als Attribute
class Dashboard:
    def __init__(self, datenbank, gui):
        self.datenbank = datenbank
        self.gui = gui
        # 180 ECTS als Standard gewählt
        self.fortschritt = Fortschritt(180, 0)
        self.vergangene_zeit = VergangeneZeit(0, 0)
        self.notenschnitt = Notenschnitt(0.0, 0.0, 0.0)
        self.lernzeit_tracker = LernzeitTracker()

    # Lädt die benötigten Daten aus der Datenbank oder fordert sie über die GUI vom Benutzer an
    def lade_dashboard(self):

        # Lädt die Studienzeit aus der Datenbank
        self.vergangene_zeit.lade_studienzeit(self.datenbank)

        # Fragt Studienbeginn und Studiendauer ab, wenn keine Daten vorhanden sind
        if self.vergangene_zeit.gesamt_monate == 0:
            startdatum, gesamt_monate = self.gui.abfrage_studienzeit()
            if startdatum and gesamt_monate:
                # Speichert die erhaltenen Daten in der Datenbank
                self.vergangene_zeit.speichere_studienzeit(self.datenbank, startdatum, gesamt_monate)
                self.vergangene_zeit.lade_studienzeit(self.datenbank)

        # Lädt die Zielnote aus der Datenbank. Wenn keine vorhanden wird sie über die GUI vom USER angefragt
        self.notenschnitt.lade_zielnote(self.datenbank)
        if self.notenschnitt.zielnote == 0.0:
            zielnote = self.gui.abfrage_zielnote()
            if zielnote is not None:
                self.notenschnitt.zielnote = zielnote
                self.notenschnitt.speichere_zielnote(self.datenbank)

        # Lädt Fortschritts- und Notendaten aus der Datenbank
        self.fortschritt.lade_fortschritt(self.datenbank)
        self.notenschnitt.berechne_notenschnitt(self.datenbank)

        # Lädt und berechnet lernzeitdaten
        self.lernzeit_tracker.lade_lernzeit(self.datenbank)

        # Berechnet Fortschritt und Notenabweichung basierend auf den geladenen Daten
        self.fortschritt.berechne_fortschritt()
        self.notenschnitt.berechne_abweichung()

    """
    Bereitet das Dashboard für die Anzeige vor. Zeige_dashboard gibt die folgenden Werte zurück:
    - Fortschritt in Prozent
    - Zeit in Prozent
    - Erreichte ECTS
    - Vergangene Monate seit Beginn des Studiums
    - Notenschnitt
    - Abweichung Notenschnitt von Zielnote
    - Lernzeit der jeweiligen Wochen
    """
    def zeige_dashboard(self):
        fortschritt_prozent = self.fortschritt.prozent
        zeit_prozent = self.vergangene_zeit.berechne_vergangene_zeit()
        vergangene_monate = self.vergangene_zeit.vergangene_monate
        erreichte_ects = self.fortschritt.erreichte_ects
        schnitt = self.notenschnitt.schnitt
        differenz = self.notenschnitt.abweichung_notenschnitt
        wochen, zeiten = self.lernzeit_tracker.wochen, self.lernzeit_tracker.zeiten
        return fortschritt_prozent, zeit_prozent, erreichte_ects, vergangene_monate, schnitt, differenz, wochen, zeiten