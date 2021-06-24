import time
import selenium 
import csv
import re
from selenium import webdriver
from urllib3 import request


def do_nothing():
    print("Nothing")

def runCommand(info, text, opponent, driver):
    list_of_death_and_strength = driver.execute_script(get_deaths_and_strength_info.format(text, opponent))
    # -1 Stands for no casulties or strength found.
    if list_of_death_and_strength == 'none':
        info.append(-1)
    else:
        sum_of_value = 0 
        max_value = 0
        found_total = False
        for val in list_of_death_and_strength:
            if "total" in val or "Total" in val:
                found_total = True

            val = re.sub('\s+', '', val)
            val = re.sub(',', '', val)
            try:
                if all(x.isdigit() or x.isspace() for x in val) and val != '' and '\n' not in val and not float(re.sub("[^0-9]", "",info[1]))*0.999 <= float(val) <= float(re.sub("[^0-9]", "",info[2]))*1.001:
                    sum_of_value += int(val)
                    if int(val) > max_value:
                        max_value = int(val)
            except:
                pass
        # -2 Stands for unknown details, search for heavily or maybe little
        if sum_of_value == 0:
            info.append("unknown")
        else:
            if found_total == False:
                info.append(sum_of_value)
            else:
                info.append(max_value)

#This function will return all wa from a specific site in Wikipedia.
#The csv will contaiin : war_name, start_year, end_year, location, war_casualties

get_deaths_and_strength_info = ''' 
        var trs = document.getElementsByTagName('tr');
        var save = 'none'
        for(var i = 0; i < trs.length; i++){{
            if(trs[i].innerText == '{0}'){{
                save = i + 1;
            }}
        }}

        if (save == 'none'){{
            return save;
        }}
        if (trs[save].children.length >= 2){{
            x = trs[save].children[{1}].innerText;
        }} else {{
            x = trs[save].children[0].innerText;
        }}
        x = x.split(/([0-9 ,]+)/)
        for(i = 0; i < x.length; i++){{
            x[i] = x[i].replace(',','');
            x[i] = x[i].replace(' ','');
            x[i] = x[i].replace('-','');
        }}
        return x;
        '''
