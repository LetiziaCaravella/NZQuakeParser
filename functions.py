from bs4 import BeautifulSoup
import csv
import asyncio
import aiohttp
import os
import numpy as np
import nest_asyncio
import pandas as pd
import glob


def get_ID_for_download(queryfolder, idfolder):
    """ 
    This function reads the GeoNet query CSV files downloaded from the
    GeoNet Quake Search website (https://https://quakesearch.geonet.org.nz/), 
    selects the earthquakes only and generates .dat ID files

    Input
    queryfolder : str
        Path to the folder containing CSV catalog files downloaded from GeoNet.
    idfolder : str
        Path to the output folder where the generated ID `.dat` files will be saved.

    Output
    catalogue : pandas.DataFrame
        Combined and filtered earthquake catalog containing all input data.
    
    """
    
    # Reading the files from the "queryfolder"
    file_pattern = "*.csv"
    filepaths = glob.glob(os.path.join(queryfolder, "*.csv"))
    df_list = [pd.read_csv(file) for file in filepaths]

    # Defining Pandas Dataframe for the seismic catalogue
    catalogue = pd.concat(df_list, ignore_index=True)

    # Select earthquakes only
    catalogue = catalogue[catalogue['eventtype']=="earthquake"].copy()
    catalogue = catalogue.sort_values(by='origintime').reset_index().copy()
    catalogue = catalogue.drop(columns='index').copy()    
    catalogue['origintime'] = pd.to_datetime(catalogue['origintime'],)
    catalogue['year'] = catalogue['origintime'].dt.year
    catalogue['month'] = catalogue['origintime'].dt.month
    catalogue['day'] = catalogue['origintime'].dt.day
    catalogue['hour'] = catalogue['origintime'].dt.hour
    catalogue['minute'] = catalogue['origintime'].dt.minute
    catalogue['second'] = catalogue['origintime'].dt.second

    # Generating output files, two per year: 
    # one from January to June and the second from July to December
    years = catalogue['year'].unique()
    for year in years:
        
        # Split into half-year periods
        jan_jun = catalogue.loc[(catalogue['year'] == year) & (catalogue['month'] <= 6), 'publicid']
        jul_dec = catalogue.loc[(catalogue['year'] == year) & (catalogue['month'] > 6), 'publicid']

        # Save non-empty halves to .dat files
        if len(jan_jun) > 0:
            fnameout1 = os.path.join(idfolder, f"NZ_{year}_01-06_ID.dat")
            jan_jun.to_csv(fnameout1, index=False, header=None)
    
        if len(jul_dec) > 0:
            fnameout2 = os.path.join(idfolder, f"NZ_{year}_07-12_ID.dat")
            jul_dec.to_csv(fnameout2, index=False, header=None)
    
    return catalogue


