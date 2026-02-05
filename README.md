# 📅 Calendar Thermal Printer

Automated daily schedule printer that connects to Google Calendar and Google Tasks, then prints your agenda to a Bluetooth thermal printer. Features a user-friendly GUI for scheduling, task prioritization, and printer management.

## 🧠 Why I Built This

I built this project to help manage my ADHD.

I noticed that I could focus for hours on video games, but starting simple real-world tasks was difficult.  
The issue wasn’t motivation — it was **friction and lack of immediate feedback**.

This project prints my **daily schedule and tasks** on a **thermal receipt printer**, making them:
- physical and visible
- easier to start
- satisfying to complete

The code is intentionally simple and heavily commented because this is a learning project.

## ✨ Features

- 🖨️ **Automatic Printing**: Schedule multiple print times throughout the day
- 📅 **Google Calendar Integration**: Fetches your daily events automatically
- ✅ **Google Tasks Integration**: Shows your to-do list with priorities
- 🎯 **Task Prioritization**: Set High/Normal/Low priorities for better organization
- 🖥️ **User-Friendly GUI**: Easy-to-use interface with tabs for different functions
- ⚙️ **Customizable Settings**: Configure printer port, baudrate, and schedules
- 📊 **Activity Logging**: Track all printing activities in real-time
- 🔄 **Manual Override**: Print on-demand anytime with one click

## 🎨 Interface Preview

### Control Panel
- 🖨️ One-click manual printing
- ▶️ Start/Stop automatic scheduler with live status
- 📋 Real-time activity log
- View all scheduled print times

### Schedule Manager
- ➕ Add multiple print times throughout the day
- ➖ Remove unwanted schedules
- 24-hour format (HH:MM)
- Automatic execution at specified times

### Task Priorities
- 🔴 **High Priority**: Prints first with "!!!" marker
- 🟡 **Normal Priority**: Default setting
- 🟢 **Low Priority**: Prints last
- 🔄 Refresh to sync latest tasks from Google

### Printer Settings
- Configure COM port (default: COM4)
- Adjust baudrate (9600, 19200, 38400, 115200)
- 🧪 Test printer connection
- Save settings permanently

## 🚀 Getting Started

### Prerequisites

