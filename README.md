# 🧬 AutoDock Vina Log Parser

[Live Demo](https://vinalog.streamlit.app/)

---

## Overview

This web app allows users to upload and parse **AutoDock Vina** `.log` files to extract the **best docking conformation (Mode 1)** affinity and RMSD values quickly and easily. It supports uploading:

- One or multiple `.log` files directly
- A `.zip` archive containing multiple `.log` files

The app extracts key docking metrics from each log file and presents the results in an interactive table, with an option to download all parsed results as a CSV file.

---

## Features

- **Multi-file upload:** Select and upload multiple `.log` files at once.
- **ZIP upload:** Upload a zipped folder containing multiple `.log` files.
- **Automatic parsing:** Extracts Mode 1 affinity and RMSD values from each log.
- **Results summary:** Displays parsed data in a sortable and searchable table.
- **CSV export:** Download all parsed results as a CSV file for offline use.
- **Side-by-side uploader:** Easy UI with separate panes for `.log` and `.zip` uploads.

---

## Usage

1. Navigate to the [AutoDock Vina Log Parser](https://vinalog.streamlit.app/) app.
2. Upload your docking log files:
   - Drag and drop or browse to select multiple `.log` files in the left pane, **or**
   - Upload a `.zip` file containing `.log` files in the right pane.
3. Wait a moment while the app parses your files.
4. View the extracted Mode 1 results (affinity, RMSD lower and upper bounds) in the table.
5. Download the results as a CSV file using the "Download CSV" button.

---

##Contact
Created by Vijay Suryakant Kapse

Feedback and contributions are welcome!
