#####
# arg1: specify company

from function import *
import csv

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
        result_companies = wd.find_elements_by_css_selector('div#kensaku_kekka ul li')
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
    elif term_flag == 'm'
        term = '月間株価':
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

# WebDriver => Dict
def get_price_table(wd):
    result = {}
    #find table and tr
    table = wd.find_elements_by_css_selector('table.srock_kabuka2')[0]
    header_row = table.find_elements_by_tag_name('tr')[0]

    #register th
    labels = list(map(lambda e: e.text, header_row.find_elements_by_tag_name('th')))
    result = {k: [] for k in labels}


    #loop
    while True:
        data_rows = table.find_elements_by_tag_name('tr')[1:]
        for row in data_rows:
            datas = list(map(lambda e: e.text, row.find_elements_by_tag_name('td')))
            for k in result:
                result[k].append()
        # click next
    #each 
    return {}


if __name__ == '__main__':
    #set variable
    target_url = 'https://kabutan.jp/'
    company = sys.argv[1]
    
    dv = launchChrome()
    dv.get(target_url)
    search_by_company(dv, company)
    
    get_result_companies_link(dv)[0].click()

    get_company_stock_price_link(dv).click()

    get_company_stock_price_link_by_time(dv, 'w').click()


    