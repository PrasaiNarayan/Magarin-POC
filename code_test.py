# magarin_code=[]
# shortening_Code=[]
# order_data_code=[]

# import pandas as pd

# # order_data=pd.read_csv('order.csv')
# # order_data_code=order_data['品目コード'].values

# # print(order_data_code)

# import pandas as pd
# from datetime import datetime
# from time import sleep

# # Load the Excel file
# file_path = '鹿島東_生産調整依頼書202403.xlsx'#'鹿島東西生産依頼202403-05.xlsx'
# xls = pd.ExcelFile(file_path)
# # Load the '東' sheet starting from row 8
# df_east = pd.read_excel(xls, sheet_name='東', header=6)
# # print(df_east)
# # df_east.to_csv('head.csv',encoding='cp932',index=False)

# column_mapping = {
#     0:'繰上不可(×）',
#     2: '依頼日',
#     3: 'コード',
#     4: '品名',
#     5: '入目',
#     6: '荷姿',
#     7: 'UOT',
#     8: '増t',
#     9: '増ﾊﾞｯﾁ数',
#     10: '減t',
#     11: '減ﾊﾞｯﾁ数',
#     12: '生産',
#     13: '倉入',
#     16: '包材',
# }

# # Rename columns using the dictionary
# df_east.columns = [column_mapping.get(i, col) for i, col in enumerate(df_east.columns)]

# selected_columns = list(column_mapping.values())
# df_east_filtered = df_east[selected_columns]


# df_east_filtered = df_east_filtered.applymap(lambda x: x.strip() if isinstance(x, str) else x)
# df_east_filtered.replace('', pd.NA, inplace=True)

# # # Drop rows where all values are NaN
# # df_east_filtered.to_csv('before_dropping_nan.csv',encoding='cp932',index=False)
# df_east_filtered.dropna(how='all', inplace=True)
# # Display the final DataFrame with only the selected columns
# print(df_east_filtered.head())
# df_east_filtered.to_csv('after_dropping_nan.csv',encoding='cp932',index=False)

# order_data=pd.DataFrame(columns=['繰上不可(×）','品目コード','品名','入目','予定数量(㎏)','納期','チケットＮＯ'])

# def is_datetime(value):
#     return isinstance(value, (pd.Timestamp, datetime))

# # Function to parse custom date formats
# def parse_custom_date(date_str):
#     try:
#         return datetime.strptime(date_str, '%m/%d%p')  # Handling '2/7PM' format
#     except ValueError:
#         pass
#     try:
#         return datetime.strptime(date_str, '%Y-%m-%d')
#     except ValueError:
#         pass
#     return None


# for ind,row in df_east_filtered.iterrows():

#     weight=0
#     pre_deadline=None
#     val=row['繰上不可(×）']
#     print(f'checking {val}')
#     print(is_datetime(row['繰上不可(×）']))

#     if is_datetime(row['繰上不可(×）']):
#         pre_deadline=row['繰上不可(×）']
    

    
#     if not pd.isna(row['増t']) and not pd.isna(row['増ﾊﾞｯﾁ数']):
#         weight=row['増t']*row['増ﾊﾞｯﾁ数']*1000

#     # elif not pd.isna(row['減t']) and not pd.isna(row['減ﾊﾞｯﾁ数']):
#     #     weight=row['減t']*row['減ﾊﾞｯﾁ数']*1000
#     else:
#         continue

    
#     # if isinstance(row.コード,str):
#     #     continue

#     noukistr=None
#     date_format = '%Y-%m-%d'
#     if not pd.isna(row['倉入']):       
#         nouki=datetime.strptime(str(row['倉入']).split()[0],date_format)
#         print(nouki)
#         print(str(nouki.year)+str(nouki.month).zfill(2)+str(nouki.day).zfill(2))
#         noukistr=str(nouki.year)+str(nouki.month).zfill(2)+str(nouki.day).zfill(2)
#         # exit()

#     elif not pd.isna(row['生産']):
#         # date_format = '%Y%m%d'
#         try:
#             nouki=datetime.strptime(str(row['生産']).split()[0],date_format)
#             noukistr=str(nouki.year)+str(nouki.month).zfill(2)+str(nouki.day).zfill(2)
#         except:
#             print('in continue')
#             sleep(3)
#             continue



