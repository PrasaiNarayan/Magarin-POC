import csv
import math
from datetime import datetime, timedelta
import pandas as pd
import priority
import ganttchart
import random

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


    def split_if_needed(self):
        # If weight is over 6000, create two new instances
        if int(getattr(self,'予定数量(㎏)')) > 6000:
            # Copy the instance's attributes and update the weight
            attributes = self.__dict__.copy()
            attributes['予定数量(㎏)'] = int(getattr(self,'予定数量(㎏)')) / 2
            # print(SecondClass(**attributes))
            # Create two new instances
            # new_instance1 = SecondClass(**attributes)
            # new_instance2 = SecondClass(**attributes)
            new_instance1 = SecondClass(attributes)
            new_instance2 = SecondClass(attributes)



            return new_instance1, new_instance2

        # If not, return the instance itself
        return self
    
def resetting_instances_attributes(objects_with_inherited_features):
        for eachobject in objects_with_inherited_features:
            setattr(eachobject,'get_used',0)
            setattr(eachobject,'生産日',None)
            setattr(eachobject,'start',None)
            setattr(eachobject,'end',None)
            setattr(eachobject,'pushed_forward',0)
            setattr(eachobject,'ko_remark',False)
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

            writer.writerow(obj.__dict__)

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

        usablesat=[datetime(2023,4,22).date()]
       
        if getattr(eachobject,'納期_copy').strftime('%A')=='Saturday' :#and getattr(eachobject,'納期_copy').date() not in usablesat:
            setattr(eachobject,'納期_copy',(getattr(eachobject,'納期_copy')- timedelta(days=1)))

        # if getattr(eachobject,'納期_copy').strftime('%A')=='Sunday':
        #     setattr(eachobject,'納期_copy',(getattr(eachobject,'納期_copy')- timedelta(days=2)))


        setattr(eachobject,'first',0)
        setattr(eachobject ,'last',0)
        # print(eachobject.__dict__)

        if '最終' in getattr(eachobject,'(一般マーガリンのみ)区分'):
            setattr(eachobject,'last',1)

        if '初回' in getattr(eachobject,'(一般マーガリンのみ)区分'):
            setattr(eachobject,'first',1)        

        if (getattr(eachobject,'FK流量_time')==0 and getattr(eachobject,'KO流量_time')==0 and getattr(eachobject,'MK流量_time')!=0) or int(getattr(eachobject,'予定数量(㎏)'))>=6000:
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
    objects_with_inherited_features = create_objects_with_inherited_features('master.csv', input_file)
    # objects_with_inherited_features_previous = create_objects_with_inherited_features('master.csv', input_file)
    # objects_with_inherited_features=[]
    # newly_instance=[]
    # for instance in objects_with_inherited_features_previous:
    #     if int(getattr(instance,'予定数量(㎏)'))>6000:
    #         instance1,instance2=instance.split_if_needed()
    #         random_number = random.randint(1, 100)
    #         setattr(instance1,'new_creation',random_number)
    #         setattr(instance2,'new_creation',random_number)
    #         newly_instance.append(instance1)
    #         newly_instance.append(instance2)



    #     else:
    #         setattr(instance,'new_creation',0)
    #         objects_with_inherited_features.append(instance)

    

    # newly_instance=create_objects_with_inherited_features_new_instances('master.csv', newly_instance)
    # for ele in newly_instance:
    #     print(ele.__dict__)
    
    objects_with_inherited_features=objects_with_inherited_features#+newly_instance


    additional_features(objects_with_inherited_features)
    objects_with_inherited_features=sorted(objects_with_inherited_features,key=lambda obj:obj.納期_copy)
    for ele in objects_with_inherited_features:
        if not hasattr(ele, 'day'):
            setattr(ele,'day',None)

    return objects_with_inherited_features




