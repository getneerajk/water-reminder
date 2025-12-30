# Water Reminder Manager

A simple Linux desktop application with a graphical interface to create, list, and delete scheduled desktop notification reminders using **cron**. It is designed to be lightweight, reliable, and desktop-environment friendly.

This application was primarily built and tested on **Ubuntu Budgie**, but it works on most GTK-based Linux desktops.

---

## Features

* Graphical interface to create reminders
* Set start time, end time, interval, days, and message text
* Uses a single cron line per reminder (clean cron usage)
* Lists all reminders created by the app
* Delete reminders safely without affecting other cron jobs
* Uses native desktop notifications (`notify-send`)
* No background daemon or service
* Reminders persist across reboot and logout

---

## How It Works

Each reminder is stored in the **user crontab** as a small block:

```
# WATER_REMINDER_APP | id=xxxxxx
<single cron line>
```

The application only manages cron entries with this tag and does not modify any other scheduled jobs.

---

## System Requirements

* Linux (Ubuntu / Debian-based recommended)
* Python 3.8 or newer
* GTK 3
* User cron (`crontab`)
* libnotify

Supported desktop environments:

* Budgie
* GNOME
* XFCE
* Cinnamon
* MATE

---

## Dependencies

Install required packages:

```bash
sudo apt install python3 python3-gi gir1.2-gtk-3.0 libnotify-bin cron
```

---

## Running the Application

1. Clone the repository:

```bash
git clone <repository-url>
cd <repository-folder>
```

2. Run the application:

```bash
python3 water_reminder_manager.py
```

No root access is required.

---

## Using the Application

### Adding a Reminder

1. Enter the notification message
2. Set start time and end time
3. Choose the interval (in minutes)
4. Set days using cron format (example: `1-5` for Monday to Friday)
5. Click **Add Reminder**

The reminder will be added to your user crontab.

### Listing Reminders

All reminders created by the app are listed in the table below the form.

### Deleting a Reminder

1. Select a reminder from the list
2. Click **Delete Selected**

This removes both the cron entry and its tag.

---

## Cron Day Format Examples

* `1-5` → Monday to Friday
* `0,6` → Sunday and Saturday
* `*` → Every day

---

## Notifications

The application uses `notify-send`, which integrates with the system notification daemon. Notifications appear as native desktop notifications.

---

## Security and Privacy

* Runs entirely as the current user
* Only modifies the user crontab
* No system-wide changes
* No network access
* No data collection

---

## Limitations

* Requires a desktop session (not suitable for headless servers)
* Depends on cron availability
* Does not currently support editing existing reminders

---

## Possible Future Improvements

* Edit existing reminders
* System tray integration
* Preset schedules
* Sound notifications
* Packaging as .deb or AppImage

---

## License

MIT License

---

## Author

Created for personal and lightweight reminder management on Linux deskto
