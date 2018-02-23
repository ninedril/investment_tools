#####
# arg1: specify company

##### Loading other libraries
import sys, os, re
sys.path.append(os.pardir)
from selenium_tools.function import *
from functions import *
from kabutan import Kabutan
#####

import csv
import numpy as np
import pandas as pd

class IndexCalculater:
    MN = '日付'
    OP = '始値'
    HP = '高値'
    LP = '安値'
    CP = '終値'
    MMB = '前月比'
    MMBP = '前月比％'
    SV = '売買高(株)'
    MC = '時価総額'
    WR = '加重率'
    MR = '月間収益率'
    MWR = '月間加重収益率'
    PR = '過去収益率'
    T_MC = 'TOPIX時価総額'

    AVE25 = '25日平均'
    DV = '乖離率'
    DVW = '乖離率変化幅'

    def __init__(self):
        self.company_codes = []
        self.dv = launchChrome(is_headless=False)
        self.kb = Kabutan(self.dv)
    def set_top_company_codes(self, codes):
        self.company_codes = codes
    def calc_1st_index(self):
        pass
    def calc_2nd_index(self):
        pass
    def calc_3rd_index(self):
        ### 変数チェック
        if not self.company_codes:
            print('No company codes. Set them.')
            return False
        
        ### メイン処理
        #　行：企業名、列：月　の過少反応傾向率（UR）テーブルmon_ur作成
        mon_ur = pd.DataFrame()
        #　各企業のコード名のリスト取得、各企業Xについて
        for code in self.company_codes:
            #　企業Xの日次テーブル取得
            df = self.kb.get_data_by_code(code, 'd')
            #　日付をTimestampに変換し、AVE25, DV, DVW列を算出して追加
            df = self.arrange_col_3rd(df)
            #　DVWが連続しているものを25日ずつそれぞれ合計し、各月URを算出
            ur_row = self.make_mon_ur_row(df)
            ur_row.name = code
            #　mon_urにXの月ごとのURを行として追加
            mon_ur.append(ur_row)
        return mon_ur

    # DataFrame => DataFrame
    def arrange_col_3rd(self, df):
        df = self.set_MN_to_TS(df)
        df = self.set_AVE25(df)
        df = self.set_DV(df)
        df = self.set_DVW(df)
        return df
    # DataFrame => DataFrame
    def set_MN_to_TS(self, df):
        df = df.assign(**{self.MN: pd.to_datetime(df[self.MN], yearfirst=True)})
        return df
    # DataFrame => DataFrame
    def set_AVE25(self, df):
        row_AVE25 = []
        for i, r in df.iterrows():
            try:
                row_AVE25.append(df.loc[i:i+25, self.CP].mean())
            except:
                row_AVE25.append(df.loc[i:, self.CP].mean())
        df = df.assign(**{self.AVE25: row_AVE25})
        return df
    # DataFrame => DataFrame
    def set_DV(self, df):
        row_DV = df[self.CP]/df[self.AVE25] - 1
        df = df.assign(**{self.DV: row_DV})
        return df
    # DataFrame => DataFrame
    def set_DVW(self, df):
        row_DVW = df[self.DV].diff(-1)
        df = df.assign(**{self.DVW: row_DVW}).dropna(axis=0, how='any')
        return df
    
    # DataFrame => Series
    def make_mon_ur_row(self, df):
        grouped = df[self.DVW].groupby(lambda i: df.loc[i, self.MN].month)
        result = grouped.apply(self.calc_ur_in_series)
        return result
    # Series => int
    def calc_ur_in_series(self, s):
        df = pd.DataFrame(s, columns=['original'])
        # True, False
        df = df.assign(**{'is_pos': df['original'] > 0})
        #　連続値カウント
        seq_c = self.count_seq(df['is_pos'])
        # dfにseq_c追加
        df = df.assign(**{'seq_c': seq_c})
        # 列seq_cが > 0　である行の　列originalを全加算
        result = df[df[seq_c] > 0]['original'].sum()
        return result
    # Series => Series
    def count_seq(self, s):
        result = []
        for n, g in itertools.groupby(s):
            result.extend(range(g))
        return pd.Series(result)



