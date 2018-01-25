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
import numpy as np
import pandas as pd

if __name__ == '__main__':
    kb = Kabutan(dv)
    caps_rank_url = "https://info.finance.yahoo.co.jp/ranking/?kd=4&tm=d&vl=a&mk=3"
    dv = launchChrome(is_headless=False)
    dv.get(caps_rank_url)

    ### TOPIX(code=0010)の月次テーブル取得
    topix_mon_rows = kb.get_data_by_code('0010', 'm')
    topix_mon_rows = pd.DataFrame(topix_mon_rows[1:], columns=topix_mon_rows[0])
    
    ### MC列を算出して列を追加
    t_mc_col = topix_mon_rows[:, t_cp_i]*topix_mon_rows[:, t_sv_i]
    t_mc_col = [[t] for t in t_mc_col]
    topix_mon_rows = np.hstack(topix_mon_rows, t_mc_col)
    t_mc_i = len(topix_mon_rows[0]) - 1

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
