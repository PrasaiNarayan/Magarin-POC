import csv
import math
from datetime import datetime, timedelta
import pandas as pd
import priority
import ganttchart
import random
import copy
import sys


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
        if row_data['品目コード'] == first_class.品目コード:#self.first_class.品目コード:
            for key, value in row_data.items():
                setattr(self, key, value)
            for key, value in first_class.__dict__.items():#self.first_class.__dict__.items():
                if key != '品目コード':
                    setattr(self, key, value)


    # def split_if_needed(self):
    #     # If weight is over 6000, create two new instances
    #     if int(getattr(self,'予定数量(㎏)')) > 6000:
    #         # Copy the instance's attributes and update the weight
    #         attributes = self.__dict__.copy()
    #         attributes['予定数量(㎏)'] = int(getattr(self,'予定数量(㎏)')) / 2

    #         new_instance1 = SecondClass(attributes)
    #         new_instance2 = SecondClass(attributes)
    #         return new_instance1, new_instance2
    #     # If not, return the instance itself
    #     return self
    
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
        


def create_csv_from_objects(file_name, objects):
    if not objects:
        return

    fieldnames = list(objects[0].__dict__.keys())
    # print(fieldnames)

    # if 'first_class' in fieldnames:
    #     fieldnames.remove('first_class')

    with open(file_name, 'w', newline='',encoding='utf_8_sig') as csvfile:
    # with open(file_name, 'w', newline='',encoding='cp932') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
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

