import time, datetime, os, csv
import pandas as pd

from api.capacity import BoulderbarCapacity

class BoulderbarCapacityLogger:
    
    data_path = './boulderbar-capacity-log.csv'    
    
    @staticmethod
    def run(_delay_min, _plot=False):

        if _plot:
            BoulderbarCapacityLogger.plot()
            return

        BoulderbarCapacityLogger.init()

        data = []

        try:
            # write first            
            data.append((datetime.datetime.now(),  BoulderbarCapacity.fetch_capacities()))
            BoulderbarCapacityLogger.save(data)
            data = []   
            time.sleep(_delay_min * 60.0)

            while True:                
                data.append((datetime.datetime.now(),  BoulderbarCapacity.fetch_capacities()))

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
                fieldnames = ['Date', ] + [v[0] for v in BoulderbarCapacity.start_urls]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()                

    @staticmethod
    def save(data):
        file_exists = os.path.exists(BoulderbarCapacityLogger.data_path)
            
        with open(BoulderbarCapacityLogger.data_path, 'a', newline='\n') as csvfile:
            fieldnames = ['Date', ] + [v[0] for v in BoulderbarCapacity.start_urls]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for date, vals in data:                    
                entry = {'Date': date.strftime(BoulderbarCapacity.date_fmt)}
                for i, v in enumerate(vals):
                    entry[BoulderbarCapacity.start_urls[i][0]] = v
                print(entry)
                writer.writerow(entry)


    @staticmethod
    def plot():
        import plotext as plt
        
        df = BoulderbarCapacity.data_frame()
        if df is None:
            print('No entries.')
            return
        
        dtf = BoulderbarCapacity.date_fmt.replace('%', '')
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