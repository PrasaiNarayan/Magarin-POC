
import pandas as pd
from datetime import timedelta
import csv
import copy
from itertools import zip_longest
# import ganttchart
# import datetime
class Line_select:
    def __init__(self,line,current_date,cleaning_time,Magarin):
        self.line=line
        self.magarin=Magarin
        self.cleaning_time=cleaning_time
        self.set_time_for_line(line,current_date,Magarin)

    def set_time_for_line(self,line,current_date,Magarin):
        if line=='MK' or line=='FK':
            self.start_time=current_date+timedelta(minutes=440)
            self.end_time=current_date+timedelta(minutes=440)

        if line=='KO' and not Magarin:
            if current_date.day_name()=='Sunday':
                self.start_time=current_date+timedelta(hours=23)
                self.end_time=current_date+timedelta(days=5)+timedelta(hours=23)
            else:
                self.start_time=current_date
                if current_date.day_name()=='Monday':
                    self.end_time=current_date+timedelta(days=4)+timedelta(hours=23)
                elif current_date.day_name()=='Tuesday':
                    self.end_time=current_date+timedelta(days=3)+timedelta(hours=23)

                elif current_date.day_name()=='Wednesday':
                    self.end_time=current_date+timedelta(days=2)+timedelta(hours=23)

                elif current_date.day_name()=='Thursday':
                    self.end_time=current_date+timedelta(days=1)+timedelta(hours=23)

                elif current_date.day_name()=='Friday':
                    self.end_time=current_date+timedelta(hours=23)

                # elif current_date.day_name()=='Saturday':
                #     self.end_time=current_date+timedelta(hours=23)



            self.day_breaktime_flag={}
            for i in range(self.start_time.day,self.end_time.day):
                self.day_breaktime_flag[i]=0

        if line=='KO' and Magarin:
            self.start_time=current_date+timedelta(minutes=440)
            self.end_time=current_date+timedelta(minutes=440)


def mk_tokusyouhin_handler(E_Group,line,elements,attribute,counter,line_total_time,allowable_time):
    e1_group=[]

    for ele in E_Group:
        if line_total_time-line.cleaning_time-getattr(ele,attribute)>0:
            e1_group.append(ele)
            line_total_time=line_total_time-line.cleaning_time-getattr(ele,attribute)
            setattr(ele,'get_used',1)


    
    for ele in e1_group:

        before_time=allowable_time
        after_time=before_time+timedelta(minutes=getattr(ele,attribute))
        allowable_time=after_time+timedelta(minutes=line.cleaning_time)

        setattr(ele,'slot',f'{before_time}-->{after_time}')
        setattr(ele,'順番',counter)
        setattr(ele,'生産日',elements.date())
        setattr(ele,'start',f'{before_time}')
        setattr(ele,'end',f'{after_time}')


        counter+=1

    if len(e1_group):
        allowable_time=allowable_time+timedelta(hours=4)
        line_total_time=line_total_time-line.cleaning_time-240

    return e1_group,counter,line_total_time,allowable_time

def grouping(instances,groupname):

    # Split instances into three groups
    pre_instances = []
    xyz_instances = []
    post_instances = []

    pre = True
    post = False

    for instance in instances:
        if hasattr(instance, '品名') and not instance.品名.startswith(groupname) and not post:

            pre_instances.append(instance)
        elif hasattr(instance, '品名') and instance.品名.startswith(groupname):#
            post=True
            xyz_instances.append(instance)
        else:
            post=True
            post_instances.append(instance)

    # Sort the 'xyz' instances
    xyz_instances.sort(key=lambda instance: instance.品名)

    # Concatenate the lists to get the final list
    instances = pre_instances + xyz_instances + post_instances

    return instances

# def randi_len_check(instances):

#     for instance in instances:








def sorting_FHA6(instances):

    # Split instances into three groups
    pre_instances = []
    xyz_instances = []
    post_instances = []
    post = False

    for instance in instances:
        if hasattr(instance, '品名') and not instance.品名.startswith('FH-A6') and not post:

            pre_instances.append(instance)
        elif hasattr(instance, '品名') and instance.品名.startswith('FH-A6'):
            post=True
            xyz_instances.append(instance)
        else:
            post=True
            post_instances.append(instance)

    # xyz_instances.sort(key=lambda instance: getattr(instance,'予定数量(㎏)'))

    xyz_instances=sorted(xyz_instances, key=lambda instance: int(getattr(instance,'予定数量(㎏)')))
    #ele: (ele.生産日

    # Concatenate the lists to get the final list
    instances = pre_instances + xyz_instances + post_instances

    return instances

def grouping_two_groups_consecutively(instances,groupname1,groupname2,newycs=None):

    # Split instances into three groups
    pre_instances = []
    xyz_instances = []
    post_instances = []
    post = False

    for instance in instances:
        if hasattr(instance, '品名') and not post and not instance.品名.startswith(groupname1) and not instance.品名.startswith(groupname2):
            pre_instances.append(instance)

        elif hasattr(instance, '品名') and (instance.品名.startswith(groupname1) or instance.品名.startswith(groupname2)):
            post=True
            xyz_instances.append(instance)
        else:
            post=True
            post_instances.append(instance)


    if newycs==None:

        lis1=[]
        lis2=[]
        for ele in xyz_instances:
            if ele.品名.startswith(groupname1):
                lis1.append(ele)
            else:
                lis2.append(ele)

        xyz_instances=lis1+lis2


    else:
        lis1=[]
        lis2=[]
        for ele in xyz_instances:
            if ele.品名.startswith(groupname1):
                lis1.append(ele)
            else:
                lis2.append(ele)


        pairs = list(zip_longest(lis1, lis2))
        xyz_instances = [x for pair in pairs for x in pair if x is not None]

    instances = pre_instances + xyz_instances + post_instances

    return instances



            


def create_csv_from_objects(file_name, objects):
    if not objects:
        return

    fieldnames = list(objects[0].__dict__.keys())
   

    with open(file_name, 'w', newline='',encoding='utf_8_sig') as csvfile:
    # with open(file_name, 'w', newline='',encoding='cp932') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for obj in objects:
            # print(obj)
            # print(obj.__dict__)

            new_dict=copy.deepcopy(obj.__dict__)
            if new_dict.get('品名')=='ﾘｽｻｸｻｸﾏ-ｶﾞﾘﾝV':
                new_dict['塩']='普通'

            writer.writerow(new_dict)


def last_remaining_appender_second_part(copy_future_groups):
    copy_future_groups=allowable_in_same_group(copy_future_groups)
    copy_future_groups=arerugen_checker(copy_future_groups)


    last_from_arerugen=[ele for ele in copy_future_groups if getattr(ele,'last')==1]

    current_last,corresponding_type=last_checker(last_from_arerugen)

    if len(last_from_arerugen)>0 and len(current_last)==0:
        # last_from_arerugen=sorted(last_from_arerugen, key=lambda ele: (ele.納期_copy))
        current_last=[last_from_arerugen[0]]


    copy_future_groups=[ele for ele in copy_future_groups if getattr(ele,'last')!=1]+current_last

    return copy_future_groups



