#####
# arg1: specify company

##### Loading other libraries
import sys, os
sys.path.append(os.pardir)
from selenium_tools.function import *
#####

import csv
import numpy as np

# Array, String => Boolean
def make_csv_from(array2d, path):
    with open(path, 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(array2d)

# WebElement => List
def get_list_from_table(table_element):
    header_row = table_element.find_elements_by_tag_name('tr')[0]
    labels = list(map(lambda e: e.text, header_row.find_elements_by_tag_name('th')))

    result = [labels]
    data_rows = table_element.find_elements_by_tag_name('tr')[1:]
    for row in data_rows:
        datas = list(map(lambda e: e.text, row.find_elements_by_tag_name('td')))
        result.append(datas)

    return result

# ndarray, String => int
def get_label_index(table_array, label_name):
    header_row = table_array[0]
    try:
        i = header_row.index(label_name)
        return i
    except:
        print('get_label_index')
        return -1

# WebDriver, String, String => List
def get_all_table_datas(wd, table_selector, nextlink_selector):
    all_datas = []
    is_first_table = True
    while True:
        try:
            table = wd.find_elements_by_css_selector(table_selector)[0]
        except:
            break

        new_datas = get_list_from_table(table)
        if not(is_first_table):
            new_datas = new_datas[1:]
        else:
            is_first_table = False
        all_datas.extend(new_datas)
        
        try:
            next_table_link = wd.find_elements_by_css_selector(nextlink_selector)[0]
        except:
            break
        next_table_link.click()

    exit_driver(wd)
    return all_datas
    