def additional_features(objects):
    if not objects:
        return

    for eachobject in objects:
        try:
            #if eachobject['予定数量(㎏)']!=0 and eachobject['MK流量(㎏/h)']!=0:

            if 'or' in getattr(eachobject,'MK流量(㎏/h)'):
                dividing_value=getattr(eachobject,'MK流量(㎏/h)').split('or')[0]

            else:
                dividing_value=float(getattr(eachobject,'MK流量(㎏/h)'))
            setattr(eachobject,'MK流量_time',math.ceil(float(getattr(eachobject, "予定数量(㎏)"))/float(dividing_value)*60))
        except:
            setattr(eachobject,'MK流量_time',0)

        try:
            if 'or' in getattr(eachobject,'FK流量(㎏/h)'):
                dividing_value=getattr(eachobject,'FK流量(㎏/h)').split('or')[0]

            else:
                dividing_value=float(getattr(eachobject,'FK流量(㎏/h)'))
            setattr(eachobject,'FK流量_time',math.ceil(float(getattr(eachobject,'予定数量(㎏)'))/float(dividing_value)*60))
        except:
            setattr(eachobject,'FK流量_time',0)

        try:
            if 'or' in getattr(eachobject,'KO流量(㎏/h)'):
                dividing_value=getattr(eachobject,'KO流量(㎏/h)').split('or')[0]

            else:
                dividing_value=float(getattr(eachobject,'KO流量(㎏/h)'))            

            setattr(eachobject,'KO流量_time',math.ceil(float(getattr(eachobject,'予定数量(㎏)'))/float(dividing_value)*60))
        except:
            setattr(eachobject,'KO流量_time',0)


        setattr(eachobject,'納期_copy',datetime.strptime(getattr(eachobject,'納期'),'%Y%m%d'))
        if 'ストレッチ' in getattr(eachobject,'特記事項'):
            setattr(eachobject,'納期_copy',getattr(eachobject,'納期_copy')- timedelta(days=7))

        # abc=False

        # if getattr(eachobject,'納期_copy').strftime('%A')=='Saturday' and getattr(eachobject,'品名').startswith('ﾌﾟﾚﾐｱﾑｴ-ｽ-3'):
        #     print('premium')
        #     print(getattr(eachobject,'繰上不可(×）'))
            
        #     print(getattr(eachobject,'納期_copy'))
            
        #     # exit()
        #     abc=True

        # ==
        if getattr(eachobject,'納期_copy').strftime('%A')=='Saturday' and (getattr(eachobject,'繰上不可(×）')==None or getattr(eachobject,'繰上不可(×）')==''):#and getattr(eachobject,'納期_copy').date() not in usablesat:
            setattr(eachobject,'納期_copy',(getattr(eachobject,'納期_copy')- timedelta(days=1)))
            # print('reached data changer')
       
        # if abc:
        #     print('changed to')
        #     print(getattr(eachobject,'納期_copy'))
        #     exit()


        # if getattr(eachobject,'納期_copy').strftime('%A')=='Sunday':
        #     setattr(eachobject,'納期_copy',(getattr(eachobject,'納期_copy')- timedelta(days=2)))


        setattr(eachobject,'first',0)
        setattr(eachobject ,'last',0)
        setattr(eachobject,'break',0)
        setattr(eachobject,'kostarttime',0)
        # setattr(eachobject,'long_break',0)

        if not hasattr(eachobject,'updated_date'):
            setattr(eachobject ,'updated_date',None)
        # print(eachobject.__dict__)

        if '最終' in getattr(eachobject,'(一般マーガリンのみ)区分'):
            setattr(eachobject,'last',1)

        if '初回' in getattr(eachobject,'(一般マーガリンのみ)区分'):
            setattr(eachobject,'first',1)        

        if (getattr(eachobject,'FK流量_time')==0 and getattr(eachobject,'KO流量_time')==0 and getattr(eachobject,'MK流量_time')!=0) or float(getattr(eachobject,'予定数量(㎏)'))>=6000:
            setattr(eachobject,'priority_MK',1)
        else:
            setattr(eachobject,'priority_MK',0)

        if getattr(eachobject,'MK流量_time')==0 and getattr(eachobject,'KO流量_time')==0 and getattr(eachobject,'FK流量_time')!=0:
            setattr(eachobject,'priority_FK',1)
        else:
            setattr(eachobject,'priority_FK',0)

        if getattr(eachobject,'MK流量_time')==0 and getattr(eachobject,'FK流量_time')==0 and getattr(eachobject,'KO流量_time')!=0:
            setattr(eachobject,'priority_KO',1)
        else:
            setattr(eachobject,'priority_KO',0)

        setattr(eachobject,'get_used',0)
        setattr(eachobject,'生産日',None)
        setattr(eachobject,'start',None)
        setattr(eachobject,'end',None)
        if not hasattr(eachobject, 'pushed_forward'):
            setattr(eachobject,'pushed_forward',0)
        setattr(eachobject,'ko_remark',False)

        setattr(eachobject,'day',None)


        #making the salt type of ﾘｽｻｸｻｸﾏ-ｶﾞﾘﾝ to '無し'　lateron we will return in back to '普通' to its original form

        if eachobject.品名.startswith('ﾘｽｻｸｻｸﾏ-ｶﾞﾘﾝV'):
            setattr(eachobject,'塩','無し')



        #lets set saisyuu gentei little differently:
        if getattr(eachobject,'アロマゴールド')=='○' and getattr(eachobject,'バター')=='○':
            setattr(eachobject,'aromagold_butter','○')
            setattr(eachobject,'アロマゴールド','×')
            setattr(eachobject,'バター','×')

        else:
            setattr(eachobject,'aromagold_butter','×')


        if getattr(eachobject,'ジェネルー')=='○' and getattr(eachobject,'バター')=='○':
            setattr(eachobject,'general_butter','○')
            setattr(eachobject,'ジェネルー','×')
            setattr(eachobject,'バター','×')

        else:
            setattr(eachobject,'general_butter','×')


        if getattr(eachobject,'エレバールFB　Ⅱ')=='○' and getattr(eachobject,'バター')=='○':
            setattr(eachobject,'arebar_butter','○')
            setattr(eachobject,'エレバールFB　Ⅱ','×')
            setattr(eachobject,'バター','×')

        else:
            setattr(eachobject,'arebar_butter','×')



        if getattr(eachobject,'バレット')=='○' and getattr(eachobject,'バター')=='○':
            setattr(eachobject,'baret_butter','○')
            setattr(eachobject,'バレット','×')
            setattr(eachobject,'バター','×')

        else:
            setattr(eachobject,'baret_butter','×')

        
        if getattr(eachobject,'品名')=='ﾘｽﾏ-ｶﾞﾘﾝDP(M)':

            setattr(eachobject,'A','○')
         
        else:
            setattr(eachobject,'A','×')



        if getattr(eachobject,'品名')=='CNCﾏｰｶﾞﾘﾝ':

            setattr(eachobject,'B','○')
         
        else:
            setattr(eachobject,'B','×')



        if getattr(eachobject,'品名')=='ﾛ-ﾚﾙ ｽﾀ- (S)':

            setattr(eachobject,'C','○')
         
        else:
            setattr(eachobject,'C','×')



        if getattr(eachobject,'品名')=='ﾏｰﾍﾞﾗｽSL':

            setattr(eachobject,'D','○')
         
        else:
            setattr(eachobject,'D','×')



        if getattr(eachobject,'品名')=='ｴﾚﾊﾞ-ﾙｿﾌﾄ(S)':

            setattr(eachobject,'E','○')
         
        else:
            setattr(eachobject,'E','×')


        if getattr(eachobject,'品名')=='BRKﾏｰｶﾞﾘﾝ':

            setattr(eachobject,'F','○')
         
        else:
            setattr(eachobject,'F','×')



        if getattr(eachobject,'品名')=='ﾊﾞﾀ-ﾘﾂﾁﾄｶﾁADF(M)':

            setattr(eachobject,'G','○')
         
        else:
            setattr(eachobject,'G','×')

        if getattr(eachobject,'品名')=='ﾛ-ﾚﾙ ｽﾀ- (H)':

            setattr(eachobject,'H','○')
         
        else:
            setattr(eachobject,'H','×')


        if getattr(eachobject,'繰上不可(×）') is not None and getattr(eachobject,'繰上不可(×）')!='':
            try:
                advance_date=datetime.strptime(getattr(eachobject,'繰上不可(×）'),'%Y/%m/%d %H:%M:%S').date()
                setattr(eachobject,'Advance_Date',advance_date)
            except:
                advance_date=datetime.strptime(getattr(eachobject,'繰上不可(×）'),'%Y-%m-%d %H:%M:%S').date()
                setattr(eachobject,'Advance_Date',advance_date)

        else:
            setattr(eachobject,'Advance_Date',None)



