import csv
import math
from datetime import datetime, timedelta
import pandas as pd
import priority_replanning
import ganttchart
import random
import copy
import sys
from time import sleep


class FirstClass:
    def __init__(self, row_data):
        self.read_csv_and_set_attributes(row_data)

    def read_csv_and_set_attributes(self, row_data):
        for key, value in row_data.items():
            setattr(self, key, value)

class SecondClass():
    # def __init__(self, row_data, first_class):
    #     # self.first_class = first_class
    #     self.read_csv_and_set_attributes(row_data,first_class)

    def __init__(self, attributes=None, first_class=None):
        if attributes is not None:
            self.set_attributes(attributes)
        if first_class is not None:
            self.read_csv_and_set_attributes(attributes, first_class)

    def set_attributes(self, attributes):
        # print(attributes)
        for key, value in attributes.items():
            setattr(self, key, value)



    def read_csv_and_set_attributes(self, row_data,first_class):
        if str(row_data['品目コード']) == str(first_class.品目コード):#self.first_class.品目コード:
            for key, value in row_data.items():
                setattr(self, key, value)
            for key, value in first_class.__dict__.items():#self.first_class.__dict__.items():
                if key != '品目コード':
                    setattr(self, key, value)


    def split_if_needed(self,split_weight):
        # Get the current weight and convert to int
        weight = int(float(getattr(self, '予定数量(㎏)')))

        # If weight is over 6000, split it
        if weight > split_weight:
            # Calculate the maximum weight per instance, which should be a multiple of 12 and not exceed 6000
            max_weight_per_instance = split_weight

            # Find the largest multiple of 12 that is less than or equal to max_weight_per_instance
            weight_per_instance = (max_weight_per_instance // 12) * 12

            # Calculate the number of instances needed
            num_instances = weight // weight_per_instance

            # If there's a remainder, we need one more instance to cover the remaining weight
            if weight % weight_per_instance != 0:
                num_instances += 1

            # Create the new instances
            instances = []
            for i in range(num_instances):
                attributes = self.__dict__.copy()

                if i == num_instances - 1:  # Last instance
                    # Remaining weight for the last instance
                    attributes['予定数量(㎏)'] = weight % weight_per_instance or weight_per_instance
                else:
                    attributes['予定数量(㎏)'] = weight_per_instance

                new_instance = SecondClass(attributes)
                instances.append(new_instance)

            return instances

        # If not, return the instance itself
        return [self]
    
class Date_Class:
    def __init__(self,each_date,every_line_break_pattern):
        self.date=each_date
        self.every_line_break_pattern=every_line_break_pattern

        self.UDF=0
        self.old_UDF=0
        if len(every_line_break_pattern['KO_break_pattern']):
            self.UDF=1  
            self.old_UDF=1 

    
def resetting_instances_attributes(objects_with_inherited_features):
        for eachobject in objects_with_inherited_features:
            setattr(eachobject,'get_used',0)
            setattr(eachobject,'生産日',None)
            setattr(eachobject,'start',None)
            setattr(eachobject,'end',None)
            setattr(eachobject,'pushed_forward',0)
            setattr(eachobject,'ko_remark',False)
            setattr(eachobject,'break',0)
            if hasattr(eachobject, '順番'):
                delattr(eachobject, '順番')
            if hasattr(eachobject, 'slot'):
                delattr(eachobject, 'slot')

            if hasattr(eachobject, 'day'):
                delattr(eachobject, 'day')



def create_csv_from_objects_unmerged(file_name, objects):
    if not objects:
        return

    fieldnames = list(objects[0].__dict__.keys())
    # print(fieldnames)

    # if 'first_class' in fieldnames:
    #     fieldnames.remove('first_class')

    with open(file_name, 'w', newline='',encoding='utf_8_sig') as csvfile:
    # with open(file_name, 'w', newline='',encoding='cp932') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for obj in objects:
           
            if hasattr(obj, 'KOスライス製品') and getattr(obj, 'KOスライス製品') =='○' and hasattr(obj, 'break') and getattr(obj, 'break') == 1:
                # if hasattr(obj, 'break') and getattr(obj, 'break') == 1:
                    # Write an empty line
                writer.writerow({})
                writer.writerow(obj.__dict__)

                # else

            else:

                writer.writerow(obj.__dict__)
                # Check if the 'break' attribute exists and is set to 1
                if hasattr(obj, 'break') and getattr(obj, 'break') == 2 and hasattr(obj, 'KOスライス製品') and getattr(obj, 'KOスライス製品') =='○':
                    # Write an empty line
                    writer.writerow({})

                if  hasattr(obj, 'break') and getattr(obj, 'break') == 1:
                    # Write an empty line
                    writer.writerow({})
        

def create_csv_from_objects(file_name, objects, df=None):
    if not objects:
        return

    # Convert objects to a DataFrame
    objects_df = pd.DataFrame([obj.__dict__ for obj in objects])

    # Merge the objects DataFrame with the original DataFrame
    merged_df = pd.concat([df, objects_df], ignore_index=True)


     # Ensure '納期_copy' is in datetime format if necessary
    # if '納期_copy' in merged_df.columns:
    #     merged_df['納期_copy'] = pd.to_datetime(merged_df['生産日'], format='%Y/%m/%d', errors='coerce')


   
    # Sort by '納期_copy' and '順番'
    if '順番' in merged_df.columns:
        merged_df = merged_df.sort_values(by=['生産日', '順番'], ascending=[True, True])

    merged_df.fillna('', inplace=True)

    # print(merged_df)
    merged_df.to_csv('merged_df.csv',encoding='utf_8_sig',index=False)

    # Get fieldnames from the merged DataFrame
    fieldnames = list(merged_df.columns)

    with open(file_name, 'w', newline='', encoding='utf_8_sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Iterate over each row in the merged DataFrame and write to the CSV
        for _, row in merged_df.iterrows():
            row_dict = row.to_dict()

            # Custom logic based on your object attributes
            if 'KOスライス製品' in row_dict and row_dict['KOスライス製品'] == '○' and 'break' in row_dict and row_dict['break'] == 1:
                writer.writerow({})  # Write an empty line
                writer.writerow(row_dict)
            else:
                writer.writerow(row_dict)
                if 'break' in row_dict and row_dict['break'] == 2 and 'KOスライス製品' in row_dict and row_dict['KOスライス製品'] == '○':
                    writer.writerow({})  # Write an empty line
                if 'break' in row_dict and row_dict['break'] == 1:
                    writer.writerow({})  # Write an empty line




# def create_csv_from_objects(file_name, objects):
#     if not objects:
#         return

#     fieldnames = list(objects[0].__dict__.keys())
#     # print(fieldnames)

#     # if 'first_class' in fieldnames:
#     #     fieldnames.remove('first_class')

#     with open(file_name, 'w', newline='',encoding='utf_8_sig') as csvfile:
#     # with open(file_name, 'w', newline='',encoding='cp932') as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()

#         for obj in objects:
           
#             if hasattr(obj, 'KOスライス製品') and getattr(obj, 'KOスライス製品') =='○' and hasattr(obj, 'break') and getattr(obj, 'break') == 1:
#                 # if hasattr(obj, 'break') and getattr(obj, 'break') == 1:
#                     # Write an empty line
#                 writer.writerow({})
#                 writer.writerow(obj.__dict__)

#                 # else

#             else:

#                 writer.writerow(obj.__dict__)
#                 # Check if the 'break' attribute exists and is set to 1
#                 if hasattr(obj, 'break') and getattr(obj, 'break') == 2 and hasattr(obj, 'KOスライス製品') and getattr(obj, 'KOスライス製品') =='○':
#                     # Write an empty line
#                     writer.writerow({})

#                 if  hasattr(obj, 'break') and getattr(obj, 'break') == 1:
#                     # Write an empty line
#                     writer.writerow({})

# def additional_features(objects):
    # if not objects:
    #     return

    # for eachobject in objects:
    #     try:
    #         #if eachobject['予定数量(㎏)']!=0 and eachobject['MK流量(㎏/h)']!=0:

    #         if 'or' in getattr(eachobject,'MK流量(㎏/h)'):
    #             dividing_value=getattr(eachobject,'MK流量(㎏/h)').split('or')[0]

    #         else:
    #             dividing_value=float(getattr(eachobject,'MK流量(㎏/h)'))
    #         setattr(eachobject,'MK流量_time',math.ceil(float(getattr(eachobject, "予定数量(㎏)"))/float(dividing_value)*60))
    #     except:
    #         setattr(eachobject,'MK流量_time',0)

    #     try:
    #         if 'or' in getattr(eachobject,'FK流量(㎏/h)'):
    #             dividing_value=getattr(eachobject,'FK流量(㎏/h)').split('or')[0]

    #         else:
    #             dividing_value=float(getattr(eachobject,'FK流量(㎏/h)'))
    #         setattr(eachobject,'FK流量_time',math.ceil(float(getattr(eachobject,'予定数量(㎏)'))/float(dividing_value)*60))
    #     except:
    #         setattr(eachobject,'FK流量_time',0)

    #     try:
    #         if 'or' in getattr(eachobject,'KO流量(㎏/h)'):
    #             dividing_value=getattr(eachobject,'KO流量(㎏/h)').split('or')[0]

    #         else:
    #             dividing_value=float(getattr(eachobject,'KO流量(㎏/h)'))            

    #         setattr(eachobject,'KO流量_time',math.ceil(float(getattr(eachobject,'予定数量(㎏)'))/float(dividing_value)*60))
    #     except:
    #         setattr(eachobject,'KO流量_time',0)


    #     setattr(eachobject,'納期_copy',datetime.strptime(str(getattr(eachobject,'納期')),'%Y%m%d'))


    #     attribute_value = getattr(eachobject, '特記事項')

    #     # Check if the attribute is a string before trying to use 'in'
    #     if isinstance(attribute_value, str) and 'ストレッチ' in attribute_value:
    #         setattr(eachobject, '納期_copy', getattr(eachobject, '納期_copy') - timedelta(days=7))
    #         print('string found')
    #     # else:
    #     #     print(f"Skipped processing for '特記事項' as it is not a string: {attribute_value}")




    #     # ==
    #     if getattr(eachobject,'納期_copy').strftime('%A')=='Saturday' and (getattr(eachobject,'繰上不可(×）')==None or getattr(eachobject,'繰上不可(×）')==''):#and getattr(eachobject,'納期_copy').date() not in usablesat:
    #         setattr(eachobject,'納期_copy',(getattr(eachobject,'納期_copy')- timedelta(days=1)))
    #         # print('reached data changer')
       
    #     # if abc:
    #     #     print('changed to')
    #     #     print(getattr(eachobject,'納期_copy'))
    #     #     exit()


    #     # if getattr(eachobject,'納期_copy').strftime('%A')=='Sunday':
    #     #     setattr(eachobject,'納期_copy',(getattr(eachobject,'納期_copy')- timedelta(days=2)))


    #     setattr(eachobject,'first',0)
    #     setattr(eachobject ,'last',0)
    #     setattr(eachobject,'break',0)
    #     setattr(eachobject,'kostarttime',0)
    #     # setattr(eachobject,'long_break',0)

    #     if not hasattr(eachobject,'updated_date'):
    #         setattr(eachobject ,'updated_date',None)
    #     # print(eachobject.__dict__)

    #     if '最終' in getattr(eachobject,'(一般マーガリンのみ)区分'):
    #         setattr(eachobject,'last',1)

    #     if '初回' in getattr(eachobject,'(一般マーガリンのみ)区分'):
    #         setattr(eachobject,'first',1)        

    #     if (getattr(eachobject,'FK流量_time')==0 and getattr(eachobject,'KO流量_time')==0 and getattr(eachobject,'MK流量_time')!=0) or float(getattr(eachobject,'予定数量(㎏)'))>=6000:
    #         setattr(eachobject,'priority_MK',1)
    #     else:
    #         setattr(eachobject,'priority_MK',0)

    #     if getattr(eachobject,'MK流量_time')==0 and getattr(eachobject,'KO流量_time')==0 and getattr(eachobject,'FK流量_time')!=0:
    #         setattr(eachobject,'priority_FK',1)
    #     else:
    #         setattr(eachobject,'priority_FK',0)

    #     if getattr(eachobject,'MK流量_time')==0 and getattr(eachobject,'FK流量_time')==0 and getattr(eachobject,'KO流量_time')!=0:
    #         setattr(eachobject,'priority_KO',1)
    #     else:
    #         setattr(eachobject,'priority_KO',0)

    #     setattr(eachobject,'get_used',0)
    #     if not hasattr(eachobject,'生産日'):
    #         setattr(eachobject,'生産日',None)

    #     setattr(eachobject,'start',None)
    #     setattr(eachobject,'end',None)
    #     if not hasattr(eachobject, 'pushed_forward'):
    #         setattr(eachobject,'pushed_forward',0)
    #     setattr(eachobject,'ko_remark',False)

    #     setattr(eachobject,'day',None)


    #     #making the salt type of ﾘｽｻｸｻｸﾏ-ｶﾞﾘﾝ to '無し'　lateron we will return in back to '普通' to its original form

    #     if eachobject.品名.startswith('ﾘｽｻｸｻｸﾏ-ｶﾞﾘﾝV'):
    #         setattr(eachobject,'塩','無し')



    #     #lets set saisyuu gentei little differently:
    #     if getattr(eachobject,'アロマゴールド')=='○' and getattr(eachobject,'バター')=='○':
    #         setattr(eachobject,'aromagold_butter','○')
    #         setattr(eachobject,'アロマゴールド','×')
    #         setattr(eachobject,'バター','×')

    #     else:
    #         setattr(eachobject,'aromagold_butter','×')


    #     if getattr(eachobject,'ジェネルー')=='○' and getattr(eachobject,'バター')=='○':
    #         setattr(eachobject,'general_butter','○')
    #         setattr(eachobject,'ジェネルー','×')
    #         setattr(eachobject,'バター','×')

    #     else:
    #         setattr(eachobject,'general_butter','×')


    #     if getattr(eachobject,'エレバールFB　Ⅱ')=='○' and getattr(eachobject,'バター')=='○':
    #         setattr(eachobject,'arebar_butter','○')
    #         setattr(eachobject,'エレバールFB　Ⅱ','×')
    #         setattr(eachobject,'バター','×')

    #     else:
    #         setattr(eachobject,'arebar_butter','×')



    #     if getattr(eachobject,'バレット')=='○' and getattr(eachobject,'バター')=='○':
    #         setattr(eachobject,'baret_butter','○')
    #         setattr(eachobject,'バレット','×')
    #         setattr(eachobject,'バター','×')

    #     else:
    #         setattr(eachobject,'baret_butter','×')

        
    #     if getattr(eachobject,'品名')=='ﾘｽﾏ-ｶﾞﾘﾝDP(M)':

    #         setattr(eachobject,'A','○')
         
    #     else:
    #         setattr(eachobject,'A','×')



    #     if getattr(eachobject,'品名')=='CNCﾏｰｶﾞﾘﾝ':

    #         setattr(eachobject,'B','○')
         
    #     else:
    #         setattr(eachobject,'B','×')



    #     if getattr(eachobject,'品名')=='ﾛ-ﾚﾙ ｽﾀ- (S)':

    #         setattr(eachobject,'C','○')
         
    #     else:
    #         setattr(eachobject,'C','×')



    #     if getattr(eachobject,'品名')=='ﾏｰﾍﾞﾗｽSL':

    #         setattr(eachobject,'D','○')
         
    #     else:
    #         setattr(eachobject,'D','×')



    #     if getattr(eachobject,'品名')=='ｴﾚﾊﾞ-ﾙｿﾌﾄ(S)':

    #         setattr(eachobject,'E','○')
         
    #     else:
    #         setattr(eachobject,'E','×')


    #     if getattr(eachobject,'品名')=='BRKﾏｰｶﾞﾘﾝ':

    #         setattr(eachobject,'F','○')
         
    #     else:
    #         setattr(eachobject,'F','×')



    #     if getattr(eachobject,'品名')=='ﾊﾞﾀ-ﾘﾂﾁﾄｶﾁADF(M)':

    #         setattr(eachobject,'G','○')
         
    #     else:
    #         setattr(eachobject,'G','×')

    #     if getattr(eachobject,'品名')=='ﾛ-ﾚﾙ ｽﾀ- (H)':

    #         setattr(eachobject,'H','○')
         
    #     else:
    #         setattr(eachobject,'H','×')


    #     if getattr(eachobject,'繰上不可(×）') is not None and getattr(eachobject,'繰上不可(×）')!='' and getattr(eachobject, '繰上不可(×）').lower() != 'nan':
    #         try:
    #             advance_date=datetime.strptime(str(getattr(eachobject,'繰上不可(×）')),'%Y/%m/%d %H:%M:%S').date()
    #             setattr(eachobject,'Advance_Date',advance_date)
    #         except:
    #             print('here')
    #             print(getattr(eachobject,'繰上不可(×）'))
    #             advance_date=datetime.strptime(str(getattr(eachobject,'繰上不可(×）')),'%Y-%m-%d %H:%M:%S').date()
    #             setattr(eachobject,'Advance_Date',advance_date)

    #     else:
    #         setattr(eachobject,'Advance_Date',None)
    #         setattr(eachobject,'繰上不可(×）',None)


def additional_features(objects):
    """
    Processes a list of objects, adding additional calculated features such as flow time,
    priority status, and updating date/time-related fields based on specific conditions.
    
    Parameters:
        objects (list): A list of objects, where each object contains various attributes
                        related to flow rates, due dates, and product details.
    
    Returns:
        None
    """
    if not objects:
        return

    # Helper function to calculate flow time for various flow types
    def calculate_flow_time(eachobject, flow_type, quantity_attr):
        """
        Calculates flow time based on flow rate and total quantity.

        Args:
            eachobject: The object containing the flow rate and quantity.
            flow_type: The specific flow rate attribute to check (e.g., 'MK流量(㎏/h)').
            quantity_attr: The attribute for the total quantity (e.g., '予定数量(㎏)').
        """
        flow_time_field = flow_type.replace('流量(㎏/h)', '流量_time')
        try:
            # Handle cases where the flow rate contains "or"
            if 'or' in getattr(eachobject, flow_type):
                dividing_value = getattr(eachobject, flow_type).split('or')[0]
            else:
                dividing_value = float(getattr(eachobject, flow_type))
                
            # Calculate flow time
            flow_time = math.ceil(float(getattr(eachobject, quantity_attr)) / float(dividing_value) * 60)
            setattr(eachobject, flow_time_field, flow_time)
        except:
            setattr(eachobject, flow_time_field, 0)

    # Process each object
    for eachobject in objects:
        # Calculate flow times for MK, FK, and KO flow rates
        for flow_type in ['MK流量(㎏/h)', 'FK流量(㎏/h)', 'KO流量(㎏/h)']:
            calculate_flow_time(eachobject, flow_type, '予定数量(㎏)')

        # Update '納期_copy' (due date) and handle date-related logic
        setattr(eachobject, '納期_copy', datetime.strptime(str(getattr(eachobject, '納期')), '%Y%m%d'))

        # print(getattr(eachobject,'品名'))
        # print(getattr(eachobject,'納期_copy'))
        
        # Check for specific notes ('ストレッチ') and adjust the date
        attribute_value = getattr(eachobject, '特記事項')
        if isinstance(attribute_value, str) and 'ストレッチ' in attribute_value:
            setattr(eachobject, '納期_copy', getattr(eachobject, '納期_copy') - timedelta(days=7))

        # If '納期_copy' falls on a Saturday and '繰上不可' is empty, adjust the date
        if getattr(eachobject, '納期_copy').strftime('%A') == 'Saturday' and not getattr(eachobject, '繰上不可(×）'):
            setattr(eachobject, '納期_copy', getattr(eachobject, '納期_copy') - timedelta(days=1))

        # Initialize various fields if not already set
        for field in ['first', 'last', 'break', 'kostarttime', 'get_used', '生産日', 'start', 'end', 'pushed_forward', 'ko_remark', 'day']:
            setattr(eachobject, field, 0 if field in ['first', 'last', 'break', 'kostarttime', 'get_used', 'pushed_forward'] else None)

        if not hasattr(eachobject, 'updated_date'):
            setattr(eachobject, 'updated_date', None)

        # Set 'first' and 'last' flags based on certain conditions
        区分 = getattr(eachobject, '(一般マーガリンのみ)区分')
        if '最終' in 区分:
            setattr(eachobject, 'last', 1)
        if '初回' in 区分:
            setattr(eachobject, 'first', 1)

        # Determine priorities based on flow times and quantities
        quantity = float(getattr(eachobject, '予定数量(㎏)'))
        setattr(eachobject, 'priority_MK', 1 if (getattr(eachobject, 'FK流量_time') == 0 and getattr(eachobject, 'KO流量_time') == 0 and getattr(eachobject, 'MK流量_time') != 0) or quantity >= 6000 else 0)
        setattr(eachobject, 'priority_FK', 1 if getattr(eachobject, 'MK流量_time') == 0 and getattr(eachobject, 'KO流量_time') == 0 and getattr(eachobject, 'FK流量_time') != 0 else 0)
        setattr(eachobject, 'priority_KO', 1 if getattr(eachobject, 'MK流量_time') == 0 and getattr(eachobject, 'FK流量_time') == 0 and getattr(eachobject, 'KO流量_time') != 0 else 0)

        # Adjust product-specific attributes based on 品名 (product name)
        special_products = {
            'ﾘｽﾏ-ｶﾞﾘﾝDP(M)': 'A',
            'CNCﾏｰｶﾞﾘﾝ': 'B',
            'ﾛ-ﾚﾙ ｽﾀ- (S)': 'C',
            'ﾏｰﾍﾞﾗｽSL': 'D',
            'ｴﾚﾊﾞ-ﾙｿﾌﾄ(S)': 'E',
            'BRKﾏｰｶﾞﾘﾝ': 'F',
            'ﾊﾞﾀ-ﾘﾂﾁﾄｶﾁADF(M)': 'G',
            'ﾛ-ﾚﾙ ｽﾀ- (H)': 'H'
        }
        for product_name, flag in special_products.items():
            setattr(eachobject, flag, '○' if getattr(eachobject, '品名') == product_name else '×')

        # Adjust butter-related product types (including aromagold_butter, general_butter, etc.)
        butter_combinations = {
            'アロマゴールド': 'aromagold_butter',
            'ジェネルー': 'general_butter',
            'エレバールFB　Ⅱ': 'arebar_butter',
            'バレット': 'baret_butter'
        }
        for butter_type, butter_flag in butter_combinations.items():
            if getattr(eachobject, butter_type) == '○' and getattr(eachobject, 'バター') == '○':
                setattr(eachobject, butter_flag, '○')
                setattr(eachobject, butter_type, '×')
                setattr(eachobject, 'バター', '×')
            else:
                setattr(eachobject, butter_flag, '×')



        def parse_date(date_string):
            formats = [
                '%Y/%m/%d %H:%M:%S',  # Format with seconds
                '%Y/%m/%d %H:%M',     # Format without seconds
                '%Y-%m-%d %H:%M:%S',  # Another format with seconds
                '%Y-%m-%d %H:%M',      # Another format without seconds
                '%Y-%m-%d',
                '%Y/%m/%d'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_string, fmt).date()
                except ValueError:
                    continue
            
            # If none of the formats match, raise an error or handle it as needed
            raise ValueError(f"Date string '{date_string}' does not match any expected format.")

        # Handle '繰上不可(×）' (advance not allowed) and parse as date if possible...
        # if getattr(eachobject, '繰上不可(×）') and getattr(eachobject, '繰上不可(×）').lower() != 'nan':
        #     try:
        #         advance_date = datetime.strptime(str(getattr(eachobject, '繰上不可(×）')), '%Y/%m/%d %H:%M:%S').date()
        #     except ValueError:
        #         advance_date = datetime.strptime(str(getattr(eachobject, '繰上不可(×）')), '%Y-%m-%d %H:%M:%S').date()
        #     setattr(eachobject, 'Advance_Date', advance_date)
        # else:
        #     setattr(eachobject, 'Advance_Date', None)
        #     setattr(eachobject, '繰上不可(×）', None)

        # Your main logic
       
        if getattr(eachobject, '繰上不可(×）') and str(getattr(eachobject, '繰上不可(×）')).strip().lower() != 'nan':
            date_string = str(getattr(eachobject, '繰上不可(×）')).strip()
            try:
                advance_date = parse_date(date_string)
            except ValueError:
                advance_date = None
        else:
            advance_date = None

       
        # Set the parsed date or None as appropriate
        setattr(eachobject, 'Advance_Date', advance_date)
        setattr(eachobject, '繰上不可(×）', None if advance_date is None else getattr(eachobject, '繰上不可(×）'))

        if eachobject.品名.startswith('MB-ｵﾘﾝﾋﾟｱ'):
            setattr(eachobject,'荷姿','コンテナ')



def create_objects_with_inherited_features(first_csv, second_csv):
    objects = []

    df_first = pd.read_csv(first_csv, encoding='utf_8_sig')

    # Iterate over the rows of the first DataFrame
    for _, first_class_row in df_first.iterrows():
        # Create an object of FirstClass using the current row
        first_class_obj = FirstClass(first_class_row.to_dict())
        
        # Iterate over the rows of the second DataFrame
        for _, second_class_row in second_csv.iterrows():

            check=second_class_row['品目コード']

            if isinstance(second_class_row['品目コード'],float):
                check=str(int(second_class_row['品目コード']))

            if isinstance(second_class_row['品目コード'],int):
                check=str(second_class_row['品目コード'])


            if str(first_class_row['品目コード']) == check:

                second_class_dict=second_class_row.to_dict()
                second_class_dict['品目コード']=check
                
                second_class_obj = SecondClass(second_class_dict, first_class_obj)
                
                objects.append(second_class_obj)

    return objects

def create_objects_with_inherited_features_new_instances(first_csv, second_csv):
    obj=[]
    with open(first_csv, 'r', encoding='utf_8_sig') as file1:
    # with open(first_csv, 'r', encoding='cp932') as file1:
        first_class_reader = csv.DictReader(file1)
        # print(type(first_class_reader))
        for first_class_row in first_class_reader:
            first_class_obj = FirstClass(first_class_row)


            for second_class_row in second_csv:
                # print(second_class_row.__dict__)
                if str(first_class_row['品目コード']) == str(getattr(second_class_row,'品目コード')):
                    obj1=SecondClass(second_class_row.__dict__, first_class_obj)
                    obj.append(obj1)
                    # print(obj1.__dict__)
                    # return second_class_obj
    return obj
        




def manufacture_multiple_files(input_file):
    # objects_with_inherited_features = create_objects_with_inherited_features('master.csv', input_file)
    objects_with_inherited_features_previous = create_objects_with_inherited_features('master.csv', input_file)

    additional_features(objects_with_inherited_features_previous)


    objects_with_inherited_features_previous=sorted(objects_with_inherited_features_previous,key=lambda obj:obj.納期_copy)
    for ele in objects_with_inherited_features_previous:
        if not hasattr(ele, 'day'):
            setattr(ele,'day',None)

    return objects_with_inherited_features_previous




# def main_function(file1,file2,start,end, holiday_from, holiday_to):
line_name='KO'

file1=f'{line_name}_planning.csv'

# new_orders_file=f'new_orders.csv'
new_orders_file=f'new_orders__.csv'
KO_SLICE=True

# file2='reorder_data_2024_3_月.csv'
previous_output =pd.read_csv(file1,encoding='utf_8_sig')
previous_output['生産日'] =pd.to_datetime(previous_output['生産日'])

previous_output['start'] =pd.to_datetime(previous_output['start'])
previous_output['end'] =pd.to_datetime(previous_output['end'])

start = '2024/03/03'
end = '2024/03/05'
date_format = '%Y/%m/%d'

if line_name =='KO' and KO_SLICE:
    
    start= '2024/3/4  4:45:00'
    end= '2024/3/5  18:28:00'
    date_format = '%Y/%m/%d  %H:%M:%S'

# else:
    
    
# Convert the strings to datetime objects
start_dt = datetime.strptime(start, date_format)
end_dt = datetime.strptime(end, date_format)
# saturdays=['04/08/2023','04/15/2023']
holiday_from= None
holiday_to= None

if line_name=='KO' and KO_SLICE:
    # start= '2024/3/4  4:45:00'
    # end= '2024/3/5  18:28:00'
    # date_format = '%Y/%m/%d  %H:%M:%S'

    start_date=start_dt.date()
    end_date=end_dt.date()

    current_target=previous_output[(previous_output['start']>=start_dt) & (previous_output['end']<=end_dt)]
    

    before_jyunban= int(current_target[current_target['順番'].notna()].head(1)['順番'].values[0])#current_target['順番']
    after_jyunban= int(current_target[current_target['順番'].notna()].tail(1)['順番'].values[0])

    print(before_jyunban)
    print(after_jyunban)

    # if before_jyunban>1:

    #     print(start_dt.date())
        # print(previous_output['生産日'].head(15).values())
        # exit()
    pre_object=previous_output[(previous_output['end'].dt.date==pd.to_datetime(start_dt.date())) & (previous_output['順番']==before_jyunban-1)]

    post_object=previous_output[(previous_output['start'].dt.date==pd.to_datetime(start_dt.date())) & (previous_output['順番']==after_jyunban+1)]

    pre_object.to_csv('pre_object.csv',index=False,encoding='utf_8_sig')
    post_object.to_csv('post_object.csv',index=False,encoding='utf_8_sig')
    previous_output=previous_output[(previous_output['start']<start_dt) | (previous_output['end']>end_dt)]

    print(pre_object)
    print(post_object)

    exit()


else:

    current_target=previous_output[(previous_output['生産日']>=start_dt) & (previous_output['生産日']<=end_dt)]
    previous_output=previous_output[(previous_output['生産日']<start_dt) | (previous_output['生産日']>end_dt)]


previous_output.to_csv('previous_output.csv',encoding='utf_8_sig',index=False)
current_target.to_csv('current_target.csv',encoding='utf_8_sig',index=False)


for ind,row in current_target.iterrows():
    if row.fix==1:
        # print(row['start'].date())
        current_target.at[ind,'繰上不可(×）']= str(row['start'].date())#row['生産日']
        string_date=str(row['start'].year)+str(row['start'].month).zfill(2)+str(row['start'].day).zfill(2)
        current_target.at[ind,'納期']=string_date

       
current_target=current_target[['繰上不可(×）','依頼日','品目コード','品名','入目','予定数量(㎏)','納期','チケットＮＯ','fix']]
current_target['繰上不可(×）']=current_target['繰上不可(×）'].astype(str)
current_target['納期']=current_target['納期'].astype(int)
current_target['納期']=current_target['納期'].astype(str)
# current_target['品目コード']=current_target['品目コード'].astype(str)

current_target.to_csv('current_target.csv',encoding='utf_8_sig',index=False)
# exit()
objects_with_inherited_features=manufacture_multiple_files(current_target)

#reading new orders for given deadline
new_orders=pd.read_csv(new_orders_file,encoding='utf_8_sig')
new_orders=new_orders[['繰上不可(×）','依頼日','品目コード','品名','入目','予定数量(㎏)','納期','チケットＮＯ']]

objects_with_inherited_features_new_order= manufacture_multiple_files(new_orders)
objects_with_inherited_features=objects_with_inherited_features+objects_with_inherited_features_new_order

# Convert start and end times to datetime objects
start_datetime = pd.to_datetime(start)
end_datetime = pd.to_datetime(end)

# Generate dates between start and end (excluding start and end dates)
# Normalize the start and end dates to remove the time component
start_date = start_datetime.normalize()
end_date = end_datetime.normalize()

# Create a date range between the day after the start date and the day before the end date
if start_date + pd.Timedelta(days=1) <= end_date - pd.Timedelta(days=1):
    in_between_dates = pd.date_range(
        start=start_date + pd.Timedelta(days=1),
        end=end_date - pd.Timedelta(days=1),
        freq='D'
    )
else:
    in_between_dates = pd.DatetimeIndex([])

# Set time component of in-between dates to 00:00:00
in_between_dates = in_between_dates.normalize()

# Combine start datetime, in-between dates, and end datetime
dat = pd.DatetimeIndex([start_datetime] + list(in_between_dates) + [end_datetime])

# print(dat)

# exit()

master_sunday_data=[ele for ele in objects_with_inherited_features if ele.品名.startswith('ﾏﾙﾆｼﾛ')]#[0]
if len(master_sunday_data)>1:
    master_sunday_data=[master_sunday_data[0]]

try:
    dat2 = pd.date_range(holiday_from, holiday_to)
except (ValueError, pd.errors.ParserError):
    dat2 = pd.date_range(start='1900-01-01', periods=0)


list_of_saturdays=[]
for days in dat:
    if days.day_name()=='Saturday' and days not in dat2:
        list_of_saturdays.append(days)


length_non_used_data = sys.maxsize

MK_LIST2,FK_LIST2,KO_LIST2=[],[],[]

dates_with_features=[]
for each_date in dat:

    long_break_start_time_MK=[]#each_date+timedelta(hours=11)+timedelta(minutes=30)
    long_break_start_time_FK=[]#[each_date+timedelta(hours=11)+timedelta(minutes=30)]
    long_break_start_time_KO=[]#[each_date+timedelta(hours=11)+timedelta(minutes=30)]


    break_duration_in_hour_MK=[]#[60]
    break_duration_in_hour_FK=[]#[60]
    break_duration_in_hour_KO=[]#[60]


    if each_date.day_name()=='Sunday':
        long_break_start_time_MK=[]
        long_break_start_time_FK=[]
        long_break_start_time_KO=[]

        break_duration_in_hour_MK=[]
        break_duration_in_hour_FK=[]
        break_duration_in_hour_KO=[]

    every_line_break_pattern={}
    every_line_break_pattern['MK_break_pattern']={}
    every_line_break_pattern['FK_break_pattern']={}
    every_line_break_pattern['KO_break_pattern']={}



    for index,each_brake in enumerate(long_break_start_time_MK):
        # Ensure 'MK_break_pattern' key exists and add new nested dictionaries under it
        if 'MK_break_pattern' not in every_line_break_pattern:
            every_line_break_pattern['MK_break_pattern'] = {}
        every_line_break_pattern['MK_break_pattern'][f'break{index}']= {'break':each_brake,f'break_duration':break_duration_in_hour_MK[index]}

    for index,each_brake in enumerate(long_break_start_time_FK):
        #Ensure 'FK_break_pattern' key exists and add new nested dictionaries under it

        if 'FK_break_pattern' not in every_line_break_pattern:
            every_line_break_pattern['FK_break_pattern'] = {}

        every_line_break_pattern['FK_break_pattern'][f'break{index}']= {'break':each_brake,f'break_duration':break_duration_in_hour_FK[index]}

    for index,each_brake in enumerate(long_break_start_time_KO):
        #Ensure 'FK_break_pattern' key exists and add new nested dictionaries under it

        if 'KO_break_pattern' not in every_line_break_pattern:
            every_line_break_pattern['KO_break_pattern'] = {}

        every_line_break_pattern['KO_break_pattern'][f'break{index}']= {'break':each_brake,f'break_duration':break_duration_in_hour_KO[index]}

    each_date_feature= Date_Class(each_date,every_line_break_pattern)

    
    dates_with_features.append(each_date_feature)





dates=[]
MK_LIST1,FK_LIST1,KO_LIST1=[],[],[]


for ele in dates_with_features:
    if  ele.date.day_name()!='Saturday' and ele.date not in dat2:#ele.day_name()!='Sunday' and
        dates.append(ele)

    if ele.date.day_name()=='Saturday' or ele==dates_with_features[-1]:

        # optimizer_list=[0,1,2,3,4,5,6,7,8]
        optimizer_list=[0]
        least_non_used_data_list=[]

        for optimization_value in optimizer_list:
            objects_with_inherited_features=sorted(objects_with_inherited_features, key=lambda ele: ele.納期_copy)

            non_used_data,MK_LIST,FK_LIST,KO_LIST=priority_replanning.schedule_manager(objects_with_inherited_features,dates,master_sunday_data,optimization_value,line_name,see_future=14,dat2=dat2,arg='planning')

            prior_value=0
            yusen_non_used_data=[task for task in non_used_data if getattr(task,'納期_copy')>=ele.date and getattr(task,'納期_copy')<=ele.date+timedelta(days=7)]
            for task in yusen_non_used_data:

                if task.納期_copy==ele.date:
                    prior_value+=1600

                if task.納期_copy==ele.date+timedelta(days=1):
                    prior_value+=700

                elif task.納期_copy==ele.date+timedelta(days=2):
                    prior_value+=600

                elif task.納期_copy==ele.date+timedelta(days=3):
                    prior_value+=500

                elif task.納期_copy==ele.date+timedelta(days=4):
                    prior_value+=400

                elif task.納期_copy==ele.date+timedelta(days=5):
                    prior_value+=300

                elif task.納期_copy==ele.date+timedelta(days=6):
                    prior_value+=200

                elif task.納期_copy==ele.date+timedelta(days=7):
                    prior_value+=100



            # prior_value=len(non_used_data)
            least_non_used_data_list.append(prior_value)

            resetting_instances_attributes(objects_with_inherited_features)

            #the flags were made 0 so reset it to its original state
            for att in dates:
                att.UDF=att.old_UDF


        

        min_value_index = least_non_used_data_list.index(min(least_non_used_data_list))
        optimization_value=optimizer_list[min_value_index]

        non_used_data,MK_LIST,FK_LIST,KO_LIST =priority_replanning.schedule_manager(objects_with_inherited_features,dates,master_sunday_data,optimization_value,line_name,see_future=14,dat2=dat2,arg='planning')
        MK_LIST1+= MK_LIST
        FK_LIST1+= FK_LIST
        KO_LIST1+= KO_LIST

        print(f"the length of KO list {len(KO_LIST)}")

        objects_with_inherited_features=[ele for ele in objects_with_inherited_features if getattr(ele,'get_used')==0]
        dates=[]
    # print(f'the dates at the end is :{dates}')

if len(non_used_data)<=length_non_used_data:

    length_non_used_data=len(non_used_data)
    
    arg='RE_planning'
    if len (MK_LIST1):
        create_csv_from_objects_unmerged(f'MK_{arg}_range.csv', KO_LIST1)
        create_csv_from_objects(f'MK_{arg}.csv', MK_LIST1,previous_output)

    if len (FK_LIST1):
        create_csv_from_objects_unmerged(f'FK_{arg}_range.csv', KO_LIST1)
        create_csv_from_objects(f'FK_{arg}.csv', FK_LIST1,previous_output)

    if len (KO_LIST1):
        create_csv_from_objects_unmerged(f'KO_{arg}_range.csv', KO_LIST1)

        create_csv_from_objects(f'KO_{arg}.csv', KO_LIST1,previous_output)

    create_csv_from_objects(f'unused_data_{arg}.csv', non_used_data)

    # print(least_non_used_data_list)
    # print(f'the optimization value used was: {optimization_value}')

    MK_LIST2,FK_LIST2,KO_LIST2 = copy.deepcopy(MK_LIST1),copy.deepcopy(FK_LIST1),copy.deepcopy(KO_LIST1) 

    


if len(MK_LIST2) or len(FK_LIST2) or len(KO_LIST2):

    ganttchart.ganttchart_creator(MK_LIST2,FK_LIST2,KO_LIST2)

        


