def parse_data(html, public_id):
    """
    Parse earthquake data HTML from GeoNet by event IDs 
    and extract origin and magnitudes information.

    Input 
    html : str
        Raw HTML content of the event's "technical" page from GeoNet.
    public_id : str
        Public event ID corresponding to the GeoNet earthquake.put

    Output
    dict
        Dictionary containing:
        - 'PublicID' : str
        - 'Origin' : dict with origin data (Latitude, Longitude, Depth, etc.)
        - 'PreferredM' : dict with preferred magnitude value and type
        - 'Magnitudes' : dict of all reported magnitude types and values
        
    """

    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract Origin Data
    origin_data = {}
    origin_table = soup.find('h4', string='Origin')
    if origin_table:
        table = origin_table.find_next('table')
        for row in table.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) == 2:
                key = columns[0].text.strip().replace(" ", "") 
                value = columns[1].text.strip()

                if key in ['Latitude', 'Longitude', 'Depth']:
                    # Clean numeric values and split uncertainty if present
                    cleaned_value = value.replace("\n", "").replace("                    km", "").replace("km", "").replace(" (± ", ",").replace(")", "").strip()
                    values = cleaned_value.split(',')
                    
                    try:
                        # Ensure there are both value and uncertainty
                        if len(values) == 2:  
                            origin_data[key] = float(values[0])
                            origin_data[f"{key}Uncertainty"] = float(values[1])
                        # If not set to NaN
                        elif len(values) == 1:  
                            origin_data[key] = float(values[0])
                            origin_data[f"{key}Uncertainty"] = np.nan  
                    except ValueError as e:
                        print(f"Error parsing {key} for {public_id}: {e}")
                
                else:
                    # Keep other fields as strings
                    origin_data[key] = value  

    # Extract Magnitude Data
    magnitudes = {}
    magnitude_table = soup.find('h4', string='Magnitudes')
    if magnitude_table:
        table = magnitude_table.find_next('table')
        for row in table.find_all('tr')[1:]:  
            columns = row.find_all('td')
            if len(columns) == 3:
                mag_type = columns[0].text.strip().replace(" ", "")              
                mag_value = columns[1].text.strip()
                station_count = columns[2].text.strip()

                # Clean numeric data and uncertainty
                cleaned_value = mag_value.replace(" (± ", ",").replace(")", "").strip()
                values = cleaned_value.split(',')

                try:
                    if len(values) == 2:
                        magnitude = float(values[0])
                        magnitude_uncertainty = float(values[1])
                    else:
                        magnitude = float(values[0])
                        magnitude_uncertainty = np.nan  
                        
                    # Preferred magnitude (e.g., "Preferred(Mw(mB))")                    
                    if "Preferred" in mag_type:
                        if mag_type.startswith("Preferred(") and mag_type.endswith(")"):
                            m_type = mag_type[len("Preferred("):-1]
                        else:
                            m_type = mag_type  # fallback if the format is unexpected

                        preferredM = {
                            'PreferredM': magnitude,
                            'PreferredM_type': m_type,
                        }

                        
                    else:                    
                        magnitudes[mag_type] = {
                            'Magnitude': magnitude,
                            'MagnitudeUncertainty': magnitude_uncertainty,
                            'StationCount': station_count.strip()
                        }
                except ValueError as e:
                    print(f"Error parsing magnitude {mag_type} for {public_id}: {e}")

    return {'PublicID': public_id, 'Origin': origin_data, 'PreferredM': preferredM, 'Magnitudes': magnitudes}




def save_to_csv(data_list, filename, output_folder):
    """
    Save a list of parsed earthquake data dictionaries to a CSV file.

    Parameters
    data_list : list of dict
        List of earthquake data (output of `parse_data()`).
    filename : str
        Output CSV filename (without folder path).
    output_folder : str, optional
        Destination folder for saving the CSV file (default: './earthquake_data/').

    Notes
    -----
    - The function dynamically builds CSV columns based on the available
      magnitude types across all events.
    - A `PreferredMag` column indicates the preferred magnitude type (e.g. Mw(mB)).
    - Missing numeric values are left blank in the output CSV.
    """
    
    filepath = os.path.join(output_folder, filename)
    with open(filepath, 'w', newline='') as csvfile:
        #Set column names
        fieldnames = ['PublicID', 'UTCTime', 'Latitude', 'LatitudeUncertainty', 'Longitude', 'LongitudeUncertainty', 
                      'Depth', 'DepthUncertainty',  'PreferredMag'
                    ]
        mag_types = set()
        
        # Collect all unique magnitude types
        for data in data_list:
            if data:
                mag_types.update(data['Magnitudes'].keys())
                
        # Dynamically extend fieldnames with magnitude columns
        for mag_type in mag_types:
            fieldnames.append(f"{mag_type}")
            fieldnames.append(f"{mag_type}_Uncertainty")
            fieldnames.append(f"{mag_type}_StationCount")

        # Initialize CSV writer
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Write a row for each event
        for data in data_list:
            if data:
                row = {
                    'PublicID': data['PublicID'],
                    'UTCTime': data['Origin'].get('UTCTime', ''),
                    'Latitude': data['Origin'].get('Latitude', ''),
                    'LatitudeUncertainty': data['Origin'].get('LatitudeUncertainty', ''),
                    'Longitude': data['Origin'].get('Longitude', ''),
                    'LongitudeUncertainty': data['Origin'].get('LongitudeUncertainty', ''),
                    'Depth': data['Origin'].get('Depth', ''),
                    'DepthUncertainty': data['Origin'].get('DepthUncertainty', ''),         
                    'PreferredMag': data.get('PreferredM', {}).get('PreferredM_type', ''),
                }
                
                # Add all available magnitude data
                for mag_type in mag_types:
                    row[f"{mag_type}"] = data['Magnitudes'].get(mag_type, {}).get('Magnitude', '')
                    row[f"{mag_type}_Uncertainty"] = data['Magnitudes'].get(mag_type, {}).get('MagnitudeUncertainty', '')
                    row[f"{mag_type}_StationCount"] = data['Magnitudes'].get(mag_type, {}).get('StationCount', '')               
                writer.writerow(row)