#     order_data=order_data.append({'繰上不可(×）':pre_deadline,
#                                   '品目コード':str(row.コード),
#                                   '品名':row.品名,
#                                   '入目':row.入目,
#                                   '予定数量(㎏)':int(weight),
#                                   '納期':noukistr,
#                                   'チケットＮＯ':None,
#                                   },
#                                   ignore_index=True)


# order_data_code=order_data['品目コード'].tolist()

# print(order_data_code)




# shortening_data=pd.read_csv('shortening_code.csv')
# shortening_Code=shortening_data['品目コード'].tolist()
# print(shortening_Code)

# magarin_data=pd.read_csv('magarin_code.csv')
# magarin_Code=magarin_data['品目コード'].tolist()
# print(magarin_Code)

# allcpdes=magarin_Code+shortening_Code
# missing_code=[]
# for ele in order_data_code:
#     if ele not in allcpdes and ele not in missing_code:
#         missing_code.append(ele)

# column_name='品目コード'
# df = pd.DataFrame(missing_code, columns=[column_name])
# df.to_csv('Missing_codes.csv',index=False,encoding='cp932')

# merged_df = pd.merge(df, order_data, on='品目コード', how='left')

# df_no_duplicates = merged_df.drop_duplicates(subset='品目コード')
# df_no_duplicates.to_csv('Missing_codes_with_names.csv',index=False,encoding='cp932')
# print(df_no_duplicates)


# from datetime import datetime
# from itertools import groupby

# class Order:
#     def __init__(self, 品名, 納期_copy):
#         self.品名 = 品名
#         self.納期_copy = 納期_copy

#     def __repr__(self):
#         return f"Order(品名={self.品名}, 納期_copy={self.納期_copy})"

# def sort_orders(orders):
#     result = []
#     for key, group in groupby(orders, key=lambda x: x.品名):
#         sorted_group = sorted(group, key=lambda x: x.納期_copy)
#         for ele in sorted_group:
#             print(ele.品名,ele.納期_copy)
#             # print('each')
#         print('nestS')

#         result.extend(sorted_group)
#     return result

# # Example usage:
# orders = [
#     Order("Product B", datetime(2024, 8, 6)),
#     Order("Product A", datetime(2024, 8, 5)),
#     Order("Product A", datetime(2024, 8, 3)),
#     Order("Product A", datetime(2024, 8, 4)),
#     Order("Product B", datetime(2024, 8, 7)),
# ]

# sorted_orders = sort_orders(orders)

# # Output the sorted list
# for order in sorted_orders:
#     print(order)


# def starts_with_any(string, prefixes):
#     for prefix in prefixes:
#         if string.startswith(prefix):
#             return True
#     return False

# # Example usage
# string = "hello world"
# prefixes = ["h", "hi", "helo"]

# result = starts_with_any(string, prefixes)
# print(result)  # Output: True

# def xor_gate(a, b):
#     return (a or b) and not (a and b)

# # Example usage
# print(xor_gate(True, True))   # Output: False
# print(xor_gate(False, False)) # Output: False
# print(xor_gate(True, False))  # Output: True
# print(xor_gate(False, True))  # Output: True
def starts_with_any(string, prefixes):
    for prefix in prefixes:
        if string.startswith(prefix):
            return True
    return False
prefixes_with_two_hrs=['ｱﾛﾏ-ﾃﾞﾏｲﾙﾄﾞｽﾗｲｽDG','ｵﾘﾝﾋﾟｱｽﾗｲｽ(ｽｲｰﾄﾐﾙｸ)','ｵﾘﾝﾋﾟｱﾒﾛ-ｼ-ﾄ(ｽｲ-ﾄ)','ｵﾘﾝﾋﾟｱｸﾚ-ﾙ(ｽﾗｲｽ)',
                                       'ｶﾚﾝﾃｲｼ-ﾄ(ｽｲ-ﾄ)','ｵﾘﾋﾟｱﾅﾁﾕﾗﾙｼ-ﾄ','ｵﾘﾝﾋﾟｱCLｼ-ﾄ20','Pｼ-ﾄDB-R']

current_start1=starts_with_any('ｵﾘﾝﾋﾟｱANｼ-ﾄ1.7K(M)' ,'ｵﾘﾝﾋﾟｱANｼ-ﾄ1.7K(M)')
current_start2=starts_with_any('ｵﾘﾝﾋﾟｱANｼ-ﾄ1.7K(M)', prefixes_with_two_hrs)
current_start= current_start1 and current_start2
print(current_start1,current_start2,current_start)

