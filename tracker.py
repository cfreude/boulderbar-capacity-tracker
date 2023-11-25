from urllib.request import urlopen
from urllib.error import URLError

import time, json, datetime, pickle, os, csv

import pandas as pd
import plotext as plt


class BoulderbarCapacityTracker:

    date_fmt = "%d-%m-%Y %H:%M:%S"
    data_path = './data-packup.csv'    
    prefix_url = 'https://flash-cloud.boulderbar.net/modules/bbext/CustomerCapacity.php?gym=%s'

    start_urls = [
    ('Hannovergasse', 'han'),
    ('Wienerberg', 'wb'),
    ('Hauptbahnhof', 'hbf'),
    ('Seestadt', 'see'),
    ('Linz', 'LNZ'),
    ('Salzburg', 'SGB'),
]
    def save(data):
        file_exists = os.path.exists(BoulderbarCapacityTracker.data_path)
            
        with open(BoulderbarCapacityTracker.data_path, 'a', newline='\n') as csvfile:
            fieldnames = ['Date', ] + [v[0] for v in BoulderbarCapacityTracker.start_urls]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for date, vals in data:                    
                entry = {'Date': date.strftime(BoulderbarCapacityTracker.date_fmt)}
                for i, v in enumerate(vals):
                    entry[BoulderbarCapacityTracker.start_urls[i][0]] = v
                print(entry)
                writer.writerow(entry)

    def run(self, _delay_min, _plot=False):

        if _plot:
            self.plot()
            return

        data = []

        try: 
            while True:

                values = []
                try: 
                    for name, url_postfix in BoulderbarCapacityTracker.start_urls:
                        page = urlopen(BoulderbarCapacityTracker.prefix_url % url_postfix)
                        html_bytes = page.read()
                        html = html_bytes.decode("utf-8")
                        cap_index = html.find('capacity_bar')
                        h2_index = html.find('<h2>', cap_index)
                        h2_end = html.find('</h2>', h2_index+4)
                        percent = html[h2_index+4:h2_end-1]
                        values.append(percent)       
                except URLError as e:
                    values.append((name, None))  
                    print("Error:", e.reason)
                
                entry = (datetime.datetime.now(), values)
                print(entry)
                data.append(entry)

                # write to file
                if len(data) > 10:
                    self.save(data)
                    data = []                
                
                time.sleep(_delay_min * 60.0)
        except KeyboardInterrupt:   
            pass
        finally:
            self.save(data)
            

    def plot(self):
        dtf = BoulderbarCapacityTracker.date_fmt.replace('%', '')
        plt.date_form(dtf, dtf)
        df = pd.read_csv(BoulderbarCapacityTracker.data_path)
        df.set_index('Date')       
        plt.title('Boulderbar Capacity')        
        for name in df.columns.values[1:]:
            date_vals = df.loc[:,'Date'].values
            percent = df.loc[:,name].values
            plt.scatter(date_vals, percent, label=f'{name}:')
        plt.show()
    

if __name__ == '__main__':

    import argparse  

    parser = argparse.ArgumentParser(
                    prog='Boulderbar Capacity Tracker',
                    description='Periodically fetches the Boulderbar capacity from the web (https://boulderbar.net/) and stores it in a CSV.')

    parser.add_argument('period', type=float, default=5.0,
                        help='The period in minutes.')
    parser.add_argument('--d', action='store_true', default=False,
                        help='Display data in the cmd-line.')
    args = parser.parse_args()

    BoulderbarCapacityTracker().run(args.period, args.d)