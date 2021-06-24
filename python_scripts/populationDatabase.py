import time
import selenium 
import csv
import re
from selenium import webdriver
from urllib3 import request

get_population_and_year = '''
total_info = [];
rows = document.getElementsByTagName('tr')
len = rows.length;
for(r = 1; r < len; r++){
    total_info.push([parseFloat(rows[r].cells[0].innerText.replace(/,/g, '')), parseFloat(rows[r].cells[1].innerText.replace(/,/g, ''))]);}
return total_info;
'''
def get_population():
    driver = webdriver.Chrome()
    driver.get("https://www.worldometers.info/world-population/world-population-by-year/")
    time.sleep(2)
    total_info = driver.execute_script(get_population_and_year)    
    driver.close()
    with open("/home/liam/Desktop/dataScience/Databases/population.csv","a") as my_csv:
            newarray = csv.writer(my_csv,delimiter=',')
            newarray.writerows(total_info)
get_population()