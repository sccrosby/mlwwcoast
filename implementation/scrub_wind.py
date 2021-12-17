import requests
from datetime import datetime
from pathlib import Path
import csv
import re

def read_station_csv(csvName):
    ## Read in the data from CSV and make a dictionary
    with open(csvName) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        # Make lists to house data from CSV
        name = []
        ID = []
        # Append values in CSV to variables
        for row in readCSV:
            name.append(row[0])
            ID.append(row[1])
        # Make a dictionary from the data
    station_data = dict(zip(name, ID))
    return station_data

# Constant
km2mph = 0.621371

# Select station
stas = read_station_csv('sta_list.csv')

for key, sta in stas.items():
    #sta = '26840' # Locust (For testing)
    #sta = '95770' # Faihaven

    # Setup ulr request
    base_url = 'https://www.sailflow.com/spot/'
    unique_url = base_url + sta

    # Access Page, and pull data values
    # Format of "data_values":[["2021-12-16 21:31:59","10 kph NNW",9.7,null,null,338,"NNW",2.9,null,null,null,null,"2021-12-17 05:31:59",null,null,91.0,null]],"Stations"
    page = requests.get(unique_url)
    try:
        page.raise_for_status() # Will throw an exception if the page is not found
        m = re.search('"data_values":\[\[(.+?)\]\],"Stations"', str(page.content))
        data = m.group(1).split(',')

        # If there is data
        if data[0] != 'null' and data[1] != ''"Station is down"'':

            # Format time, careful with the milliseconds that occasionally show up
            time = data[0].strip('"')
            if len(time) > 19:
                time = datetime.strptime(data[0].strip('"'),'%Y-%m-%d %H:%M:%S.%f')
            else:
                time = datetime.strptime(data[0].strip('"'),'%Y-%m-%d %H:%M:%S')

            spd = float(data[2])*km2mph
            md = float(data[5])

            print([key, spd, md])

            # Append data to CSV
            myfile = Path('data/' + sta + '.csv')
            myfile.touch(exist_ok=True)
            f = open(myfile,'a')
            f.write(str(time) + ',' + str(spd) + ',' + str(md) + '\n')
            f.close()
        else:
            print(sta + ' is down')
    except:
        print(sta + ' has been removed')

# Notes:
# Access Page (Alternative way to access just speed)
#m = re.search('wind_speed=(.+?)">', str(page.content))
#spd2 = m.group(1)