def main_function(file1,file2,start,end, holiday_from, holiday_to):
    # file1='order_3月.csv'
    # file2='sunday_product.csv'
    
    # file1='order_3月-4月.csv'
    # file2 = 'Monday_product.csv'
    # start = '03/01/2023'
    # end = '04/30/2023'

    # saturdays=['04/08/2023','04/15/2023']

    objects_with_inherited_features= manufacture_multiple_files(file1)
    objects_with_inherited_features= [ele for ele in objects_with_inherited_features if not ele.品名.startswith('ﾏﾙﾆｼﾛ')]
    master_sunday_data= manufacture_multiple_files(file2)
    create_csv_from_objects('output.csv', objects_with_inherited_features)

    # dat=pd.date_range(start='03/05/2023', end='04/10/2023')
    dat=pd.date_range(start, end)
    # dat2=pd.date_range('03/29/2023','04/03/2023')

    try:
        dat2 = pd.date_range(holiday_from, holiday_to)
    except (ValueError, pd.errors.ParserError):
        dat2 = pd.date_range(start='1900-01-01', periods=0)

    dat2=pd.date_range(holiday_from,holiday_to)
    dates=[]

    #weekwise planning
    # dater=[datetime(2023,4,10),datetime(2023,4,17)]

    # objects_with_inherited_features=[ele for ele in objects_with_inherited_features if getattr(ele,'納期_copy') in dater]
    # print(len(objects_with_inherited_features))


    # for ele in objects_with_inherited_features:
    #     if ele.納期_copy in dat2:
    #         ele.納期_copy=datetime(2023,3,28)


    MK_LIST1,FK_LIST1,KO_LIST1=[],[],[]
    # objects_with_inherited_features=[ele for ele in objects_with_inherited_features if str(getattr(ele,'品目コード'))!='25288121830' and ele.納期_copy.date()!=datetime(2023,3,27).date()]

    # objects_with_inherited_features=[ele for ele in objects_with_inherited_features if str(getattr(ele,'チケットＮＯ'))!='K-202303-0231' and ele.納期_copy.date()!=datetime(2023,3,27).date()]
    #K-202303-0231
    for ele in dat:
        if  ele.day_name()!='Saturday' and ele not in dat2:#ele.day_name()!='Sunday' and
            dates.append(ele)

        if ele.day_name()=='Saturday':
            # if ele.date()==datetime(2023,4,22).date() or ele.date()==datetime(2023,4,15).date():
            if ele.date()==datetime(2023,4,15).date():#datetime(2023,4,15).date():
                dates.append(ele)

            optimizer_list=[0,1,2,3,4,5,6,7,8]
            least_non_used_data_list=[]


            for optimization_value in optimizer_list:
                objects_with_inherited_features=sorted(objects_with_inherited_features, key=lambda ele: ele.納期_copy)

                non_used_data,MK_LIST,FK_LIST,KO_LIST=priority.schedule_manager(objects_with_inherited_features,dates,master_sunday_data,optimization_value,see_future=14,dat2=dat2,arg='planning')

                prior_value=0
                yusen_non_used_data=[task for task in non_used_data if getattr(task,'納期_copy')>ele and getattr(task,'納期_copy')<=ele+timedelta(days=7)]
                for task in yusen_non_used_data:
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


        print(f'the dates at the end is :{dates}')

    arg='planning'
    MK_LIST1=sorted(MK_LIST1, key=lambda ele: (ele.生産日, ele.順番))
    FK_LIST1=sorted(FK_LIST1, key=lambda ele: (ele.生産日, ele.順番))
    KO_LIST1=sorted(KO_LIST1, key=lambda ele: (ele.生産日, ele.順番))

    create_csv_from_objects(f'MK_{arg}.csv', MK_LIST1)
    create_csv_from_objects(f'FK_{arg}.csv', FK_LIST1)
    create_csv_from_objects(f'KO_{arg}.csv', KO_LIST1)

    create_csv_from_objects(f'unused_data_{arg}.csv', non_used_data)

    print(f'the length of non_used data list is: {len(non_used_data)}')

    print(least_non_used_data_list)
    # print(f'the optimization value used was: {optimization_value}')
    ganttchart.ganttchart_creator(MK_LIST1,FK_LIST1,KO_LIST1)

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