if __name__ == '__main__':
    #caps_rank_url = "https://info.finance.yahoo.co.jp/ranking/?kd=4&tm=d&vl=a&mk=3"
    dv = launchChrome(is_headless=False)
    kb = Kabutan(dv)
    #dv.get(caps_rank_url)

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
    #=====# topix_mon_rows = kb.get_data_by_code('0010', 'm')
    topix_mon_df = pd.read_csv('0010_m.csv', engine='python')
    #=====# topix_mon_df = pd.DataFrame(topix_mon_rows[1:], columns=topix_mon_rows[0])
    #=====# del topix_mon_rows
    
    ### DataFrameを整理し、各要素を数値化する
    ### OP, CP, SV
    def convert_to_numeric(f_str):
        f_str = f_str.replace(r',', '')
        if re.search(r'[^\d.+-]', f_str):
            return f_str
        elif '.' in f_str:
            return float(f_str)
        else:
            return int(f_str)
    garbage_columns = [LABELS['HP'], LABELS['LP'], LABELS['MMB'], LABELS['MMBP']]
    topix_mon_df = topix_mon_df.drop(garbage_columns, axis=1)
    topix_mon_df = topix_mon_df.applymap(convert_to_numeric)
    topix_mon_df = topix_mon_df.astype({LABELS['OP']:'int32', LABELS['CP']:'int32', LABELS['SV']:'int32'})

    ### MC列を算出して列を追加
    topix_mon_df = topix_mon_df.assign(**{LABELS['T_MC'] : topix_mon_df[LABELS['CP']] * topix_mon_df[LABELS['SV']]})

    ### TOPIXの月次MN-MCテーブルを作る
    topix_mon_df = topix_mon_df[[LABELS['MN'], LABELS['T_MC']]]


    ### 上位企業のcodeを手に入れてリスト「codes」に格納
    company_codes = ['7203', '8306', '9432', '9437', '9984', '6861', '2914', '9433', '7267', '8316']
    
    ### 変数の用意
    ###　m_1st_indexes = {'2017-01': DataFrame(columns=時価総額,過去収益率,月間加重収益), ...], '2017-02': [(...)], ...}
    m_1st_indexes = defaultdict(lambda: pd.DataFrame(columns=[LABELS['MC'], LABELS['PR'], LABELS['MWR']]))
    ###　各月の指標値を格納する結果のSeriesを作る
    result_1st = pd.Series(index=[LABELS['MN']], name='各月のMWR合計（グループ毎）')

    #result_2nd = pd.Series(index=[LABELS['MN']], name='各月のMWR（全体）')
    result_2nd = defaultdict(int)

    ##### codesループで各企業のURLにアクセス、月次テーブルをnd配列で取得
    for code in company_codes:
        c_mon_rows = kb.get_data_by_code(code, 'm')
        c_mon_df = pd.DataFrame(c_mon_rows[1:], columns=c_mon_rows[0])
        del c_mon_rows
        #=====# c_mon_df = pd.read_csv('7203_m.csv', engine='python')

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
        for i, r in c_mon_df.iterrows():
            mn = r[LABELS['MN']]
            ########### 1st Index Process
            m_1st_indexes[mn] = m_1st_indexes[mn].append({
                LABELS['MC']: r[LABELS['MC']],
                LABELS['PR']: r[LABELS['PR']],
                LABELS['MWR']: r[LABELS['MWR']]
            }, ignore_index=True)
            ########### END

            ########### 2nd Index Process
            result_2nd[mn]+=r[LABELS['MWR']]
            ########### END
        
    ########### 1st Index Process
    ### m_1st_indexesの各キーループ
    for m, df in m_1st_indexes.items():
        # MCで降順
        df = df.sort_values(by=LABELS['MC'], ascending=False)
        # top, bottomに分ける
        top_g_l = round(len(df.index)/2)
        top_g, bottom_g = df.iloc[:top_g_l], df.iloc[-top_g_l:]

        # PRで降順
        top_g = top_g.sort_values(by=LABELS['PR'], ascending=False)
        bottom_g = bottom_g.sort_values(by=LABELS['PR'], ascending=False)
        #　topをtop_top, top_bottomに分ける
        top_top_g_l = round(len(top_g.index)*0.3)
        top_top_g, top_bottom_g = top_g.iloc[:top_top_g_l], top_g.iloc[-top_top_g_l:]
        #　bottomをbottom_top, bottom_bottomに分ける
        bottom_top_g, bottom_bottom_g = bottom_g.iloc[:top_top_g_l], bottom_g.iloc[-top_top_g_l:]

        # top_top_mwr, top_bottom_mwr, bottom_top_mwr, bottom_bottom_mwrを出す
        top_top_mwr = top_top_g[LABELS['MWR']].sum()
        top_bottom_mwr = top_bottom_g[LABELS['MWR']].sum()
        bottom_top_mwr = bottom_top_g[LABELS['MWR']].sum()
        bottom_bottom_mwr = bottom_bottom_g[LABELS['MWR']].sum()

        # MWR指標値を算出
        mwr_i = ((top_top_mwr+bottom_top_mwr)-(top_bottom_mwr+bottom_bottom_mwr))/2
        result_1st[m] = mwr_i
    ########### END
    
    result_1st.to_csv('1st_index.csv')
    pd.Series(result_2nd, name='各月のMWR（全体）').to_csv('2nd_index.csv')
    exit_driver(dv)
    sys.exit(0)