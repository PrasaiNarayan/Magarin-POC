import pandas as pd
from datetime import datetime
from time import sleep

# Load the Excel file
file_path ='鹿島東西生産依頼202403-05.xlsx'#'鹿島東西生産依頼202403-05.xlsx'
xls = pd.ExcelFile(file_path)
# Load the '東' sheet starting from row 8
df_east = pd.read_excel(xls, sheet_name='西', header=6)

column_mapping = {
    0:'繰上不可(×）',
    2: '依頼日',
    3: 'コード',
    4: '品名',
    5: '入目',
    6: '荷姿',
    7: 'UOT',
    8: '増t',
    9: '増ﾊﾞｯﾁ数',
    10: '減t',
    11: '減ﾊﾞｯﾁ数',
    12: '生産',
    13: '倉入',
    16: '包材',
}

# Rename columns using the dictionary
df_east.columns = [column_mapping.get(i, col) for i, col in enumerate(df_east.columns)]

selected_columns = list(column_mapping.values())
df_east_filtered = df_east[selected_columns]


df_east_filtered = df_east_filtered.applymap(lambda x: x.strip() if isinstance(x, str) else x)
df_east_filtered.replace('', pd.NA, inplace=True)

df_east_filtered.to_csv('before_dropping_nan.csv',encoding='cp932',index=False)

# # Drop rows where all values are NaN
# df_east_filtered.to_csv('before_dropping_nan.csv',encoding='cp932',index=False)
df_east_filtered.dropna(how='all', inplace=True)
# Display the final DataFrame with only the selected columns
# print(df_east_filtered.head())
df_east_filtered.to_csv('after_dropping_nan.csv',encoding='cp932',index=False)

order_data=pd.DataFrame(columns=['繰上不可(×）','依頼日','品目コード','品名','入目','予定数量(㎏)','納期','チケットＮＯ'])

def is_datetime(value):
    return isinstance(value, (pd.Timestamp, datetime))

# Function to parse custom date formats
def parse_custom_date(date_str):
    try:
        return datetime.strptime(date_str, '%m/%d%p')  # Handling '2/7PM' format
    except ValueError:
        pass
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        pass
    return None


for ind,row in df_east_filtered.iterrows():
    weight=0
    pre_deadline=None
    val=row['繰上不可(×）']
    print(f'checking {val}')
    print(is_datetime(row['繰上不可(×）']))

    if is_datetime(row['繰上不可(×）']):
        pre_deadline=row['繰上不可(×）']

    if pd.isna(row['増t']) or pd.isna(row['増ﾊﾞｯﾁ数']):
        continue

    for i in range(0,int(row['増ﾊﾞｯﾁ数'])):

        weight=row['増t']*1000#row['増t']*row['増ﾊﾞｯﾁ数']*1000

        if row.コード=='稟議中':
            continue

        noukistr=None
        date_format = '%Y-%m-%d'
        if not pd.isna(row['倉入']):       
            nouki=datetime.strptime(str(row['倉入']).split()[0],date_format)
            noukistr=str(nouki.year)+str(nouki.month).zfill(2)+str(nouki.day).zfill(2)
            # exit()

        if not pd.isna(row['生産']):
            # date_format = '%Y%m%d'
            pre_deadline=row['生産']
            try:
                nouki=datetime.strptime(str(row['生産']).split()[0],date_format)
                noukistr=str(nouki.year)+str(nouki.month).zfill(2)+str(nouki.day).zfill(2)
            except:
                print('in continue')
                sleep(3)
                continue

        
        ticket_number='A'+str(ind)+str(i)+'00'
        print(f'the ticket number is :{ticket_number}')

        order_data=order_data.append({'繰上不可(×）':pre_deadline,
                                    '依頼日':row.依頼日,
                                    '品目コード':row.コード,
                                    '品名':row.品名,
                                    '入目':row.入目,
                                    '予定数量(㎏)':int(weight),
                                    '納期':noukistr,
                                    'チケットＮＯ':ticket_number,
                                    },
                                    ignore_index=True)
    

order_data.to_csv('whip_cream.csv',index=False,encoding='cp932')