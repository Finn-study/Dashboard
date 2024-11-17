from dashboard import Dashboard
from database import Datenbank
from gui import GUI

# Die Hauptfunktion. Steuert den Ablauf der Anwendung. Beim Ausführen von main.py wird das Dashboard erstellt.
def main():

    # Übergabe der Parameter für die Datenbank
    db = Datenbank(host="localhost", username="root", password="xxxx", database="dashboard")

    # Verbindung mit der Datenbank
    connection = db.connect()

    if connection:
        # Erstellt die Tabellen
        db.tabellen_erstellen()

        # Erstellt ein Dashboard-Objekt
        dashboard = Dashboard(db, None)

        # Erstellung eines GUI Objekts und Übergabe an das Dashboard
        gui = GUI(dashboard)

        # Verknüpfung des GUI mit dem Dashboard
        dashboard.gui = gui

        # Erstellt die Benutzeroberfläche
        gui.erstelle_gui()

if __name__ == "__main__":
    main()