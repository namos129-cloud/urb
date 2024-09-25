import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
from datetime import datetime
import subprocess


class UrbexApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Urbex Management System")

        # Imposta lo sfondo e il colore del testo
        self.root.configure(bg="#2c2c2c")  # Sfondo scuro
        self.text_color = "white"  # Testo bianco

        # Connessione al database
        self.conn = sqlite3.connect('urbex.db')
        self.create_tables()

        # Variabili
        self.current_user = None

        # Pagina di Login
        self.login_frame = tk.Frame(self.root, bg="#2c2c2c")
        self.login_frame.pack()

        self.username_label = tk.Label(self.login_frame, text="Username:", bg="#2c2c2c", fg=self.text_color)
        self.username_label.pack()

        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.pack()

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.pack()

    def create_tables(self):
        # Crea le tabelle se non esistono
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS crew (
                                    name TEXT PRIMARY KEY,
                                    notes TEXT,
                                    score INTEGER)''')
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
                                    end_time TEXT)''')

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
        self.main_frame.pack()

        tk.Label(self.main_frame, text=f"Welcome, {self.current_user}!", bg="#2c2c2c", fg=self.text_color).pack()

        tk.Button(self.main_frame, text="Manage Crew", command=self.manage_crew).pack()
        tk.Button(self.main_frame, text="Manage Locations", command=self.manage_locations).pack()
        tk.Button(self.main_frame, text="Plan Urbex", command=self.plan_urbex).pack()
        tk.Button(self.main_frame, text="Scan Wi-Fi", command=self.scan_wifi).pack()
        tk.Button(self.main_frame, text="Exit", command=self.root.quit).pack()

    def manage_crew(self):
        crew_member = simpledialog.askstring("Add Crew Member", "Enter crew member name:")
        if crew_member:
            with self.conn:
                self.conn.execute("INSERT OR REPLACE INTO crew (name, notes, score) VALUES (?, ?, ?)", 
                                  (crew_member, '', 0))
            messagebox.showinfo("Success", f"{crew_member} added to the crew.")

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
        self.date_label = tk.Label(self.plan_window, text="Select Date for Urbex:", bg="#2c2c2c", fg=self.text_color)
        self.date_label.pack()

        self.date_entry = tk.Entry(self.plan_window)
        self.date_entry.pack()

        self.plan_button = tk.Button(self.plan_window, text="Plan Urbex", command=self.select_date)
        self.plan_button.pack()

    def select_date(self):
        date_str = self.date_entry.get()
        try:
            # Controlla se la data è valida
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            self.show_location_and_crew(date_obj)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid date (YYYY-MM-DD).")

    def show_location_and_crew(self, date):
        self.location_crew_window = tk.Toplevel(self.root)
        self.location_crew_window.title("Choose Location and Crew")
        self.location_crew_window.configure(bg="#2c2c2c")

        tk.Label(self.location_crew_window, text="Select Location:", bg="#2c2c2c", fg=self.text_color).pack()
        self.location_combobox = ttk.Combobox(self.location_crew_window, values=self.get_locations())
        self.location_combobox.pack()

        tk.Label(self.location_crew_window, text="Select Crew Member:", bg="#2c2c2c", fg=self.text_color).pack()
        self.crew_combobox = ttk.Combobox(self.location_crew_window, values=self.get_crew())
        self.crew_combobox.pack()

        self.start_button = tk.Button(self.location_crew_window, text="Start Urbex", command=lambda: self.start_urbex(date))
        self.start_button.pack()

    def start_urbex(self, date):
        location = self.location_combobox.get()
        crew = self.crew_combobox.get()

        # Salva l'attività nel database
        with self.conn:
            self.conn.execute("INSERT INTO urbex_dates (date, location, crew, notes, exploration_percentage, start_time, end_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                              (date.strftime('%Y-%m-%d'), location, crew, '', 0, '', ''))

        messagebox.showinfo("Urbex Started", f"Urbex planned for {date.strftime('%Y-%m-%d')} at {location} with crew {crew}.")
        self.open_activity_window(date.strftime('%Y-%m-%d'), location, crew)

    def open_activity_window(self, date, location, crew):
        self.activity_window = tk.Toplevel(self.root)
        self.activity_window.title("Activity Details")
        self.activity_window.configure(bg="#2c2c2c")

        tk.Label(self.activity_window, text=f"Urbex on {date} at {location}", bg="#2c2c2c", fg=self.text_color).pack()

        tk.Label(self.activity_window, text="Notes:", bg="#2c2c2c", fg=self.text_color).pack()
        self.notes_entry = tk.Text(self.activity_window, height=5, width=40)
        self.notes_entry.pack()

        tk.Label(self.activity_window, text="Exploration Percentage:", bg="#2c2c2c", fg=self.text_color).pack()
        self.percentage_entry = tk.Entry(self.activity_window)
        self.percentage_entry.pack()

        tk.Label(self.activity_window, text="Start Time:", bg="#2c2c2c", fg=self.text_color).pack()
        self.start_time_entry = tk.Entry(self.activity_window)
        self.start_time_entry.insert(0, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.start_time_entry.pack()

        tk.Label(self.activity_window, text="End Time:", bg="#2c2c2c", fg=self.text_color).pack()
        self.end_time_entry = tk.Entry(self.activity_window)
        self.end_time_entry.pack()

        self.save_button = tk.Button(self.activity_window, text="Save Activity", command=lambda: self.save_activity(date, location, crew))
        self.save_button.pack()

        tk.Button(self.activity_window, text="Scan Wi-Fi", command=self.scan_wifi).pack()

    def save_activity(self, date, location, crew):
        notes = self.notes_entry.get("1.0", tk.END).strip()
        exploration_percentage = self.percentage_entry.get()
        start_time = self.start_time_entry.get()
        end_time = self.end_time_entry.get()

        # Aggiornare l'attività nel database
        with self.conn:
            self.conn.execute("UPDATE urbex_dates SET notes=?, exploration_percentage=?, start_time=?, end_time=? WHERE date=? AND location=? AND crew=?",
                              (notes, exploration_percentage, start_time, end_time, date, location, crew))

        messagebox.showinfo("Activity Saved", "Activity details saved successfully!")

    def get_locations(self):
        return [row[0] for row in self.conn.execute("SELECT name FROM locations")]

    def get_crew(self):
        return [row[0] for row in self.conn.execute("SELECT name FROM crew")]

    def scan_wifi(self):
        # Scans for Wi-Fi networks and displays them
        try:
            wifi_list = subprocess.check_output(["netsh", "wlan", "show", "network"], encoding='utf-8')
            messagebox.showinfo("Wi-Fi Networks", wifi_list)
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = UrbexApp(root)
    root.mainloop()
