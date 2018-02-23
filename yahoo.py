#####
# arg1: specify company

##### Loading other libraries
import sys, os
sys.path.append(os.pardir)
from selenium_tools.function import *
from functions import *
from kabutan import Kabutan
#####

import csv
import pandas as pd
import traceback


#################################### Funcs #####################################
################################################################################
def get_topMC_company_codes(num=-1, wd=None):
    ###　引数のチェック
    if not wd:
        wd = launchChrome(is_headless=False)
    
    ###　初期変数の設定
    topMC_company_url = "https://info.finance.yahoo.co.jp/ranking/?kd=4&tm=d&vl=a&mk=3"
    loc = {
        'table': '//table[@class="rankingTable"]',
        'nextlink': '//a[text()="次へ"]'
    }
    CODE = 'コード'

    ###　メイン処理
    try:
        wd.get(topMC_company_url)
        rows = get_table_datas(wd, loc['table'], loc['nextlink'], num)
        
        result = list(pd.DataFrame(rows[1:], columns=rows[0])[CODE])
        return result
    except:
        traceback.print_exc()
    finally:
        exit_driver(wd)