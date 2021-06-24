import time
import selenium 
import csv
import re
from selenium import webdriver
from urllib3 import request

borders_cmd = '''
tr = document.getElementsByTagName('tr')
total_info = []
for(i = 2; i < 206; i++){{
    total_info.push([tr[i].cells[0].innerText.replace('\xa0', ''), tr[i].cells[1].innerText.split('[')[0],tr[i].cells[4].innerText.split('[')[0]])
}}
return total_info
'''

coast_line_cmd = '''
tr = document.getElementsByTagName('tr')
total_info = []
for(i = 3; i < 254; i++){{
    total_info.push([tr[i].cells[0].innerText.replace('\xa0', ''), tr[i].cells[2].innerText.split('[')[0]])
}}
return total_info
'''
religions_cmd = '''
tr = document.getElementsByTagName('tr')
religons = ['Christian', 'Islam', 'Roman', 'Buddhist', 'Catholic', 'Protestant', 'indigenous', 'Hindu', 'Judaism']
total = []
for(i = 0; i < tr.length - 1; i++){
    re = ""
    arr = tr[i].cells[1].innerText.split(' ') 
    flag = false
    for (word in arr){
        for( religon in religons){
            if(arr[word] == religons[religon]){
                re = arr[word];
                flag = true;
                break;
            }
        }
        if(flag == true){
            break;
        }
    }
    if(re == "indigenous")
        total.push([tr[i].cells[0].innerText,tr[i].cells[0].innerText]);
    else{
        if(re == "")
            total.push([tr[i].cells[0].innerText,"Unknown"]);
        else{
            total.push([tr[i].cells[0].innerText,re]);
        }
    }
}
return total
'''
temp_cmd = '''
tr = document.getElementsByTagName('tr')
total_info = []
for(i = 1; i < tr.length; i++){{
    total_info.push([tr[i].cells[0].innerText.replace('\xa0', ''),tr[i].cells[1].innerText])
}}
return total_info
'''
sea_level_command = '''
tr = document.getElementsByTagName('tr')
total_info = []
for(i = 2; i <= 159; i++){{
    total_info.push([tr[i].cells[0].innerText.replace('\xa0', ''),tr[i].cells[1].innerText.split(/\s/g)[0]])
}}
return total_info
'''
borders_url = "https://en.wikipedia.org/wiki/List_of_countries_and_territories_by_land_borders"
coastline_url = "https://en.wikipedia.org/wiki/List_of_countries_by_length_of_coastline"
religion_url = "https://www.infoplease.com/world/social-statistics/world-religions"
temp_url = "https://en.wikipedia.org/wiki/List_of_countries_by_average_yearly_temperature"
sea_level_url = "https://en.wikipedia.org/wiki/List_of_countries_by_average_elevation"

def write_to_csv(database_name, data):
    with open("Databases/countries/{0}.csv".format(database_name),"a") as my_csv:
            newarray = csv.writer(my_csv,delimiter=',')
            newarray.writerows(data)

def country_feature(driver, cmd, file_name, url):
    driver.get("{}".format(url))
    time.sleep(2)
    total = driver.execute_script(cmd)
    write_to_csv(file_name,total)
    return total

driver = webdriver.Chrome()
#country_feature(driver,coast_line_cmd,"coast_line",coastline_url)
#country_feature(driver,religions_cmd,"religon",religion_url)
#country_feature(driver,temp_cmd,"temp", temp_url)
#country_feature(driver,sea_level_command,"sea_level",sea_level_url)
#country_feature(driver,borders_cmd,"borders",borders_url)
driver.close()