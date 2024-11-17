import mysql.connector

# Die Klasse Datenbank verwaltet die Verbindung zu einer MySQL-Datenbank. Sie ist für die Datenbankoperationen zuständig und ermöglicht das Ausführen von SELECT- und INSERT-Abfragen und erstellt benötigte Tabellen.
class Datenbank:
    def __init__(self, host, username, password, database):
        self.host       = host
        self.username   = username
        self.password   = password
        self.database   = database
        self.connection = None
        self.cursor     = None

    # Stellt eine Verbindung zur MySQL-Datenbank her. Falls die Datenbank noch nicht existiert wird sie erstellt.
    def connect(self):
        try:
            config = {
                "user" : self.username,
                "password" : self.password,
                "host" : self.host,
            }
            self.connection = mysql.connector.connect(**config)
            self.cursor = self.connection.cursor()

            # Datenbank erstellen, sofern noch nicht existiert
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")

            # Mit Datenbank verbinden
            self.connection.database = self.database
            print("Verbindung zur Datenbank hergestellt.")

            return self.connection
        except mysql.connector.Error as e:
            print(f"Fehler bei der Verbindung: {e}")
            self.connection = None
            return None

    # Schließt die Verbindung zur MySQL-Datenbank. Wird ausgeführt, sobald das Fenster des Dashboards geschlossen wird.
    def disconnect(self):
        try:
            if self.connection is not None and self.connection.is_connected():
                if self.cursor:
                    self.cursor.close()
                self.connection.close()
                print("Verbindung zu MySQL geschlossen.")
        except Exception as e:
            print(f"Fehler beim Schließen der Verbindung: {e}")

    # Führt eine SELECT-Abfrage auf der Datenbank aus. Wird benötigt, damit die verschiedenen Klassen Daten aus der Datenbank erhalten können.
    def query_select(self, sql_statement, params=None):
        try:
            if params is not None:
                self.cursor.execute(sql_statement, params)
            else:
                self.cursor.execute(sql_statement)
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as e:
            print(f"Fehler beim Ausführen der SELECT-Abfrage: {e}")
            return None

    # Führt eine Insert-Abfrage auf der Datenbank aus. Wird benötigt, damit die verschiedenen Klassen Daten in die Datenbank speichern können.
    def query_insert(self, sql_statement, params=None):
        try:
            if params is not None:
                self.cursor.execute(sql_statement, params)
            else:
                self.cursor.execute(sql_statement)
            self.connection.commit()
            return True
        except mysql.connector.Error as e:
            self.connection.rollback()
            print(f"Fehler beim Ausführen der INSERT-Abfrage: {e}")
            return False

    # Erstellt alle benötigten Tabellen, falls sie noch nicht existieren. Werden benötigt um die Daten zu speichern.
    def tabellen_erstellen(self):
        try:
            # Tabelle: vergangen für die Vergangene Zeit
            self.cursor.execute("""
                   CREATE TABLE IF NOT EXISTS vergangen (
                       id INT AUTO_INCREMENT PRIMARY KEY,
                       gesamt_monate INT NOT NULL,
                       startdatum DATE NOT NULL,
                       vergangene_monate INT
                   )
               """)
            print("Tabelle \"vergangen\" erstellt oder existiert bereits.")

            # Tabelle: gelernt für die Speicherung der Lernzeiten in den entsprechenden Tagen. Die Tage werden mit anderen Funktionen den verschiedenen Wochen zugeordnet.
            self.cursor.execute("""
                   CREATE TABLE IF NOT EXISTS gelernt (
                       id INT AUTO_INCREMENT PRIMARY KEY,
                       tag DATE NOT NULL,
                       gelernte_zeit FLOAT NOT NULL
                   )
               """)
            print("Tabelle \"gelernt\" erstellt oder existiert bereits.")

            # Tabelle: noten für die Speicherung und zum Abrufen der Noten.
            self.cursor.execute("""
                   CREATE TABLE IF NOT EXISTS noten (
                       id INT AUTO_INCREMENT PRIMARY KEY,
                       modulname VARCHAR(255) NOT NULL,
                       note FLOAT NOT NULL CHECK (note BETWEEN 1.0 AND 5.0),
                       ects INT NOT NULL CHECK (ects IN (5, 10, 30))
                   )
               """)
            print("Tabelle \"noten\" erstellt oder existiert bereits.")

            # Tabelle: endnote zum Speicher der Zielnote, welche beim erstmaligen Ausführen des Codes angefragt wird.
            self.cursor.execute("""
                           CREATE TABLE IF NOT EXISTS endnote (
                               zielnote FLOAT NOT NULL CHECK (zielnote BETWEEN 1.0 AND 4.0)
                           )
                       """)
            print("Tabelle \"endnote\" erstellt oder existiert bereits.")

        except Exception as e:
            print(f"Fehler beim Erstellen der Tabellen: {e}")