- **Operating System**: Windows 10/11
- **Python**: 3.7 or higher
- **Hardware**: Bluetooth thermal printer (ESC/POS compatible)
- **Google Account**: With Calendar and Tasks enabled

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/calendar-thermal-printer.git
   cd calendar-thermal-printer
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Calendar & Tasks API**
   
   a. Go to [Google Cloud Console](https://console.cloud.google.com/)
   
   b. Create a new project (e.g., "Calendar Printer")
   
   c. Enable APIs:
      - Google Calendar API
      - Google Tasks API
   
   d. Create credentials:
      - Go to "Credentials" → "+ CREATE CREDENTIALS" → "OAuth client ID"
      - Click "Configure Consent Screen"
      - Choose "External" → Fill in app name and your email
      - Back to Credentials → Create "OAuth client ID"
      - Application type: "Desktop app"
      - Download JSON file
   
   e. Rename downloaded file to `credentials.json` and place it in the project folder

4. **Connect your thermal printer**
   - Pair Bluetooth printer with Windows
   - Note the COM port in Device Manager (Ports → COM & LPT)

### Usage

**Run the GUI application:**
```bash
python Project_Thermal_Printer_ADHD_UITASK.py
```

Or open the file in PyCharm and press `Shift + F10`

### First-Time Setup

1. **Authentication**:
   - Browser will open automatically
   - Sign in to your Google account
   - Approve Calendar and Tasks permissions
   - Close browser when it says "authentication flow completed"

2. **Configure Printer** (Settings Tab):
   - Set correct COM port (check Device Manager)
   - Select appropriate baudrate (try 9600 first)
   - Click "Test Printer Connection" to verify

3. **Set Schedules** (Schedule Tab):
   - Add times when you want automatic printing
   - Example: `08:00`, `12:00`, `18:00`
   - Times are in 24-hour format

4. **Prioritize Tasks** (Task Priorities Tab):
   - Click "Refresh Tasks" to load from Google
   - Select tasks and assign priorities
   - High priority tasks will print first

5. **Start Scheduler** (Control Panel):
   - Click "▶️ Start Scheduler"
   - Verify status shows "Running ✓"
   - Watch activity log for confirmations

## 📁 Project Structure

```
PythonProject6/
├── .venv/                                          # Virtual environment (not tracked)
├── credentials.json                                # Google API credentials (not tracked)
├── token.json                                      # OAuth token (not tracked)
├── printer_config.json                             # User settings (not tracked)
├── Project_Thermal_Printer_ADHD.py                # Basic calendar printer
├── Project_Thermal_Printer_ADHD_MIXTASK+CAL.py    # Calendar + Tasks version
├── Project_Thermal_Printer_ADHD_UITASK.py         # Full GUI application ⭐
├── .gitignore                                      # Git ignore rules
├── LICENSE                                         # MIT License
├── README.md                                       # This file
└── requirements.txt                                # Python dependencies
```

### File Descriptions

- **Project_Thermal_Printer_ADHD_UITASK.py**: Main GUI application with full features (recommended)
- **Project_Thermal_Printer_ADHD_MIXTASK+CAL.py**: Command-line version with Calendar + Tasks
- **Project_Thermal_Printer_ADHD.py**: Basic command-line calendar printer

## ⚙️ Configuration

### Default Settings

| Setting | Default Value | Description |
|---------|--------------|-------------|
| Printer Port | COM4 | Bluetooth printer COM port |
| Baudrate | 9600 | Communication speed |
| Schedules | 08:00, 12:00, 18:00 | Default print times |

### Modifying Settings

All settings can be changed through the GUI without editing code:
- Printer settings → Settings Tab
- Schedules → Schedule Tab  
- Task priorities → Task Priorities Tab

Configuration is saved automatically in `printer_config.json`

## 🛠️ Troubleshooting

### ❌ Printer Won't Connect

**Problem**: "Could not connect to printer on COM4"

**Solutions**:
1. Verify Bluetooth pairing in Windows Settings → Bluetooth & devices
2. Open Device Manager → Ports (COM & LPT) → Check actual COM port
3. Update COM port in Settings tab
4. Try different baudrates: 19200, 38400, or 115200
5. Ensure printer is powered on and within range

### ❌ Google API Errors

**Problem**: "insufficient authentication scopes" or "Request had insufficient authentication"

**Solutions**:
1. Delete `token.json` file from project folder
2. Run the program again
3. Re-authenticate when browser opens
4. Make sure to approve BOTH Calendar and Tasks permissions

**Problem**: "credentials.json not found"

**Solutions**:
1. Verify `credentials.json` is in the same folder as the .py file
2. Download it again from Google Cloud Console if missing
3. Make sure it's named exactly `credentials.json` (not `client_secret_...json`)

### ❌ Scheduler Not Working

**Problem**: Scheduler shows "Running" but nothing prints

**Solutions**:
1. Check Activity Log for errors
2. Verify at least one schedule time is added
3. Make sure current time hasn't passed all scheduled times
4. Try adding a time 2-3 minutes from now to test
5. Check printer connection with "Test Printer" button

### ❌ No Tasks Showing

**Problem**: "Found 0 task list(s)" or no tasks displayed

**Solutions**:
1. Verify Google Tasks API is enabled in Google Cloud Console
2. Check you have tasks in Google Tasks (tasks.google.com)
3. Delete `token.json` and re-authenticate
4. Click "Refresh Tasks" button in Task Priorities tab

## 🔐 Security & Privacy

### Protected Files (Never Commit to Git)

These files contain sensitive information and are automatically excluded:
- ✅ `credentials.json` - Your Google API credentials
- ✅ `token.json` - Your OAuth access token  
- ✅ `printer_config.json` - May contain personal settings
- ✅ `.venv/` - Virtual environment folder

The `.gitignore` file ensures these are never uploaded to GitHub.

## 🎯 Use Cases

This project is perfect for:
- 📅 **ADHD Management**: Visual daily schedules help with time blindness
- 🏢 **Office Workers**: Morning briefings of meetings and tasks
- 👨‍💼 **Freelancers**: Print daily client calls and deliverables
- 👨‍🎓 **Students**: Automatic class schedules and assignment reminders
- 🏠 **Home Organization**: Family calendar on the fridge

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Ideas for Contributions

- Add support for multiple calendars
- Weather information on printouts
- Email notifications integration
- Mobile app companion
- Web interface
- Support for different printer brands
- Multi-language support

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google APIs**: Calendar and Tasks integration
- **PySerial**: Thermal printer communication
- **Schedule**: Python job scheduling
- **Tkinter**: Cross-platform GUI framework
- **Python Community**: For excellent libraries and documentation

## 📧 Support

Having issues? Here's how to get help:

1. **Check Troubleshooting section** above
2. **Search existing issues** on GitHub
3. **Open a new issue** with:
   - Your Python version (`python --version`)
   - Error messages (copy from Activity Log)
   - Steps to reproduce the problem
   - Screenshots if relevant

## 🔮 Future Features

Ideas for future versions:
- [ ] Mobile companion app
- [ ] Web dashboard
- [ ] Multiple printer support
- [ ] Custom print templates
- [ ] Recurring task patterns
- [ ] Weather forecast integration
- [ ] Meeting preparation reminders
- [ ] Task completion tracking

## 💖 Support the Project

If you find this project helpful:
- ⭐ Star the repository
- 🐛 Report bugs
- 💡 Suggest features
- 🤝 Contribute code
- 📢 Share with others who might benefit

---

**Made with ❤️ for better daily organization**

*Print your schedule, not your stress!* 🖨️✨
