"""
Graphical BMI Calculator with history, storage, and trend graphs
- Tkinter GUI
- sqlite3 local database for storing entries
- matplotlib for plotting BMI trends

Features:
- Input: user name, weight (kg), height (m)
- Validation of inputs
- Compute BMI and category
- Save entries to SQLite with timestamp
- View history in a listbox (select to see details)
- Plot BMI trend for selected user
- Export history to CSV

Run: python bmi_gui.py
Requires: Python 3.x, matplotlib
Install matplotlib: pip install matplotlib
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import csv
import math

# Matplotlib embedding
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

DB_NAME = "bmi_history.db"

# ----------------------- Database helpers -----------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY,
            name TEXT,
            weight REAL,
            height REAL,
            bmi REAL,
            category TEXT,
            timestamp TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_entry(name, weight, height, bmi, category):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    ts = datetime.now().isoformat(sep=' ', timespec='seconds')
    c.execute(
        "INSERT INTO entries (name, weight, height, bmi, category, timestamp) VALUES (?,?,?,?,?,?)",
        (name, weight, height, bmi, category, ts)
    )
    conn.commit()
    conn.close()


def get_all_entries():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, weight, height, bmi, category, timestamp FROM entries ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def get_entries_for_user(name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, weight, height, bmi, category, timestamp FROM entries WHERE name=? ORDER BY timestamp", (name,))
    rows = c.fetchall()
    conn.close()
    return rows

# ----------------------- BMI logic -----------------------

def calculate_bmi_value(weight, height):
    # weight: kg, height: meters
    if height <= 0:
        raise ValueError("Height must be positive")
    bmi = weight / (height ** 2)
    return bmi


def bmi_category(bmi):
    # WHO standard categories
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal weight"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"

# ----------------------- GUI -----------------------

class BMIGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMI Calculator — Advanced GUI")
        self.geometry("900x600")
        self.resizable(False, False)

        # Main frames
        input_frame = ttk.LabelFrame(self, text="Enter Data")
        input_frame.place(x=10, y=10, width=380, height=220)

        result_frame = ttk.LabelFrame(self, text="Result")
        result_frame.place(x=10, y=240, width=380, height=150)

        history_frame = ttk.LabelFrame(self, text="History")
        history_frame.place(x=400, y=10, width=480, height=380)

        plot_frame = ttk.LabelFrame(self, text="Trend / Plot")
        plot_frame.place(x=10, y=400, width=870, height=190)

        # Input fields
        ttk.Label(input_frame, text="Name:").place(x=10, y=12)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(input_frame, textvariable=self.name_var)
        self.name_entry.place(x=100, y=12, width=240)

        ttk.Label(input_frame, text="Weight (kg):").place(x=10, y=52)
        self.weight_var = tk.StringVar()
        self.weight_entry = ttk.Entry(input_frame, textvariable=self.weight_var)
        self.weight_entry.place(x=100, y=52, width=120)

        ttk.Label(input_frame, text="Height (m):").place(x=10, y=92)
        self.height_var = tk.StringVar()
        self.height_entry = ttk.Entry(input_frame, textvariable=self.height_var)
        self.height_entry.place(x=100, y=92, width=120)

        # Buttons
        calc_btn = ttk.Button(input_frame, text="Calculate & Save", command=self.on_calculate)
        calc_btn.place(x=10, y=140, width=160)

        clear_btn = ttk.Button(input_frame, text="Clear Fields", command=self.clear_fields)
        clear_btn.place(x=200, y=140, width=140)

        # Result labels
        self.result_bmi = tk.StringVar(value="BMI: —")
        self.result_cat = tk.StringVar(value="Category: —")
        ttk.Label(result_frame, textvariable=self.result_bmi, font=(None, 14)).place(x=10, y=10)
        ttk.Label(result_frame, textvariable=self.result_cat, font=(None, 14)).place(x=10, y=50)

        # History listbox + scrollbar
        self.history_list = tk.Listbox(history_frame)
        self.history_list.place(x=10, y=10, width=440, height=300)
        self.history_list.bind('<<ListboxSelect>>', self.on_history_select)

        sb = ttk.Scrollbar(history_frame, orient='vertical', command=self.history_list.yview)
        sb.place(x=452, y=10, height=300)
        self.history_list.configure(yscrollcommand=sb.set)

        # History buttons
        refresh_btn = ttk.Button(history_frame, text="Refresh History", command=self.load_history)
        refresh_btn.place(x=10, y=320, width=120)

        export_btn = ttk.Button(history_frame, text="Export CSV", command=self.export_csv)
        export_btn.place(x=150, y=320, width=120)

        plot_btn = ttk.Button(history_frame, text="Plot Selected User", command=self.plot_selected_user)
        plot_btn.place(x=290, y=320, width=160)

        # Matplotlib figure
        self.fig = Figure(figsize=(8.2, 2.7), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title('BMI Trend')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('BMI')
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initialize
        self.load_history()

    # ---------------- GUI methods ----------------
    def validate_inputs(self):
        name = self.name_var.get().strip()
        if not name:
            raise ValueError("Name cannot be empty")
        try:
            weight = float(self.weight_var.get())
            height = float(self.height_var.get())
        except ValueError:
            raise ValueError("Weight and height must be numbers")
        if weight <= 0 or weight > 500:
            raise ValueError("Weight must be between 0 and 500 kg")
        if height <= 0 or height > 3:
            raise ValueError("Height must be between 0 and 3 meters")
        return name, weight, height

    def on_calculate(self):
        try:
            name, weight, height = self.validate_inputs()
            bmi = calculate_bmi_value(weight, height)
            # Round BMI sensibly
            bmi_rounded = round(bmi, 2)
            cat = bmi_category(bmi)
            # Save
            save_entry(name, weight, height, bmi_rounded, cat)
            self.result_bmi.set(f"BMI: {bmi_rounded}")
            self.result_cat.set(f"Category: {cat}")
            messagebox.showinfo("Saved", f"Entry saved for {name} (BMI: {bmi_rounded})")
            self.load_history()
        except Exception as e:
            messagebox.showerror("Input error", str(e))

    def clear_fields(self):
        self.name_var.set("")
        self.weight_var.set("")
        self.height_var.set("")
        self.result_bmi.set("BMI: —")
        self.result_cat.set("Category: —")

    def load_history(self):
        self.history_list.delete(0, tk.END)
        rows = get_all_entries()
        for r in rows:
            # Display: [timestamp] name — BMI
            display = f"[{r[6]}] {r[1]} — BMI: {r[4]} ({r[5]})"
            self.history_list.insert(tk.END, display)
        # Keep rows in memory for selection mapping
        self._history_rows = rows

    def on_history_select(self, event):
        sel = event.widget.curselection()
        if not sel:
            return
        idx = sel[0]
        row = self._history_rows[idx]
        # Populate fields with selected
        self.name_var.set(row[1])
        self.weight_var.set(str(row[2]))
        self.height_var.set(str(row[3]))
        self.result_bmi.set(f"BMI: {row[4]}")
        self.result_cat.set(f"Category: {row[5]}")

    def export_csv(self):
        rows = get_all_entries()
        if not rows:
            messagebox.showinfo("No data", "No history to export")
            return
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files','*.csv')])
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id','name','weight','height','bmi','category','timestamp'])
                writer.writerows(rows)
            messagebox.showinfo("Exported", f"Exported history to {path}")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

    def plot_selected_user(self):
        sel = self.history_list.curselection()
        if not sel:
            messagebox.showinfo("Choose user", "Select an entry in history (any entry of the user) to plot that user's trend")
            return
        idx = sel[0]
        row = self._history_rows[idx]
        name = row[1]
        entries = get_entries_for_user(name)
        if not entries:
            messagebox.showinfo("No data", f"No entries found for {name}")
            return
        # Extract timestamps and bmi
        times = [datetime.fromisoformat(r[6]) for r in entries]
        bmis = [r[4] for r in entries]

        # Clear and plot
        self.ax.clear()
        self.ax.plot(times, bmis, marker='o')
        self.ax.set_title(f'BMI Trend — {name}')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('BMI')
        self.ax.grid(True)
        self.fig.autofmt_xdate()
        self.canvas.draw()


if __name__ == '__main__':
    init_db()
    app = BMIGUI()
    app.mainloop()