def create_objects_with_inherited_features(first_csv, second_csv):
    objects = []

    with open(first_csv, 'r', encoding='utf_8_sig') as file1:
    # with open(first_csv, 'r', encoding='cp932') as file1:
        first_class_reader = csv.DictReader(file1)
        # print(type(first_class_reader))
        for first_class_row in first_class_reader:
            first_class_obj = FirstClass(first_class_row)

            with open(second_csv, 'r', encoding='cp932') as file2:
                second_class_reader = csv.DictReader(file2)
                for second_class_row in second_class_reader:
                    if first_class_row['品目コード'] == second_class_row['品目コード']:
                        second_class_obj = SecondClass(second_class_row, first_class_obj)
                        objects.append(second_class_obj)
    print(len(objects))
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
                if first_class_row['品目コード'] == getattr(second_class_row,'品目コード'):
                    obj1=SecondClass(second_class_row.__dict__, first_class_obj)
                    obj.append(obj1)
                    # print(obj1.__dict__)
                    # return second_class_obj
    return obj
        




def manufacture_multiple_files(input_file):
    # objects_with_inherited_features = create_objects_with_inherited_features('master.csv', input_file)
    objects_with_inherited_features_previous = create_objects_with_inherited_features('master.csv', input_file)

    # objects_with_inherited_features=objects_with_inherited_features_previous


    objects_with_inherited_features=[]
    newly_instance=[]
    for instance in objects_with_inherited_features_previous:
        if getattr(instance,'KOライン')=='限定':
            split_weight=4800
        elif getattr(instance,'FKライン')=='限定':
            split_weight=5500

        elif getattr(instance,'MKライン')=='限定':
            split_weight=6000

        elif (instance,'KOライン')=='○' and getattr(instance,'FKライン')=='○' and (instance,'MKライン')=='○' and getattr(instance,'予定数量(㎏)')>6000:
            split_weight=4800

        elif (instance,'KOライン')=='○' and getattr(instance,'FKライン')=='○'  and getattr(instance,'予定数量(㎏)')>5500:
            split_weight=4800

        elif getattr(instance,'FKライン')=='○' and (instance,'MKライン')=='○' and getattr(instance,'予定数量(㎏)')>6000:
            split_weight=5500

        elif getattr(instance,'KOライン')=='○' and (instance,'MKライン')=='○' and getattr(instance,'予定数量(㎏)')>6000:
            split_weight=4800


        else:
            split_weight=6000


        if int(getattr(instance,'予定数量(㎏)'))>split_weight:
            instances=instance.split_if_needed(split_weight)
            random_number = random.randint(1, 100)

            for ele in instances:
                setattr(ele,'new_creation',random_number)
                newly_instance.append(ele)

        else:
            setattr(instance,'new_creation',0)
            objects_with_inherited_features.append(instance)

    

    newly_instance=create_objects_with_inherited_features_new_instances('master.csv', newly_instance)
    for ele in newly_instance:
        print(ele.__dict__)

    objects_with_inherited_features=objects_with_inherited_features+newly_instance



    additional_features(objects_with_inherited_features)


    objects_with_inherited_features=sorted(objects_with_inherited_features,key=lambda obj:obj.納期_copy)
    for ele in objects_with_inherited_features:
        if not hasattr(ele, 'day'):
            setattr(ele,'day',None)

    return objects_with_inherited_features




