"""
Calendar Printer GUI (Beginner Project)

This program shows a simple GUI (window) using Tkinter.
From this window I can:
- Print today's Google Calendar events
- Print today's Google Tasks
- Schedule automatic printing
- Set task priorities
- Configure printer settings

I wrote this while learning Python, GUIs, and Google APIs.
So the code is very verbose and heavily commented.
"""

# ------------------------------------------------
# IMPORTS (things Python needs)
# ------------------------------------------------

import os                 # Used to check if files exist
import datetime           # Used for dates and time
import serial             # Used to talk to thermal printer
import tkinter as tk      # Main GUI library
from tkinter import ttk, messagebox, scrolledtext  # GUI widgets
import threading          # Used so printing doesn't freeze GUI
import schedule           # Used for automatic time scheduling
import time               # Used for sleep in scheduler
import json               # Used to save settings to file

# Google API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# ------------------------------------------------
# BASIC CONFIGURATION
# ------------------------------------------------

# Default printer settings
PRINTER_PORT = 'COM4'
PRINTER_BAUDRATE = 9600

# Google permissions
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/tasks.readonly'
]

# File where settings are saved
CONFIG_FILE = 'printer_config.json'


# ------------------------------------------------
# LOAD AND SAVE CONFIG FILE
# ------------------------------------------------

def load_config():
    """
    Loads saved configuration from file.
    If file does not exist, use default values.
    """

    # Default settings
    default_config = {
        'printer_port': PRINTER_PORT,
        'printer_baudrate': PRINTER_BAUDRATE,
        'schedules': ['08:00', '12:00', '18:00'],
        'task_priorities': {},
        'auto_start': False
    }

    # If config file exists, try to read it
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)

            # Make sure all keys exist
            for key in default_config:
                if key not in config:
                    config[key] = default_config[key]

            return config

        except Exception:
            # If file is broken, return defaults
            return default_config

    # If file does not exist
    return default_config


def save_config(config):
    """
    Saves configuration to JSON file
    """
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


# ------------------------------------------------
# GOOGLE AUTHENTICATION
# ------------------------------------------------

def authenticate_google():
    """
    Handles Google login for Calendar and Tasks.
    """

    creds = None

    # Load token if it exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If token missing or invalid
    if not creds or not creds.valid:

        # Refresh expired token
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        # First time login
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


# ------------------------------------------------
# FETCH GOOGLE CALENDAR EVENTS
# ------------------------------------------------

def get_todays_events():
    """
    Fetches today's calendar events
    """

    creds = authenticate_google()
    service = build('calendar', 'v3', credentials=creds)

    now = datetime.datetime.now()

    start_day = datetime.datetime.combine(now.date(), datetime.time.min)
    end_day = datetime.datetime.combine(now.date(), datetime.time.max)

    time_min = start_day.isoformat() + 'Z'
    time_max = end_day.isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    return events_result.get('items', [])


# ------------------------------------------------
# FETCH GOOGLE TASKS
# ------------------------------------------------

def get_todays_tasks():
    """
    Fetches incomplete Google Tasks
    """

    creds = authenticate_google()
    service = build('tasks', 'v1', credentials=creds)

    all_tasks = []

    try:
        task_lists = service.tasklists().list().execute()
        lists = task_lists.get('items', [])

        for task_list in lists:
            list_id = task_list['id']
            list_name = task_list['title']

            tasks_result = service.tasks().list(
                tasklist=list_id,
                showCompleted=False,
                showHidden=False
            ).execute()

            tasks = tasks_result.get('items', [])

            for task in tasks:
                task['list_name'] = list_name
                all_tasks.append(task)

    except Exception as e:
        print("Error loading tasks:", e)

    return all_tasks


# ------------------------------------------------
# PRINTER HELPERS
# ------------------------------------------------

def connect_to_printer(port, baudrate):
    """
    Connects to the thermal printer
    """
    try:
        return serial.Serial(port=port, baudrate=baudrate, timeout=1)
    except Exception as e:
        raise Exception(f"Printer connection failed: {e}")


def print_text(printer, text):
    """
    Sends text to printer
    """
    if printer:
        printer.write(text.encode('utf-8', errors='ignore'))


def print_line(printer):
    """
    Prints a separator line
    """
    print_text(printer, "-" * 32 + "\n")


def print_feed(printer, lines=3):
    """
    Feeds paper
    """
    if printer:
        printer.write(b"\n" * lines)


# ------------------------------------------------
# FORMAT FUNCTIONS
# ------------------------------------------------

def format_event(event):
    """
    Formats calendar event text
    """
    title = event.get('summary', 'Untitled Event')
    start = event['start'].get('dateTime', event['start'].get('date'))

    if 'T' in start:
        dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
        time_str = dt.strftime('%I:%M %p')
    else:
        time_str = 'All Day'

    return f"{time_str} - {title}\n"


