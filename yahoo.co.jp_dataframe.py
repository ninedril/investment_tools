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

     ##### Variable
    LABELS = {
        'MN':'日付',
        'OP':'始値',
        'HP':'高値',
        'LP':'安値',
        'CP':'終値',
        'MMB':'前月比',
        'MMBP':'前月比％',
        'SV':'売買高(株)',
        'MC':'時価総額',
        'WR':'加重率',
        'MR':'月間収益率',
        'MWR':'月間加重収益率',
        'PR':'過去収益率',
        'T_MC':'TOPIX時価総額'
    }

    ### TOPIX(code=0010)の月次テーブル取得
    topix_mon_rows = kb.get_data_by_code('0010', 'm')
    topix_mon_df = pd.DataFrame(topix_mon_rows[1:], columns=topix_mon_rows[0])
    del topix_mon_rows
    
    ### DataFrameを整理し、各要素を数値化する
    ### OP, CP, SV
    def convert_to_numeric(f_str):
        f_str = f_str.replace(r',', '')
        if '.' in f_str:
            n = float(f_str)
        else:
            n = int(f_str)
        return n
    garbage_columns = [LABELS['HP'], LABELS['LP'], LABELS['MMB'], LABELS['MMBP']]
    topix_mon_df = topix_mon_df.drop(garbage_columns, axis=1)
    topix_mon_df = topix_mon_df.applymap(convert_to_numeric)
    topix_mon_df = topix_mon_df.astype({LABELS['OP']:'int32', LABELS['CP']:'int32', LABELS['SV']:'int32'})

    ### MC列を算出して列を追加
    topix_mon_df = topix_mon_df.assign(**{LABELS['T_MC'] : topix_mon_df[LABELS['CP']] * topix_mon_df[LABELS['SV']]})

    ### TOPIXの月次MN-MCテーブルを作る
    topix_mon_df = topix_mon_df[[LABELS['MN'], LABELS['T_MC']]]


    ### 上位企業のcodeを手に入れてリスト「codes」に格納
    company_codes = []
    
    ### 変数の用意
    ###　m_1st_indexes = {'2017-01': DataFrame(columns=時価総額,過去収益率,月間加重収益), ...], '2017-02': [(...)], ...}
    m_1st_indexes = defaultdict(pd.DataFrame)

    ##### codesループで各企業のURLにアクセス、月次テーブルをnd配列で取得
    
    #for code in codes:
    c_mon_rows = kb.get_data_by_code(code)
    c_mon_df = pd.DataFrame(c_mon_rows[1:], columns=c_mon_rows[0])
    del c_mon_rows

    ### DataFrameを整理し、各要素を数値化する
    ### OP, CP, SV
    c_mon_df = c_mon_df.drop(garbage_columns, axis=1)
    c_mon_df = c_mon_df.applymap(convert_to_numeric)
    c_mon_df = c_mon_df.astype({LABELS['OP']:'int32', LABELS['CP']:'int32', LABELS['SV']:'int32'})

    ### MC列を算出して列を追加
    c_mon_df = c_mon_df.assign(**{LABELS['MC'] : c_mon_df[LABELS['CP']] * c_mon_df[LABELS['SV']]})

    ### MR列を算出して列を追加
    c_mon_df = c_mon_df.assign(**{LABELS['MR'] : c_mon_df[LABELS['CP']] / c_mon_df[LABELS['OP']]})

    ### PR列を算出して列を追加
    pr_row = []
    for i, r in c_mon_df.iterrows():
        try:
            pr_row.append(c_mon_df.loc[i+2, LABELS['CP']] / c_mon_df.loc[i+11, LABELS['OP']] - 1)
        except KeyError:
            pr_row.append(pd.np.nan)
    c_mon_df = c_mon_df.assign(**{LABELS['PR']: pr_row})
    c_mon_df = c_mon_df.dropna(axis=0, how='any')

    ### c_mon_dfとtopix_mon_dfをMNをキーとして統合
    c_mon_df = pd.merge(c_mon_df, topix_mon_df, on=LABELS['MN'])

    ### WR列を算出して列を追加
    c_mon_df = c_mon_df.assign(**{LABELS['WR']: c_mon_df[LABELS['MC']] / c_mon_df[LABELS['T_MC']]})

    ### MWR列を算出して列を追加
    c_mon_df = c_mon_df.assign(**{LABELS['MWR']: c_mon_df[LABELS['MR']] * c_mon_df[LABELS['WR']]})

    ### 各行ループで、m_1st_indexesの　キー：MN　に　値：DataFrame（columns=[MC, PR, MWR]）　を追加
    for i, row in enumerate(monthly_rows):
        mn = row[mn_i]
        mc = row[mc_i]
        pr = row
        mwr = row

        m_1st_indexes[mn].append((mc, pr, mwr))

    ### m_1st_indexesの各キーループで、MCで並び替えてtop群、bottom群を作る

    ### top群、bottom群内でさらにPRによって3つに分け、top_top, top_middle, top_bottom, bottom_top, bottom_middle, bottom_bottomの6群を作る

    ### 6群のMWRをそれぞれ算出