# def main_function(file1,file2,start,end, holiday_from, holiday_to):
#     print(start,end)
file1='order_data_2024_3_月.csv'
file2='reorder_data_2024_3_月.csv'

# file1='order_3月-4月.csv'
# file2 = 'Monday_product.csv'
start = '03/01/2024'
end = '03/15/2024'

# start = '04/5/2023'
# end = '04/17/2023'

# saturdays=['04/08/2023','04/15/2023']
holiday_from= None
holiday_to= None

replanning_file_objects_listed=manufacture_multiple_files(file2)

objects_with_inherited_features_deep_copy=manufacture_multiple_files(file1)


# objects_with_inherited_features = copy.deepcopy(objects_with_inherited_features_deep_copy)
# replanning_file_objects= copy.deepcopy(replanning_file_objects_listed)

#those days on which request came
unique_dates=sorted({getattr(ele, '依頼日') for ele in replanning_file_objects_listed})

# print(unique_dates)
# exit()

compare_date=datetime.strptime(start, '%m/%d/%Y')
unique_dates_to_use=[ele for ele in unique_dates if datetime.strptime(ele, '%Y-%m-%d') <= compare_date]
print(type(compare_date))

for ele in unique_dates_to_use:
    print(type(ele)) 
    print(ele)


#making sure that the planning happens for the start date as well
date_object = datetime.strptime(start, '%m/%d/%Y')
# Reformat the date string to 'YYYY-MM-DD'
formatted_date = date_object.strftime('%Y-%m-%d')

if formatted_date not in unique_dates_to_use:
    unique_dates_to_use.insert(0,formatted_date)