def last_remaining_appender(machine,attribute,future_groups,line_total_time,my_tuple,list2):


    subete_ikeru_task=allowable_in_same_group(list2+future_groups)
    subete_ikeru_task=arerugen_checker(subete_ikeru_task)
    # if elements.month==3 and elements.day==24:
    #     create_csv_from_objects(f'subete.csv', subete_ikeru_task)
    #     create_csv_from_objects(f'future_group.csv', future_groups)
    subete_ikeru_task=[ele for ele in subete_ikeru_task if ele not in list2]

    if len(list2)==0:
        for ele in subete_ikeru_task:
            if line_total_time-machine.cleaning_time-getattr(ele,attribute)>0:
                list2.append(ele)
                line_total_time=line_total_time-machine.cleaning_time-getattr(ele,attribute)
                setattr(ele,'get_used',1)


    far_current_line_middle,far_current_line_last,far_remaining_line_middle,far_remaining_line_last,far_first_list=my_tuple

    far_current_line_middle=[ele for ele in far_current_line_middle if getattr(ele,'get_used')==0]
    far_current_line_last=[ele for ele in far_current_line_last if getattr(ele,'get_used')==0]
    far_remaining_line_middle=[ele for ele in far_remaining_line_middle if getattr(ele,'get_used')==0]
    far_remaining_line_last=[ele for ele in far_remaining_line_last if getattr(ele,'get_used')==0]
    far_first_list=[ele for ele in far_first_list if getattr(ele,'get_used')==0]



    future_A_Group,future_B_Group,future_C_Group,future_D_Group,future_F_Group,future_E_Group=sequence(far_current_line_middle,far_current_line_last,far_remaining_line_middle,far_remaining_line_last,far_first_list)
    future_groups=future_A_Group+future_B_Group+future_C_Group+future_D_Group+future_F_Group

    # if elements.month==3 and elements.day==24 and attribute=='MK流量_time':
    #     create_csv_from_objects(f"future_group_{elements.day_name()}_{elements.day}.csv",future_groups)
    # future_groups=far_current_line_middle+far_current_line_last+far_remaining_line_middle+far_remaining_line_last+far_first_list

    future_groups=[ele for ele in future_groups if getattr(ele,'get_used')==0]
    remaining_future_groups=arerugen_checker(future_groups)



    while len(remaining_future_groups)>0 and line_total_time>0:
        list3=[]
        
            
        
        three_hours_handler=0
        for ele in remaining_future_groups:
            if three_hours_handler==0:
                if line_total_time-machine.cleaning_time-getattr(ele,attribute)-180>0 and len(list2)!=0:
                    list3.append(ele)
                    line_total_time=line_total_time-machine.cleaning_time-getattr(ele,attribute)-180
                    setattr(ele,'get_used',1)
                    setattr(ele,'pushed_forward',1)
                    three_hours_handler=1
                    print('pushed forward')

            else:
                if line_total_time-machine.cleaning_time-getattr(ele,attribute)>0:
                    list3.append(ele)
                    line_total_time=line_total_time-machine.cleaning_time-getattr(ele,attribute)
                    setattr(ele,'get_used',1)
        
        #for every remaining we need to create the sequential order so that new sequence could be different
        
        far_current_line_middle=[ele for ele in far_current_line_middle if getattr(ele,'get_used')==0]
        far_current_line_last=[ele for ele in far_current_line_last if getattr(ele,'get_used')==0]
        far_remaining_line_middle=[ele for ele in far_remaining_line_middle if getattr(ele,'get_used')==0]
        far_remaining_line_last=[ele for ele in far_remaining_line_last if getattr(ele,'get_used')==0]
        far_first_list=[ele for ele in far_first_list if getattr(ele,'get_used')==0]
        future_A_Group,future_B_Group,future_C_Group,future_D_Group,future_F_Group,future_E_Group=sequence(far_current_line_middle,far_current_line_last,far_remaining_line_middle,far_remaining_line_last,far_first_list)
        future_groups=future_A_Group+future_B_Group+future_C_Group+future_D_Group+future_F_Group


        future_groups=[ele for ele in future_groups if getattr(ele,'get_used')==0]
        remaining_future_groups=arerugen_checker(future_groups)

        if len(list3)==0:
            line_total_time=0

        list2+=list3
    


    return list2

def arerugen_checker(subete_task):
    i=0
    allowable=[]

    for task in subete_task:
        
        if i==0:
            allowable.append(task)
            i=len(allowable)

        
        else:
           
            prev_task=allowable[i-1]
            if ((getattr(prev_task,'塩')=='無し・低' or getattr(prev_task,'塩')=='低' or getattr(prev_task,'塩')=='普通' or getattr(prev_task,'塩')=='普通' or getattr(prev_task,'塩')=='高') and getattr(task,'塩')=='無し'):
                continue

            if ((getattr(prev_task,'last')==1 and getattr(task,'last')==0 )):
                continue

            if  getattr(prev_task,'first')==0 and getattr(task,'first')==1:
                continue

            if getattr(prev_task,'アレルゲン')=='A' and getattr(task,'アレルゲン')=='A':
                allowable.append(task)

            elif getattr(prev_task,'アレルゲン')=='A' and getattr(task,'アレルゲン')=='B':
        
                allowable.append(task)

            elif getattr(prev_task,'アレルゲン')=='B' and getattr(task,'アレルゲン')=='B':
                allowable.append(task)

            elif getattr(prev_task,'アレルゲン')=='B' and getattr(task,'アレルゲン')=='C':

                allowable.append(task)
                

            elif getattr(prev_task,'アレルゲン')=='C' and getattr(task,'アレルゲン')=='C':
                allowable.append(task)

            elif getattr(prev_task,'アレルゲン')=='B' and getattr(task,'アレルゲン')=='F':
                allowable.append(task)                    
            
            elif getattr(prev_task,'アレルゲン')=='F' and getattr(task,'アレルゲン')=='F':
                allowable.append(task)


            elif getattr(prev_task,'アレルゲン')=='A' and getattr(task,'アレルゲン')=='C':
                allowable.append(task)                    

            elif getattr(prev_task,'アレルゲン')=='A' and getattr(task,'アレルゲン')=='F':
                allowable.append(task)         

            elif getattr(prev_task,'アレルゲン')=='C' and getattr(task,'アレルゲン')=='F':
                allowable.append(task)           

            i=len(allowable)
    return allowable

def allowable_in_same_group_type_wise(incoming_group,type_name):
    allowable=[]
    i=0
    for task in incoming_group:
        if i==0:
            allowable.append(task)
            i=len(allowable)
        else:
            prev_task=allowable[i-1]
            if getattr(prev_task,type_name)=='×' and getattr(task,type_name)=='×':
                allowable.append(task)

            elif getattr(prev_task,type_name)=='×' and getattr(task,type_name)=='○':
                allowable.append(task)

            elif getattr(prev_task,type_name)=='○' and getattr(task,type_name)=='○':
                allowable.append(task)
            i=len(allowable)
    return allowable   

def allowable_in_same_group(incoming_group):
    final1=allowable_in_same_group_type_wise(incoming_group,'色')
    final2=allowable_in_same_group_type_wise(final1,'香料')
    final3=allowable_in_same_group_type_wise(final2,'乳化剤')
    return final3


def allowable_in_last_group(incoming_group,type_name):
    
    allowable=[]
    i=0
    for task in incoming_group:
        if  getattr(task,type_name)=='○':

            allowable.append(task)

    return allowable,type_name

def last_checker(incoming_group):

    types_and_lists = [
        allowable_in_last_group(incoming_group,'エレバール'),
        allowable_in_last_group(incoming_group,'エレバールFB　Ⅱ'),
        allowable_in_last_group(incoming_group,'FHシリーズ'),
        allowable_in_last_group(incoming_group,'ランディ'),
        allowable_in_last_group(incoming_group,'アロマゴールド'),
        allowable_in_last_group(incoming_group,'アロマーデソフト'),
        allowable_in_last_group(incoming_group,'バター'),
        allowable_in_last_group(incoming_group,'リス'),
        allowable_in_last_group(incoming_group,'ＳＯＺＡ　Ｙ'),
        allowable_in_last_group(incoming_group,'ネオシュー'),
        allowable_in_last_group(incoming_group,'ジェネルー'),
        allowable_in_last_group(incoming_group,'バレット')
    ]

    longest_list, corresponding_type = max(types_and_lists, key=lambda x: len(x[0]))
    return longest_list, corresponding_type

def last_checker_using_type(incoming_group,type_name):
    allowable,type_name=allowable_in_last_group(incoming_group,type_name)

    return allowable,type_name        



