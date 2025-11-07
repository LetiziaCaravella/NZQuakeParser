# NZQuakeParser
# ==============================================================
# Project: GeoNet Earthquake Data Parser (NZQuakeParser)
# Author: L. Caravella, lcaravella@ogs.it
# Year: 2025
# Overview:
# The GeoNet Quake Search (https://quakesearch.geonet.org.nz/) application 
# does not list all the available magnitude information into a single file.

# This script automates the download of **all magnitude data** 
# from individual event web pages on 
# [GeoNet](https://www.geonet.org.nz/earthquake/technical/{eventID}).

# After reading the '.csv' files obtained from the GeoNet Quake Search site, 
# it filters for earthquake data only, lists the event IDs, 
# fetches the technical pages asynchronously, extracts key information, 
# and saves the results in a catalogue `.csv` file.


# License:
#   This program is free software: you can redistribute it and/or modify it 
#   under the terms of the GNU General Public License as published by 
#   the Free Software Foundation, either version 3 of the License, or 
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful, 
#   but WITHOUT ANY WARRANTY; without even the implied warranty of 
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#   See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Citation:
#   If you use this software in your research or publications, please cite it as:
#   [Your Name]. (2025). GeoNet Earthquake Data Parser (Version 1.0) [Software].
#   Zenodo. https://doi.org/10.xxxx/zenodo.xxxxx
# ==============================================================


## Folder Structure
project_root/
│
├── main.py # Main driver script (run this)
├── functions.py # Helper functions for parsing, saving, and ID extraction
│
├── query/ # Input GeoNet catalogue CSVs
│ └── *.csv
│
├── IDS/ # Generated half-year ID files (.dat)
│ └── *_ID.dat
│
├── earthquake_data/ # Output parsed earthquake catalogue
│ └── *_earthquake_data.csv
│
├── requirements.txt # list of required libraries
│
└── README.md # This file


---

## How It Works

1. Reads GeoNet catalogues in `query/` via `get_ID_for_download()`.  
   → Extracts only earthquake events and splits their IDs by half-year into `.dat` files.
2. Fetches event pages from  
   [https://www.geonet.org.nz/earthquake/technical/{eventID}]


3. Parses earthquakes' details:
   - Event ID
   - Origin time, location, depth 
   - Available magnitude types and their value

4. Saves output catalogue to `earthquake_data/` as structured CSVs.

---

## 🚀 How to Run

(Make sure all the required libraries and packages are installed.)
1. Download the user-selected CSV catalogue catalogue from https://quakesearch.geonet.org.nz/
2. Copy the downloaded CSV file(s) into folder './query'
    (NOTE: all the files in query directory will be processed)
3. Run the program
    Option 1 — Jupyter Notebook
    open main.ipynb and run all the cells 
    Option 2 — standalone Python script
    Run the script from the terminal or Anaconda prompt:
    python main.py
4. The output catalogues will be saved automatically in ./earthquake_data/
