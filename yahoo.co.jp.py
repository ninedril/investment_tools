#####
# arg1: specify company

##### Loading other libraries
import sys, os
sys.path.append(os.pardir)
from selenium_tools.function import *
from functions import *
#####

import csv

# 
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

# WebElement => Array
def get_array_from_table(table_element):
    header_row = table_element.find_elements_by_tag_name('tr')[0]
    labels = list(map(lambda e: e.text, header_row.find_elements_by_tag_name('th')))

    result = [labels]
    data_rows = table_element.find_elements_by_tag_name('tr')[1:]
    for row in data_rows:
        datas = list(map(lambda e: e.text, row.find_elements_by_tag_name('td')))
        result.append(datas)

    return result

if __name__ == '__main__':
    caps_rank_url = "https://info.finance.yahoo.co.jp/ranking/?kd=4&tm=d&vl=a&mk=3"
    #dv = launchChrome(is_headless=True)
    dv = launchChrome(is_headless=False)
    dv.get(caps_rank_url)

    ### 上位企業のcodeを手に入れてリスト「codes」に格納

    ### codesの各企業のURLにアクセス、月次テーブル、日次テーブルをnd配列で取得
    monthly_table = [[]]
    daily_table = [[]]
    
    #####【月次】monthly_table 
    ###　１．m_return_index = {'2017-01': [(時価総額,過去収益率,月間加重収益), ...], '2017-02': [(...)], ...}
    m_return_index = {}
    ###　２．各行から、「月情報」「時価総額」「過去収益率」「月間加重収益率」を計算
    ###
    mn_i = get_MN_index(monthly_table)
    sv_i = get_SV_index(monthly_table)
    cp_i = get_CP_index(monthly_table)
    op_i = get_OP_index(monthly_table)

    monthly_rows = monthly_table[1:]
    for row in monthly_rows:
        mn = make_dateId(row[mn_i])
        mc = row[sv_i]*
        pr = calc_PR(data)
        mr = calc_MR(row)
        mwr = calc_MWR(data)

    ###　３．

def make_MN(m_str):
    pass

def calc_MC(sv, cp):
    return sv*cp

def calc_PR()

def calc_MWR()

class StockIndexIterator(object):
    ### 月or日テーブル，それぞれの指標が何列目にあるかを示す辞書{'SV':0, 'CP': 2, ...}
    ### header_rowを除いたdata_rowsを渡す
    def __init__(self, data_rows, index_dict):
        self.data_rows = data_rows
        self.index_dict = index_dict
    
    def __iter__(self):
        return self
    
    def __next__(self):
        try:

            self.data_rows = self.data_rows[1:]
        except:
            raise StopIteration()
        return 

### class: 出来高（），終値（），月間加重収益率（）、月間収益率（）、過去収益率（）
###　から