def sequence(current_line_middle,current_line_last,remaining_line_middle,remaining_line_last,first_list):
    salt_order={"無し":1}
    current_line_middle=sorted(current_line_middle, key=lambda obj: (salt_order.get(obj.塩, float('inf')),))#sorted(current_line_middle,key=lambda x:salt_order[getattr(x,'塩')])
    current_line_last=sorted(current_line_last, key=lambda obj: (salt_order.get(obj.塩, float('inf')),))#sorted(current_line_last,key=lambda x:salt_order[getattr(x,'塩')])

    remaining_line_middle=sorted(remaining_line_middle, key=lambda obj: (salt_order.get(obj.塩, float('inf')),))#sorted(remaining_line_middle,key=lambda x:salt_order[getattr(x,'塩')])
    remaining_line_last=sorted(remaining_line_last, key=lambda obj: (salt_order.get(obj.塩, float('inf')),))#sorted(remaining_line_last,key=lambda x:salt_order[getattr(x,'塩')])


    current_line_only=current_line_middle+ remaining_line_middle
    remaining_list=current_line_last+remaining_line_last

    A_first=[ele for ele in first_list if getattr(ele,'アレルゲン')=='A']
    B_first=[ele for ele in first_list if getattr(ele,'アレルゲン')=='B']
    C_first=[ele for ele in first_list if getattr(ele,'アレルゲン')=='C']
    D_first=[ele for ele in first_list if getattr(ele,'アレルゲン')=='D']
    F_first=[ele for ele in first_list if getattr(ele,'アレルゲン')=='F']

    E_first=[ele for ele in first_list if getattr(ele,'アレルゲン')=='E']
    

    A_Group=A_first+[ele for ele in current_line_only if getattr(ele,'アレルゲン')=='A']+[ele for ele in remaining_list if getattr(ele,'アレルゲン')=='A']
    A_Group=sorted(A_Group, key=lambda obj: (salt_order.get(obj.塩, float('inf')),))#sorted(A_Group,key=lambda x:salt_order[getattr(x,'塩')])
    # A_Group=allowable_in_same_group(A_Group)

    B_Group=B_first+[ele for ele in current_line_only if getattr(ele,'アレルゲン')=='B']+[ele for ele in remaining_list if getattr(ele,'アレルゲン')=='B']
    B_Group=sorted(B_Group, key=lambda obj: (salt_order.get(obj.塩, float('inf')),))#sorted(B_Group,key=lambda x:salt_order[getattr(x,'塩')])
    

    C_Group=C_first+[ele for ele in current_line_only if getattr(ele,'アレルゲン')=='C']+[ele for ele in remaining_list if getattr(ele,'アレルゲン')=='C']
    C_Group=sorted(C_Group, key=lambda obj: (salt_order.get(obj.塩, float('inf')),))#sorted(C_Group,key=lambda x:salt_order[getattr(x,'塩')])
 

    D_Group=D_first+[ele for ele in current_line_only if getattr(ele,'アレルゲン')=='D']+[ele for ele in remaining_list if getattr(ele,'アレルゲン')=='D']
    D_Group=sorted(D_Group, key=lambda obj: (salt_order.get(obj.塩, float('inf')),))#sorted(D_Group,key=lambda x:salt_order[getattr(x,'塩')])


    F_Group=F_first+[ele for ele in current_line_only if getattr(ele,'アレルゲン')=='F']+[ele for ele in remaining_list if getattr(ele,'アレルゲン')=='F']
    F_Group=sorted(F_Group, key=lambda obj: (salt_order.get(obj.塩, float('inf')),))#sorted(F_Group,key=lambda x:salt_order[getattr(x,'塩')])


    E_Group=E_first+[ele for ele in current_line_only if getattr(ele,'アレルゲン')=='E']+[ele for ele in remaining_list if getattr(ele,'アレルゲン')=='E']
    E_Group=sorted(E_Group, key=lambda obj: (salt_order.get(obj.塩, float('inf')),))#sorted(F_Group,key=lambda x:salt_order[getattr(x,'塩')])

    return A_Group,B_Group,C_Group,D_Group,F_Group,E_Group