def format_task(task, priority='Normal'):
    """
    Formats task text
    """
    title = task.get('title', 'Untitled Task')
    list_name = task.get('list_name', 'Tasks')

    marker = '!!!' if priority == 'High' else ''

    text = f"[ ] {marker} {title}\n"

    if list_name != 'My Tasks':
        text += f"    List: {list_name}\n"

    return text


# ------------------------------------------------
# PRINT FULL SCHEDULE
# ------------------------------------------------

def print_schedule(config, events, tasks, priorities):
    """
    Prints events and tasks
    """

    try:
        printer = connect_to_printer(
            config['printer_port'],
            config['printer_baudrate']
        )

        print_feed(printer)
        print_text(printer, "DAILY SCHEDULE\n")
        print_line(printer)

        today = datetime.datetime.now().strftime('%A %b %d %Y')
        print_text(printer, today + "\n")
        print_line(printer)

        print_text(printer, "\nEVENTS:\n")
        print_line(printer)

        for event in events:
            print_text(printer, format_event(event))

        print_text(printer, "\nTASKS:\n")
        print_line(printer)

        for task in tasks:
            priority = priorities.get(task.get('id', ''), 'Normal')
            print_text(printer, format_task(task, priority))

        print_feed(printer, 5)
        printer.close()

        return True, "Printed successfully"

    except Exception as e:
        return False, str(e)


# ------------------------------------------------
# GUI CLASS
# ------------------------------------------------

class CalendarPrinterGUI:
    """
    Main GUI window class
    """

    def __init__(self, root):

        self.root = root
        self.root.title("Calendar Printer")
        self.root.geometry("900x700")

        self.config = load_config()
        self.scheduler_running = False
        self.tasks_cache = []

        self.create_widgets()
        self.load_tasks()

    # ---------------- GUI LAYOUT ----------------

    def create_widgets(self):
        """
        Creates all GUI elements
        """

        ttk.Label(
            self.root,
            text="📅 Calendar Printer Control Panel",
            font=('Arial', 16, 'bold')
        ).pack(pady=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        self.create_control_tab()
        self.create_schedule_tab()
        self.create_priority_tab()
        self.create_settings_tab()

        self.status_label = ttk.Label(
            self.root,
            text="Ready",
            relief=tk.SUNKEN
        )
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

    # ---------------- CONTROL TAB ----------------

    def create_control_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Control")

        ttk.Button(
            tab,
            text="🖨️ Print Now",
            command=self.print_now_clicked
        ).pack(pady=20)

        self.log_text = scrolledtext.ScrolledText(tab, height=15)
        self.log_text.pack(fill='both', expand=True, padx=20)

    # ---------------- SCHEDULE TAB ----------------

    def create_schedule_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Schedule")

        self.schedule_list = tk.Listbox(tab, height=10)
        self.schedule_list.pack(padx=20, pady=10)

        for t in self.config['schedules']:
            self.schedule_list.insert(tk.END, t)

    # ---------------- PRIORITY TAB ----------------

    def create_priority_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Task Priority")

        self.task_tree = ttk.Treeview(tab, columns=('task', 'priority'), show='headings')
        self.task_tree.heading('task', text='Task')
        self.task_tree.heading('priority', text='Priority')
        self.task_tree.pack(fill='both', expand=True)

    # ---------------- SETTINGS TAB ----------------

    def create_settings_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Settings")

        ttk.Label(tab, text="COM Port").pack()
        self.port_entry = ttk.Entry(tab)
        self.port_entry.insert(0, self.config['printer_port'])
        self.port_entry.pack()

        ttk.Label(tab, text="Baudrate").pack()
        self.baud_entry = ttk.Entry(tab)
        self.baud_entry.insert(0, str(self.config['printer_baudrate']))
        self.baud_entry.pack()

    # ---------------- ACTIONS ----------------

    def log(self, text):
        """
        Writes message to log box
        """
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def load_tasks(self):
        """
        Loads tasks into GUI
        """
        self.tasks_cache = get_todays_tasks()

    def print_now_clicked(self):
        """
        Trigger print in background thread
        """
        threading.Thread(target=self.do_print, daemon=True).start()

    def do_print(self):
        """
        Performs printing
        """
        events = get_todays_events()
        tasks = get_todays_tasks()

        success, msg = print_schedule(
            self.config,
            events,
            tasks,
            self.config.get('task_priorities', {})
        )

        self.log(msg)


# ------------------------------------------------
# MAIN ENTRY POINT
# ------------------------------------------------

def main():
    root = tk.Tk()
    app = CalendarPrinterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
