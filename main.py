import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import subprocess
import sqlite3

class UrbexApp:
    def __init__(self, root):
        self.root = root
        self.style = tb.Style(theme="superhero")  # Tema scuro e professionale
        self.root.title("Urbex Crew Management System")
        self.root.geometry("800x700")

        # Connetti al database SQLite
        self.conn = sqlite3.connect("urbex_crew.db")
        self.create_tables()

        # Frame principale
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(pady=20)

        # Titolo
        title_label = ttk.Label(frame, text="Urbex Crew Management", font=("Helvetica", 24), style="primary.TLabel")
        title_label.pack(pady=10)

        # Selezione data e luogo
        self.date_entry = ttk.Entry(frame, bootstyle="info", width=20)
        self.date_entry.insert(0, "DD-MM-YYYY")  # Placeholder per la data
        self.date_entry.pack(pady=5)
        
        self.location_entry = ttk.Entry(frame, bootstyle="info", width=20)
        self.location_entry.insert(0, "Abandoned Place")  # Placeholder per il luogo
        self.location_entry.pack(pady=5)

        # Dropdown per crew membri
        self.crew_var = tk.StringVar(value=self.get_crew())
        self.crew_listbox = tk.Listbox(frame, listvariable=self.crew_var, height=5, selectmode=tk.MULTIPLE)
        self.crew_listbox.pack(pady=10)

        # Pulsanti di azione
        ttk.Button(frame, text="Add Urbex Plan", bootstyle="primary", command=self.add_plan).pack(pady=5)
        ttk.Button(frame, text="View Completed Urbex", bootstyle="info", command=self.view_completed).pack(pady=5)
        ttk.Button(frame, text="Crew Stats", bootstyle="secondary", command=self.view_crew_stats).pack(pady=5)

        # Barra di avanzamento circolare per la percentuale di esplorazione
        self.progress = ttk.Progressbar(frame, mode='determinate', length=200, style="info.Horizontal.TProgressbar")
        self.progress.pack(pady=20)
        self.percent_label = ttk.Label(frame, text="0%", font=("Helvetica", 16), style="info.TLabel")
        self.percent_label.pack(pady=5)

        # Avvia il monitoraggio del progresso (esempio di avanzamento)
        self.update_progress(0)

        # Scansione Wi-Fi
        ttk.Button(frame, text="Scan Wi-Fi Networks", bootstyle="warning", command=self.scan_wifi).pack(pady=5)

    def create_tables(self):
        """Crea le tabelle nel database se non esistono"""
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS crew 
                                 (name TEXT, role TEXT, score INTEGER, status TEXT)''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS urbex_plans 
                                 (date TEXT, location TEXT, crew TEXT, status TEXT, exploration INTEGER)''')

    def add_plan(self):
        """Aggiungi un nuovo piano di esplorazione urbex"""
        date = self.date_entry.get()
        location = self.location_entry.get()
        crew = [self.crew_listbox.get(i) for i in self.crew_listbox.curselection()]

        if not date or not location or not crew:
            messagebox.showerror("Error", "Please fill out all fields")
            return
        
        # Salva il piano di urbex nel database
        with self.conn:
            self.conn.execute("INSERT INTO urbex_plans (date, location, crew, status, exploration) VALUES (?, ?, ?, ?, ?)",
                              (date, location, ','.join(crew), 'Not Started', 0))

        messagebox.showinfo("Success", "Urbex Plan Added!")
        self.date_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)

    def view_completed(self):
        """Mostra gli urbex completati"""
        self.completed_window = tk.Toplevel(self.root)
        self.completed_window.title("Completed Urbex Plans")
        self.completed_window.geometry("600x400")

        with self.conn:
            cursor = self.conn.execute("SELECT * FROM urbex_plans WHERE status='Completed'")
            activities = cursor.fetchall()

        for activity in activities:
            ttk.Label(self.completed_window, text=f"Date: {activity[0]}, Location: {activity[1]}, Crew: {activity[2]}, Exploration: {activity[4]}%", style="info.TLabel").pack(pady=5)

    def view_crew_stats(self):
        """Mostra le statistiche della crew"""
        self.stats_window = tk.Toplevel(self.root)
        self.stats_window.title("Crew Stats")
        self.stats_window.geometry("400x400")

        with self.conn:
            cursor = self.conn.execute("SELECT * FROM crew")
            crew_members = cursor.fetchall()

        for member in crew_members:
            ttk.Label(self.stats_window, text=f"{member[0]} - Score: {member[2]}, Status: {member[3]}", style="primary.TLabel").pack(pady=5)

    def get_crew(self):
        """Ottieni la lista dei membri della crew dal database"""
        with self.conn:
            cursor = self.conn.execute("SELECT name FROM crew")
            return [row[0] for row in cursor.fetchall()]

    def update_progress(self, progress):
        """Simula l'aggiornamento della barra di progresso"""
        if progress < 100:
            self.progress['value'] = progress
            self.percent_label.config(text=f"{progress}%")
            self.root.after(100, self.update_progress, progress + 1)

    def scan_wifi(self):
        """Esegue la scansione delle reti Wi-Fi disponibili"""
        try:
            wifi_list = subprocess.check_output(["netsh", "wlan", "show", "network"], encoding='utf-8')
            self.show_wifi_list(wifi_list)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_wifi_list(self, wifi_list):
        """Mostra la lista delle reti Wi-Fi trovate"""
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
        """Aggiorna la lista delle reti Wi-Fi ogni 10 secondi"""
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
