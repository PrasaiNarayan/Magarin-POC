import pandas as pd

KO=pd.read_csv('KO_planning.csv',encoding='utf_8_sig')
FK=pd.read_csv('FK_planning.csv',encoding='utf_8_sig')
MK=pd.read_csv('MK_planning.csv',encoding='utf_8_sig')

KO=KO[['品名','チケットＮＯ','生産日','納期_copy']]
FK=FK[['品名','チケットＮＯ','生産日','納期_copy']]

MK=MK[['品名','チケットＮＯ','生産日','納期_copy']]

# print(KO)

# Check for チケットＮＯ with multiple 生産日
# duplicate_ticket_no = MK.groupby('チケットＮＯ')['生産日'].nunique()

# # Filter those チケットＮＯ where 生産日 count is more than 1
# duplicate_ticket_no = duplicate_ticket_no[duplicate_ticket_no > 1]

# # Display the チケットＮＯ that have multiple 生産日
# print(duplicate_ticket_no)
unused_data_planning = pd.read_csv('unused_data_planning.csv',encoding='utf_8_sig')

unused_data_planning=unused_data_planning[['品名','チケットＮＯ','生産日','納期_copy']]

result = pd.merge(MK, unused_data_planning, on='チケットＮＯ', how='inner')
result.to_csv('inner_joins.csv',encoding='utf_8_sig',index=False)
print(result)