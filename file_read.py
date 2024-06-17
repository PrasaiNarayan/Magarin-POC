import pandas as pd
import datetime

fk=pd.read_csv("KO_planning.csv",encoding='utf_8_sig')
fk['line']='FK'
mk=pd.read_csv("MK_planning.csv",encoding='utf_8_sig')
mk['line']='MK'
ko=pd.read_csv("KO_planning.csv",encoding='utf_8_sig')
ko['line']='KO'






# fk['納期_copy']=pd.to_datetime(fk['納期_copy'])
# mk['納期_copy']=pd.to_datetime(mk['納期_copy'])
# ko['納期_copy']=pd.to_datetime(ko['納期_copy'])

# fk['生産日']=pd.to_datetime(fk['生産日'])
# mk['生産日']=pd.to_datetime(mk['生産日'])
# ko['生産日']=pd.to_datetime(ko['生産日'])


# fk=fk[fk['納期_copy']<=datetime.datetime(2023,4,6)]
# fk=fk[fk['生産日']>datetime.datetime(2023,3,22)]

# mk=mk[mk['納期_copy']<=datetime.datetime(2023,4,6)]
# mk=mk[mk['生産日']>datetime.datetime(2023,3,23)]

# ko=ko[ko['納期_copy']<=datetime.datetime(2023,4,6)]
# ko=ko[ko['生産日']>datetime.datetime(2023,3,22)]
# ko=ko[ko['KOスライス製品']!='○']

ko=ko.append(mk)
ko=ko.append(fk)

#生産日	start	end

cols = ko.columns.tolist()
cols.insert(0, cols.pop(cols.index('生産日')))
cols.insert(1, cols.pop(cols.index('start')))
cols.insert(2, cols.pop(cols.index('end')))
cols.insert(3, cols.pop(cols.index('end')))
ko = ko[cols]




ko.to_csv('all_data.csv',index=False,encoding='utf_8_sig')