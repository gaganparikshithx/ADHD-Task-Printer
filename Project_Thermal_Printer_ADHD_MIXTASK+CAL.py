"""
Calendar Printer (Beginner Project)

This script prints:
- Today's Google Calendar events
- Today's Google Tasks
to a Bluetooth thermal printer.

I wrote this while learning Python, Google APIs, and serial printers.
So comments are very detailed and simple.
"""

# -------------------------
# Import required modules
# -------------------------

import os                     # Used to check if files exist
import datetime               # Used to work with dates and time
import serial                 # Used to talk to thermal printer

# Google authentication imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# ============================================================
# CONFIGURATION SECTION (change if needed)
# ============================================================

# Bluetooth COM port of thermal printer
PRINTER_PORT = 'COM4'

# Printer speed (most printers use 9600)
PRINTER_BAUDRATE = 9600

# Google permissions needed
# Calendar = events
# Tasks = to-do list
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/tasks.readonly'
]


# ============================================================
# GOOGLE LOGIN FUNCTION
# ============================================================

def authenticate_google():
    """
    This function logs into Google (Calendar + Tasks).

    First time:
    - Browser opens
    - You login
    - token.json is created

    Next time:
    - token.json is reused
    """

    creds = None  # Start with empty credentials

    # Check if token file already exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If no credentials or invalid credentials
    if not creds or not creds.valid:

        # If token expired but refresh token exists
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing Google access token...")
            creds.refresh(Request())

        # First time login
        else:
            print("Opening browser for Google login...")
            print("Please approve BOTH Calendar and Tasks access")

            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                SCOPES
            )

            # Start local server for login
            creds = flow.run_local_server(port=0)

        # Save token for next time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

        print("Login successful. Token saved.")

    return creds


# ============================================================
# GET TODAY'S CALENDAR EVENTS
# ============================================================

def get_todays_events():
    """
    Fetches today's Google Calendar events
    """

    print("Connecting to Google Calendar...")
    creds = authenticate_google()

    # Create calendar service
    service = build('calendar', 'v3', credentials=creds)

    # Get current date and time
    now = datetime.datetime.now()

    # Start of today (00:00)
    start_of_day = datetime.datetime.combine(
        now.date(),
        datetime.time.min
    )

    # End of today (23:59)
    end_of_day = datetime.datetime.combine(
        now.date(),
        datetime.time.max
    )

    # Convert time to Google format
    time_min = start_of_day.isoformat() + 'Z'
    time_max = end_of_day.isoformat() + 'Z'

    # Fetch events from Google Calendar
    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    # Extract events list
    events = events_result.get('items', [])

    print(f"Found {len(events)} calendar event(s)")
    return events


# ============================================================
# GET TODAY'S GOOGLE TASKS
# ============================================================

def get_todays_tasks():
    """
    Fetches all incomplete Google Tasks
    """

    print("Connecting to Google Tasks...")
    creds = authenticate_google()

    # Create tasks service
    service = build('tasks', 'v1', credentials=creds)

    all_tasks = []  # List to store all tasks

    try:
        # Get all task lists
        task_lists = service.tasklists().list().execute()
        lists = task_lists.get('items', [])

        print(f"Found {len(lists)} task list(s)")

        # Loop through each task list
        for task_list in lists:

            list_name = task_list['title']
            list_id = task_list['id']

            # Get tasks from list
            tasks_result = service.tasks().list(
                tasklist=list_id,
                showCompleted=False,
                showHidden=False
            ).execute()

            tasks = tasks_result.get('items', [])

            # Add list name to each task
            for task in tasks:
                task['list_name'] = list_name
                all_tasks.append(task)

        print(f"Found {len(all_tasks)} incomplete task(s)")

    except Exception as e:
        print("Error while fetching tasks")
        print(e)

    return all_tasks


# ============================================================
# PRINTER FUNCTIONS
# ============================================================

def connect_to_printer():
    """
    Connects to Bluetooth thermal printer
    """

    try:
        print(f"Connecting to printer on {PRINTER_PORT}...")

        printer = serial.Serial(
            port=PRINTER_PORT,
            baudrate=PRINTER_BAUDRATE,
            timeout=1
        )

        print("Printer connected successfully!")
        return printer

    except Exception as e:
        print("Printer connection failed")
        print(e)
        return None


def print_text(printer, text):
    """
    Sends text to printer
    """
    if printer:
        printer.write(text.encode('utf-8'))


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


# ============================================================
# FORMAT FUNCTIONS
# ============================================================

def format_event(event):
    """
    Converts calendar event to printable text
    """

    title = event.get('summary', 'No Title')

    start = event['start'].get(
        'dateTime',
        event['start'].get('date')
    )

    if 'T' in start:
        dt = datetime.datetime.fromisoformat(
            start.replace('Z', '+00:00')
        )
        time_str = dt.strftime('%I:%M %p')
    else:
        time_str = 'ALL DAY'

    return f"{time_str} - {title}\n"


def format_task(task):
    """
    Converts task to printable text
    """

    title = task.get('title', 'Untitled Task')
    list_name = task.get('list_name', 'Tasks')

    output = f"[ ] {title}\n"

    if list_name != 'My Tasks':
        output += f"    List: {list_name}\n"

    return output


# ============================================================
# PRINT DAILY SCHEDULE
# ============================================================

def print_daily_schedule(printer, events, tasks):
    """
    Prints events and tasks
    """

    if not printer:
        print("Printer not connected")
        return

    # Header
    print_feed(printer, 1)
    print_text(printer, "DAILY SCHEDULE\n")
    print_line(printer)

    today = datetime.datetime.now().strftime('%A %d %B %Y')
    print_text(printer, today + "\n")
    print_line(printer)

    # Events section
    print_text(printer, "\nCALENDAR EVENTS:\n")
    print_line(printer)

    if events:
        for i, event in enumerate(events, 1):
            print_text(printer, f"{i}. {format_event(event)}")
    else:
        print_text(printer, "No events today\n")

    # Tasks section
    print_text(printer, "\nTODAY'S TASKS:\n")
    print_line(printer)

    if tasks:
        for i, task in enumerate(tasks, 1):
            print_text(printer, f"{i}. {format_task(task)}")
    else:
        print_text(printer, "No pending tasks 🎉\n")

    # Footer
    print_line(printer)
    print_text(
        printer,
        f"Events: {len(events)} | Tasks: {len(tasks)}\n"
    )
    print_feed(printer, 5)

    print("Printed successfully!")


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():
    """
    Main program entry point
    """

    print("\nStarting Calendar Printer...\n")

    try:
        events = get_todays_events()
        tasks = get_todays_tasks()

        printer = connect_to_printer()

        if printer:
            print_daily_schedule(printer, events, tasks)
            printer.close()
            print("Printer closed")
        else:
            print("Printer not available")

    except Exception as e:
        print("Something went wrong")
        print(e)

    print("\nProgram finished\n")


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()
