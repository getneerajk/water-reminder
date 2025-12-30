#!/usr/bin/env python3

import gi
import subprocess
import uuid

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

CRON_TAG = "WATER_REMINDER_APP"


class WaterReminderManager(Gtk.Window):
    def __init__(self):
        super().__init__(title="Water Reminder Manager")
        self.set_border_width(12)
        self.set_default_size(560, 420)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        # ===== FORM =====
        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        vbox.pack_start(grid, False, False, 0)

        # Message
        grid.attach(Gtk.Label(label="Message"), 0, 0, 1, 1)
        self.message = Gtk.Entry(text="Drink water 💧")
        grid.attach(self.message, 1, 0, 3, 1)

        # Start time
        grid.attach(Gtk.Label(label="Start Time"), 0, 1, 1, 1)
        self.start_h = Gtk.SpinButton(adjustment=Gtk.Adjustment(10, 0, 23, 1))
        self.start_m = Gtk.SpinButton(adjustment=Gtk.Adjustment(0, 0, 59, 1))
        grid.attach(self.start_h, 1, 1, 1, 1)
        grid.attach(self.start_m, 2, 1, 1, 1)

        # End time
        grid.attach(Gtk.Label(label="End Time"), 0, 2, 1, 1)
        self.end_h = Gtk.SpinButton(adjustment=Gtk.Adjustment(19, 0, 23, 1))
        self.end_m = Gtk.SpinButton(adjustment=Gtk.Adjustment(0, 0, 59, 1))
        grid.attach(self.end_h, 1, 2, 1, 1)
        grid.attach(self.end_m, 2, 2, 1, 1)

        # Interval
        grid.attach(Gtk.Label(label="Interval (minutes)"), 0, 3, 1, 1)
        self.interval = Gtk.ComboBoxText()
        for i in ("30", "45", "60"):
            self.interval.append_text(i)
        self.interval.set_active(0)
        grid.attach(self.interval, 1, 3, 2, 1)

        # Days
        grid.attach(Gtk.Label(label="Days (cron format)"), 0, 4, 1, 1)
        self.days = Gtk.Entry(text="1-5")  # Mon–Fri
        grid.attach(self.days, 1, 4, 2, 1)

        # Add button
        add_btn = Gtk.Button(label="Add Reminder")
        add_btn.connect("clicked", self.add_reminder)
        grid.attach(add_btn, 1, 5, 2, 1)

        # ===== LIST =====
        self.store = Gtk.ListStore(str, str)
        self.tree = Gtk.TreeView(model=self.store)

        for i, title in enumerate(["ID", "Cron Schedule"]):
            col = Gtk.TreeViewColumn(title, Gtk.CellRendererText(), text=i)
            col.set_resizable(True)
            self.tree.append_column(col)

        scroller = Gtk.ScrolledWindow()
        scroller.set_vexpand(True)
        scroller.add(self.tree)
        vbox.pack_start(scroller, True, True, 0)

        # ===== ACTIONS =====
        hbox = Gtk.Box(spacing=10)
        vbox.pack_start(hbox, False, False, 0)

        del_btn = Gtk.Button(label="Delete Selected")
        del_btn.connect("clicked", self.delete_selected)

        refresh_btn = Gtk.Button(label="Refresh")
        refresh_btn.connect("clicked", lambda *_: self.load_reminders())

        hbox.pack_start(del_btn, False, False, 0)
        hbox.pack_start(refresh_btn, False, False, 0)

        self.load_reminders()

    # ===== CRON HELPERS =====
    def get_cron(self):
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else ""

    def save_cron(self, text):
        subprocess.run(["crontab"], input=text.strip() + "\n", text=True)

    # ===== FEATURES =====
    def add_reminder(self, _):
        uid = subprocess.check_output(["id", "-u"]).decode().strip()
        rid = uuid.uuid4().hex[:6]

        sh, sm = self.start_h.get_value_as_int(), self.start_m.get_value_as_int()
        eh, em = self.end_h.get_value_as_int(), self.end_m.get_value_as_int()
        interval = int(self.interval.get_active_text())
        days = self.days.get_text().strip()
        msg = self.message.get_text().strip()

        # Minute field
        if interval == 30 and sm == 0:
            minute = "0,30"
        else:
            minute = f"{sm}-59/{interval}"

        hour = f"{sh}-{eh}"

        cron_line = (
            f"{minute} {hour} * * {days} "
            f"DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus "
            f'notify-send "{msg}"'
        )

        cron = self.get_cron()
        block = (
            f"\n# {CRON_TAG} | id={rid}\n"
            f"{cron_line}\n"
        )

        self.save_cron(cron + block)
        self.load_reminders()

    def load_reminders(self):
        self.store.clear()
        lines = self.get_cron().splitlines()

        for i, line in enumerate(lines):
            if line.startswith(f"# {CRON_TAG}") and i + 1 < len(lines):
                rid = line.split("id=")[1]
                self.store.append([rid, lines[i + 1]])

    def delete_selected(self, _):
        model, itr = self.tree.get_selection().get_selected()
        if not itr:
            return

        rid = model[itr][0]
        lines = self.get_cron().splitlines()
        new_lines = []
        skip_next = False

        for line in lines:
            if skip_next:
                skip_next = False
                continue

            if line.startswith(f"# {CRON_TAG}") and f"id={rid}" in line:
                skip_next = True
                continue

            new_lines.append(line)

        self.save_cron("\n".join(new_lines))
        self.load_reminders()


if __name__ == "__main__":
    win = WaterReminderManager()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
