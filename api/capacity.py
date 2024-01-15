from urllib.request import urlopen
from urllib.error import URLError

import pandas as pd

class BoulderbarCapacity:
    
    date_fmt = "%d-%m-%Y %H:%M:%S"  

    prefix_url_wien = 'https://flash-cloud.boulderbar.net/modules/bbext/CustomerCapacity.php?gym=%s'
    prefix_url_other = 'https://flash-cloud-sbg.boulderbar.net/modules/bbext/CustomerCapacity.php?gym=%s'

    start_urls = [
        ('Hannovergasse', prefix_url_wien, 'han'),
        ('Wienerberg', prefix_url_wien, 'wb'),
        ('Hauptbahnhof', prefix_url_wien, 'hbf'),
        ('Seestadt', prefix_url_wien, 'see'),
        ('Linz', prefix_url_other, 'LNZ'),
        ('Salzburg', prefix_url_other, 'SBG'),
    ]

    @staticmethod
    def fetch_capacities():
        values = []
        try: 
            for name, prefix_url, url_postfix in BoulderbarCapacity.start_urls:
                page = urlopen(prefix_url % url_postfix)
                html_bytes = page.read()
                html = html_bytes.decode("utf-8")
                cap_index = html.find('capacity_bar')
                h2_index = html.find('<h2>', cap_index)
                h2_end = html.find('</h2>', h2_index+4)
                percent = html[h2_index+4:h2_end-1]
                values.append(percent)       
        except URLError as e:
            values.append(-1)
            print("Error:", e.reason)
        return values
    
    @staticmethod
    def fetch_capacities_df():
        values = BoulderbarCapacity.fetch_capacities()
        return pd.DataFrame([int(v) for v in values], index=[v[0] for v in BoulderbarCapacity.start_urls], columns=['Occupancy Rate (%)'])
        
    @staticmethod
    def data_frame(_data_path):
        try:
            df = pd.read_csv(
                _data_path,
                header=0,
                sep=',',
                na_values = {"-1",""})
        except FileNotFoundError:
            print(f'{_data_path} not found.')
            return None       
        
        df['Date']= pd.to_datetime(df['Date'], format=BoulderbarCapacity.date_fmt, yearfirst=False, dayfirst=True)
        df = df.set_index('Date')

        if len(df) < 1:
            df = None

        return df 