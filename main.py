import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import folium
import os
import requests
from datetime import datetime
import pytz

class UrbexApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Urbex Crew Management System")
        self.root.geometry("800x700")

        # Connect to SQLite database
        self.conn = sqlite3.connect("urbex_crew.db")
        self.create_tables()

        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Initialize pages
        self.create_login_page()
        self.create_home_page()
        self.create_completed_page()
        self.create_crew_stats_page()
        self.create_add_crew_page()

        # Show the login page by default
        self.show_frame(self.login_frame)

    def create_tables(self):
        """Create the necessary tables in the database."""
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS crew 
                                 (name TEXT, role TEXT, score INTEGER, status TEXT)''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS urbex_plans 
                                 (date TEXT, location TEXT, latitude REAL, longitude REAL, crew TEXT, notes TEXT, status TEXT)''')

    def create_login_page(self):
        """Create the login page."""
        self.login_frame = ttk.Frame(self.main_frame)
        self.login_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(self.login_frame, text="Login", font=("Helvetica", 24)).pack(pady=10)

        # Username entry
        self.username_entry = ttk.Entry(self.login_frame, width=30)
        self.username_entry.insert(0, "Username")
        self.username_entry.pack(pady=5)

        # Password entry
        self.password_entry = ttk.Entry(self.login_frame, show='*', width=30)
        self.password_entry.insert(0, "Password")
        self.password_entry.pack(pady=5)

        # Login button
        ttk.Button(self.login_frame, text="Login", command=self.login).pack(pady=10)

    def create_home_page(self):
        """Create the home page for adding urbex plans."""
        self.home_frame = ttk.Frame(self.main_frame)
        self.home_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(self.home_frame, text="Urbex Crew Management", font=("Helvetica", 24))
        title_label.pack(pady=10)

        # Current Time Label
        self.time_label = ttk.Label(self.home_frame, font=("Helvetica", 12))
        self.time_label.pack(pady=5)

        # Weather Info Label
        self.weather_label = ttk.Label(self.home_frame, font=("Helvetica", 12))
        self.weather_label.pack(pady=5)

        # Date entry
        self.date_entry = ttk.Entry(self.home_frame, width=20)
        self.date_entry.insert(0, "DD-MM-YYYY")
        self.date_entry.pack(pady=5)

        # Location entry
        self.location_entry = ttk.Entry(self.home_frame, width=20)
        self.location_entry.insert(0, "Abandoned Place")
        self.location_entry.pack(pady=5)

        # Latitude and Longitude entry
        self.latitude_entry = ttk.Entry(self.home_frame, width=20)
        self.latitude_entry.insert(0, "Latitude")
        self.latitude_entry.pack(pady=5)

        self.longitude_entry = ttk.Entry(self.home_frame, width=20)
        self.longitude_entry.insert(0, "Longitude")
        self.longitude_entry.pack(pady=5)

        # Notes entry
        self.notes_entry = ttk.Entry(self.home_frame, width=50)
        self.notes_entry.insert(0, "Notes about the location")
        self.notes_entry.pack(pady=5)

        # Crew members list
        self.crew_list = tk.StringVar(value=self.get_crew())
        self.crew_listbox = tk.Listbox(self.home_frame, listvariable=self.crew_list, height=5, selectmode=tk.MULTIPLE)
        self.crew_listbox.pack(pady=10)

        # Buttons
        ttk.Button(self.home_frame, text="Add Urbex Plan", command=self.add_plan).pack(pady=5)
        ttk.Button(self.home_frame, text="View Completed Urbex", command=lambda: self.show_frame(self.completed_frame)).pack(pady=5)
        ttk.Button(self.home_frame, text="View Crew Stats", command=lambda: self.show_frame(self.crew_stats_frame)).pack(pady=5)
        ttk.Button(self.home_frame, text="Add Crew Member", command=lambda: self.show_frame(self.add_crew_frame)).pack(pady=5)

    def create_completed_page(self):
        """Create the completed plans page."""
        self.completed_frame = ttk.Frame(self.main_frame)

        # Title
        ttk.Label(self.completed_frame, text="Completed Urbex Plans", font=("Helvetica", 24)).pack(pady=10)

        # Completed plans list
        self.completed_listbox = tk.Listbox(self.completed_frame, height=15)
        self.completed_listbox.pack(pady=20)

        # Back button
        ttk.Button(self.completed_frame, text="Back", command=lambda: self.show_frame(self.home_frame)).pack(pady=5)

    def create_crew_stats_page(self):
        """Create the crew statistics page."""
        self.crew_stats_frame = ttk.Frame(self.main_frame)

        # Title
        ttk.Label(self.crew_stats_frame, text="Crew Statistics", font=("Helvetica", 24)).pack(pady=10)

        # Crew stats list
        self.crew_stats_listbox = tk.Listbox(self.crew_stats_frame, height=15)
        self.crew_stats_listbox.pack(pady=20)

        # Back button
        ttk.Button(self.crew_stats_frame, text="Back", command=lambda: self.show_frame(self.home_frame)).pack(pady=5)

    def create_add_crew_page(self):
        """Create the page for adding crew members."""
        self.add_crew_frame = ttk.Frame(self.main_frame)

        # Title
        ttk.Label(self.add_crew_frame, text="Add Crew Member", font=("Helvetica", 24)).pack(pady=10)

        # Name entry
        self.name_entry = ttk.Entry(self.add_crew_frame, width=20)
        self.name_entry.insert(0, "Crew Member Name")
        self.name_entry.pack(pady=5)

        # Role entry
        self.role_entry = ttk.Entry(self.add_crew_frame, width=20)
        self.role_entry.insert(0, "Role")
        self.role_entry.pack(pady=5)

        # Score entry
        self.score_entry = ttk.Entry(self.add_crew_frame, width=20)
        self.score_entry.insert(0, "Score")
        self.score_entry.pack(pady=5)

        # Status entry
        self.status_entry = ttk.Entry(self.add_crew_frame, width=20)
        self.status_entry.insert(0, "Status")
        self.status_entry.pack(pady=5)

        # Add button
        ttk.Button(self.add_crew_frame, text="Add Crew", command=self.add_crew).pack(pady=5)

        # Back button
        ttk.Button(self.add_crew_frame, text="Back", command=lambda: self.show_frame(self.home_frame)).pack(pady=5)

    def login(self):
        """Handle the login process."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "admin" and password == "password":  # Simple hard-coded check
            messagebox.showinfo("Login Successful", "Welcome to Urbex Management!")
            self.show_frame(self.home_frame)
            self.update_time()
            self.update_weather()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def update_time(self):
        """Update the current time label."""
        timezone = pytz.timezone("Europe/Rome")
        current_time = datetime.now(timezone).strftime("%H:%M:%S")
        self.time_label.config(text=f"Current Time: {current_time}")
        self.root.after(1000, self.update_time)  # Update every second

    def update_weather(self):
        """Fetch and display the current weather for a specific location."""
        location = "Rome"  # Example location; you can modify this
        api_key = "YOUR_API_KEY"  # Replace with your OpenWeatherMap API key
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        
        try:
            response = requests.get(url)
            weather_data = response.json()
            if response.status_code == 200:
                weather_desc = weather_data["weather"][0]["description"]
                temp = weather_data["main"]["temp"]
                self.weather_label.config(text=f"Weather in {location}: {temp}°C, {weather_desc}")
            else:
                self.weather_label.config(text="Weather information not available.")
        except Exception as e:
            self.weather_label.config(text="Error fetching weather data.")

    def show_frame(self, frame):
        """Show the specified frame and hide others."""
        frame.tkraise()

    def add_plan(self):
        """Add a new urbex plan to the database."""
        date = self.date_entry.get()
        location = self.location_entry.get()
        latitude = self.latitude_entry.get()
        longitude = self.longitude_entry.get()
        notes = self.notes_entry.get()
        crew = [self.crew_listbox.get(i) for i in self.crew_listbox.curselection()]

        if not date or not location or not latitude or not longitude or not crew:
            messagebox.showerror("Error", "Please fill out all fields")
            return

        # Save the urbex plan to the database
        with self.conn:
            self.conn.execute("INSERT INTO urbex_plans (date, location, latitude, longitude, crew, notes, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                              (date, location, latitude, longitude, ', '.join(crew), notes, 'Not Started'))

        messagebox.showinfo("Success", "Urbex Plan Added!")
        self.clear_entries()

    def add_crew(self):
        """Add a new crew member to the database."""
        name = self.name_entry.get()
        role = self.role_entry.get()
        score = self.score_entry.get()
        status = self.status_entry.get()

        if not name or not role or not score or not status:
            messagebox.showerror("Error", "Please fill out all fields")
            return

        # Save the crew member to the database
        with self.conn:
            self.conn.execute("INSERT INTO crew (name, role, score, status) VALUES (?, ?, ?, ?)",
                              (name, role, int(score), status))

        messagebox.showinfo("Success", "Crew Member Added!")
        self.clear_crew_entries()

    def clear_entries(self):
        """Clear input fields after adding a plan."""
        self.date_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)
        self.latitude_entry.delete(0, tk.END)
        self.longitude_entry.delete(0, tk.END)
        self.notes_entry.delete(0, tk.END)

    def clear_crew_entries(self):
        """Clear input fields after adding a crew member."""
        self.name_entry.delete(0, tk.END)
        self.role_entry.delete(0, tk.END)
        self.score_entry.delete(0, tk.END)
        self.status_entry.delete(0, tk.END)

    def get_crew(self):
        """Retrieve the list of crew members from the database."""
        with self.conn:
            cursor = self.conn.execute("SELECT name FROM crew")
            return [row[0] for row in cursor.fetchall()]

if __name__ == "__main__":
    root = tk.Tk()
    app = UrbexApp(root)
    root.mainloop()
