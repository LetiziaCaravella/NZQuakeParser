# NZQuakeParser
Project: GeoNet Earthquake Data Parser (NZQuakeParser)  
DOI: 10.5281/zenodo.17552472  
Author: L. Caravella, lcaravella@ogs.it  
Year: 2025  
## Overview:  
The GeoNet [Quake Search application](https://quakesearch.geonet.org.nz/) (GNS Science, 2025)  
does not list all the available magnitude information into a single file.  

This script automates the download of **all magnitude data** 
from individual event web pages on 
[GeoNet](https://www.geonet.org.nz/earthquake/technical/{eventID}).

After reading the `.csv` file(s) obtained from the GeoNet Quake Search site, 
it filters for earthquake data only,  
lists the event IDs, fetches the technical pages asynchronously, extracts key information,  
and saves the results in a catalogue `.csv` file.  


## License:
This program is a free software: you can redistribute it and/or modify it under the terms of the  
GNU General Public License as published by the Free Software Foundation,  
either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;  
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details.

A copy of the GNU General Public License is listed along with this program.  
## Folder Structure
<pre>project_root/  
   │  
   ├── main.py # Main driver script (run this)  
   │  
   ├── main.ipynb
   │  
   ├── functions.py # Helper functions for parsing, saving, and ID extraction  
   │  
   ├── query/ # Input GeoNet catalogue (.csv)  
   │  └── *.csv  
   │  
   ├── IDS/ # Generated half-year ID files (.dat)  
   │ └── *_ID.dat  
   │  
   ├── earthquake_data/ # Output parsed earthquake catalogue  
   │ └── *_earthquake_data.csv  
   │  
   ├── requirements.txt # List of required libraries  
   │  
   └── README.md # This file </pre>

## How It Works

1. Reads GeoNet catalogues in `query/` via `get_ID_for_download()`.  
   → Extracts only earthquake events and splits their IDs by half-year into `.dat` files.
2. Fetches event pages from [GeoNet](https://www.geonet.org.nz/earthquake/technical/{eventID}).
3. Parses earthquakes' details:
   - Event ID
   - Origin time, location, depth 
   - Available magnitude types and their value

4. Saves output catalogue to `earthquake_data/` as structured CSVs.


## How to Run

(Make sure all the required libraries and packages are installed.)
1. Download the user-selected CSV catalogue from the [GeoNet Quake Search application](https://quakesearch.geonet.org.nz/)  
2. Copy the downloaded `.csv` file(s) into `./query`  
    (NOTE: all the files in query directory will be processed)
3. Run the program  
   - Option 1 — Jupyter Notebook  
      Open `main.ipynb` and run all the cells  
   - Option 2 — standalone Python script  
       Run the script `main.py` from the terminal or Anaconda prompt:  
       python main.py  
4. The output catalogues will be saved automatically in `./earthquake_data/`

-----
The GeoNet website is a collaboration between NHC Toka Tū Ake and Earth Sciences New Zealand.  
We used the Quake Search system to obtain a seismic catalog from New Zealand.  
We acknowledge the New Zealand GeoNet programme and its sponsors NHC, GNS Science, LINZ, NEMA and MBIE for providing access to their datasets.