for uni_date in unique_dates_to_use:
    print(f'the unique date is {uni_date}')

    objects_with_inherited_features = copy.deepcopy(objects_with_inherited_features_deep_copy)
    replanning_file_objects= copy.deepcopy(replanning_file_objects_listed)

    #lets convert ﾌﾟﾚﾐｱﾑｴ-ｽ-3 into 一般マーガリン　and we will convert it back to プレミアムスタ once planning is done
    #this is because thouh it is premium star but it needs to be manufactured with ippanmagarin or mk tokusyouhin
    # for premium_ace in objects_with_inherited_features:
    #     if getattr(premium_ace,'品名').startswith('ﾌﾟﾚﾐｱﾑｴ-ｽ-3'):
    #         setattr(premium_ace,'一般マーガリン製品','○')
    #         setattr(premium_ace,'プレミアムスター製品','×')

    

    each_day_reorder=[ele for ele in replanning_file_objects if ele.依頼日<=uni_date]

    if uni_date== formatted_date:
        each_day_reorder=[]

    matched_data=[]

    for reorder_data in each_day_reorder:
        matching_record=[ele for ele in objects_with_inherited_features if getattr(ele,'納期_copy')==getattr(reorder_data,'納期_copy') 
                         and getattr(ele,'品目コード')==getattr(reorder_data,'品目コード')]

        print([ele.品名 for ele in matching_record])

        for orders in matching_record:
            if orders not in matched_data:
                matched_data.append(orders)


    #now remove those matched record
    objects_with_inherited_features=[ele for ele in objects_with_inherited_features if ele not in matched_data]

    #change the nouki of  reorder data
    for reorder in each_day_reorder:
        print(type(reorder.updated_date))

        if reorder.updated_date:
            print(reorder.品名)
            print('previous date')
            print(reorder.納期_copy)
            print('the updated date')
            print(reorder.updated_date)
            setattr(reorder,'納期_copy',datetime.strptime(getattr(reorder,'updated_date'),'%Y%m%d'))#reorder.updated_date

            print('chaged date')
            print(reorder.納期_copy)

    objects_with_inherited_features+= each_day_reorder

    master_sunday_data=[ele for ele in objects_with_inherited_features if ele.品名.startswith('ﾏﾙﾆｼﾛ')]#[0]
    if len(master_sunday_data)>1:
        master_sunday_data=[master_sunday_data[0]]
    print(file2)

    objects_with_inherited_features=[ele for ele in objects_with_inherited_features if not ele.品名.startswith('ﾏﾙﾆｼﾛ')]

    #ﾏﾙﾆｼﾛ is the product you want to produce every monday either it is in order data or not
    # master_sunday_data=manufacture_multiple_files(file2)

    # master_sunday_data=file2
    create_csv_from_objects('output.csv', objects_with_inherited_features)

    # dat=pd.date_range(start='03/05/2023', end='04/10/2023')
    # print(objects_with_inherited_features)
    dat=pd.date_range(start, end)
    # print('the date is:::')
    # print(dat)

    # dat2=pd.date_range('03/29/2023','04/03/2023')

    try:
        dat2 = pd.date_range(holiday_from, holiday_to)
    except (ValueError, pd.errors.ParserError):
        dat2 = pd.date_range(start='1900-01-01', periods=0)

    # dat2=pd.date_range(holiday_from,holiday_to)


    #weekwise planning
    # dater=[datetime(2023,4,10),datetime(2023,4,17)]

    # objects_with_inherited_features=[ele for ele in objects_with_inherited_features if getattr(ele,'納期_copy') in dater]
    # print(len(objects_with_inherited_features))


    # for ele in objects_with_inherited_features:
    #     if ele.納期_copy in dat2:
    #         ele.納期_copy=datetime(2023,3,28)


    list_of_saturdays=[]
    for days in dat:
        if days.day_name()=='Saturday' and days not in dat2:
            list_of_saturdays.append(days)


    length_non_used_data = sys.maxsize

    MK_LIST2,FK_LIST2,KO_LIST2=[],[],[]
    all_inherited_features=copy.deepcopy(objects_with_inherited_features)


    for each_saturday in list_of_saturdays:

        print(each_saturday)
        objects_with_inherited_features=copy.deepcopy(all_inherited_features)

        dates=[]
        MK_LIST1,FK_LIST1,KO_LIST1=[],[],[]

        # dat=[ele for ele in dat if ele not in used_dates]
        for ele in dat:
            if  ele.day_name()!='Saturday' and ele not in dat2:#ele.day_name()!='Sunday' and
                dates.append(ele)

            if ele.day_name()=='Saturday' or ele==dat[-1]:
                
                #Inclusion of saturday
                if ele.date()==each_saturday.date():
                    # dates.append(ele)
                    print()

                # used_dates= used_dates+[ele for ele in dates]

                optimizer_list=[0,1,2,3,4,5,6,7,8]
                least_non_used_data_list=[]


                for optimization_value in optimizer_list:
                    objects_with_inherited_features=sorted(objects_with_inherited_features, key=lambda ele: ele.納期_copy)

                    non_used_data,MK_LIST,FK_LIST,KO_LIST=priority.schedule_manager(objects_with_inherited_features,dates,master_sunday_data,optimization_value,see_future=14,dat2=dat2,arg='planning')

                    prior_value=0
                    yusen_non_used_data=[task for task in non_used_data if getattr(task,'納期_copy')>=ele and getattr(task,'納期_copy')<=ele+timedelta(days=7)]
                    for task in yusen_non_used_data:

                        if task.納期_copy==ele:
                            prior_value+=1600

                        if task.納期_copy==ele+timedelta(days=1):
                            prior_value+=700

                        elif task.納期_copy==ele+timedelta(days=2):
                            prior_value+=600

                        elif task.納期_copy==ele+timedelta(days=3):
                            prior_value+=500

                        elif task.納期_copy==ele+timedelta(days=4):
                            prior_value+=400

                        elif task.納期_copy==ele+timedelta(days=5):
                            prior_value+=300

                        elif task.納期_copy==ele+timedelta(days=6):
                            prior_value+=200

                        elif task.納期_copy==ele+timedelta(days=7):
                            prior_value+=100



                    # prior_value=len(non_used_data)
                    least_non_used_data_list.append(prior_value)

                    resetting_instances_attributes(objects_with_inherited_features)

                

                min_value_index = least_non_used_data_list.index(min(least_non_used_data_list))
                optimization_value=optimizer_list[min_value_index]

                non_used_data,MK_LIST,FK_LIST,KO_LIST=priority.schedule_manager(objects_with_inherited_features,dates,master_sunday_data,optimization_value,see_future=14,dat2=dat2,arg='planning')
                MK_LIST1+=MK_LIST
                FK_LIST1+=FK_LIST
                KO_LIST1+=KO_LIST

                objects_with_inherited_features=[ele for ele in objects_with_inherited_features if getattr(ele,'get_used')==0]
                dates=[]
            # print(f'the dates at the end is :{dates}')

        if len(non_used_data)<=length_non_used_data:

            length_non_used_data=len(non_used_data)
            
            arg='planning'
            # MK_LIST1=sorted(MK_LIST1, key=lambda ele: (ele.生産日, ele.順番))
            # FK_LIST1=sorted(FK_LIST1, key=lambda ele: (ele.生産日, ele.順番))
            # KO_LIST1=sorted(KO_LIST1, key=lambda ele: (ele.生産日, ele.順番))
            # for premium_ace in objects_with_inherited_features:
            #     if getattr(premium_ace,'品名').startswith('ﾌﾟﾚﾐｱﾑｴ-ｽ-3'):
            #         setattr(premium_ace,'一般マーガリン製品','×')
            #         setattr(premium_ace,'プレミアムスター製品','○')



            if uni_date!= formatted_date:
                create_csv_from_objects(f'MK_{arg}_{uni_date}.csv', MK_LIST1)
                create_csv_from_objects(f'FK_{arg}_{uni_date}.csv', FK_LIST1)
                create_csv_from_objects(f'KO_{arg}_{uni_date}.csv', KO_LIST1)
                create_csv_from_objects(f'unused_data_{arg}_{uni_date}.csv', non_used_data)
                
            else:
                create_csv_from_objects(f'MK_{arg}.csv', MK_LIST1)
                create_csv_from_objects(f'FK_{arg}.csv', FK_LIST1)
                create_csv_from_objects(f'KO_{arg}.csv', KO_LIST1)
                create_csv_from_objects(f'unused_data_{arg}.csv', non_used_data)

            print(least_non_used_data_list)
            # print(f'the optimization value used was: {optimization_value}')

            MK_LIST2,FK_LIST2,KO_LIST2 = copy.deepcopy(MK_LIST1),copy.deepcopy(FK_LIST1),copy.deepcopy(KO_LIST1) 

            


    if len(MK_LIST2) or len(FK_LIST2) or len(KO_LIST2):

        ganttchart.ganttchart_creator(MK_LIST2,FK_LIST2,KO_LIST2)
        # objects_with_inherited_features=MK_LIST2+FK_LIST2+KO_LIST2+non_used_data

        # for ele in MK_LIST2:
        #     if ele not in total_elements:
        #         total_elements.append(ele)

        




















    #either prioritize 最終限定 till 21 days or not 
                # saisyu_gentei_list=[0,1]
                # least_non_used_data_list_inside=[]

                # for saisyu_value in saisyu_gentei_list:


                #     inside_prior_value=0
                    

                #     non_used_data,MK_LIST,FK_LIST,KO_LIST=priority.schedule_manager(objects_with_inherited_features,dates,master_sunday_data,optimization_value,saisyu_value,see_future=14,dat2=dat2,arg='planning')

                #     inside_yusen_non_used_data=[task for task in non_used_data if getattr(task,'納期_copy')>ele and getattr(task,'納期_copy')<=ele+timedelta(days=7)]

                #     for task in inside_yusen_non_used_data:
                #         if task.納期_copy==ele+timedelta(days=1):
                #             inside_prior_value+=2000

                #         elif task.納期_copy==ele+timedelta(days=2):
                #             inside_prior_value+=1600

                #         elif task.納期_copy==ele+timedelta(days=3):
                #             inside_prior_value+=1200

                #         elif task.納期_copy==ele+timedelta(days=4):
                #             inside_prior_value+=800

                #         elif task.納期_copy==ele+timedelta(days=5):
                #             inside_prior_value+=400

                #         elif task.納期_copy==ele+timedelta(days=6):
                #             inside_prior_value+=200

                #         elif task.納期_copy==ele+timedelta(days=7):
                #             inside_prior_value+=100

                #     least_non_used_data_list_inside.append(inside_prior_value)


                #     resetting_instances_attributes(objects_with_inherited_features)

                
                # min_value_index_inside = least_non_used_data_list_inside.index(max(least_non_used_data_list_inside))
                # saisyu_value=saisyu_gentei_list[min_value_index_inside]










    # for ele in dat:
    #     if  ele.day_name()!='Saturday' and ele not in dat2:#ele.day_name()!='Sunday' and
    #         dates.append(ele)


    # optimizer_list=[0,1,2,3,4]
    # # optimizer_list=[0]
    # least_non_used_data_list=[]

    # for optimization_value in optimizer_list:
    #     non_used_data,MK_LIST,FK_LIST,KO_LIST=priority.schedule_manager(objects_with_inherited_features,dates,master_sunday_data,optimization_value,see_future=14,dat2=dat2,arg='planning')
    #     length_of_non_used_data=len(non_used_data)
    #     least_non_used_data_list.append(length_of_non_used_data)

    #     resetting_instances_attributes(objects_with_inherited_features)

    # min_value_index = least_non_used_data_list.index(min(least_non_used_data_list))
    # optimization_value=optimizer_list[min_value_index]
    # non_used_data,MK_LIST,FK_LIST,KO_LIST=priority.schedule_manager(objects_with_inherited_features,dates,master_sunday_data,optimization_value,see_future=14,dat2=dat2,arg='planning')
    # print(least_non_used_data_list)
    # print(optimization_value)
    # ganttchart.ganttchart_creator(MK_LIST,FK_LIST,KO_LIST)









    #saturday_included stuff

    # resetting_instances_attributes(objects_with_inherited_features)
    # # # usable_saturday= datetime(1990, 6, 20, 0, 0, 0)

    # least_non_used_data_list=[]
    # list_of_saturdays=[]
    # list_of_list_non_used_data=[]

    # # #lets create first five saturdays 
    # saturdays_list=[]

    # for ele in dat:
    #     if  ele.day_name()=='Saturday' and ele not in dat2:#ele.day_name()!='Sunday' and
    #         saturdays_list.append(ele)


    # dictionary={}


    # if len(non_used_data)>0:

    #     # for optimization_value in optimizer_list:
    #     if len(non_used_data)>0:
    #     # for each_saturday in saturdays_list:
    #         # for optimization_value in optimizer_list:
            




    #         first_non_used_data=non_used_data[0]
    #         non_used_data=sorted(non_used_data,key=lambda x:x.納期_copy)
    #         first_unused_date=getattr(first_non_used_data,'納期_copy')#
    #         day_name=first_unused_date.strftime("%A")
            
    #         if day_name=='Sunday':
    #             usable_saturday=first_unused_date-timedelta(days=1)

    #         elif day_name=='Monday':
    #             usable_saturday=first_unused_date-timedelta(days=2)

    #         elif day_name=='Tuesday':
    #             usable_saturday=first_unused_date-timedelta(days=3)

    #         elif day_name=='Wednesday':
    #             usable_saturday=first_unused_date-timedelta(days=4)

    #         elif day_name=='Thursday':
    #             usable_saturday=first_unused_date-timedelta(days=5)
            
    #         elif day_name=='Friday':
    #             usable_saturday=first_unused_date-timedelta(days=6)

    #         usable_saturday=pd.to_datetime(usable_saturday)
    #         if usable_saturday not in saturdays_list:
    #             # for sat in saturdays_list:
    #             #     new_list=
    #             new_sat_list=[sat for sat in saturdays_list if sat<usable_saturday]
    #             if len(new_sat_list):
    #                 usable_saturday=new_sat_list[-1]
    #             else:
    #                 usable_saturday=saturdays_list[0]


        

#         dates.append(usable_saturday)
#         dates.sort()
#         setattr(ele,'納期_copy',usable_saturday)
#         current_non_used_data_nouki=getattr(first_non_used_data,'納期_copy')
#         setattr(first_non_used_data,'納期_copy',usable_saturday)

        



#         non_used_data,MK_LIST,FK_LIST,KO_LIST=priority.schedule_manager(objects_with_inherited_features,dates,master_sunday_data,optimization_value,see_future=14,dat2=dat2,arg='Replanning')

    # ganttchart.ganttchart_creator(MK_LIST,FK_LIST,KO_LIST)
