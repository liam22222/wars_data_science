import os
import pandas as pd
import csv

header = ["war_url","start_year","finish_year","winner_list","losser_list","war_name","location","casualties_A","casualties_B","strength_A","strength_B","terror","war_or_battle"]
database_names = os.listdir("Databases/")    
database_names = list(filter(lambda f: f.endswith('.csv'), database_names))

def combine_csv():

    with open('Databases/combine_files.csv', 'a') as comb:
            writer = csv.writer(comb)
            writer.writerow(header)

    for csv_name in database_names:
        with open("Databases/{0}".format(csv_name), 'r') as csv_file:
            original = csv_file.read()
        
        with open('Databases/combine_files.csv', 'a') as comb:
            comb.write('\n')
            comb.write(original)
    