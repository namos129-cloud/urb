import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
from datetime import datetime
import subprocess
import ttkbootstrap as tb  # Libreria per migliorare l'interfaccia


class UrbexApp:
    def __init__(self, root):
        # Usando ttkbootstrap per applicare un tema moderno
        self.root = root
        self.style = tb.Style("superhero")  # Tema scuro professionale
        self.root.title("Urbex Management System")
        self.root.geometry("600x700")

        # Connessione al database
        self.conn = sqlite3.connect('urbex.db')
        self.create_tables()

        # Variabili
        self.current_user = None

        # Pagina di Login
        self.login_frame = ttk.Frame(self.root, padding=20)
        self.login_frame.pack(pady=20)

        self.username_label = ttk.Label(self.login_frame, text="Username:", style="primary.TLabel")
        self.username_label.pack()

        self.username_entry = ttk.Entry(self.login_frame, width=30)
        self.username_entry.pack(pady=10)

        self.login_button = ttk.Button(self.login_frame, text="Login", command=self.login, style="primary.TButton")
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
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(pady=20)

        ttk.Label(self.main_frame, text=f"Welcome, {self.current_user}!", style="primary.TLabel").pack(pady=10)

        ttk.Button(self.main_frame, text="Manage Crew", command=self.manage_crew, style="success.TButton").pack(pady=5)
        ttk.Button(self.main_frame, text="Manage Locations", command=self.manage_locations, style="success.TButton").pack(pady=5)
        ttk.Button(self.main_frame, text="Plan Urbex", command=self.plan_urbex, style="success.TButton").pack(pady=5)
        ttk.Button(self.main_frame, text="View Completed Urbex", command=self.view_completed_urbex, style="success.TButton").pack(pady=5)
        ttk.Button(self.main_frame, text="Scan Wi-Fi", command=self.scan_wifi, style="success.TButton").pack(pady=5)
        ttk.Button(self.main_frame, text="View Crew Stats", command=self.view_crew_stats, style="info.TButton").pack(pady=5)
        ttk.Button(self.main_frame, text="Exit", command=self.root.quit, style="danger.TButton").pack(pady=10)

    def manage_crew(self):
        crew_member = simpledialog.askstring("Add Crew Member", "Enter crew member name:")
        if crew_member:
            with self.conn:
                self.conn.execute("INSERT OR REPLACE INTO crew (name, notes, score, status) VALUES (?, ?, ?, ?)",
                                  (crew_member, '', 0, ''))
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
        self.plan_window.geometry("500x400")

        self.date_label = ttk.Label(self.plan_window, text="Select Date (GG-MM-AAAA):")
        self.date_label.pack(pady=5)

        self.date_entry = ttk.Entry(self.plan_window, width=20)
        self.date_entry.pack(pady=5)

        self.location_label = ttk.Label(self.plan_window, text="Select Location:")
        self.location_label.pack(pady=5)

        self.location_combobox = ttk.Combobox(self.plan_window, values=self.get_locations(), width=30)
        self.location_combobox.pack(pady=5)

        self.crew_label = ttk.Label(self.plan_window, text="Select Crew Member:")
        self.crew_label.pack(pady=5)

        self.crew_combobox = ttk.Combobox(self.plan_window, values=self.get_crew(), width=30)
        self.crew_combobox.pack(pady=5)

        self.status_label = ttk.Label(self.plan_window, text="Set Status (HOST, FERITO, PERSO, etc):")
        self.status_label.pack(pady=5)

        self.status_combobox = ttk.Combobox(self.plan_window, values=["HOST", "FERITO", "PERSO", "FERMO", "SCAPPATO"], width=20)
        self.status_combobox.pack(pady=5)

        self.start_button = ttk.Button(self.plan_window, text="Start Urbex", command=self.start_urbex)
        self.start_button.pack(pady=10)

    def start_urbex(self):
        date_str = self.date_entry.get()
        try:
            date_obj = datetime.strptime(date_str, '%d-%m-%Y')
            location = self.location_combobox.get()
            crew_member = self.crew_combobox.get()
            status = self.status_combobox.get()

            if not location or not crew_member or not status:
                messagebox.showerror("Error", "Please fill in all fields.")
                return

            with self.conn:
                self.conn.execute("INSERT INTO urbex_dates (date, location, crew, notes, exploration_percentage, start_time, end_time, coordinates) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                  (date_obj.strftime('%d-%m-%Y'), location, crew_member, '', 0, '', '', ''))

            messagebox.showinfo("Urbex Started", f"Urbex planned for {date_str} at {location} with crew {crew_member} ({status}).")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid date (GG-MM-AAAA).")

    def view_completed_urbex(self):
        self.completed_window = tk.Toplevel(self.root)
        self.completed_window.title("Completed Urbex Activities")
        self.completed_window.geometry("600x400")

        with self.conn:
            cursor = self.conn.execute("SELECT * FROM urbex_dates")
            activities = cursor.fetchall()

        for activity in activities:
            ttk.Label(self.completed_window, text=f"Date: {activity[0]}, Location: {activity[1]}, Crew: {activity[2]}, Exploration: {activity[4]}%", style="info.TLabel").pack(pady=5)

    def view_crew_stats(self):
        self.stats_window = tk.Toplevel(self.root)
        self.stats_window.title("Crew Stats")
        self.stats_window.geometry("400x400")

        with self.conn:
            cursor = self.conn.execute("SELECT * FROM crew")
            crew_members = cursor.fetchall()

        for member in crew_members:
            ttk.Label(self.stats_window, text=f"{member[0]} - Score: {member[2]}, Status: {member[3]}", style="primary.TLabel").pack(pady=5)

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
            wifi_list = subprocess.check_output(["netsh", "wlan", "show", "network"], encoding='utf-8')
            self.show_wifi_list(wifi_list)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_wifi_list(self, wifi_list):
        self.wifi_window = tk.Toplevel(self.root)
        self.wifi_window.title("Available Wi-Fi Networks")
        self.wifi_window.geometry("500x300")

        ttk.Label(self.wifi_window, text="Wi-Fi Networks:", style="primary.TLabel").pack(pady=10)

        wifi_text = tk.Text(self.wifi_window, height=15, width=50)
        wifi_text.pack(pady=10)
        wifi_text.insert(tk.END, wifi_list)
        wifi_text.config(state=tk.DISABLED)

        self.update_wifi_list()

    def update_wifi_list(self):
        try:
            wifi_list = subprocess.check_output(["netsh", "wlan", "show", "network"], encoding='utf-8')
            wifi_text = self.wifi_window.children['!text']
            wifi_text.config(state=tk.NORMAL)
            wifi_text.delete('1.0', tk.END)
            wifi_text.insert(tk.END, wifi_list)
            wifi_text.config(state=tk.DISABLED)
            self.wifi_window.after(10000, self.update_wifi_list)
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = UrbexApp(root)
    root.mainloop()
