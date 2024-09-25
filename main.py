import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
from datetime import datetime
import subprocess
import re


class UrbexApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Urbex Management System")
        self.root.geometry("500x600")
        self.root.configure(bg="#2c2c2c")  # Sfondo scuro
        self.text_color = "white"  # Testo bianco

        # Connessione al database
        self.conn = sqlite3.connect('urbex.db')
        self.create_tables()

        # Variabili
        self.current_user = None

        # Pagina di Login
        self.login_frame = tk.Frame(self.root, bg="#2c2c2c")
        self.login_frame.pack(pady=20)

        self.username_label = tk.Label(self.login_frame, text="Username:", bg="#2c2c2c", fg=self.text_color)
        self.username_label.pack()

        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.pack(pady=10)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.pack(pady=10)

    def create_tables(self):
        # Crea le tabelle se non esistono
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS crew (
                                    name TEXT PRIMARY KEY,
                                    notes TEXT,
                                    score INTEGER,
                                    status TEXT)''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS locations (
                                    name TEXT PRIMARY KEY,
                                    activities TEXT)''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS urbex_dates (
                                    date TEXT PRIMARY KEY,
                                    location TEXT,
                                    crew TEXT,
                                    notes TEXT,
                                    exploration_percentage INTEGER,
                                    start_time TEXT,
                                    end_time TEXT,
                                    coordinates TEXT)''')

    def login(self):
        username = self.username_entry.get()
        if username:
            self.current_user = username
            self.login_frame.pack_forget()
            self.show_main_menu()
        else:
            messagebox.showwarning("Login Error", "Please enter a username.")

    def show_main_menu(self):
        self.main_frame = tk.Frame(self.root, bg="#2c2c2c")
        self.main_frame.pack(pady=20)

        tk.Label(self.main_frame, text=f"Welcome, {self.current_user}!", bg="#2c2c2c", fg=self.text_color).pack()

        tk.Button(self.main_frame, text="Manage Crew", command=self.manage_crew).pack(pady=5)
        tk.Button(self.main_frame, text="Manage Locations", command=self.manage_locations).pack(pady=5)
        tk.Button(self.main_frame, text="Plan Urbex", command=self.plan_urbex).pack(pady=5)
        tk.Button(self.main_frame, text="View Completed Urbex", command=self.view_completed_urbex).pack(pady=5)
        tk.Button(self.main_frame, text="Scan Wi-Fi", command=self.scan_wifi).pack(pady=5)
        tk.Button(self.main_frame, text="Exit", command=self.root.quit).pack(pady=5)

    def manage_crew(self):
        crew_member = simpledialog.askstring("Add Crew Member", "Enter crew member name:")
        if crew_member:
            status = simpledialog.askstring("Status", "Enter status (HOST, FERITO, FERMO, PERSO, SCAPPATO):")
            with self.conn:
                self.conn.execute("INSERT OR REPLACE INTO crew (name, notes, score, status) VALUES (?, ?, ?, ?)",
                                  (crew_member, '', 0, status))
            messagebox.showinfo("Success", f"{crew_member} added to the crew with status '{status}'.")

    def manage_locations(self):
        location = simpledialog.askstring("Add Location", "Enter abandoned location name:")
        if location:
            with self.conn:
                self.conn.execute("INSERT OR REPLACE INTO locations (name, activities) VALUES (?, ?)",
                                  (location, ''))
            messagebox.showinfo("Success", f"{location} added to locations.")

    def plan_urbex(self):
        # Creare una nuova finestra per pianificare l'urbex
        self.plan_window = tk.Toplevel(self.root)
        self.plan_window.title("Plan Urbex")
        self.plan_window.configure(bg="#2c2c2c")

        # Tabella delle date
        self.date_label = tk.Label(self.plan_window, text="Select Date (GG-MM-AAAA):", bg="#2c2c2c", fg=self.text_color)
        self.date_label.pack()

        self.date_entry = tk.Entry(self.plan_window)
        self.date_entry.pack(pady=10)

        self.plan_button = tk.Button(self.plan_window, text="Plan Urbex", command=self.select_date)
        self.plan_button.pack(pady=10)

    def select_date(self):
        date_str = self.date_entry.get()
        try:
            # Controlla se la data è valida
            date_obj = datetime.strptime(date_str, '%d-%m-%Y')
            self.show_location_and_crew(date_obj)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid date (GG-MM-AAAA).")

    def show_location_and_crew(self, date):
        self.location_crew_window = tk.Toplevel(self.root)
        self.location_crew_window.title("Choose Location and Crew")
        self.location_crew_window.configure(bg="#2c2c2c")

        tk.Label(self.location_crew_window, text="Select Location:", bg="#2c2c2c", fg=self.text_color).pack()
        self.location_combobox = ttk.Combobox(self.location_crew_window, values=self.get_locations())
        self.location_combobox.pack(pady=10)

        tk.Label(self.location_crew_window, text="Select Crew Member:", bg="#2c2c2c", fg=self.text_color).pack()
        self.crew_combobox = ttk.Combobox(self.location_crew_window, values=self.get_crew())
        self.crew_combobox.pack(pady=10)

        tk.Label(self.location_crew_window, text="Coordinates (Lat, Long):", bg="#2c2c2c", fg=self.text_color).pack()
        self.coordinates_entry = tk.Entry(self.location_crew_window)
        self.coordinates_entry.pack(pady=10)

        self.start_button = tk.Button(self.location_crew_window, text="Start Urbex", command=lambda: self.start_urbex(date))
        self.start_button.pack(pady=10)

    def start_urbex(self, date):
        location = self.location_combobox.get()
        crew = self.crew_combobox.get()
        coordinates = self.coordinates_entry.get()

        # Salva l'attività nel database
        with self.conn:
            self.conn.execute("INSERT INTO urbex_dates (date, location, crew, notes, exploration_percentage, start_time, end_time, coordinates) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                              (date.strftime('%d-%m-%Y'), location, crew, '', 0, '', '', coordinates))

        messagebox.showinfo("Urbex Started", f"Urbex planned for {date.strftime('%d-%m-%Y')} at {location} with crew {crew}.")
        self.open_activity_window(date.strftime('%d-%m-%Y'), location, crew, coordinates)

    def open_activity_window(self, date, location, crew, coordinates):
        self.activity_window = tk.Toplevel(self.root)
        self.activity_window.title("Activity Details")
        self.activity_window.configure(bg="#2c2c2c")

        tk.Label(self.activity_window, text=f"Urbex on {date} at {location}", bg="#2c2c2c", fg=self.text_color).pack()

        tk.Label(self.activity_window, text="Notes:", bg="#2c2c2c", fg=self.text_color).pack()
        self.notes_entry = tk.Text(self.activity_window, height=5, width=40)
        self.notes_entry.pack(pady=10)

        tk.Label(self.activity_window, text="Exploration Percentage:", bg="#2c2c2c", fg=self.text_color).pack()
        self.percentage_entry = tk.Entry(self.activity_window)
        self.percentage_entry.pack(pady=10)

        tk.Label(self.activity_window, text="Start Time:", bg="#2c2c2c", fg=self.text_color).pack()
        self.start_time_entry = tk.Entry(self.activity_window)
        self.start_time_entry.insert(0, datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
        self.start_time_entry.pack(pady=10)

        tk.Label(self.activity_window, text="End Time:", bg="#2c2c2c", fg=self.text_color).pack()
        self.end_time_entry = tk.Entry(self.activity_window)
        self.end_time_entry.pack(pady=10)

        self.save_button = tk.Button(self.activity_window, text="Save Activity", command=lambda: self.save_activity(date, location, crew, coordinates))
        self.save_button.pack(pady=10)

    def save_activity(self, date, location, crew, coordinates):
        notes = self.notes_entry.get("1.0", tk.END)
        percentage = self.percentage_entry.get()
        start_time = self.start_time_entry.get()
        end_time = self.end_time_entry.get()

        # Aggiorna l'attività nel database
        with self.conn:
            self.conn.execute("UPDATE urbex_dates SET notes = ?, exploration_percentage = ?, start_time = ?, end_time = ? WHERE date = ? AND location = ? AND crew = ?",
                              (notes, percentage, start_time, end_time, date, location, crew))

        messagebox.showinfo("Success", "Activity saved successfully!")

    def view_completed_urbex(self):
        self.completed_window = tk.Toplevel(self.root)
        self.completed_window.title("Completed Urbex Activities")
        self.completed_window.configure(bg="#2c2c2c")

        # Mostra attività urbex completate
        with self.conn:
            cursor = self.conn.execute("SELECT * FROM urbex_dates")
            activities = cursor.fetchall()

        for activity in activities:
            tk.Label(self.completed_window, text=f"Date: {activity[0]}, Location: {activity[1]}, Crew: {activity[2]}, Notes: {activity[3]}, Exploration %: {activity[4]}, Start: {activity[5]}, End: {activity[6]}, Coordinates: {activity[7]}",
                     bg="#2c2c2c", fg=self.text_color).pack(pady=5)

    def get_locations(self):
        with self.conn:
            cursor = self.conn.execute("SELECT name FROM locations")
            return [row[0] for row in cursor.fetchall()]

    def get_crew(self):
        with self.conn:
            cursor = self.conn.execute("SELECT name FROM crew")
            return [row[0] for row in cursor.fetchall()]

    def scan_wifi(self):
        try:
            # Ottieni la lista delle reti Wi-Fi
            wifi_list = subprocess.check_output(["netsh", "wlan", "show", "network"], encoding='utf-8')
            self.show_wifi_list(wifi_list)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_wifi_list(self, wifi_list):
        self.wifi_window = tk.Toplevel(self.root)
        self.wifi_window.title("Available Wi-Fi Networks")
        self.wifi_window.configure(bg="#2c2c2c")

        tk.Label(self.wifi_window, text="Wi-Fi Networks:", bg="#2c2c2c", fg=self.text_color).pack()

        wifi_text = tk.Text(self.wifi_window, height=15, width=50)
        wifi_text.pack(pady=10)
        wifi_text.insert(tk.END, wifi_list)
        wifi_text.config(state=tk.DISABLED)  # Restringi l'editing

        # Aggiorna la lista in tempo reale
        self.update_wifi_list()

    def update_wifi_list(self):
        try:
            # Ottieni la lista delle reti Wi-Fi
            wifi_list = subprocess.check_output(["netsh", "wlan", "show", "network"], encoding='utf-8')
            wifi_text = self.wifi_window.children['!text']  # Ottieni il widget Text
            wifi_text.config(state=tk.NORMAL)
            wifi_text.delete('1.0', tk.END)  # Cancella il contenuto precedente
            wifi_text.insert(tk.END, wifi_list)  # Inserisci la nuova lista
            wifi_text.config(state=tk.DISABLED)  # Restringi l'editing
            self.wifi_window.after(10000, self.update_wifi_list)  # Aggiorna ogni 10 secondi
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = UrbexApp(root)
    root.mainloop()
