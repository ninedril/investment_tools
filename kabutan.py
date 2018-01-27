#####
# arg1: specify company

##### Loading other libraries
import sys, os, re
sys.path.append(os.pardir)
from selenium_tools.function import *
import functions
#####
import csv

#import pdb; pdb.set_trace()

#################################### Class #####################################
################################################################################
class Kabutan:
    ####################
    ### FIELDS
    ####################
    LOCATORS = {
        'company_search_box':'//input[@id="input_id"]',
        'company_search_results':'div#kensaku_kekka ul li a',
        'price_table':'//div[@id="stock_kabuka_table"]//table[count(.//tr) > 9]', 
        'next_table_link': '//a[text()="次へ＞"]'
    }
    BASE_URL = 'https://kabutan.jp/'
    
    ####################
    ### CLASS METHODS
    ####################
    def set_locator(loc_key, loc_value):
        Kabutan.LOCATORS[loc_key] = loc_value
    
    def make_url(**kw):
        # kw = {'code':1000, 'term':'m'}
        url = Kabutan.BASE_URL + 'stock/kabuka?'
        if 'code' in kw:
            url = url + 'code=' + str(kw['code'])
        
        if 'term' in kw:
            if kw['term'] == 'm':
                url = url + '&ashi=mon'
            elif kw['term'] == 'w':
                url = url + '&ashi=wek'
        
        return url
    
    ####################
    ### INSTANCE METHODS
    ####################
    def __init__(self, wd):
        self.wd = wd

    # WebDriver => void
    def set_driver(self, wd):
        self.wd = wd

    # String, String => List
    def get_data_by_name(self, company_name, term):
        self.wd.get(Kabutan.BASE_URL)
        self.search_by_company(company_name)
        result_companies = self.wd.find_elements_by_xpath(Kabutan.LOCATORS['company_search_results'])
        result_companies[0].click()
        
        code = functions.get_url_value(self.wd.current_url, 'code')
        all_datas = self.get_data_by_code(code, term)
        return all_datas

    # String, String => List
    def get_data_by_code(self, company_code, term):
        data_url = Kabutan.make_url(code=company_code, term=term)
        self.wd.get(data_url)
        all_datas = functions.get_all_table_datas(self.wd, Kabutan.LOCATORS['price_table'], Kabutan.LOCATORS['next_table_link'])
        return all_datas

    # WevDriver => void
    def search_by_company(self, company_name):
        s_box = self.wd.find_element_by_xpath(Kabutan.LOCATORS['company_search_box'])
        s_box.send_keys(company_name)
        s_box.submit()


#################################### Main ######################################
################################################################################
if __name__ == '__main__':
    company = sys.argv[1]
    term = sys.argv[2]

    try:
        term = re.match(r'^-{1,2}(\w)$', term, re.IGNORECASE).group(1)
    except:
        print('Invalid Argument')
        sys.exit(0)
    
    #dv = launchChrome(is_headless=True)
    dv = launchChrome(is_headless=False)

    kb = Kabutan(dv)
    try:
        if re.match(r'^\d+$', company):
            all_datas = kb.get_data_by_code(company, term)
        else:
            all_datas = kb.get_data_by_name(company, term)
    except Exception as e:
        raise(e)
    finally:
        exit_driver(dv)
    
    functions.make_csv_from(all_datas, company + '_' + term + '.csv')