def schedule_manager(Class_Data,dates,master_sunday_data,optimizer,see_future,dat2=None,arg=None):

    first_time=0
    MK_LIST=[]
    FK_LIST=[]
    KO_LIST=[]

    see_future1=see_future

    for elements in dates:
        print(f"{elements}")
        
        Magarin=False
        
        if elements.day_name()!='Sunday':
            cleaning_time=20
            MK=Line_select('MK',elements,cleaning_time,Magarin=False)
            FK=Line_select('FK',elements,cleaning_time,Magarin=False)
            MK_line_total_time,FK_line_total_time=960,960
            #KO_line_total_time=1320
            

        if elements.day_name()=='Sunday' or first_time==0:
            cleaning_time=30
            KO=Line_select('KO',elements,cleaning_time,Magarin=False)
            first_time=1
            counter_type_KO=1
            ko_list=[]

        if dat2 is not None and elements==dat2[-1]+timedelta(days=1):
            cleaning_time=30
            # print(f"the dat2 is {dat2}")

            KO=Line_select('KO',elements,cleaning_time,Magarin=False)
            # print(KO.start_time)

            counter_type_KO=1
            ko_list=[]

        if elements.day_name()=='Saturday':
            Magarin=True
            KO=Line_select('KO',elements,cleaning_time,Magarin=True)
            KO_line_total_time=960


            
            
        #if KO.start_time.day_name()==KO.end_time.day_name():
        if elements.day_name()=='Sunday':
            see_future1=see_future-0

        elif elements.day_name()=='Monday':
            see_future1=see_future-1
        
        elif elements.day_name()=='Tuesday':
            see_future1=see_future-2

        elif elements.day_name()=='Wednesday':
            see_future1=see_future-3

        elif elements.day_name()=='Thursday':
            see_future1=see_future-4
        
        elif elements.day_name()=='Friday':
            see_future1=see_future-5

        start_time=pd.to_datetime(elements)
        #print(f'the start time :{start_time}')
        today_data=[]
        future_data=[]
        far_future1=[]

        for rows_data in Class_Data:
            if getattr(rows_data,'納期_copy')==start_time and rows_data.get_used==0:
                today_data.append(rows_data)

        
            if getattr(rows_data,'納期_copy')>start_time and rows_data.get_used==0:
                if getattr(rows_data,'納期_copy')<=(start_time+timedelta(days=see_future1)):
                    future_data.append(rows_data)

            if getattr(rows_data,'納期_copy')>(start_time+timedelta(days=see_future1)) and getattr(rows_data,'納期_copy')<=(start_time+timedelta(days=see_future1+14))and rows_data.get_used==0:
                far_future1.append(rows_data)

 

        total_data2=today_data+future_data
        available_lines=['KO','MK','FK']
        for eachline in available_lines:
            
            attribute_name1=f'priority_{eachline}'
            attribute_name2=f'{eachline}流量_time'

            first_list=[]
            current_line_middle=[]
            current_line_last=[]

            remaining_line_middle=[]
            remaining_line_last=[]

            # remaining_list=[]


            far_first_list=[]
            far_current_line_middle=[]
            far_current_line_last=[]
            far_remaining_line_middle=[]
            far_remaining_line_last=[]


            #selecting data at first according to lines:
            MK_margarin_nearest_date=None
            MK_premium_star_nearest_date=None

            FK_flat_spread_nearest_date=None
            FK_margarin_nearest_date=None
            if eachline=='MK':
                total_data3=[ele for ele in total_data2 if int(getattr(ele,'予定数量(㎏)'))<=6100]

                # if elements.month==3 and elements.day==1 and eachline=='MK':
                #     print(f"the current line last: {E_Group}")
                #     create_csv_from_objects(f'E_last_elements_{elements.month}_{elements.day}.csv', [ele for ele in total_data3 if getattr(ele,'get_used')==0])

                # if elements.month==3 and elements.day==2 and eachline=='MK':
                #     print(f"the current line last: {E_Group}")
                #     create_csv_from_objects(f'E_last_elements_{elements.month}_{elements.day}_2.csv', [ele for ele in total_data3 if getattr(ele,'get_used')==0])




                total_data1=[]
                # A_found = False
                i=0

                for instance in total_data3:
                    if getattr(instance,'MK特殊品')=='○' :
                       if i>0:
                           pre_instance=[ele for ele in total_data1 if getattr(ele,'MK特殊品')=='○' ][0]
                           pre_instances_length=[ele for ele in total_data1 if getattr(ele,'MK特殊品')=='○' ]
                           if getattr(pre_instance,'new_creation')==getattr(instance,'new_creation') and getattr(instance,'new_creation')!=0 and len(pre_instances_length)<2:
                               total_data1.append(instance)
                           
                       else:
                            total_data1.append(instance)
                            i+=1


                    #    A_found=True
                    #    i+=1
                    elif getattr(instance,'MK特殊品')=='×':
                        total_data1.append(instance)


                for_MK_magarin=[ele for ele in total_data1 if getattr(ele,'一般マーガリン製品')=='○']
                for_MK_magarin = sorted(for_MK_magarin, key=lambda x: x.納期_copy)
                if len(for_MK_magarin):
                    MK_margarin_nearest_date=for_MK_magarin[0].納期_copy

                for_MK_premium_star=[ele for ele in total_data1 if getattr(ele,'プレミアムスター製品')=='○']
                for_MK_premium_star = sorted(for_MK_premium_star, key=lambda x: x.納期_copy)
                if len(for_MK_premium_star):
                    MK_premium_star_nearest_date=for_MK_premium_star[0].納期_copy

                if MK_margarin_nearest_date is None and MK_premium_star_nearest_date is not None:
                    total_data=[ele for ele in total_data1 if getattr(ele,'一般マーガリン製品')!='○']
                    far_future=[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']
                
                elif MK_margarin_nearest_date is not None and MK_premium_star_nearest_date is None:
                    total_data=[ele for ele in total_data1 if getattr(ele,'プレミアムスター製品')!='○']
                    far_future=[ele for ele in far_future1 if getattr(ele,'プレミアムスター製品')!='○']

                elif MK_margarin_nearest_date is not None and MK_premium_star_nearest_date is not None:
                    if MK_premium_star_nearest_date<=MK_margarin_nearest_date:
                        total_data=[ele for ele in total_data1 if getattr(ele,'一般マーガリン製品')!='○']
                        far_future=[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']
                    else:
                        total_data=[ele for ele in total_data1 if getattr(ele,'プレミアムスター製品')!='○']
                        far_future=[ele for ele in far_future1 if getattr(ele,'プレミアムスター製品')!='○']

                
                

            

                else:
                    if len(far_future):
                        for_MK_magarin=[ele for ele in far_future if getattr(ele,'一般マーガリン製品')=='○']
                        for_MK_magarin = sorted(for_MK_magarin, key=lambda x: x.納期_copy)
                        if len(for_MK_magarin):
                            MK_margarin_nearest_date=for_MK_magarin[0].納期_copy


                        for_MK_premium_star=[ele for ele in far_future if getattr(ele,'プレミアムスター製品')=='○']
                        for_MK_premium_star = sorted(for_MK_premium_star, key=lambda x: x.納期_copy)
                        if len(for_MK_premium_star):
                            MK_premium_star_nearest_date=for_MK_premium_star[0].納期_copy

                        if MK_margarin_nearest_date is not None and MK_premium_star_nearest_date is None:
                            far_future=[ele for ele in far_future1 if getattr(ele,'プレミアムスター製品')!='○']

                        elif MK_margarin_nearest_date is None and MK_premium_star_nearest_date is not None:
                            far_future=[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']

                        elif MK_margarin_nearest_date is not None and MK_premium_star_nearest_date is not None:
                            if MK_margarin_nearest_date<=MK_premium_star_nearest_date:
                                far_future=[ele for ele in far_future1 if getattr(ele,'プレミアムスター製品')!='○']
                            else:
                                far_future=[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']


                        # else:
                        #     far_future=[ele for ele in far_future1]



            elif eachline =='FK':
                total_data1=[ele for ele in total_data2 if int(getattr(ele,'予定数量(㎏)'))<=5500]
                for_FK_flatspread=[ele for ele in total_data1 if getattr(ele,'ファットスプレッド製品')=='○']
                for_FK_flatspread=sorted(for_FK_flatspread,key=lambda x:x.納期_copy)
                if len(for_FK_flatspread):
                    FK_flat_spread_nearest_date=for_FK_flatspread[0].納期_copy

                for_FK_magarin=[ele for ele in total_data1 if getattr(ele,'一般マーガリン製品')=='○']
                for_FK_magarin = sorted(for_FK_magarin, key=lambda x: x.納期_copy)
                if len(for_FK_magarin):
                    FK_margarin_nearest_date=for_FK_magarin[0].納期_copy

                if FK_flat_spread_nearest_date is not None and FK_margarin_nearest_date is None:
                    total_data=[ele for ele in total_data1 if getattr(ele,'一般マーガリン製品')!='○']
                    far_future=[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']

                elif FK_flat_spread_nearest_date is None and FK_margarin_nearest_date is not None:
                    total_data=[ele for ele in total_data1 if getattr(ele,'ファットスプレッド製品')!='○']
                    far_future=[ele for ele in far_future1 if getattr(ele,'ファットスプレッド製品')!='○']

                elif FK_flat_spread_nearest_date is not None and FK_margarin_nearest_date is not None:
                    if FK_flat_spread_nearest_date<=FK_margarin_nearest_date:
                        total_data=[ele for ele in total_data1 if getattr(ele,'一般マーガリン製品')!='○']
                        far_future=[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']
                    else:
                        total_data=[ele for ele in total_data1 if getattr(ele,'ファットスプレッド製品')!='○']
                        far_future=[ele for ele in far_future1 if getattr(ele,'ファットスプレッド製品')!='○']

                else:
                    if len(far_future):
                        for_FK_magarin=[ele for ele in far_future if getattr(ele,'一般マーガリン製品')=='○']
                        for_FK_magarin = sorted(for_FK_magarin, key=lambda x: x.納期_copy)
                        if len(for_FK_magarin):
                            FK_margarin_nearest_date=for_FK_magarin[0].納期_copy


                        for_FK_flatspread=[ele for ele in far_future if getattr(ele,'ファットスプレッド製品')=='○']
                        for_FK_flatspread = sorted(for_FK_flatspread, key=lambda x: x.納期_copy)
                        if len(for_FK_flatspread):
                            FK_flat_spread_nearest_date=for_FK_flatspread[0].納期_copy

                        if FK_margarin_nearest_date is None and FK_flat_spread_nearest_date is not None:
                            far_future=[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']
                        elif FK_margarin_nearest_date is not None and FK_flat_spread_nearest_date is None:
                            far_future=[ele for ele in far_future1 if getattr(ele,'ファットスプレッド製品')!='○']
                        elif FK_margarin_nearest_date is not None and FK_flat_spread_nearest_date is not None:
                            if FK_flat_spread_nearest_date<=FK_margarin_nearest_date:
                                far_future=[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']
                            else:
                                far_future=[ele for ele in far_future1 if getattr(ele,'ファットスプレッド製品')!='○']
                        # else:
                        #     far_future=[ele for ele in far_future1]
                if len(total_data):
                    first_data=total_data[0]
                    if getattr(first_data,'一般マーガリン製品')=='○':
                        total_data=[ele for ele in total_data if int(getattr(ele,'予定数量(㎏)'))<=5000]


                

            elif eachline=='KO':
                total_data1=[ele for ele in total_data2 if int(getattr(ele,'予定数量(㎏)'))<=4800]
                total_data=total_data1
                far_future=far_future1
                # KO_slice_nearest_time=None
                # KO_ippan_magarin_nearest_time=None

                ko_slice=[ele for ele in total_data1 if getattr(ele,'KOスライス製品')=='○']
                #ko_slice=sorted(ko_slice,key=lambda x:x.納期_copy)
                # if len(ko_list):


                if len(ko_slice):
                    total_data=[ele for ele in total_data1 if getattr(ele,'一般マーガリン製品')!='○']
                    far_future=[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']

                else:
                    total_data=[ele for ele in total_data1 if getattr(ele,'KOスライス製品')!='○']
                    far_future=[ele for ele in far_future1 if getattr(ele,'KOスライス製品')!='○']


                    if elements>KO.start_time:
                        Magarin=True
                        KO=Line_select('KO',elements,cleaning_time,Magarin)
                        KO_line_total_time=960
                        #KO_line_total_time=1320
                    else:
                        continue





            for task in total_data:

                if getattr(task,'get_used')==0 and getattr(task,attribute_name2)!=0:
                    if getattr(task,'first')==1 and getattr(task,'納期_copy')<=start_time+timedelta(days=see_future1):
                        first_list.append(task)
                        

                    elif getattr(task,attribute_name1)==1 and getattr(task,'first')==0:

                        if getattr(task,'last')!=1:
                            current_line_middle.append(task)
                        else:
                            current_line_last.append(task)


                    elif getattr(task,attribute_name2)!=0 and getattr(task,'first')==0:

                        if getattr(task,'last')!=1:
                            remaining_line_middle.append(task)
                        else:
                            remaining_line_last.append(task)


            for future_task in far_future:
                if getattr(future_task,'get_used')==0 and getattr(future_task,attribute_name2)!=0:
                    if getattr(future_task,'first')==1:# and getattr(future_task,'納期_copy')<=start_time+timedelta(days=see_future):
                        far_first_list.append(future_task)
                        

                    elif getattr(future_task,attribute_name1)==1 and getattr(future_task,'first')==0:

                        if getattr(future_task,'last')!=1:
                            far_current_line_middle.append(future_task)
                        else:
                            far_current_line_last.append(future_task)

                        

                    elif getattr(future_task,attribute_name2)!=0 and getattr(future_task,'first')==0:

                        if getattr(future_task,'last')!=1:
                            far_remaining_line_middle.append(future_task)
                        else:
                            far_remaining_line_last.append(future_task)

                

            current_line_last=current_line_last+far_current_line_last
            remaining_line_last=remaining_line_last+far_remaining_line_last
            far_current_line_last=[]
            far_remaining_line_last=[]


            A_Group,B_Group,C_Group,D_Group,F_Group,E_Group=sequence(current_line_middle,current_line_last,remaining_line_middle,remaining_line_last,first_list)
        

            current_group= A_Group+B_Group+C_Group+D_Group+F_Group
            # name1='ﾆﾕ-YCS ｽﾄﾚﾂﾁ750K'
            # name2='ﾆﾕ-YCS ｽﾄﾚﾂﾁ720K'
            # current_group=grouping_two_groups_consecutively(current_group,name1,name2,newycs=True)
            
            future_A_Group,future_B_Group,future_C_Group,future_D_Group,future_F_Group,future_E_Group=sequence(far_current_line_middle,far_current_line_last,far_remaining_line_middle,far_remaining_line_last,far_first_list)
            future_groups=future_A_Group+future_B_Group+future_C_Group+future_D_Group+future_F_Group


            copy_future_groups=copy.deepcopy(future_groups)

            subete_group=A_Group+B_Group+C_Group+D_Group+F_Group

            subete_group=sorted(subete_group, key=lambda ele: (ele.納期_copy))

            subete_group.sort(key=lambda instance: instance.last != 1)
            subete_group.sort(key=lambda instance: instance.first != 1)
            # selector+=1

            subete_group.sort(key=lambda instance: instance.納期_copy != elements)

            today_data=[ele for ele in subete_group if getattr(ele,'納期_copy')==elements]

            if optimizer==1:
                if len(today_data)==0:
                    subete_group.sort(key=lambda instance: instance.納期_copy != elements+timedelta(days=1))
                    tomorrow_data=[ele for ele in subete_group if getattr(ele,'納期_copy')==elements+timedelta(days=1)]
                    

            elif optimizer==2:
                if len(today_data)==0:
                    subete_group.sort(key=lambda instance: instance.納期_copy != elements+timedelta(days=1))
                    tomorrow_data=[ele for ele in subete_group if getattr(ele,'納期_copy')==elements+timedelta(days=1)]

                    if len(tomorrow_data)==0:
                        subete_group.sort(key=lambda instance: instance.納期_copy != elements+timedelta(days=2))
                        day_after_tomorrow_data=[ele for ele in subete_group if getattr(ele,'納期_copy')==elements+timedelta(days=2)]

            elif optimizer==3:
                if len(today_data)==0:
                    subete_group.sort(key=lambda instance: instance.納期_copy != elements+timedelta(days=1))
                    tomorrow_data=[ele for ele in subete_group if getattr(ele,'納期_copy')==elements+timedelta(days=1)]

                    if len(tomorrow_data)==0:
                        subete_group.sort(key=lambda instance: instance.納期_copy != elements+timedelta(days=2))
                        day_after_tomorrow_data=[ele for ele in subete_group if getattr(ele,'納期_copy')==elements+timedelta(days=2)]

                        if len(day_after_tomorrow_data)==0:
                            subete_group.sort(key=lambda instance: instance.納期_copy != elements+timedelta(days=3))


            elif optimizer==4:
                if len(today_data)==0:
                    subete_group.sort(key=lambda instance: instance.納期_copy != elements+timedelta(days=1))
                    tomorrow_data=[ele for ele in subete_group if getattr(ele,'納期_copy')==elements+timedelta(days=1)]

                    if len(tomorrow_data)==0:
                        subete_group.sort(key=lambda instance: instance.納期_copy != elements+timedelta(days=2))
                        day_after_tomorrow_data=[ele for ele in subete_group if getattr(ele,'納期_copy')==elements+timedelta(days=2)]

                        if len(day_after_tomorrow_data)==0:
                            subete_group.sort(key=lambda instance: instance.納期_copy != elements+timedelta(days=3))
                            after_three_days=[ele for ele in subete_group if getattr(ele,'納期_copy')==elements+timedelta(days=3)]
                            
                            if len(after_three_days)==0:
                                subete_group.sort(key=lambda instance: instance.納期_copy != elements+timedelta(days=4))




            # if elements.month==3 and elements.day==4 and eachline=='MK':
            #     print(f"the current line last: {E_Group}")
            #     create_csv_from_objects(f'E_last_elements_{elements.month}_{elements.day}_{arg}.csv', subete_group)


            # prior_list=[ele for ele in subete_group if ele.納期_copy==elements]

            

                
            subete_group=allowable_in_same_group(subete_group)

            if elements.month==3 and elements.day==1 and eachline=='MK':
                create_csv_from_objects(f"first_list_MK_{elements.day_name()}_{elements.day}.csv",subete_group)

            if elements.month==3 and elements.day==1 and eachline=='FK':
                create_csv_from_objects(f"first_list_FK_{elements.day_name()}_{elements.day}.csv",subete_group)


            
            


            subete_ikeru_task=subete_group#A_Group+B_Group+C_Group+D_Group+F_Group
            
            if eachline!='KO':
                arerugen_check_list=arerugen_checker(subete_ikeru_task)
                # if elements.day_name()=='Monday' and eachline=='MK' and MK_FK_selector%2==0:


                #     deep_copies_list = [copy.deepcopy(obj) for obj in master_sunday_data]
                #     subete_ikeru_task=deep_copies_list+subete_ikeru_task
                #     arerugen_check_list=allowable_in_same_group(subete_ikeru_task)
                #     arerugen_check_list=arerugen_checker(arerugen_check_list)
                #     print("IN MK")
                #     MK_FK_selector+=1
                #     custom_bool=False

                # elif elements.day_name()=='Monday' and eachline=='FK' and MK_FK_selector%2==1 and custom_bool:
                #     deep_copies_list = [copy.deepcopy(obj) for obj in master_sunday_data]
                #     subete_ikeru_task=deep_copies_list+subete_ikeru_task
                #     arerugen_check_list=allowable_in_same_group(subete_ikeru_task)
                #     arerugen_check_list=arerugen_checker(arerugen_check_list)
                #     print("IN FK")
                #     MK_FK_selector+=1
                    
            else:
                if not Magarin:
                    arerugen_check_list=allowable_in_same_group(ko_list+subete_ikeru_task)
                    arerugen_check_list=arerugen_checker(arerugen_check_list)
                    arerugen_check_list=[ele for ele in arerugen_check_list if ele not in ko_list]

                    if len (arerugen_check_list)==0 and len(subete_ikeru_task)!=0:



                        #the added code portion neglects the data which needs the cleaning time and performs the 
                        #allocation on magarin data the code remsembles same to the code above because we are doing same thing
                        #we could have used a function for the same purpose to reduce the code
                        ko_list=[]
                        # for ele in subete_ikeru_task:
                        total_data=[ele for ele in total_data1 if getattr(ele,'KOスライス製品')!='○']
                        far_future=[ele for ele in far_future1 if getattr(ele,'KOスライス製品')!='○']


                        if elements>KO.start_time:
                            Magarin=True
                            KO=Line_select('KO',elements,cleaning_time,Magarin)
                            KO_line_total_time=960

                            for task in total_data:

                                if getattr(task,'get_used')==0 and getattr(task,attribute_name2)!=0:
                                    if getattr(task,'first')==1 and getattr(task,'納期_copy')<=start_time+timedelta(days=see_future1):
                                        first_list.append(task)
                                        

                                    elif getattr(task,attribute_name1)==1 and getattr(task,'first')==0:

                                        if getattr(task,'last')!=1:
                                            current_line_middle.append(task)
                                        else:
                                            current_line_last.append(task)


                                    elif getattr(task,attribute_name2)!=0 and getattr(task,'first')==0:

                                        if getattr(task,'last')!=1:
                                            remaining_line_middle.append(task)
                                        else:
                                            remaining_line_last.append(task)


                            for future_task in far_future:
                                if getattr(future_task,'get_used')==0 and getattr(future_task,attribute_name2)!=0:
                                    if getattr(future_task,'first')==1:# and getattr(future_task,'納期_copy')<=start_time+timedelta(days=see_future):
                                        far_first_list.append(future_task)
                                        

                                    elif getattr(future_task,attribute_name1)==1 and getattr(future_task,'first')==0:

                                        if getattr(future_task,'last')!=1:
                                            far_current_line_middle.append(future_task)
                                        else:
                                            far_current_line_last.append(future_task)

                                        

                                    elif getattr(future_task,attribute_name2)!=0 and getattr(future_task,'first')==0:

                                        if getattr(future_task,'last')!=1:
                                            far_remaining_line_middle.append(future_task)
                                        else:
                                            far_remaining_line_last.append(future_task)

                                

                            current_line_last=current_line_last+far_current_line_last
                            remaining_line_last=remaining_line_last+far_remaining_line_last
                            far_current_line_last=[]
                            far_remaining_line_last=[]



                            A_Group,B_Group,C_Group,D_Group,F_Group,E_Group=sequence(current_line_middle,current_line_last,remaining_line_middle,remaining_line_last,first_list)


                            current_group= A_Group+B_Group+C_Group+D_Group+F_Group
                            future_A_Group,future_B_Group,future_C_Group,future_D_Group,future_F_Group,future_E_Group=sequence(far_current_line_middle,far_current_line_last,far_remaining_line_middle,far_remaining_line_last,far_first_list)

                            future_groups=future_A_Group+future_B_Group+future_C_Group+future_D_Group+future_F_Group

                            subete_group=A_Group+B_Group+C_Group+D_Group+F_Group

                            subete_group.sort(key=lambda instance: instance.納期_copy != elements)

                                
                            subete_group=allowable_in_same_group(subete_group)

                            if elements.month==3 and elements.day==4 and eachline=='MK':
                                create_csv_from_objects(f"remaining_list_FK_{elements.day_name()}_{elements.day}.csv",subete_group)


                            subete_ikeru_task=subete_group#A_Group+B_Group+C_Group+D_Group+F_Group
                            arerugen_check_list=arerugen_checker(subete_ikeru_task)


                        else:
                            continue


                else:
                    arerugen_check_list=arerugen_checker(subete_ikeru_task)

            
           

            last_from_arerugen=[ele for ele in arerugen_check_list if getattr(ele,'last')==1]
            current_last,corresponding_type=last_checker(last_from_arerugen)

            if len(last_from_arerugen)>0 and len(current_last)==0:
                # last_from_arerugen=sorted(last_from_arerugen, key=lambda ele: (ele.納期_copy))
                current_last=[last_from_arerugen[0]]
                future_groups=[ele for ele in future_groups if getattr(ele,'last')!=1]
                current_group=[ele for ele in current_group if getattr(ele,'last')!=1]
                
            elif len(last_from_arerugen)>0 and len(current_last)>0:

                future_last=[ele for ele in future_groups if getattr(ele,'last')==1]
                last_future_group,corresponding_type=last_checker_using_type(future_last,corresponding_type)

                new_current_last=[ele for ele in current_group if getattr(ele,'last')==1]
                new_current_last,corresponding_type=last_checker_using_type(new_current_last,corresponding_type)
                current_group=[ele for ele in current_group if getattr(ele,'last')!=1]+new_current_last

                # print(corresponding_type)
                future_groups=[ele for ele in future_groups if getattr(ele,'last')!=1]+last_future_group



            else:
                future_groups=[ele for ele in future_groups if getattr(ele,'last')!=1]


            arerugen_check_list=[ele for ele in arerugen_check_list if getattr(ele,'last')!=1]+current_last

            
            

            counter=1
            mk_list=[]                   
            fk_list=[]
            if eachline=='MK' and elements.day_name()!='Sunday':
                allowable_time=elements+timedelta(minutes=440)

                
                attribute_line='MK流量_time'
                e1_group,counter,MK_line_total_time,allowable_time=mk_tokusyouhin_handler(E_Group,MK,elements,attribute_line,counter,MK_line_total_time,allowable_time)


                

                if len(e1_group)==0:
                    mk_tokusyouhin=[el for el in arerugen_check_list if getattr(el,'MK特殊品')=='○']
                    if len(mk_tokusyouhin):
                        if getattr(mk_tokusyouhin[0],'new_creation')==0:

                            e1_group,counter,MK_line_total_time,allowable_time=mk_tokusyouhin_handler([mk_tokusyouhin[0]],MK,elements,attribute_line,counter,MK_line_total_time,allowable_time)

                        else:
                            splitted_random=getattr(mk_tokusyouhin[0],'new_creation')
                            same_split=[instance for instance in mk_tokusyouhin if getattr(instance,'new_creation')==splitted_random]
                            e1_group,counter,MK_line_total_time,allowable_time=mk_tokusyouhin_handler(same_split,MK,elements,attribute_line,counter,MK_line_total_time,allowable_time)

                arerugen_check_list=[ele for ele in arerugen_check_list if getattr(ele,'MK特殊品')!='○']



                # else:
                mk_list_last=[]

                for ele in arerugen_check_list:
                    if MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')>0 and getattr(ele,'last')==1:
                        mk_list_last.append(ele)   
                        MK_line_total_time=MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')
                        setattr(ele,'get_used',1)

                arerugen_check_list=[ele for ele in arerugen_check_list if getattr(ele,'last')!=1]

                for ele in arerugen_check_list:

                    if MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')>0:
                        mk_list.append(ele)   
                        MK_line_total_time=MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')
                        setattr(ele,'get_used',1)

                mk_list=mk_list+mk_list_last

                current_group=[ele for ele in current_group if getattr(ele,'MK特殊品')!='○']

                for ele in current_group:
                    if MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')>0 and getattr(ele,'get_used')==0 and not instance.品名.startswith('ﾆﾕ-YCS'):#and getattr(ele,'last')!=1:

                        
                        if len(mk_list)>0:
                            mk_list_copy=mk_list.copy()
                            mk_length=len(mk_list)
                            for i in range (mk_length+1):
                                mk_list_copy.insert(i,ele)
                                mk_list_copy=allowable_in_same_group(mk_list_copy)
                                mk_list_copy=arerugen_checker(mk_list_copy)

                                if len(mk_list_copy)>len(mk_list):
                                    mk_list=mk_list_copy.copy()
                                    MK_line_total_time=MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')
                                    setattr(ele,'get_used',1)
                                    break

                                else:
                                    mk_list_copy=mk_list.copy()


                # future_groups=[ele for ele in future_groups if getattr(ele,'last')!=1]+future_groups_last
                future_groups=[ele for ele in future_groups if getattr(ele,'MK特殊品')!='○']

                for ele in future_groups:
                    if MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')>0 and not instance.品名.startswith('ﾆﾕ-YCS'):
                        if len(mk_list)>0:
                            mk_list_copy=mk_list.copy()
                            mk_length=len(mk_list)
                            for i in range (mk_length+1):
                                mk_list_copy.insert(i,ele)
                                mk_list_copy=allowable_in_same_group(mk_list_copy)
                                mk_list_copy=arerugen_checker(mk_list_copy)

                                if len(mk_list_copy)>len(mk_list):
                                    mk_list=mk_list_copy.copy()
                                    MK_line_total_time=MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')
                                    setattr(ele,'get_used',1)
                                    break

                                else:
                                    mk_list_copy=mk_list.copy()

                if len(mk_list)==0:
                    copy_future_groups=last_remaining_appender_second_part(copy_future_groups)

                    for ele in copy_future_groups:

                        if MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')>0 and getattr(ele,'get_used')==0:
                            mk_list.append(ele)   
                            MK_line_total_time=MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')
                            setattr(ele,'get_used',1)



                # MK_LIST=MK_LIST+mk_prior_outer_list+e1_group+mk_list#+mk_list+
                premimum_group='ﾌﾟﾚﾐｱﾑｽﾀ-DX'
                mk_list=grouping(mk_list,premimum_group) #'ﾌﾟﾚﾐｱﾑｽﾀ-DX'
                mk_list=sorting_FHA6(mk_list)

                #for aroma fold
                groupname1='ｱﾛﾏ-ﾃﾞHTR'
                groupname2='ｱﾛﾏｺﾞ-ﾙﾄﾞ'

                mk_list=grouping_two_groups_consecutively(mk_list,groupname1,groupname2)
                # name1='ﾆﾕ-YCS ｽﾄﾚﾂﾁ750K'
                # name2='ﾆﾕ-YCS ｽﾄﾚﾂﾁ720K'
                # mk_list=grouping_two_groups_consecutively(mk_list,name1,name2,newycs=True)


                MK_LIST=MK_LIST+e1_group+mk_list#+mk_list+

                
                # this_linetotal_time=960
                for ele in mk_list:
                    if getattr(ele,'pushed_forward')==1:
                        allowable_time=allowable_time+timedelta(hours=3)
 
                    before_time=allowable_time
                    after_time=before_time+timedelta(minutes=getattr(ele,'MK流量_time'))
                    allowable_time=after_time+timedelta(minutes=MK.cleaning_time)

                    # this_linetotal_time=this_linetotal_time-getattr(ele,'MK流量_time')-MK.cleaning_time
                    setattr(ele,'slot',f'{before_time}-->{after_time}')
                    setattr(ele,'順番',counter)
                    setattr(ele,'生産日',elements.date())
                    setattr(ele,'start',f'{before_time}')
                    setattr(ele,'end',f'{after_time}')

                    counter+=1

            
            elif eachline=='FK' and elements.day_name()!='Sunday':#
                allowable_time=elements+timedelta(minutes=440)

                e1_group=[]
                for ele in E_Group:
                    if FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')>0:
                        e1_group.append(ele)
                        FK_line_total_time=FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')
                        setattr(ele,'get_used',1)




                for ele in E_Group:


                    before_time=allowable_time
                    after_time=before_time+timedelta(minutes=getattr(ele,'FK流量_time'))
                    allowable_time=after_time+timedelta(minutes=FK.cleaning_time)

                    setattr(ele,'slot',f'{before_time}-->{after_time}')
                    setattr(ele,'順番',counter)
                    setattr(ele,'生産日',elements.date())
                    setattr(ele,'start',f'{before_time}')
                    setattr(ele,'end',f'{after_time}')
                    

                    counter+=1
                if len(E_Group):
                    allowable_time=allowable_time+timedelta(hours=3)
                    FK_line_total_time=FK_line_total_time-FK.cleaning_time-180


                #lets prioritize the 最終限定
                fk_list_last=[]
                for ele in arerugen_check_list:
                    if FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')>0 and getattr(ele,'last')==1:
                        # FK_LIST.append(ele)
                        fk_list_last.append(ele)
                        FK_line_total_time=FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time') 
                        setattr(ele,'get_used',1)
                arerugen_check_list=[ele for ele in arerugen_check_list if getattr(ele,'last')!=1]


                for ele in arerugen_check_list:
                    if FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')>0:
                        # FK_LIST.append(ele)
                        fk_list.append(ele)
                        FK_line_total_time=FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time') 
                        setattr(ele,'get_used',1)

                
                fk_list=fk_list+fk_list_last

                for ele in current_group:
                    if FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')>0 and getattr(ele,'get_used')==0 and not instance.品名.startswith('ﾆﾕ-YCS'):# and getattr(ele,'last')!=1:
                        if len(fk_list)>0:
                            fk_list_copy=fk_list.copy()
                            fk_length=len(fk_list)
                            for i in range (fk_length+1):
                                fk_list_copy.insert(i,ele)
                                fk_list_copy=allowable_in_same_group(fk_list_copy)
                                fk_list_copy=arerugen_checker(fk_list_copy)

                                if len(fk_list_copy)>len(fk_list):
                                    fk_list=fk_list_copy.copy()
                                    FK_line_total_time=FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')
                                    setattr(ele,'get_used',1)
                                    break

                                else:
                                    fk_list_copy=fk_list.copy()

                for ele in future_groups:
                    if FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')>0 and not instance.品名.startswith('ﾆﾕ-YCS'):#and getattr(ele,'last')!=1:
                        if len(fk_list)>0:
                            fk_list_copy=fk_list.copy()
                            fk_length=len(fk_list)
                            for i in range (fk_length+1):
                                fk_list_copy.insert(i,ele)
                                fk_list_copy=allowable_in_same_group(fk_list_copy)
                                fk_list_copy=arerugen_checker(fk_list_copy)

                                if len(fk_list_copy)>len(fk_list):
                                    fk_list=fk_list_copy.copy()
                                    FK_line_total_time=FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')
                                    setattr(ele,'get_used',1)
                                    break

                                else:
                                    fk_list_copy=fk_list.copy()



            

                if len(fk_list)==0:
                    # fk_list=last_remaining_appender(FK,'FK流量_time',future_groups,FK_line_total_time,my_tuple,fk_list)
                    copy_future_groups=last_remaining_appender_second_part(copy_future_groups)

                    for ele in copy_future_groups:
                        if FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')>0 and getattr(ele,'get_used')==0:
                            # FK_LIST.append(ele)
                            fk_list.append(ele)
                            FK_line_total_time=FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time') 
                            setattr(ele,'get_used',1)
                    


                # FK_LIST=FK_LIST+fk_prior_outer_list+e1_group+fk_list
                FK_LIST=FK_LIST+e1_group+fk_list
                # this_linetotal_time=960
                premimum_group='ﾌﾟﾚﾐｱﾑｽﾀ-DX'
                fk_list=grouping(fk_list,premimum_group)
                fk_list=sorting_FHA6(fk_list)

                #for aroma gold
                groupname1='ｱﾛﾏ-ﾃﾞHTR'
                groupname2='ｱﾛﾏｺﾞ-ﾙﾄﾞ'

                fk_list=grouping_two_groups_consecutively(fk_list,groupname1,groupname2)

                # name1='ﾆﾕ-YCS ｽﾄﾚﾂﾁ750K'
                # name2='ﾆﾕ-YCS ｽﾄﾚﾂﾁ720K'
                # fk_list=grouping_two_groups_consecutively(fk_list,name1,name2,newycs=True)


                for ele in fk_list:
                    if getattr(ele,'pushed_forward')==1:
                        allowable_time=allowable_time+timedelta(hours=3)
                    before_time=allowable_time
                    after_time=before_time+timedelta(minutes=getattr(ele,'FK流量_time'))
                    allowable_time=after_time+timedelta(minutes=FK.cleaning_time)
                    # this_linetotal_time=this_linetotal_time-getattr(ele,'FK流量_time')-FK.cleaning_time
                    setattr(ele,'slot',f'{before_time}-->{after_time}')
                    setattr(ele,'順番',counter)
                    setattr(ele,'生産日',elements.date())
                    setattr(ele,'start',f'{before_time}')
                    setattr(ele,'end',f'{after_time}')
                    counter+=1

            
            elif eachline=='KO' and not Magarin and elements.day_name()!='Saturday':
                #1st allocation for KO line 
                for ele in arerugen_check_list:
                    
                    if KO.start_time+timedelta(minutes=KO.cleaning_time)+timedelta(minutes=getattr(ele,'KO流量_time'))<=elements+timedelta(hours=24) and getattr(ele,'納期_copy').date()>=KO.start_time.date() and KO.start_time+timedelta(minutes=KO.cleaning_time)+timedelta(minutes=getattr(ele,'KO流量_time'))<=KO.end_time:#KO.end_time

                        if ele.ko_remark and len(KO_LIST):
                            if KO.start_time-timedelta(hours=3)<KO.start_time.replace(hour=2,minute=0) and KO.start_time<KO.start_time.replace(hour=5,minute=0):
                                KO.start_time+=timedelta(hours=2)



                        KO_LIST.append(ele)
                        ko_list.append(ele)
                        before_time=KO.start_time
                        KO.start_time=KO.start_time+timedelta(minutes=getattr(ele,'KO流量_time'))
                        after_time=KO.start_time
                        KO.start_time=KO.start_time+timedelta(minutes=KO.cleaning_time)
                        attri=KO.start_time.day
                       
                        if attri not in KO.day_breaktime_flag:
                            KO.day_breaktime_flag[attri]=0
                        if KO.start_time>=KO.start_time.replace(hour=2,minute=0) and KO.start_time<KO.start_time.replace(hour=5,minute=0) and KO.day_breaktime_flag[attri]==0:
                            print("reached_true")
                            KO.start_time+=timedelta(hours=2)
                            KO.day_breaktime_flag[attri]=1

                        elif before_time<KO.start_time.replace(hour=2,minute=0) and after_time+timedelta(minutes=KO.cleaning_time)>KO.start_time.replace(hour=5,minute=0) and KO.day_breaktime_flag[attri]==0:
                            KO.start_time=KO.start_time-timedelta(minutes=getattr(ele,'KO流量_time'))-timedelta(minutes=KO.cleaning_time)
                            KO.start_time+=timedelta(hours=2)
                            before_time=KO.start_time
                            KO.start_time=KO.start_time+timedelta(minutes=getattr(ele,'KO流量_time'))
                            after_time=KO.start_time

                            KO.start_time=KO.start_time+timedelta(minutes=KO.cleaning_time)
                            KO.day_breaktime_flag[attri]=1

                        



                        setattr(ele,'get_used',1)
                        setattr(ele,'slot',f'{before_time}-->{after_time}')
                        setattr(ele,'順番',counter_type_KO)
                        counter_type_KO+=1
                        setattr(ele,'生産日',KO.start_time.date())
                        setattr(ele,'start',f'{before_time}')
                        setattr(ele,'end',f'{after_time}')

                
                if KO.start_time<KO.start_time.replace(hour=22,minute=59):
                    for ele in future_groups:
                        if KO.start_time+timedelta(minutes=KO.cleaning_time)+timedelta(minutes=getattr(ele,'KO流量_time'))<=elements+timedelta(hours=23) and getattr(ele,'納期_copy').date()>=KO.start_time.date() and KO.start_time+timedelta(minutes=KO.cleaning_time)+timedelta(minutes=getattr(ele,'KO流量_time'))<=KO.end_time:

                            if len(ko_list)>0:
                                ko_list_copy=ko_list.copy()
                                ko_length=len(ko_list)
                                for i in range (ko_length+1):
                                    ko_list_copy.insert(i,ele)
                                    ko_list_copy=allowable_in_same_group(ko_list_copy)
                                    ko_list_copy=arerugen_checker(ko_list_copy)

                                    if len(ko_list_copy)>len(ko_list):
                                        ko_list=ko_list_copy.copy()
                                        setattr(ele,'get_used',1)
                                        KO_LIST.append(ele)
                                        before_time=KO.start_time
                                        KO.start_time=KO.start_time+timedelta(minutes=getattr(ele,'KO流量_time'))
                                        after_time=KO.start_time
                                        KO.start_time=KO.start_time+timedelta(minutes=KO.cleaning_time)
                                        attri=KO.start_time.day

                                        if attri not in KO.day_breaktime_flag:
                                            KO.day_breaktime_flag[attri]=0
                                        if KO.start_time>=KO.start_time.replace(hour=2,minute=0) and KO.start_time<KO.start_time.replace(hour=5,minute=0) and KO.day_breaktime_flag[attri]==0:
                                            print("reached_true")
                                            KO.start_time+=timedelta(hours=2)
                                            KO.day_breaktime_flag[attri]=1

                                        elif before_time<KO.start_time.replace(hour=2,minute=0) and after_time+timedelta(minutes=KO.cleaning_time)>KO.start_time.replace(hour=5,minute=0) and KO.day_breaktime_flag[attri]==0:
                                            KO.start_time=KO.start_time-timedelta(minutes=getattr(ele,'KO流量_time'))-timedelta(minutes=KO.cleaning_time)
                                            KO.start_time+=timedelta(hours=2)
                                            before_time=KO.start_time
                                            KO.start_time=KO.start_time+timedelta(minutes=getattr(ele,'KO流量_time'))
                                            after_time=KO.start_time

                                            KO.start_time=KO.start_time+timedelta(minutes=KO.cleaning_time)
                                            KO.day_breaktime_flag[attri]=1

                                        setattr(ele,'get_used',1)
                                        setattr(ele,'slot',f'{before_time}-->{after_time}')
                                        setattr(ele,'順番',counter_type_KO)
                                        counter_type_KO+=1
                                        setattr(ele,'生産日',KO.start_time.date())
                                        setattr(ele,'start',f'{before_time}')
                                        setattr(ele,'end',f'{after_time}')


                                        break

                                    else:
                                        ko_list_copy=ko_list.copy()


            elif (eachline=='KO' and Magarin and elements.day_name()!='Saturday') :#or elements.day_name()=='Saturday':
                allowable_time=elements+timedelta(minutes=440)
                ko_magarin=[]
                for ele in arerugen_check_list:
                    if KO_line_total_time-KO.cleaning_time-getattr(ele,'KO流量_time')>0:
                        KO_LIST.append(ele)
                        ko_magarin.append(ele)

                        KO_line_total_time=KO_line_total_time-KO.cleaning_time-getattr(ele,'KO流量_time')
                        setattr(ele,'get_used',1)

               
                
                for ele in ko_magarin:
                    if getattr(ele,'pushed_forward')==1:
                        allowable_time=allowable_time+timedelta(hours=3)
                    before_time=allowable_time
                    after_time=before_time+timedelta(minutes=getattr(ele,'KO流量_time'))
                    allowable_time=after_time+timedelta(minutes=KO.cleaning_time)
                    # this_linetotal_time=this_linetotal_time-getattr(ele,'FK流量_time')-FK.cleaning_time
                    # print(f'{before_time}-->{after_time}')
                    setattr(ele,'slot',f'{before_time}-->{after_time}')
                    setattr(ele,'順番',counter)
                    setattr(ele,'生産日',elements.date())
                    setattr(ele,'start',f'{before_time}')
                    setattr(ele,'end',f'{after_time}')
                    counter+=1

                if KO_line_total_time>0:
                    for ele in future_groups:
                        if KO_line_total_time-KO.cleaning_time-getattr(ele,'KO流量_time')>0:

                            if len(ko_magarin)>0:
                                ko_list_copy=ko_magarin.copy()
                                ko_length=len(ko_magarin)
                                for i in range (ko_length+1):
                                    ko_list_copy.insert(i,ele)
                                    ko_list_copy=allowable_in_same_group(ko_list_copy)
                                    ko_list_copy=arerugen_checker(ko_list_copy)

                                    if len(ko_list_copy)>len(ko_magarin):
                                        ko_magarin=ko_list_copy.copy()
                                        # KO_line_total_time=KO_line_total_time-KO.cleaning_time-getattr(ele,'KK流量_time')
                                        KO_LIST.append(ele)
                                        setattr(ele,'get_used',1)
                                        KO_line_total_time=KO_line_total_time-KO.cleaning_time-getattr(ele,'KO流量_time')

                                        before_time=allowable_time
                                        after_time=before_time+timedelta(minutes=getattr(ele,'KO流量_time'))
                                        allowable_time=after_time+timedelta(minutes=KO.cleaning_time)
                                        # this_linetotal_time=this_linetotal_time-getattr(ele,'FK流量_time')-FK.cleaning_time
                                        # print(f'{before_time}-->{after_time}')
                                        setattr(ele,'slot',f'{before_time}-->{after_time}')
                                        setattr(ele,'順番',counter)
                                        setattr(ele,'生産日',elements.date())
                                        setattr(ele,'start',f'{before_time}')
                                        setattr(ele,'end',f'{after_time}')
                                        counter+=1

                                        break
                                    else:
                                        ko_list_copy=ko_magarin.copy()




           
    print(f'the length of class data{len(Class_Data)}')
    non_used_data=[ele for ele in Class_Data if getattr(ele,'get_used')==0]
    used_Data=[ele for ele in Class_Data if getattr(ele,'get_used')==1]
    MK_LIST=sorted(MK_LIST, key=lambda ele: (ele.生産日, ele.順番))
    FK_LIST=sorted(FK_LIST, key=lambda ele: (ele.生産日, ele.順番))
    KO_LIST=sorted(KO_LIST, key=lambda ele: (ele.生産日, ele.順番))

    create_csv_from_objects(f'MK_{arg}.csv', MK_LIST)
    create_csv_from_objects(f'FK_{arg}.csv', FK_LIST)
    create_csv_from_objects(f'KO_{arg}.csv', KO_LIST)

    create_csv_from_objects(f'unused_data_{arg}.csv', non_used_data)

    print(f'the length of non-used-data {len(non_used_data)} the length of used-data {len(used_Data)}')

    return non_used_data,MK_LIST,FK_LIST,KO_LIST


    # ganttchart.ganttchart_creator(MK_LIST,FK_LIST,KO_LIST)
    # return fig
    