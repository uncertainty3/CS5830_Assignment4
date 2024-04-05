import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import random
import yaml

global_param = yaml.safe_load(open('params.yaml'))['global']

year = global_param['Year']
csv_files = global_param['download_dir']
month_cols = global_param['filter_cols']

# URL of the webpage containing the CSV file links
url = f"https://www.ncei.noaa.gov/data/local-climatological-data/access/{year}/"

# Send an HTTP GET request to the URL
response = requests.get(url)

#month_cols = ['MonthlyAverageRH', 'MonthlyDewpointTemperature', 'MonthlySeaLevelPressure', 'MonthlyStationPressure', 'MonthlyWetBulb']

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract CSV file links from the HTML content
    csv_links = [a["href"] for a in soup.find_all("a") if a["href"].endswith(".csv")]

    # Create a directory to save the downloaded CSV files
    os.makedirs(csv_files, exist_ok=True)
    # Download each CSV file
    sample = random.sample(csv_links, 20)
    #sample = ['72506794720.csv','99999963871.csv']
    i = 0
    for csv_link in sample:
        # Check if the link is a relative path or an absolute URL
        if csv_link.startswith("http"):
            full_csv_url = csv_link
        else:
            full_csv_url = urljoin(url, csv_link)
        
        csv_filename = csv_link.split("/")[-1]
        csv_filepath = os.path.join(csv_files, csv_filename)
        with open(csv_filepath, "wb") as f:
            print("Downloading", csv_filename)
            csv_response = requests.get(full_csv_url)
            f.write(csv_response.content)
            print("Downloaded")
        df = pd.read_csv(csv_filepath, low_memory = False)
        emp = df[month_cols].isnull().all().all()
        if emp:
            os.remove(csv_filepath)
        if i>20:
            break
        else:
            i+=1
    print("Extraction completed.")
else:
    print("Failed to retrieve data from the URL.")