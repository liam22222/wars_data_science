from python_scripts.getDatabase_part_1 import runCommand
import time
import selenium 
import csv
import re
from selenium import webdriver
from urllib3 import request

get_info_about_sides = '''
var trs = document.getElementsByTagName('tr');
        var save = 'none'
        for(var i = 0; i < trs.length; i++){{
            if(trs[i].innerText == '{text}'){{
                save = i + 1;
            }}
        }}
        if (save == 'none'){{
            return save;
        }}
        try{{
            side_info = trs[save].cells[{pos}]
        }}catch{{ side_info = trs[save].cells[0]}}
        var answers = [];
        links = side_info.getElementsByTagName('a');
        for (i = 0; i < links.length; i++){{
           if((links[i].innerText != '') && (!/\d/.test(links[i].innerText))){{
               answers.push(links[i].innerText)
           }}
        }}
        if(answers.length == 0){{return 'non-state'}}
        else{{return answers}}
'''

rawSpan_command = '''
rows = document.getElementsByClassName('wikitable')[{table}].querySelector('tbody').rows
var rawSpans = []
for(i = 0; i < rows.length; i++){{
    try{{
        rawSpans.push(rows[i].cells[0].rowSpan)
    }}catch{{rawSpans.push(0)}}
}}
return rawSpans;
'''

get_year_command = '''
rows = document.getElementsByClassName('wikitable')[{table}].querySelector('tbody').rows
return rows[{row}].innerText.split('\t')[0]
'''
get_battle_command = '''
rows = document.getElementsByClassName('wikitable')[{table}].querySelector('tbody').rows
return rows[{row}].getElementsByTagName('a')[0].href
'''
get_locations_url_command = "if(document.getElementsByClassName('location').length != 0){var locations = document.getElementsByClassName('location')[0].getElementsByTagName('a'); var locations_links = Array.prototype.slice.call(locations); locations_links = locations_links.map(x => locations_links[x] = x.innerText); return locations_links} else {return []}"

get_war_name = "try{return document.getElementsByTagName('h1')[0].innerText}catch{'none'}"

def get_information_from_battle_page(driver, info):
    driver.get(info[0])
    time.sleep(0.25)
    info.append(driver.execute_script(get_info_about_sides.format(text = "Belligerents", pos = 0)))
    info.append(driver.execute_script(get_info_about_sides.format(text = "Belligerents", pos = 1)))
    info.append(driver.execute_script(get_war_name))
    info.append(driver.execute_script(get_locations_url_command))
    runCommand(info,'Casualties and losses',0,driver)
    runCommand(info,'Casualties and losses',1,driver)
    runCommand(info,'Strength',0,driver)
    runCommand(info,'Strength',1,driver)
    info.append(driver.execute_script("if(document.getElementsByTagName('p').length >= 3){ return document.getElementsByTagName('p')[2].innerText.search('terror'); } else { return -1; }") != -1)

def get_all_battles_from_page(page, file_name):
    total_info = []
    date = []
    battle_urls = []
    driver = webdriver.Chrome()
    driver.get(page)
    time.sleep(2)
    sum_len_of_rows = 0
    number_of_tables = driver.execute_script("return document.getElementsByClassName('wikitable').length")
    #make for all tables:
    for table_number in range(number_of_tables):
        rawSpan = driver.execute_script(rawSpan_command.format(table = table_number))
        len_of_rows = len(rawSpan)
        sum_len_of_rows += len_of_rows
        counter_for_rows = 0
        while counter_for_rows < len_of_rows:
            battle_urls.append(driver.execute_script(get_battle_command.format(table = table_number, row = counter_for_rows)))
            
            for iter in range(rawSpan[counter_for_rows]):
                date.append(driver.execute_script(get_year_command.format(table = table_number, row = counter_for_rows)))
                if iter != 0:
                    battle_urls.append(driver.execute_script(get_battle_command.format(table = table_number, row = iter)))
            
            counter_for_rows += rawSpan[counter_for_rows]
    #end of make for all tables

    for iter in range(sum_len_of_rows):
        if "redlink" not in battle_urls[iter] and "#" not in battle_urls[iter]:
            total_info.append([battle_urls[iter], date[iter], date[iter]])
    

    length_of_total_info = len(total_info)
    for info in range(length_of_total_info):
        get_information_from_battle_page(driver,total_info[info])
    
   
    driver.close()

    with open("Databases/{0}.csv".format(file_name),"a") as my_csv:
            newarray = csv.writer(my_csv,delimiter=',')
            newarray.writerows(total_info)

get_information_from_special_page = '''
var all_li = document.getElementsByTagName('li')
var save = []
for(i = 0; i < all_li.length; i++){
    if(/\d/.test(all_li[i].outerText.split(" ")[0])){
        save.push(all_li[i])
    }
}
var year = [];
var battle_url = []
var total_info = []
for(i = 0; i < save.length; i++){
    try{
        links = save[i].getElementsByTagName('ul')[0].getElementsByTagName('li');
        for(j = 0; j < links.length; j++){
            battle_url.push(links[j].getElementsByTagName('a')[0].href);
            year.push(save[i].outerText.split(" ")[0].replace(/\D/g,''));
        }
    }catch{console.log(i + "is problamatic");}
}

for(i = 0; i < battle_url.length; i++){
    total_info.push([battle_url[i], year[i], year[i]]);
}
return total_info
'''

def get_all_battles_from_special_page(page, file_name):
    driver = webdriver.Chrome()
    driver.get(page)
    time.sleep(2)
    total_info = driver.execute_script(get_information_from_special_page)

    length_of_total_info = len(total_info)
    for info in range(length_of_total_info):
        get_information_from_battle_page(driver,total_info[info])
    
    driver.close()

    with open("Databases/{0}.csv".format(file_name),"a") as my_csv:
            newarray = csv.writer(my_csv,delimiter=',')
            newarray.writerows(total_info)
