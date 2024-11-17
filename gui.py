import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import dashboard

# Die Klasse GUI dient als Benutzerschnittstelle und ermöglicht die Anzeige, sowie die Interaktion des Users mit dem Dashboard
# Sie initialisiert alle GUI-Elemente, aktualisiert sie und behandelt Benutzerinteraktionen
class GUI:
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.root = tk.Tk()
        self.root.title("Dashboard")
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        # Frames initialisieren und speichern
        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=1, column=0, padx=30, pady=10)

        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, padx=30, pady=10, sticky="nw")

    # Funktion für das Schließen des Programms. Hierbei wird der Timer gestoppt und die Datenbankverbindung getrennt
    def close(self, event=None):
        print("Schließe das Programm")

        if self.dashboard.lernzeit_tracker.running:
            self.dashboard.lernzeit_tracker.stop_timer(self.dashboard.datenbank)

        self.dashboard.datenbank.disconnect()
        self.root.quit()
        self.root.destroy()

    # Erstellt die GUi und initialisiert alle Komponenten
    def erstelle_gui(self):
        self.dashboard.lade_dashboard()

        # Überschrift
        self.dashboard_gui()

        # Daten aus dem Dashboard abrufen
        fortschritt_prozent, zeit_prozent, erreichte_ects, vergangene_monate, schnitt, differenz, wochen, zeiten = self.dashboard.zeige_dashboard()

        # Fortschritt anzeigen
        self.fortschritt_gui(fortschritt_prozent, erreichte_ects)

        # Vergangene Zeit anzeigen
        self.zeit_gui(zeit_prozent, vergangene_monate)

        self.notenschnitt_gui(schnitt, differenz)

        self.timer_gui()

        self.lernzeit_gui(wochen, zeiten)

        self.root.mainloop()


    # Aktualisiert die GUI, wenn etwas hinzugefügt wurde
    def update_gui(self):
        self.dashboard.lade_dashboard()
        # Daten aus dem Dashboard abrufen
        fortschritt_prozent, zeit_prozent, erreichte_ects, vergangene_monate, schnitt, differenz, wochen, zeiten = self.dashboard.zeige_dashboard()

        # Fortschritt anzeigen
        self.fortschritt_gui(fortschritt_prozent, erreichte_ects)

        # Notenschnitt anzeigen
        self.notenschnitt_gui(schnitt, differenz)

        # Diagramm anzeigen
        self.lernzeit_gui(wochen, zeiten)

    # Aktualisierte die Visualisierung der Timer-Anzeige während der Timer läuft.
    def update_timer_gui(self):
        if self.dashboard.lernzeit_tracker.running:
            stunden, minuten = self.dashboard.lernzeit_tracker.update_timer()
            self.timer_label.config(text=f"{stunden:02} h {minuten:02} min")
            self.root.after(1000, self.update_timer_gui)

    # Erstellt die Überschrift des Dashboards
    def dashboard_gui(self):
        dashboard_label = tk.Label(self.root, text="Dashboard IU", font=("Arial", 24, "bold"))
        dashboard_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="n")

    # Erstellt die Fortschrittsanzeige für ECTS-Punkte
    def fortschritt_gui(self, fortschritt_prozent, erreichte_ects):
        # Fortschrittsanzeige für ECTS
        fortschritt_label = tk.Label(self.left_frame, text="Fortschritt ECTS:", font=("Arial", 16))
        fortschritt_label.grid(row=1, column=0, sticky="w", pady=5)

        ects_fortschritt = ttk.Progressbar(self.left_frame, orient="horizontal", length=300, mode="determinate")
        ects_fortschritt['value'] = fortschritt_prozent
        ects_fortschritt.grid(row=2, column=0, sticky="w", pady=5)

        # Zeige die ECTS mit Prozentsatz an
        ects_label = tk.Label(self.left_frame, text=f"{erreichte_ects} ECTS ({fortschritt_prozent:.2f}% erreicht)", font=("Arial", 12))
        ects_label.grid(row=3, column=0, sticky="w", pady=5)

    # Anzeige die Anzeige für die vergangene Studienzeit
    def zeit_gui(self, zeit_prozent, vergangene_monate):
        zeit_label = tk.Label(self.left_frame, text="Vergangene Zeit:", font=("Arial", 16))
        zeit_label.grid(row=4, column=0, sticky="w", pady=5)

        zeit_fortschritt = ttk.Progressbar(self.left_frame, orient="horizontal", length=300, mode="determinate")
        zeit_fortschritt['value'] = zeit_prozent
        zeit_fortschritt.grid(row=5, column=0, sticky="w", pady=5)

        # Zeige die verstrichenen Monate mit Prozentsatz an
        zeit_prozent_label = tk.Label(self.left_frame, text=f"{vergangene_monate} Monate ({zeit_prozent:.2f}%)", font=("Arial", 12))
        zeit_prozent_label.grid(row=6, column=0, sticky="w", pady=5)

    # Erstellt die Anzeige für den Notenschnitt und den Button zum Hinzufügen einer neuen Note
    def notenschnitt_gui(self, schnitt, differenz):
        # Erstelle ein Frame für Notenschnitt und Buttons nebeneinander
        notenschnitt_button_frame = tk.Frame(self.right_frame)
        notenschnitt_button_frame.grid(row=0, column=0, pady=5, padx=60, sticky="nsew")

        notenschnitt_inner_frame = tk.Frame(notenschnitt_button_frame)
        notenschnitt_inner_frame.grid(row=0, column=0, padx=10, sticky="w")

        notenschnitt_label = tk.Label(notenschnitt_inner_frame, text="Notenschnitt", font=("Arial", 22))
        notenschnitt_label.grid(row=0, column=0, sticky="w", columnspan=2)

        notenschnitt_wert = tk.Label(notenschnitt_inner_frame, text=f"{schnitt:.2f}", font=("Arial", 40), padx=10, pady=5)
        notenschnitt_wert.grid(row=1, column=0, sticky="w")

        pfeil, farbe = ("↑", "green") if differenz <= 0 else ("↓", "red")
        differenz_label = tk.Label(notenschnitt_inner_frame, text=f"{pfeil} {abs(differenz):.2f}", font=("Arial", 18), fg=farbe)
        differenz_label.grid(row=1, column=1, sticky="w")

        neue_note_button = tk.Button(notenschnitt_button_frame, text="Neue Note", font=("Arial", 14), command=lambda: self.abfrage_note())
        neue_note_button.grid(row=0, column=1, pady=10, sticky="w")

    # Erstellt die Timer Anzeige mit Start- und Stop-Button
    def timer_gui(self):
        timer_frame = tk.Frame(self.right_frame)
        timer_frame.grid(row=1, column=0, pady=10, sticky="n")

        # Sanduhr Emoji neben dem Timer
        sanduhr_label = tk.Label(timer_frame, text="⏳", font=("Arial", 24))
        sanduhr_label.grid(row=0, column=0, padx=5, pady=5)

        # Zeitanzeige
        self.timer_label = tk.Label(timer_frame, text="00 h 00 min", font=("Arial", 24), padx=10, pady=5)
        self.timer_label.grid(row=0, column=1, padx=5, pady=5)

        # Start-Button
        self.start_button = tk.Button(timer_frame, text="▶", font=("Arial", 24),
                                      command=lambda: [self.dashboard.lernzeit_tracker.start_timer(), self.update_timer_gui()])
        self.start_button.grid(row=0, column=2, padx=5, pady=5)

        # Stop-Button
        self.stop_button = tk.Button(timer_frame, text="⏸", font=("Arial", 24), command=lambda: [
            self.dashboard.lernzeit_tracker.stop_timer(self.dashboard.datenbank), self.update_gui()])
        self.stop_button.grid(row=0, column=3, padx=5, pady=5)


    # Erstellt das Lernzeitdiagramm der letzten 10 Wochen.
    def lernzeit_gui(self, wochen, zeiten):
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(wochen, zeiten, marker="o", linestyle="-")
        ax.set_xlabel("Kalenderwochen")
        ax.set_ylabel("Stunden")
        ax.set_title("Gelernte Zeit der letzten 10 Wochen")
        fig.autofmt_xdate()

        fig.subplots_adjust(bottom=0.3, left=0.1)

        canvas = FigureCanvasTkAgg(fig, master=self.main_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=0, columnspan=2, padx=10, pady=15, sticky="nsew")

    # Öffnet ein Dialogfenster, nachdem der Button gedrückt wurde, um eine neue Note, das Modul und die ECTS vom User abzufragen.
    def abfrage_note(self):
        try:
            modulname = simpledialog.askstring("Neue Note", "Gib den Modulnamen ein:")
            note = float(simpledialog.askstring("Neue Note", "Gib die Note ein (z.B. 1.0):"))
            ects = int(simpledialog.askstring("Neue Note", "Gib die ECTS ein (z.B. 5, 10):"))

            success = self.dashboard.notenschnitt.speichere_note(self.dashboard.datenbank, modulname, note, ects)

            if success:
                messagebox.showinfo("Erfolg", f"Note für {modulname} erfolgreich hinzugefügt.")
                self.update_gui()
            else:
                messagebox.showerror("Fehler", "Fehler beim Hinzufügen der Note.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Eingabe der Note: {e}")

    # Öffnet ein Dialogfenster, wenn keine Zielnote vorhanden ist, um den Ziel-Notenshcnitt abzufragen.
    def abfrage_zielnote(self):
        try:
            zielnote = simpledialog.askfloat("Ziel-Notenschnitt", "Gib deinen gewünschten Notenschnitt ein (z.B. 2.5):")
            if zielnote is not None:
                return zielnote
            else:
                messagebox.showerror("Fehler", "Fehler beim Speichern des Ziel-Notenschnitts.")
                return None
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Eingabe des Ziel-Notenschnitts: {e}")

    # Öffnet ein Dialogfenster, wenn keine Studienzeit vorhanden ist, um diese abzufragen.
    def abfrage_studienzeit(self):
        try:
            startdatum = simpledialog.askstring("Studienbeginn","Gib das Startdatum deines Studiums ein (YYYY-MM-DD): ")
            gesamt_monate = simpledialog.askinteger("Studiendauer", "Wie viele Monate planst du für dein Studium ein? ")
            if startdatum and gesamt_monate:
                return startdatum, gesamt_monate
            else:
                messagebox.showerror("Fehler", "Fehler beim Speichern der Studienzeit.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Eingabe der Studienzeit: {e}")