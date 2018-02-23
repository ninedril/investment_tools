#####
# arg1: specify company

##### Loading other libraries
import sys, os, urllib
sys.path.append(os.pardir)
from selenium_tools.function import *
#####

import csv
import numpy as np
from itertools import chain

# Array, String => Boolean
def make_csv_from(array2d, path):
    with open(path, 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(array2d)

# WebElement => List
def get_list_from_table(table_element):
    header_row = table_element.find_elements_by_tag_name('tr')[0]

    def parse_th(th_elem):
        col_len = th_elem.get_attribute('colspan')
        if col_len:
            col_len = int(col_len)
            new_elem = []
            for i in range(1, col_len+1):
                new_elem.append(th_elem.text + '_' + str(i))
            return new_elem
        return [th_elem.text]
    labels = map(parse_th, header_row.find_elements_by_tag_name('th'))
    labels = list(chain.from_iterable(labels))

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
def get_all_table_datas(wd, table_locator, nextlink_locator):
    # WebDriver must be in the page with a table
    all_datas = []
    is_first_table = True
    while True:
        try:
            table = wd.find_element_by_xpath(table_locator)
        except:
            break

        new_datas = get_list_from_table(table)
        if not(is_first_table):
            new_datas = new_datas[1:]
        else:
            is_first_table = False
        all_datas.extend(new_datas)
        
        try:
            next_table_link = wd.find_element_by_xpath(nextlink_locator)
        except:
            break
        next_table_link.click()

    return all_datas

# WebDriver, String, String, int => List
def get_table_datas(wd, table_locator, nextlink_locator, num=-1):
    # WebDriver must be in the page with a table
    all_datas = []
    is_first_table = True
    while True:
        try:
            table = wd.find_element_by_xpath(table_locator)
        except:
            break

        new_datas = get_list_from_table(table)
        if not(is_first_table):
            new_datas = new_datas[1:]
        else:
            is_first_table = False
        all_datas.extend(new_datas)
        
        if 0 < num <= len(all_datas[1:]):
            return all_datas[:num+1]

        try:
            next_table_link = wd.find_element_by_xpath(nextlink_locator)
        except:
            break
        next_table_link.click()

    return all_datas

# String, String => String
def get_url_value(url, q_key):
    try:
        q_str = urllib.parse.urlparse(url)[4]
        v = urllib.parse.parse_qs(q_str)[q_key][0]
        return v
    except:
        return ''