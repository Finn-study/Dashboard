from datetime import datetime, timedelta, time


# Die Klasse Fortschritt verwaltet den Studienfortschritt des Users
class Fortschritt:
    def __init__(self, gesamt_ects, erreichte_ects):
        self.gesamt_ects = gesamt_ects
        self.erreichte_ects = erreichte_ects
        self.prozent = self.berechne_fortschritt()

    # Fortschrittsdaten werden aus der MySQL-Datenbank geladen und in erreichte_ects gespeichert
    def lade_fortschritt(self, datenbank):
        try:
            sql_select = "SELECT SUM(ects) FROM noten"
            result = datenbank.query_select(sql_select)

            self.erreichte_ects = result[0][0] if result[0][0] is not None else 0
        except Exception as e:
            print(f"Fehler beim Laden von ECTS-Daten: {e}")

    # Berechnet Fortschritt in Prozent anhand der erreichten ECTS und der Gesamt ECTS
    def berechne_fortschritt(self):
        self.prozent = (self.erreichte_ects / self.gesamt_ects) * 100 if self.gesamt_ects else 0



# Die Klasse VergangeneZeit berechnet den prozentualen Fortschritt der vergangenen Studienmonate
class VergangeneZeit:
    def __init__(self, gesamt_monate, vergangene_monate):
        self.gesamt_monate = gesamt_monate
        self.vergangene_monate = vergangene_monate
        self.prozent = self.berechne_vergangene_zeit()


    # Lädt das Startdatum des Studiums und die gesamten Monate aus der Datenbank, um anhand des heutigen Datums die vergangene Zeit zu ermitteln
    def lade_studienzeit(self, datenbank):
        try:
            sql_select = "SELECT startdatum, gesamt_monate FROM vergangen ORDER BY id DESC LIMIT 1"
            result = datenbank.query_select(sql_select)

            if result:
                startdatum = result[0][0]
                self.gesamt_monate = result[0][1]

                # Aktuelles Datum und die vergangenen Monate berechnen
                heutiges_datum = datetime.today().date()
                self.startdatum = startdatum

                jahre_diff = heutiges_datum.year - startdatum.year
                monate_diff = heutiges_datum.month - startdatum.month
                self.vergangene_monate = jahre_diff * 12 + monate_diff

                # Falls der Tag des Monats noch nicht erreicht wurde zieht 1 Monat ab.
                # Ansonsten würde ein Monat zu viel angezeigt werden, da nur die Monate und nicht die Tage bei der vorherigen Berechnung betrachtet werden
                if heutiges_datum.day < self.startdatum.day:
                    self.vergangene_monate -= 1

                # Berechnung des prozentualen Fortschritts
                self.prozent = self.berechne_vergangene_zeit()

                # Rückgabe der berechneten Werte an das Dashboard
                return self.vergangene_monate, self.gesamt_monate, self.prozent

        except Exception as e:
            print(f"Fehler beim Laden der Studienzeit: {e}")
            return None, None, 0

    # Speichert die Studienzeit beim erstmaligen Ausführen des Codes, sofern keine Daten in der Datenbank enthalten sind
    def speichere_studienzeit(self, datenbank, startdatum, gesamt_monate):
        try:
            startdatum = datetime.strptime(startdatum, '%Y-%m-%d').date()

            sql_insert = "INSERT INTO vergangen (startdatum, gesamt_monate) VALUES (%s, %s)"
            params = (startdatum, gesamt_monate)
            success = datenbank.query_insert(sql_insert, params)
        except Exception as e:
            print(f"Fehler beim Speichern der Studienzeit: {e}")

    # Berechnet den prozentualen Fortschritt der vergangenen Studienzeit.
    def berechne_vergangene_zeit(self):
        return (self.vergangene_monate / self.gesamt_monate) * 100 if self.gesamt_monate else 0




