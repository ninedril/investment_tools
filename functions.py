#####
# arg1: specify company

##### Loading other libraries
import sys, os
sys.path.append(os.pardir)
from selenium_tools.function import *
#####

import csv
import numpy as np

# WevDriver => Boolean
def search_by_company(wd, company_name):
    try:
        s_box = wd.find_element_by_id('input_id')
        s_box.send_keys(company_name)
        s_box.submit()
        return True
    except:
        return False

# WebDriver => [WebElement, ...]
def get_result_companies_link(wd):
    try:
        result_companies = wd.find_elements_by_css_selector('div#kensaku_kekka ul li a')
        return result_companies
    except:
        return []

# WebDriver => WebElement
def get_company_stock_price_link(wd):
    try:
        c_link = wd.find_element_by_xpath("//a[text()='時系列']")
    except:
        print("cant find chart link")
        c_link = None
    return c_link

# WebDriver, String => WebElement
def get_company_stock_price_link_by_time(wd, term_flag):
    if term_flag == 'w':
        term = '週間株価'
    elif term_flag == 'm':
        term = '月間株価'
    else:
        print('Invalid term')
        return None
    
    try:
        c_link = wd.find_element_by_xpath("//a[text()='" + term + "']")
    except:
        print("cant find stock price link by " + term)
        c_link = None
    
    return c_link

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

def get_MN_index(monthly_table):
    return 0 

def get_OP_index(monthly_table):
    return 1 

def get_CP_index(monthly_table):
    return 2

def get_SV_index(monthly_table):
    return 4

def make_dateId(date_str):
    return date_str

# WebElement, String => ndarray
def get_datas_from_table(table_element, header_label):
    header_datas = np.array(get_list_from_table(table_element))
    if not(header_label in header_datas[0]):
        return []
    i = header_datas[0].index(header_label)
    label_datas = header_datas[0:, i:i+1]
    return label_datas

# function => boolean
def loop_function(looped_func):
    try:
        while looped_func():
            pass
    except:
        return False
    else:
        return True
    

class Company:
    def __init__(self):
        pass
 
class TablePageManager:
    def __init__(self, driver=None):
        if driver:
            self.dv = driver
        else:
            self.dv = launchChrome(is_headless=False)

        
        self.table = self.find_table(self.dv)
      
    def find_table(self):
        pass


if __name__ == '__main__':
    target_url = 'https://kabutan.jp/'
    company = sys.argv[1]
    
    dv = launchChrome(is_headless=True)
    #dv = launchChrome(is_headless=False)
    dv.get(target_url)
    search_by_company(dv, company)
    
    #import pdb; pdb.set_trace()

    try:
        get_result_companies_link(dv)[0].click()
    except:
        pass

    get_company_stock_price_link(dv).click()

    get_company_stock_price_link_by_time(dv, 'w').click()

    all_datas = []
    is_first_table = True
    while True:
        table = dv.find_elements_by_css_selector('table.stock_kabuka2')[0]
        new_datas = get_array_from_table(table)
        if not(is_first_table):
            new_datas = new_datas[1:]
        else:
            is_first_table = False
        all_datas.extend(new_datas)
        
        try:
            next_table_link = dv.find_element_by_xpath("//a[text()='次へ＞']")
        except:
            break
        next_table_link.click()

    make_csv_from(all_datas, company + '.csv')
    exit_driver(dv)
    