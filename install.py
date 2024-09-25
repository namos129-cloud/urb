import subprocess
import sys

def install(package):
    """Installa un pacchetto usando pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Lista di pacchetti necessari
packages = [
    "ttkbootstrap",  # Tema grafico per Tkinter
    "sqlite3",       # Database integrato
]

# Loop per installare ogni pacchetto
for package in packages:
    try:
        print(f"Installing {package}...")
        install(package)
        print(f"{package} installed successfully.")
    except Exception as e:
        print(f"Failed to install {package}: {e}")

print("All libraries installed!")