# Die Klasse Notenschnitt verwaltet den aktuellen Notensdurchschnitt, die Zielnote und berechnet die Abweichung zwischen diesen.
class Notenschnitt:
    def __init__(self, schnitt, zielnote, abweichung_notenschnitt):
        self.schnitt = schnitt
        self.zielnote = zielnote
        self.abweichung_notenschnitt = abweichung_notenschnitt

    # Lädt die Zielnote aus der Datenbank
    def lade_zielnote(self, datenbank):
        try:
            sql_select = "SELECT zielnote FROM endnote LIMIT 1"
            result = datenbank.query_select(sql_select)

            if result:
                self.zielnote = result[0][0]

        except Exception as e:
            print(f"Fehler beim Laden der Zielnote: {e}")
            return None, None, 0

    # Berechnet den aktuellen Notendurchschnitt basierend auf den in der Datenbank gespeicherten Noten
    def berechne_notenschnitt(self, datenbank):
        try:
            sql_select = "SELECT AVG(note) FROM noten"
            result = datenbank.query_select(sql_select)
            self.schnitt = result[0][0] if result and result[0][0] is not None else 0
        except Exception as e:
            print(f"Fehler beim Berechnen des Notenschnitts: {e}")

    # Speichert die Zielnote in der Datenbank nachdem der User sie eingegeben hat beim erstmaligen Ausführen
    def speichere_zielnote(self, datenbank):
        try:
            sql_insert = "INSERT INTO endnote (zielnote) VALUES (%s)"
            params = (self.zielnote,)
            datenbank.query_insert(sql_insert, params)
            print(f"Ziel-Notenschnitt {self.zielnote} gespeichert.")
        except Exception as e:
            print(f"Fehler beim Speichern der Zielnote: {e}")


    # Berechnet die Differenz zwischen aktuellem Notenschnitt und Zielnotenschnitt
    def berechne_abweichung(self):
        self.abweichung_notenschnitt = self.schnitt - self.zielnote

    # Speichert eine neue Note, das zugehörige Modul und die Anzahl der ECTS, nachdem der User diese eingetragen hat
    def speichere_note(self, datenbank, modulname, note, ects):
        sql_insert = "INSERT INTO noten (modulname, note, ects) VALUES (%s, %s, %s)"
        params = (modulname, note, ects)
        success = datenbank.query_insert(sql_insert, params)
        return success




# Die Klasse LernzeitTracker verwaltet die Lernzeit, ermöglicht das Starten und Stoppen des Timers und lädt die Lernzeiten der letzten 10 Wochen aus der Datenbank
class LernzeitTracker:
    def __init__(self):
        self.wochen = []
        self.zeiten = []
        self.startzeit = None
        self.running = False

    # Lädt die Lernzeit der letzten 10 Wochen aus der Datenbank. Summiert die gelernte Zeit nach Kalenderwochen, um sie korrekt im Diagramm anzeigen zu können.
    def lade_lernzeit(self, datenbank):
        try:
            sql_select = """
                SELECT YEARWEEK(tag, 1) AS kal_woche, SUM(gelernte_zeit) AS wochen_zeit
                FROM gelernt
                GROUP BY kal_woche
                ORDER BY kal_woche DESC
                LIMIT 10;
            """
            result = datenbank.query_select(sql_select)

            self.wochen = []
            self.zeiten = []
            for row in result:
                jahr_woche = str(row[0])
                jahr, kal_woche = jahr_woche[:4], jahr_woche[4:]
                self.wochen.append(f"KW {kal_woche}")
                self.zeiten.append(row[1])

            self.wochen = self.wochen[::-1]
            self.zeiten = self.zeiten[::-1]

        except Exception as e:
            print(f"Fehler beim Laden der letzten 10 Wochen: {e}")
            self.wochen, self.zeiten = [], []

    # Startet den Timer.
    def start_timer(self):
        if not self.running:
            self.running = True
            self.startzeit = datetime.now()
            print("Timer gestartet")

    # Stoppt den Timer und speichert die Zeit in der Datenbank.
    def stop_timer(self, datenbank):
        if self.running:
            self.running = False
            endzeit = datetime.now()
            print("Timer gestoppt")

            # Rechnet die Lernzeit aus und wandelt sie in Stunden um
            stunden = (endzeit - self.startzeit).total_seconds() / 3600
            datum = datetime.now().strftime('%Y-%m-%d')
            sql_insert = "INSERT INTO gelernt (tag, gelernte_zeit) VALUES (%s, %s)"
            params = (datum, stunden)
            success = datenbank.query_insert(sql_insert, params)
            return success

    # Aktualisiert die Anzeige des Timers während dieser läuft.
    def update_timer(self):
        if self.running:
            zeit = datetime.now() - self.startzeit
            gesamt_sekunden = int(zeit.total_seconds())

            stunden, remainder = divmod(gesamt_sekunden, 3600)
            minuten = remainder // 60

            return stunden, minuten