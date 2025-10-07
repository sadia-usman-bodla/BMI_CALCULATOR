# Advanced BMI Calculator (Python GUI)

## Overview

This project is an **Advanced BMI Calculator** with a graphical user interface (GUI) built using **Tkinter**. It allows users to calculate their Body Mass Index (BMI), store multiple entries, view historical data, and analyze BMI trends through interactive graphs.

## Features

* **User Input:** Enter Name, Weight (kg), and Height (m).
* **Input Validation:** Ensures valid and reasonable input ranges.
* **BMI Calculation:** Computes BMI using the standard formula.
* **BMI Categories:** Classifies BMI as Underweight, Normal, Overweight, or Obese.
* **Data Storage:** Saves entries in a **SQLite database** with timestamp.
* **History Viewing:** Displays previous entries in a listbox; select an entry to view details.
* **Trend Visualization:** Plots historical BMI trends using **Matplotlib**.
* **Export Data:** Export history to CSV.
* **Error Handling:** Gracefully handles invalid inputs and database errors.
* **User-Friendly GUI:** Intuitive layout with clear instructions and feedback.

## Requirements

* Python 3.x
* Tkinter (usually included with Python)
* Matplotlib (`pip install matplotlib`)
* SQLite (comes with Python standard library)

## How to Run

1. Install Matplotlib if not installed:

```bash
pip install matplotlib
```

2. Run the script:

```bash
python bmi_gui.py
```

3. The GUI window will open:

   * Enter Name, Weight (kg), and Height (m).
   * Click **Calculate & Save** to compute BMI and save the entry.
   * View history in the listbox.
   * Select an entry to see details and plot the BMI trend.

## Usage

* **Calculate BMI:** Fill in the fields and click the button.
* **Clear Fields:** Click **Clear Fields** to reset input.
* **View History:** All saved entries appear in the history list.
* **Plot Trend:** Select a user entry and click **Plot Selected User** to see BMI trend.
* **Export CSV:** Click **Export CSV** to save history data.

## BMI Categories

| BMI       | Category      |
| --------- | ------------- |
| < 18.5    | Underweight   |
| 18.5–24.9 | Normal weight |
| 25–29.9   | Overweight    |
| >= 30     | Obese         |

## File Structure

* `bmi_gui.py` — main Python script with GUI and database functionality.
* `bmi_history.db` — SQLite database file (auto-generated).

## Notes

* Ensure proper input ranges: Weight (0–500 kg), Height (0–3 meters).
* The trend graph requires Matplotlib.
* All data is stored locally using SQLite.

## Author

Developed for educational purposes and advanced beginner Python projects.
