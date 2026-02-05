"""
Simple Google Calendar Printer
--------------------------------
This script connects to my Google Calendar
and prints today's events on a thermal printer.

I wrote this while learning Python 😅
So comments are very detailed and simple.
"""

import os
import datetime
import serial

# Google API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# ============================================================
# BASIC SETTINGS (CHANGE THESE IF NEEDED)
# ============================================================

# Bluetooth COM port of my thermal printer
PRINTER_PORT = "COM4"

# Baudrate of printer (some printers use 19200 or 115200)
PRINTER_BAUDRATE = 9600

# Google Calendar read-only permission
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


# ============================================================
# GOOGLE CALENDAR LOGIN PART
# ============================================================

def google_login():
    """
    This function logs into Google Calendar.

    First run:
    - Opens browser
    - Asks Google login
    - Creates token.json

    Next runs:
    - Uses token.json automatically
    """
    creds = None

    # Check if token file already exists
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If token not valid, login again
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing Google login...")
            creds.refresh(Request())
        else:
            print("Opening browser for Google login...")
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token so we don't login every time
        with open("token.json", "w") as token:
            token.write(creds.to_json())

        print("Google login successful!")

    return creds


# ============================================================
# GET TODAY'S CALENDAR EVENTS
# ============================================================

def get_today_events():
    """
    Gets all today's events from Google Calendar
    """
    creds = google_login()

    service = build("calendar", "v3", credentials=creds)

    now = datetime.datetime.now()

    # Start and end of today
    start_day = datetime.datetime.combine(now.date(), datetime.time.min)
    end_day = datetime.datetime.combine(now.date(), datetime.time.max)

    # Google needs ISO format
    time_min = start_day.isoformat() + "Z"
    time_max = end_day.isoformat() + "Z"

    print("Fetching today's events...")

    events_result = service.events().list(
        calendarId="primary",
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])

    print(f"Found {len(events)} event(s)")
    return events


# ============================================================
# PRINTER CONNECTION
# ============================================================

def connect_printer():
    """
    Connects to thermal printer using serial
    """
    try:
        print("Connecting to printer...")
        printer = serial.Serial(
            port=PRINTER_PORT,
            baudrate=PRINTER_BAUDRATE,
            timeout=1
        )
        print("Printer connected!")
        return printer

    except Exception as e:
        print("Printer connection failed 😢")
        print(e)
        return None


def printer_write(printer, text):
    """
    Sends text to printer
    """
    if printer:
        printer.write(text.encode("utf-8"))


def printer_line(printer):
    """
    Prints a separator line
    """
    printer_write(printer, "-" * 32 + "\n")


def printer_feed(printer, lines=3):
    """
    Feeds paper
    """
    if printer:
        printer.write(b"\n" * lines)


# ============================================================
# FORMAT EVENTS FOR PRINTING
# ============================================================

def format_event(event):
    """
    Converts event into printable text
    """
    title = event.get("summary", "No Title")

    start = event["start"].get("dateTime", event["start"].get("date"))

    # If event has time
    if "T" in start:
        dt = datetime.datetime.fromisoformat(start.replace("Z", "+00:00"))
        time_str = dt.strftime("%I:%M %p")
    else:
        time_str = "ALL DAY"

    text = f"{time_str} - {title}\n"
    return text


# ============================================================
# PRINT FULL DAY
# ============================================================

def print_schedule(printer, events):
    """
    Prints everything nicely
    """
    printer_feed(printer, 1)
    printer_write(printer, "DAILY SCHEDULE\n")
    printer_line(printer)

    today = datetime.datetime.now().strftime("%A %d %B %Y")
    printer_write(printer, today + "\n")
    printer_line(printer)

    if events:
        for i, event in enumerate(events, 1):
            printer_write(printer, f"{i}. ")
            printer_write(printer, format_event(event))
    else:
        printer_write(printer, "No events today 🎉\n")

    printer_line(printer)
    printer_write(printer, f"Total events: {len(events)}\n")
    printer_feed(printer, 5)

    print("Printed successfully!")


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():
    print("\n--- Calendar Printer Started ---\n")

    events = get_today_events()
    printer = connect_printer()

    if printer:
        print_schedule(printer, events)
        printer.close()
        print("Printer closed.")
    else:
        print("\nPrinter not connected. Showing events here:\n")
        for e in events:
            print(format_event(e))

    print("\n--- Program Finished ---\n")


# Run program
if __name__ == "__main__":
    main()
