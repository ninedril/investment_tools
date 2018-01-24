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

    ### TOPIX(code=0010)の月次テーブル取得
    topix_mon_rows = np.array([[]])[1:]
    t_mn_i = 0
    t_cp_i = 4
    t_sv_i = 7

    ### MC列を算出して列を追加
    t_mc_col = topix_mon_rows[:, t_cp_i]*topix_mon_rows[:, t_sv_i]
    t_mc_col = [[t] for t in t_mc_col]
    topix_mon_rows = np.hstack(topix_mon_rows, t_mc_col)
    t_mc_i = len(topix_mon_rows[0]) - 1

    ### MN列を標準化
    std_mn(topix_mon_rows, t_mn_i)

    ### TOPIXの月次MN-MCテーブルを作る
    topix_mc_rows = np.hstack([[m] for m in topix_mon_rows[:, t_mn_i]], topix_mon_rows[:, t_mc_i])

    ### 上位企業のcodeを手に入れてリスト「codes」に格納
    company_codes = []
    
    ### 変数の用意
    ###　m_1st_indexes = {'2017-01': [(時価総額,過去収益率,月間加重収益), ...], '2017-02': [(...)], ...}
    m_1st_indexes = defaultdict(dict())

    ### codesループで各企業のURLにアクセス、月次テーブル、日次テーブルをnd配列で取得
    monthly_rows = np.array([[]])[1:]
    daily_rows = [[]]

    #####【月次】monthly_rows
    mn_i = 0
    sv_i = 5
    cp_i = 4
    op_i = 1

    ### MC列を算出して列を追加
    mc_col = monthly_rows[:, cp_i]*monthly_rows[:, sv_i]
    mc_col = [[t] for t in mc_col]
    monthly_rows = np.hstack(monthly_rows, mc_col)
    mc_i = len(monthly_rows[0]) - 1

    ### MN列を標準化
    std_mn(monthly_rows, mn_i)

    ### MR列を算出して列を追加
    monthly_rows, mr_i = add_mr(monthly_rows, op_i, cp_i)

    ### monthly_rowsとtopix_mon_rowsをMNをキーとして統合
    monthly_rows = join_tables_by(mn_i, monthly_rows, topix_mc_rows)


    ### 各行ループで、m_1st_indexesの　キー：MN　に　値：（MC, PR, MWR）　を追加
    for i, row in enumerate(monthly_rows):
        mn = row[mn_i]
        mc = row[mc_i]
        pr = row
        mwr = row

        m_1st_indexes[mn].append((mc, pr, mwr))

    ### m_1st_indexesの各キーループで、タプル配列をMCで並び替えてtop群、bottom群を作る

    ### top群、bottom群内でさらに3つに分け、top_top, top_middle, top_bottom, bottom_top, bottom_middle, bottom_bottomの6群を作る

    ### 6群を用いて指標値を算出する
