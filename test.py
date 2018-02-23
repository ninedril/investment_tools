import pandas as pd
import re

def convert_to_numeric(f_str):
	f_str = f_str.replace(r',', '')
	if re.search(r'[^\d.+-]', f_str):
		return f_str
	elif '.' in f_str:
		return float(f_str)
	else:
		return int(f_str)

def test(file_name, row_num=10):
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
		'PR':'過去収益率'
	}
	df = pd.read_csv(file_name, engine='python')
	df = df.head(row_num)
	garbage_columns = [LABELS['HP'], LABELS['LP'], LABELS['MMB'], LABELS['MMBP']]
	df = df.drop(garbage_columns, axis=1)
	df = df.applymap(convert_to_numeric)

	### MNカラム以外のカラムのデータ型をint32に
	df = df.astype({LABELS['OP']:'int32', LABELS['CP']:'int32', LABELS['SV']:'int64'})

	return df

def calc_1st_index(df):
	###　MCで降順に並び替え
	df = df.sort_values(by=LABELS[''])
	###　上位グループと下位グループに分ける
	###　上中下グループに分ける
	###　指標計算