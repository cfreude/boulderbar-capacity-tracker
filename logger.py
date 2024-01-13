from urllib.request import urlopen
from urllib.error import URLError

import time, datetime, os, csv

import pandas as pd


class BoulderbarCapacityLogger:

    date_fmt = "%d-%m-%Y %H:%M:%S"
    data_path = './boulderbar-capacity-log.csv'    
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
            for name, prefix_url, url_postfix in BoulderbarCapacityLogger.start_urls:
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
        values = BoulderbarCapacityLogger.fetch_capacities()
        return pd.DataFrame([int(v) for v in values], index=[v[0] for v in BoulderbarCapacityLogger.start_urls], columns=['Occupancy Rate (%)'])

    @staticmethod
    def run(_delay_min, _plot=False):

        if _plot:
            BoulderbarCapacityLogger.plot()
            return

        BoulderbarCapacityLogger.init()

        data = []

        try: 
            while True:

                values = BoulderbarCapacityLogger.fetch_capacities()
                
                entry = (datetime.datetime.now(), values)
                print(entry)
                data.append(entry)

                # write to file
                if len(data) > 10:
                    BoulderbarCapacityLogger.save(data)
                    data = []                
                
                time.sleep(_delay_min * 60.0)
        except KeyboardInterrupt:   
            pass
        finally:
            BoulderbarCapacityLogger.save(data)

    @staticmethod
    def init():
        file_exists = os.path.exists(BoulderbarCapacityLogger.data_path)

        if not file_exists:   
            with open(BoulderbarCapacityLogger.data_path, 'a', newline='\n') as csvfile:
                fieldnames = ['Date', ] + [v[0] for v in BoulderbarCapacityLogger.start_urls]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()                

    @staticmethod
    def save(data):
        file_exists = os.path.exists(BoulderbarCapacityLogger.data_path)
            
        with open(BoulderbarCapacityLogger.data_path, 'a', newline='\n') as csvfile:
            fieldnames = ['Date', ] + [v[0] for v in BoulderbarCapacityLogger.start_urls]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for date, vals in data:                    
                entry = {'Date': date.strftime(BoulderbarCapacityLogger.date_fmt)}
                for i, v in enumerate(vals):
                    entry[BoulderbarCapacityLogger.start_urls[i][0]] = v
                print(entry)
                writer.writerow(entry)

    @staticmethod
    def data_frame():
        try:
            df = pd.read_csv(
                BoulderbarCapacityLogger.data_path,
                header=0,
                sep=',',
                na_values = {"-1",""})
        except FileNotFoundError:
            print(f'{BoulderbarCapacityLogger.data_path} not found.')
            return None       
        
        df['Date']= pd.to_datetime(df['Date'], format="%d-%m-%Y %H:%M:%S", yearfirst=False, dayfirst=True)
        df = df.set_index('Date')

        if len(df) < 1:
            df = None

        return df 

    @staticmethod
    def plot():
        import plotext as plt
        
        df = BoulderbarCapacityLogger.data_frame()
        if df is None:
            print('No entries.')
            return
        
        dtf = BoulderbarCapacityLogger.date_fmt.replace('%', '')
        plt.date_form(dtf, dtf)     
        plt.title('Boulderbar Capacity')        
        for name in df.columns.values[1:]:
            date_vals = df.loc[:,'Date'].values
            percent = df.loc[:,name].values
            plt.scatter(date_vals, percent, label=f'{name}:')
        plt.show()
    

if __name__ == '__main__':

    import argparse  

    parser = argparse.ArgumentParser(
                    prog='Boulderbar Capacity Logger',
                    description='Periodically fetches the Boulderbar capacity from the web (https://boulderbar.net/) and stores it in a CSV.')

    parser.add_argument('--p', required=False, type=float, default=5.0,
                        help='The period in minutes.')
    parser.add_argument('--d', action='store_true', default=False,
                        help='Display data in the cmd-line.')
    args = parser.parse_args()

    BoulderbarCapacityLogger().run(args.p, args.d)