def get_database_from_url(url, database_name):
    driver = webdriver.Chrome()
    driver.get("{0}".format(url))

    #Data to recive from site itself: 
    #Run on each table and extract information 
    time.sleep(0.5)
    number_of_tables = driver.execute_script("return document.getElementsByClassName('wikitable').length")
    for ind in range(number_of_tables):
        #total data.
        total_info = []
        time.sleep(0.25)
        number_of_rows = driver.execute_script("return document.getElementsByClassName('wikitable')[{0}].querySelector('tbody').rows.length".format(ind))
        #Data to recive from war_url itslef:
        wars_url = []
        winners_list = []
        lossers_list = []
        start_year = []
        finish_year = []
        war_name = []
        pre_base_command ="return document.getElementsByClassName('wikitable')[{0}]".format(ind)
        base_command = ".querySelector('tbody').rows[{war_numbers}].cells[{war_info}]{end_command}"
        base_command = pre_base_command + base_command
        get_war_command = ".getElementsByTagName('a')[0].href"
        get_state_name_command = ".getElementsByTagName('a')[{state}].innerText"
        get_locations_url_command = "if(document.getElementsByClassName('location').length != 0){var locations = document.getElementsByClassName('location')[0].getElementsByTagName('a'); var locations_links = Array.prototype.slice.call(locations); locations_links = locations_links.map(x => locations_links[x] = x.innerText); return locations_links} else {return []}"
        check_missing_val = ''' 
        var x = document.getElementsByClassName('wikitable')[{0}].querySelector('tbody').rows[{1}].cells[{2}];
        if (x) {{
            return 1;
        }}else{{
            return 0;
        }}
        '''

        for war_number in range(2,number_of_rows):
            length_of_row = "try{{ return document.getElementsByClassName('wikitable')[{0}].rows[{1}].childElementCount; }}catch(err){{return '-1';}}".format(ind,war_number)
            if driver.execute_script(length_of_row) == 5:    
                start_year = []
        finish_year = []
        pre_base_command ="return document.getElementsByClassName('wikitable')[{0}]".format(ind)
        base_command = ".querySelector('tbody').rows[{war_numbers}].cells[{war_info}]{end_command}"
        base_command = pre_base_command + base_command
        get_war_command = ".getElementsByTagName('a')[0].href"
        get_state_name_command = ".getElementsByTagName('a')[{state}].innerText"
        get_locations_url_command = "if(document.getElementsByClassName('location').length != 0){var locations = document.getElementsByClassName('location')[0].getElementsByTagName('a'); var locations_links = Array.prototype.slice.call(locations); locations_links = locations_links.map(x => locations_links[x] = x.innerText); return locations_links} else {return []}"
        check_missing_val = ''' 
        var x = document.getElementsByClassName('wikitable')[{0}].querySelector('tbody').rows[{1}].cells[{2}];
        if (x) {{
            return 1;
        }}else{{
            return 0;
        }}
        '''

        for war_number in range(2,number_of_rows):
            length_of_row = "try{{ return document.getElementsByClassName('wikitable')[{0}].rows[{1}].childElementCount; }}catch(err){{return '-1';}}".format(ind,war_number)
            if driver.execute_script(length_of_row) == 5:    
                cmd = "try {{" + base_command.format(war_numbers = war_number, war_info = 2, end_command = get_war_command) + ";}}catch(err){{return 'none_links'}}"
                war_url = driver.execute_script(cmd)
                if war_url == 0: 
                    pass
                if "redlink" not in war_url and "none_links" not in war_url:
                    #Wars urls
                    wars_url.append(war_url)

                    #Start and end of each war
                    start_year.append(driver.execute_script(base_command.format(war_numbers = war_number, war_info = 0, end_command = ".innerText")))
                    finish_year.append(driver.execute_script(base_command.format(war_numbers = war_number, war_info = 1, end_command = ".innerText")))
                    
                    #Winner and losser for each war
                    winner = []
                    losser = []

                    
                    #Winners of wars
                    for winner_number in range(driver.execute_script(base_command.format(
                        war_numbers = war_number, war_info = 3, end_command = ".getElementsByTagName('a').length"))):
                        name_of_state = driver.execute_script(
                        base_command.format(war_numbers = war_number, war_info = 3, end_command = get_state_name_command.format(state = winner_number)))
                        if name_of_state != "" and all(x.isalpha() or x.isspace() for x in name_of_state):
                            winner.append(name_of_state)
                    
                    winners_list.append(','.join(winner))

                    #Losers of wars    
                    
                    if(driver.execute_script(check_missing_val.format(ind,war_number,4)) == 1):
                        for losser_number in range(driver.execute_script(base_command.format(
                            war_numbers = war_number, war_info = 4, end_command = ".getElementsByTagName('a').length"))):
                            name_of_state = driver.execute_script(
                            base_command.format(war_numbers = war_number, war_info = 4, end_command = get_state_name_command.format(state = losser_number)))
                            if name_of_state != "" and all(x.isalpha() or x.isspace() for x in name_of_state):
                                losser.append(name_of_state)
                    
                    lossers_list.append(','.join(losser))
                    war_name.append(driver.execute_script("try {{" + base_command.format(war_numbers = war_number, war_info = 2, end_command = ".getElementsByTagName('a')[0].title") + ";}}catch(err){{return 'none_name'}}"))
                    total_info.append([war_url,start_year[-1],finish_year[-1],winners_list[-1],lossers_list[-1],war_name[-1]])
                
        #Request stands for death/strength and opponent is zero for winner one for lossers
        
        count =  0
        for info in total_info:
            driver.get(info[0])
            time.sleep(0.25)
            info.append(','.join(driver.execute_script(get_locations_url_command)))
            runCommand(info,'Casualties and losses',0,driver)
            runCommand(info,'Casualties and losses',1,driver)
            runCommand(info,'Strength',0,driver)
            runCommand(info,'Strength',1,driver)
            info.append(driver.execute_script("if(document.getElementsByTagName('p').length >= 3){ return document.getElementsByTagName('p')[2].innerText.search('terror'); } else { return -1; }") != -1)
        
        with open("Databases/{0}.csv".format(database_name),"a") as my_csv:
            newarray = csv.writer(my_csv,delimiter=',')
            newarray.writerows(total_info)

        driver.get("{0}".format(url))
    
    driver.close()


