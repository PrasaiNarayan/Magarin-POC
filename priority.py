
import pandas as pd
from datetime import timedelta
import csv
import copy
from itertools import zip_longest
import jaconv
import datetime

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

                elif current_date.day_name()=='Saturday':
                    self.end_time=current_date+timedelta(hours=23)



            self.day_breaktime_flag={}
            for i in range(self.start_time.day,self.end_time.day):
                self.day_breaktime_flag[i]=0

        if line=='KO' and Magarin:
            self.start_time=current_date+timedelta(minutes=440)
            self.end_time=current_date+timedelta(minutes=440)

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



def convert_fullwidth_to_halfwidth(text):
    return jaconv.z2h(text, kana=True, digit=False, ascii=False)

def canned_data_allocation(MK_line_total_time,MK,canned_data,counter,allowable_time,elements,moto_canned_data):

    canned_list=[]
    for ele in canned_data:
        if MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')>0:
            canned_list.append(ele)   
            MK_line_total_time=MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')
            setattr(ele,'get_used',1)


    

    for ele in moto_canned_data:
        if MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')>0 and getattr(ele,'get_used')==0:

            canned_list_copy=canned_list.copy()
            mk_length=len(canned_list)
            for i in range (mk_length+1):
                canned_list_copy.insert(i,ele)
                canned_list_copy=allowable_in_same_group(canned_list_copy)
                canned_list_copy=arerugen_checker(canned_list_copy)

                if len(canned_list_copy)>len(canned_list):
                    canned_list=canned_list_copy.copy()
                    MK_line_total_time=MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')
                    setattr(ele,'get_used',1)
                    break

                else:
                    canned_list_copy=canned_list.copy()


    

    for ele in canned_list:
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
        setattr(ele,'day',f'{after_time.day_name()}')
        counter+=1



    return canned_list,counter,MK_line_total_time



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
        setattr(ele,'day',f'{after_time.day_name()}')


        counter+=1

    if len(e1_group):
        allowable_time=allowable_time+timedelta(hours=4)
        line_total_time=line_total_time-line.cleaning_time-240

    return e1_group,counter,line_total_time,allowable_time


def sorting_soza(instances):
    # Split instances into three groups
    pre_instances = []
    xyz_instances = []
    post_instances = []
    post = False

    for instance in instances:
        if hasattr(instance, '品名') and not instance.品名.startswith('SOZA') and not post:
            pre_instances.append(instance)
        elif hasattr(instance, '品名') and instance.品名.startswith('SOZA'):
            post=True
            xyz_instances.append(instance)
        else:
            post=True
            post_instances.append(instance)

    # Separate instances by weight
    instances_5000 = [instance for instance in xyz_instances if int(getattr(instance,'予定数量(㎏)')) == 5000]
    instances_4500 = [instance for instance in xyz_instances if int(getattr(instance,'予定数量(㎏)')) == 4500]

    sorted_instances = []
    # Decide which instance goes first based on the index after pre_instances
    if len(pre_instances) % 2 == 0:  # If index is even
        first_instances = instances_5000#
        second_instances = instances_4500
    else:  # If index is odd
        first_instances = instances_4500#
        second_instances = instances_5000

    # Append instances alternatively
    while first_instances and second_instances:
        sorted_instances.append(first_instances.pop(0))
        sorted_instances.append(second_instances.pop(0))

    # If any instances remain in either list, append them
    sorted_instances.extend(first_instances)
    sorted_instances.extend(second_instances)

    # Concatenate the lists to get the final list
    instances = pre_instances + sorted_instances + post_instances

    return instances





def yusen(subete_group,current_group,future_groups,elements,optimizer,eachline,ko_slicing=False):

    
    if eachline=='MK' :#and elements>=datetime.datetime(2023,3,22) and elements<datetime.datetime(2023,4,18)
        subete_group.sort(key=lambda instance: instance.priority_MK != 1)
        current_group.sort(key=lambda instance: instance.priority_MK != 1)
        # current_group=sorted(current_group,  key=lambda ele: getattr(ele, '予定数量(㎏)'))

    if eachline=='FK' :#and elements>=datetime.datetime(2023,3,22) and elements<datetime.datetime(2023,4,18)
        subete_group.sort(key=lambda instance: instance.priority_FK != 1)
        current_group.sort(key=lambda instance: instance.priority_FK != 1)
        # current_group=sorted(current_group,  key=lambda ele: getattr(ele, '予定数量(㎏)'))

    current_group=sorted(current_group, key=lambda ele: (ele.納期_copy))
    subete_group=sorted(subete_group, key=lambda ele: (ele.納期_copy))

    
    future_groups=sorted(future_groups, key=lambda ele: (ele.納期_copy))


    subete_group.sort(key=lambda instance: instance.last != 1)
    subete_group.sort(key=lambda instance: instance.first != 1)
    subete_group.sort(key=lambda instance: instance.納期_copy != elements)

    today_data=[ele for ele in subete_group if getattr(ele,'納期_copy')==elements]

    for i in range(1,optimizer):
        if len(today_data)==0:
            subete_group.sort(key=lambda instance: instance.納期_copy != elements+timedelta(days=i))
            today_data=[ele for ele in subete_group if getattr(ele,'納期_copy')==elements+timedelta(days=i)]
        else:
            break


    
    # subete_group.sort(key=lambda instance: instance.first != 1)
    # subete_group.sort(key=lambda instance: instance.last != 1)

    # subete_group.sort(key=lambda instance: instance.納期_copy != elements)
        
    return subete_group,current_group,future_groups


def reorder_same_name(instances):
    name_order = {}
    for i, instance in enumerate(instances):
        if instance.品名 not in name_order:
            name_order[instance.品名] = i

    # Reorder list
    reordered_instance = []
    for name in name_order:
        for instance in instances:
            if instance.品名 == name:
                reordered_instance.append(instance)


    return reordered_instance









def grouping(instances,groupname):

    # Split instances into three groups
    pre_instances = []
    xyz_instances = []
    post_instances = []
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

    xyz_instances=sorted(xyz_instances, key=lambda instance: int(getattr(instance,'予定数量(㎏)')))

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

    # xyz_instances.sort(key=lambda instance: getattr(instance,'予定数量(㎏)'))

    if newycs==None:

        lis1=[]
        lis2=[]
        for ele in xyz_instances:
            if ele.品名.startswith(groupname1):
                lis1.append(ele)
            else:
                lis2.append(ele)

        # name1='ﾆﾕ-YCS ｽﾄﾚﾂﾁ750K'
        # name2='ﾆﾕ-YCS ｽﾄﾚﾂﾁ720K'

        xyz_instances=lis1+lis2


    else:
        lis1=[]
        lis2=[]
        for ele in xyz_instances:
            if ele.品名.startswith(groupname1):
                lis1.append(ele)
            else:
                lis2.append(ele)


        # min_length = min(len(lis1), len(lis2))
        # lis1 = lis1[:min_length]
        # lis2 = lis2[:min_length]

        pairs = list(zip_longest(lis1, lis2))
        
        xyz_instances = [x for pair in pairs for x in pair if x is not None]

    instances = pre_instances + xyz_instances + post_instances

    return instances

def salt_order_in_each_group(instances):

    # Let's say instances is your original list

    # order = {'無し': 0, '低': 1, '普通': 2, '高': 3}
                # A_Group=sorted(A_Group,key=lambda x: order[x.塩])

    high_salt = [instance for instance in instances if instance.塩== '普通']
    low_salt = [instance for instance in instances if instance.塩 == '低']
    too_high=[instance for instance in instances if instance.塩 == '高']

    # Now, alternate between high_salt and low_salt instances

    result = []
    min_len = min(len(high_salt), len(low_salt))

    for i in range(min_len):
        result.append(high_salt[i])
        result.append(low_salt[i])

    # If there are any remaining instances in either list, append them
    if len(high_salt) > len(low_salt):
        result.extend(high_salt[min_len:])
    elif len(low_salt) > len(high_salt):
        remaining_low = low_salt[min_len:-2]  # exclude the last two low_salt instances
        last_lows = low_salt[-2:]  # get the last two low_salt instances
        last_high = high_salt[-1]  # get the last high_salt instance

        # Insert the remaining low salt instances before the last high salt instance
        result = result[:-1] + remaining_low + last_lows + [last_high]

    # print(result)

    result=result+too_high

    return result







def sequential_grouping(instances,groupname_type1):
    post = False
    pre_instances = []
    xyz_instances = []
    post_instances = []

    # sequential_grouping(instances,groupname_type1)
    # groupname_type1=['プラズマAR','プラズマNFC','プレミアムスターDX','プラズマDX','アロマスタ','エレバールソフト']

    # groupname_type2=['プレミアムスター','プラズマNFC','プレミアムスターDX','プラズマDX','アロマスター','ローレルスター']

    for instance in instances:
        # if hasattr(instance, '品名') and not post:
        if hasattr(instance, '品名') and any(instance.品名.startswith(name) for name in groupname_type1):
            post = True
            xyz_instances.append(instance)
        elif hasattr(instance, '品名') and not post:
            pre_instances.append(instance)
        else:
            post=True
            post_instances.append(instance)

    # sort xyz_instances according to the order in groupname_type1
    xyz_instances.sort(key=lambda x: next((i for i, groupname in enumerate(groupname_type1) if x.品名.startswith(groupname)), len(groupname_type1)))

    return pre_instances+xyz_instances+post_instances



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


def last_remaining_appender_second_part(copy_future_groups,types):
    if not types:
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
                    # print('pushed forward')

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



def arerugen_checker_new(subete_task):
    i=0
    allowable=[]

    for task in subete_task:
        
        if i==0:
            allowable.append(task)
            i=len(allowable)

        
        else:
           
            prev_task=allowable[i-1]

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


            # second_prefixes = ["MB-ｱﾛﾏｺﾞｰﾙﾄﾞCS", "MB-ｱﾛﾏｺﾞｰﾙﾄﾞCS", "ﾏｰﾍﾞﾗｽSL", "ﾘｽﾏ-ｶﾞﾘﾝDP", "ｱﾛﾏ-ﾃﾞHTR-J", "ｱﾛﾏｺﾞ-ﾙﾄﾞ", "ｱﾛﾏｺﾞ-ﾙﾄﾞ", "ｱﾛﾏｺﾞ-ﾙﾄﾞ"]
            # matching_prefixes = [prefix for prefix in second_prefixes if task.品名.startswith(prefix)]
            # if len(matching_prefixes)>0:
            #     if (getattr(prev_task,'塩')=='無し'):
            #         allowable.append(task)





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


def salt_order_checker(instances):

    allowable=[]
    i=0
    for task in instances:
        if i==0:
            allowable.append(task)
            i=len(allowable)
        else:
            prev_task=allowable[i-1]
            if getattr(prev_task,'塩')=='低' and getattr(task,'塩')=='高':
                continue

            elif getattr(prev_task,'塩')=='高' and getattr(task,'塩')=='低':

                continue
            
            else:
                allowable.append(task)


            i=len(allowable)
    return allowable





def allowable_in_last_group(incoming_group,type_name,product_name=None):
    
    allowable=[]
    i=0
    for task in incoming_group:
        if  getattr(task,type_name)=='○':

            allowable.append(task)
            # i+=1

        

        # elif  getattr(task,type_name)=='○' and i!=0 and product_name==None:
        #     if allowable[-1].品名==task.品名:
        #         allowable.append(task)

        # elif product_name!=None:
        #     if getattr(task,type_name)=='○' and task.品名==product_name:
        #         allowable.append(task)

        

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
        allowable_in_last_group(incoming_group,'バレット'),

        allowable_in_last_group(incoming_group,'aromagold_butter'),
        allowable_in_last_group(incoming_group,'general_butter'),
        allowable_in_last_group(incoming_group,'arebar_butter'),
        allowable_in_last_group(incoming_group,'baret_butter'),

        allowable_in_last_group(incoming_group,'A'),
        allowable_in_last_group(incoming_group,'B'),

        allowable_in_last_group(incoming_group,'C'),
        allowable_in_last_group(incoming_group,'D'),
        allowable_in_last_group(incoming_group,'E'),
        allowable_in_last_group(incoming_group,'F'),
        allowable_in_last_group(incoming_group,'G'),
        allowable_in_last_group(incoming_group,'H')
       
    ]

    longest_list, corresponding_type = max(types_and_lists, key=lambda x: len(x[0]))
    return longest_list, corresponding_type

def last_checker_using_type(incoming_group,type_name):
    allowable,type_name=allowable_in_last_group(incoming_group,type_name)

    return allowable,type_name        


# def line_allocation():
def sequence(current_line_middle,current_line_last,remaining_line_middle,remaining_line_last,first_list):
    salt_order={"無し":1}
    current_line_middle=sorted(current_line_middle, key=lambda obj: (salt_order.get(obj.塩, float('inf')),))#sorted(current_line_middle,key=lambda x:salt_order[getattr(x,'塩')])
    current_line_last=sorted(current_line_last, key=lambda obj: (salt_order.get(obj.塩, float('inf')),))#sorted(current_line_last,key=lambda x:salt_order[getattr(x,'塩')])

    remaining_line_middle=sorted(remaining_line_middle, key=lambda obj: (salt_order.get(obj.塩, float('inf')),))#sorted(remaining_line_middle,key=lambda x:salt_order[getattr(x,'塩')])
    remaining_line_last=sorted(remaining_line_last, key=lambda obj: (salt_order.get(obj.塩, float('inf')),))#sorted(remaining_line_last,key=lambda x:salt_order[getattr(x,'塩')])
    # remaining_line_last,corresponding_type= allowable_in_last_group(remaining_line_last,corresponding_type)
    # print(corresponding_type)

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
    # B_Group=allowable_in_same_group(B_Group)

    C_Group=C_first+[ele for ele in current_line_only if getattr(ele,'アレルゲン')=='C']+[ele for ele in remaining_list if getattr(ele,'アレルゲン')=='C']
    C_Group=sorted(C_Group, key=lambda obj: (salt_order.get(obj.塩, float('inf')),))#sorted(C_Group,key=lambda x:salt_order[getattr(x,'塩')])
    # C_Group=allowable_in_same_group(C_Group)

    D_Group=D_first+[ele for ele in current_line_only if getattr(ele,'アレルゲン')=='D']+[ele for ele in remaining_list if getattr(ele,'アレルゲン')=='D']
    D_Group=sorted(D_Group, key=lambda obj: (salt_order.get(obj.塩, float('inf')),))#sorted(D_Group,key=lambda x:salt_order[getattr(x,'塩')])
    # D_Group=allowable_in_same_group(D_Group)

    F_Group=F_first+[ele for ele in current_line_only if getattr(ele,'アレルゲン')=='F']+[ele for ele in remaining_list if getattr(ele,'アレルゲン')=='F']
    F_Group=sorted(F_Group, key=lambda obj: (salt_order.get(obj.塩, float('inf')),))#sorted(F_Group,key=lambda x:salt_order[getattr(x,'塩')])
    # F_Group=allowable_in_same_group(F_Group)

    E_Group=E_first+[ele for ele in current_line_only if getattr(ele,'アレルゲン')=='E']+[ele for ele in remaining_list if getattr(ele,'アレルゲン')=='E']
    E_Group=sorted(E_Group, key=lambda obj: (salt_order.get(obj.塩, float('inf')),))#sorted(F_Group,key=lambda x:salt_order[getattr(x,'塩')])

    return A_Group,B_Group,C_Group,D_Group,F_Group,E_Group


def schedule_manager(Class_Data,dates,master_sunday_data,optimizer,see_future,dat2=None,arg=None):
    #objects_with_inherited_features,dates,master_sunday_data,optimization_value,see_future=14,dat2=dat2,arg='planning'
    
    first_time=0
    MK_LIST=[]
    FK_LIST=[]
    KO_LIST=[]

    see_future1=see_future
    
    Magarin=False
  
                            
    for elements in dates:
        print(f"{elements}")
        ko_slicing=False
        
        
        
        if elements.day_name()!='Sunday':
            cleaning_time=20
            MK=Line_select('MK',elements,cleaning_time,Magarin=False)
            FK=Line_select('FK',elements,cleaning_time,Magarin=False)
            MK_line_total_time,FK_line_total_time=960,960
            
            #KO_line_total_time=1320
            

        if elements.day_name()=='Sunday' or first_time==0:
            cleaning_time=60
            KO=Line_select('KO',elements,cleaning_time,Magarin=False)
            first_time=1
            counter_type_KO=1
            ko_list=[]
            Magarin=False
            Class_Data=Class_Data

        if dat2 is not None and len(dat2)>0 and  elements==dat2[-1]+timedelta(days=1):
            cleaning_time=60
            # print(f"the dat2 is {dat2}")

            KO=Line_select('KO',elements,cleaning_time,Magarin=False)
            Magarin=False
            # print(KO.start_time)

            counter_type_KO=1
            ko_list=[]

        if elements.day_name()=='Saturday':
            ko_list=[]
            Magarin=True
            cleaning_time=60
            KO=Line_select('KO',elements,cleaning_time,Magarin=True)
            KO_line_total_time=840

        #if KO.start_time.day_name()==KO.end_time.day_name():
        add_day=7
        if elements.day_name()=='Sunday':
            see_future1=see_future-0
            add_day=add_day-0

        elif elements.day_name()=='Monday':
            see_future1=see_future-1
            add_day=add_day-1
        
        elif elements.day_name()=='Tuesday':
            see_future1=see_future-2
            add_day=add_day-2

        elif elements.day_name()=='Wednesday':
            see_future1=see_future-3
            add_day=add_day-3

        elif elements.day_name()=='Thursday':
            see_future1=see_future-4
            add_day=add_day-4
            Magarin=True
        
        elif elements.day_name()=='Friday':
            see_future1=see_future-5
            add_day=add_day-5
            Magarin=True

        elif elements.day_name()=='Saturday':
            see_future1=see_future-6
            add_day=add_day-6


        start_time=pd.to_datetime(elements)
        #print(f'the start time :{start_time}')
        today_data=[]
        future_data=[]
        far_future1=[]
        

        date_series = pd.Series(pd.to_datetime(dates))

        # Get the last date
        last_date = date_series.max()

        # Extract the month and day from the last date
        last_month = last_date.month
        last_day = last_date.day
        # add_day=7
    

        if  elements.month == last_month and elements.day>=26:#elements.month==4 and
            add_day=14

        for rows_data in Class_Data:
            if getattr(rows_data,'納期_copy')==start_time and rows_data.get_used==0:
                today_data.append(rows_data)

        
            if getattr(rows_data,'納期_copy')>start_time and rows_data.get_used==0:
                if getattr(rows_data,'納期_copy')<=(start_time+timedelta(days=see_future1)):
                    future_data.append(rows_data)


            # if getattr(rows_data,'納期_copy')>(start_time+timedelta(days=see_future1)) and getattr(rows_data,'納期_copy')<=(start_time+timedelta(days=see_future1+add_day))and rows_data.get_used==0:
            #     far_future1.append(rows_data) Class_Data


            if getattr(rows_data,'納期_copy')>(start_time+timedelta(days=see_future1)) and getattr(rows_data,'納期_copy')<=(start_time+timedelta(days=see_future))and rows_data.get_used==0:
                far_future1.append(rows_data)

 


        far_future1=[ele for ele in far_future1 if ele not in future_data and not ele.品名.startswith('ｿﾌﾄﾌｱｲﾝ') and not ele.品名.startswith('ｿﾌﾄｽﾍﾟｼｬﾙ') and not ele.品名.startswith('ND10') and not ele.品名.startswith('ﾊｲｿﾌﾄ')]

        for_canned_total_data=today_data+future_data+far_future1
        canned_data=[ele for ele in for_canned_total_data if getattr(ele,'荷姿')=='缶' and getattr(ele,'MK特殊品')!='○']

        today_data=[ele for ele in today_data if ele not in canned_data]
        future_data=[ele for ele in future_data if ele not in canned_data]
        far_future1=[ele for ele in far_future1 if ele not in canned_data]


        #if saturday then remove few stuffs from these lists

        if elements.day_name()=='Saturday':
            prefixes=['MB-ｱﾛﾏｺﾞｰﾙﾄﾞCS','CNCマーガリン','ｴﾚﾊﾞｰﾙ-FB','FH-A6','ｼﾞｴﾈﾙ-','ｱﾛﾏ-ﾃﾞHTR-J','ｱﾛﾏｺﾞ-ﾙﾄﾞ']
            today_data = [instance for instance in today_data if not any(instance.品名.startswith(prefix) for prefix in prefixes)]
            future_data = [instance for instance in future_data if not any(instance.品名.startswith(prefix) for prefix in prefixes)]
            far_future1 = [instance for instance in far_future1 if not any(instance.品名.startswith(prefix) for prefix in prefixes)]
            # exit()

        total_data2=today_data+future_data
        if len(total_data2)==0:
            total_data2=far_future1
            far_future1=[]

        available_lines=['MK','FK','KO']
        for eachline in available_lines:
            ko_slicing=False
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

                premium_star=False
                max_batch=8
                # total_data3=[ele for ele in total_data2 if int(getattr(ele,'予定数量(㎏)'))<=6100 and int(getattr(ele,'MK流量_time'))!=0]
                total_data3=[ele for ele in total_data2 if  int(getattr(ele,'MK流量_time'))!=0]
                total_data3=[ele for ele in total_data3 if not ele.品名.startswith('ﾏﾙﾆｼﾛ')]


                total_data1=[]
                # A_found = False
                i=0

                for instance in total_data3:

                    if getattr(instance,'MK特殊品')=='○' :
               
                           
                       if i==0:
                            total_data1.append(instance)
                            i+=1

                    elif getattr(instance,'MK特殊品')=='×':
                        total_data1.append(instance)


                high_Soft_list=[]
                highsoft=[ele for ele in total_data1 if ele.品名.startswith('ﾊｲｿﾌﾄ') and ele.納期_copy==elements and ele.get_used==0]
                ND_with_other=[]
                high_softer=False

                if len(highsoft)>0:
                    ND_with_other=[ele for ele in Class_Data if ele.品名.startswith('ｿﾌﾄﾌｱｲﾝ') or ele.品名.startswith('ｿﾌﾄｽﾍﾟｼｬﾙ') or ele.品名.startswith('ND10')  ]
                    ND_with_other=[ele for ele in ND_with_other if elements+timedelta(days=15)>=ele.納期_copy and ele.get_used==0]
                    high_softer=True

                if len(ND_with_other)>0:
                    highsoft=highsoft+ND_with_other


                total_data1=[ele for ele in total_data1 if ele not in highsoft and not ele.品名.startswith('ｿﾌﾄﾌｱｲﾝ') and not ele.品名.startswith('ｿﾌﾄｽﾍﾟｼｬﾙ') and not ele.品名.startswith('ND10') and not ele.品名.startswith('ﾊｲｿﾌﾄ')]


                for_MK_magarin=[ele for ele in total_data1 if getattr(ele,'一般マーガリン製品')=='○']
                for_MK_magarin = sorted(for_MK_magarin, key=lambda x: x.納期_copy)
                if len(for_MK_magarin):
                    MK_margarin_nearest_date=for_MK_magarin[0].納期_copy

                for_MK_premium_star=[ele for ele in total_data1 if getattr(ele,'プレミアムスター製品')=='○']
                for_MK_premium_star = sorted(for_MK_premium_star, key=lambda x: x.納期_copy)
                if len(for_MK_premium_star):
                    MK_premium_star_nearest_date=for_MK_premium_star[0].納期_copy

                # if high_softer:


                if elements.day_name()=='Monday' or high_softer:
                    total_data=[ele for ele in total_data1 if getattr(ele,'プレミアムスター製品')!='○']
                    far_future=[ele for ele in far_future1 if getattr(ele,'プレミアムスター製品')!='○']
                    max_batch=10


                elif MK_margarin_nearest_date is None and MK_premium_star_nearest_date is not None and not high_softer:
                    total_data=[ele for ele in total_data1 if getattr(ele,'一般マーガリン製品')!='○']
                    far_future=[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']
                    max_batch=8
                    premium_star=True
                
                elif MK_margarin_nearest_date is not None and MK_premium_star_nearest_date is None:
                    total_data=[ele for ele in total_data1 if getattr(ele,'プレミアムスター製品')!='○']
                    far_future=[ele for ele in far_future1 if getattr(ele,'プレミアムスター製品')!='○']
                    max_batch=10

                elif MK_margarin_nearest_date is not None and MK_premium_star_nearest_date is not None and not high_softer:
                    if MK_premium_star_nearest_date<=MK_margarin_nearest_date:
                        total_data=[ele for ele in total_data1 if getattr(ele,'一般マーガリン製品')!='○']
                        far_future=[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']
                        premium_star=True
                        max_batch=8
                    else:
                        total_data=[ele for ele in total_data1 if getattr(ele,'プレミアムスター製品')!='○']
                        far_future=[ele for ele in far_future1 if getattr(ele,'プレミアムスター製品')!='○']
                        max_batch=10                            

                else:
                    if len(far_future1):
                        for_MK_magarin=[ele for ele in far_future if getattr(ele,'一般マーガリン製品')=='○']
                        for_MK_magarin = sorted(for_MK_magarin, key=lambda x: x.納期_copy)
                        if len(for_MK_magarin):
                            MK_margarin_nearest_date=for_MK_magarin[0].納期_copy


                        for_MK_premium_star=[ele for ele in far_future if getattr(ele,'プレミアムスター製品')=='○']
                        for_MK_premium_star = sorted(for_MK_premium_star, key=lambda x: x.納期_copy)
                        if len(for_MK_premium_star):
                            MK_premium_star_nearest_date=for_MK_premium_star[0].納期_copy


                        if elements.day_name()=='Monday' or high_softer:
                            far_future=[ele for ele in far_future1 if getattr(ele,'プレミアムスター製品')!='○']
                            max_batch=10
                            

                        elif MK_margarin_nearest_date is not None and MK_premium_star_nearest_date is None :
                            far_future=[ele for ele in far_future1 if getattr(ele,'プレミアムスター製品')!='○']
                            max_batch=10

                        elif MK_margarin_nearest_date is None and MK_premium_star_nearest_date is not None and not high_softer:
                            far_future=[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']
                            max_batch=8
                            premium_star=True

                        elif MK_margarin_nearest_date is not None and MK_premium_star_nearest_date is not None:
                            if MK_margarin_nearest_date<=MK_premium_star_nearest_date:
                                far_future=[ele for ele in far_future1 if getattr(ele,'プレミアムスター製品')!='○']
                                max_batch=10
                            else:
                                far_future=[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']
                                max_batch=8
                                premium_star=True


                        # else:
                        #     far_future=[ele for ele in far_future1]


            elif eachline =='FK':
                max_batch=10
                flat_spread=False
                total_data1=[ele for ele in total_data2 if int(getattr(ele,'予定数量(㎏)'))<=5500 and int(getattr(ele,'FK流量_time'))!=0 and ele.get_used==0]
                total_data1=[ele for ele in total_data1 if not ele.品名.startswith('ﾏﾙﾆｼﾛ')]

                high_Soft_list=[]
                highsoft=[ele for ele in total_data1 if ele.品名.startswith('ﾊｲｿﾌﾄ') and ele.納期_copy==elements and ele.get_used==0]
                ND_with_other=[]
                high_softer=False

                if len(highsoft)>0:
                    ND_with_other=[ele for ele in Class_Data if ele.品名.startswith('ｿﾌﾄﾌｱｲﾝ') or ele.品名.startswith('ｿﾌﾄｽﾍﾟｼｬﾙ') or ele.品名.startswith('ND10')  ]
                    ND_with_other=[ele for ele in ND_with_other if elements+timedelta(days=15)>=ele.納期_copy and ele.get_used==0]
                    high_softer=True

                if len(ND_with_other)>0:
                    highsoft=highsoft+ND_with_other


                total_data1=[ele for ele in total_data1 if ele not in highsoft]
                # total_data1=highsoft+total_data1
                
                if elements.day==22 and elements.month==4 and eachline=='FK':
                    # print(high_softer)
                    create_csv_from_objects(f'FK_22_04_{elements.day_name()}.csv',total_data1)
                    # exit()


                for_FK_flatspread=[ele for ele in total_data1 if getattr(ele,'ファットスプレッド製品')=='○']
                for_FK_flatspread=sorted(for_FK_flatspread,key=lambda x:x.納期_copy)
                if len(for_FK_flatspread):
                    FK_flat_spread_nearest_date=for_FK_flatspread[0].納期_copy

                for_FK_magarin=[ele for ele in total_data1 if getattr(ele,'一般マーガリン製品')=='○']
                for_FK_magarin = sorted(for_FK_magarin, key=lambda x: x.納期_copy)
                if len(for_FK_magarin):
                    FK_margarin_nearest_date=for_FK_magarin[0].納期_copy

                if FK_flat_spread_nearest_date is not None and FK_margarin_nearest_date is None and not high_softer:
                    total_data=[ele for ele in total_data1 if getattr(ele,'一般マーガリン製品')!='○']
                    far_future=[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']
                    max_batch=5
                    flat_spread=True

                elif FK_flat_spread_nearest_date is None and FK_margarin_nearest_date is not None:
                    total_data=[ele for ele in total_data1 if getattr(ele,'ファットスプレッド製品')!='○']
                    far_future=[ele for ele in far_future1 if getattr(ele,'ファットスプレッド製品')!='○']
                    max_batch=10

                elif FK_flat_spread_nearest_date is not None and FK_margarin_nearest_date is not None and not high_softer:
                    if FK_flat_spread_nearest_date<=FK_margarin_nearest_date:
                        total_data=[ele for ele in total_data1 if getattr(ele,'一般マーガリン製品')!='○']
                        far_future=[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']
                        max_batch=5
                        flat_spread=True
                    else:
                        total_data=[ele for ele in total_data1 if getattr(ele,'ファットスプレッド製品')!='○']
                        far_future=[ele for ele in far_future1 if getattr(ele,'ファットスプレッド製品')!='○']
                        max_batch=10

                else:
                    if len(far_future1):
                        for_FK_magarin=[ele for ele in far_future if getattr(ele,'一般マーガリン製品')=='○']
                        for_FK_magarin = sorted(for_FK_magarin, key=lambda x: x.納期_copy)
                        if len(for_FK_magarin):
                            FK_margarin_nearest_date=for_FK_magarin[0].納期_copy


                        for_FK_flatspread=[ele for ele in far_future if getattr(ele,'ファットスプレッド製品')=='○']
                        for_FK_flatspread = sorted(for_FK_flatspread, key=lambda x: x.納期_copy)
                        if len(for_FK_flatspread):
                            FK_flat_spread_nearest_date=for_FK_flatspread[0].納期_copy

                        if FK_margarin_nearest_date is None and FK_flat_spread_nearest_date is not None and not high_softer:
                            far_future=[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']
                            max_batch=5
                            flat_spread=True


                        elif FK_margarin_nearest_date is not None and FK_flat_spread_nearest_date is None:
                            far_future=[ele for ele in far_future1 if getattr(ele,'ファットスプレッド製品')!='○']
                            max_batch=10

                        elif FK_margarin_nearest_date is not None and FK_flat_spread_nearest_date is not None:
                            if FK_flat_spread_nearest_date<=FK_margarin_nearest_date:
                                far_future=[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']
                                max_batch=5
                                flat_spread=True
                            else:
                                far_future=[ele for ele in far_future1 if getattr(ele,'ファットスプレッド製品')!='○']
                                max_batch=10
                        # else:
                        #     far_future=[ele for ele in far_future1]
                if len(total_data):
                    first_data=total_data[0]
                    if getattr(first_data,'一般マーガリン製品')=='○':
                        total_data=[ele for ele in total_data if int(getattr(ele,'予定数量(㎏)'))<=5000]


                

            elif eachline=='KO':
                total_data1=[ele for ele in total_data2 if int(getattr(ele,'予定数量(㎏)'))<=4800  and int(getattr(ele,'KO流量_time'))!=0 and getattr(ele,'窒素ガス')!='○']
                total_data=[ele for ele in total_data1]
                far_future=[ele for ele in far_future1 if int(getattr(ele,'予定数量(㎏)'))<=4800  and int(getattr(ele,'KO流量_time'))!=0 and getattr(ele,'窒素ガス')!='○']

                ko_slice=[ele for ele in total_data1 if getattr(ele,'KOスライス製品')=='○']


                if elements.day_name()=='Saturday':
                    ko_slice=[]
                    Magarin=True


                probhibited_hour=[23,0,1,2,3,4,5,6]
                non_mb_orimpia=[ele for ele in ko_slice if not ele.品名.startswith('MB-ｵﾘﾝﾋﾟｱ')]

                if KO.start_time.hour in probhibited_hour and len(non_mb_orimpia)==0:
                    ko_slice=[]
                


                if len(ko_slice)>0 and not Magarin:
                    # new_future=[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']






                    total_data=[ele for ele in total_data1 if getattr(ele,'一般マーガリン製品')!='○']#+[ele for ele in far_future1 if getattr(ele,'一般マーガリン製品')!='○']
                    far_future=[ele for ele in far_future if getattr(ele,'一般マーガリン製品')!='○']
                    ko_slicing=True


                else:
                    total_data=[ele for ele in total_data1 if getattr(ele,'KOスライス製品')!='○']
                    far_future=[ele for ele in far_future if getattr(ele,'KOスライス製品')!='○']

                    if elements.day_name()=='Saturday':
                        total_data=total_data+far_future
                        far_future=[]
                        
                    

                    if (elements>KO.start_time-timedelta(minutes=60)) or elements.day_name()=='Saturday':
                        Magarin=True
                        cleaning_time=20
                        KO=Line_select('KO',elements,cleaning_time,Magarin)
                        KO_line_total_time=840
                        
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


            # if saisyu_value==0:
            current_line_last=current_line_last+far_current_line_last
            remaining_line_last=remaining_line_last+far_remaining_line_last
            far_current_line_last=[]
            far_remaining_line_last=[]


            if eachline=='MK' and len(highsoft)>0:
                first_list=highsoft+first_list

            if eachline=='FK' and len(highsoft)>0:
                first_list=highsoft+first_list

            

            A_Group,B_Group,C_Group,D_Group,F_Group,E_Group=sequence(current_line_middle,current_line_last,remaining_line_middle,remaining_line_last,first_list)
                            
            future_A_Group,future_B_Group,future_C_Group,future_D_Group,future_F_Group,future_E_Group=sequence(far_current_line_middle,far_current_line_last,far_remaining_line_middle,far_remaining_line_last,far_first_list)
            
            if ko_slicing:

                order = {'無し': 0, '低': 1, '普通': 2, '高': 3}
                A_Group=sorted(A_Group,key=lambda x: order[x.塩])
                B_Group=sorted(B_Group,key=lambda x: order[x.塩])
                C_Group=sorted(C_Group,key=lambda x: order[x.塩])
                D_Group=sorted(D_Group,key=lambda x: order[x.塩])
                F_Group=sorted(F_Group,key=lambda x: order[x.塩])

                future_A_Group=sorted(future_A_Group,key=lambda x: order[x.塩])
                future_B_Group=sorted(future_B_Group,key=lambda x: order[x.塩])
                future_C_Group=sorted(future_C_Group,key=lambda x: order[x.塩])
                future_D_Group=sorted(future_D_Group,key=lambda x: order[x.塩])
                future_F_Group=sorted(future_F_Group,key=lambda x: order[x.塩])


            current_group= A_Group+B_Group+C_Group+D_Group+F_Group
            future_groups=future_A_Group+future_B_Group+future_C_Group+future_D_Group+future_F_Group


            copy_future_groups=copy.deepcopy(future_groups)

            subete_group=A_Group+B_Group+C_Group+D_Group+F_Group

            last_in_subete_group=[ele for ele in subete_group if ele.last==1]

            if eachline=='MK':#and elements>=datetime.datetime(2023,3,22) and elements<datetime.datetime(2023,4,18)
                last_in_subete_group.sort(key=lambda instance: instance.priority_MK != 1)
                

            if eachline=='FK':#and elements>=datetime.datetime(2023,3,22) and elements<datetime.datetime(2023,4,18)
                last_in_subete_group.sort(key=lambda instance: instance.priority_FK != 1)

            if eachline=='KO':#and elements>=datetime.datetime(2023,3,22) and elements<datetime.datetime(2023,4,18)
                last_in_subete_group.sort(key=lambda instance: instance.priority_KO != 1)


            last_in_subete_group=sorted(last_in_subete_group, key=lambda ele: ele.納期_copy)

            prefixes = ["CNCマーガリン", "ｴﾚﾊﾞｰﾙ-FB", "FH-A6",
             "FH-A6","ﾘｽｻｸｻｸﾏ-ｶﾞﾘﾝV", "ｼﾞｴﾈﾙ",  "ｴﾚﾊﾞ-ﾙ", 
             "ｱﾛﾏ-ﾃﾞｿﾌﾄ",  "ｴﾚﾊﾞ-ﾙﾚ-ﾁｴCP", "ﾗﾝﾃﾞｨCPﾏｰｶﾞﾘ", 
             "ﾗﾝﾃﾞｨCPﾏｰｶﾞﾘﾝ-F","ﾊﾞﾀ-ﾘﾂﾁﾄｶﾁADF"]
            
            

            # Create a list of instances of MyClass
            no_limit_last=[]

            if len(last_in_subete_group)>0:
                matching_prefixes_first_instance = [prefix for prefix in prefixes if last_in_subete_group[0].品名.startswith(prefix)]

                if matching_prefixes_first_instance:
                    matching_instances = [instance for instance in last_in_subete_group if 
                                          instance.品名.startswith(matching_prefixes_first_instance[0])]
                    for instance in matching_instances:
                        no_limit_last.append(instance)
                        subete_group=[ele for ele in subete_group if ele.last==0]
   

            if not ko_slicing:#
                subete_group,current_group,future_groups=yusen(subete_group,current_group,future_groups,elements,optimizer,eachline)

            subete_ikeru_task=subete_group#A_Group+B_Group+C_Group+D_Group+F_Group

            can_A_first=[ele for ele in canned_data if getattr(ele,'アレルゲン')=='A']
            can_B_first=[ele for ele in canned_data if getattr(ele,'アレルゲン')=='B']
            can_C_first=[ele for ele in canned_data if getattr(ele,'アレルゲン')=='C']
            can_D_first=[ele for ele in canned_data if getattr(ele,'アレルゲン')=='D']
            can_F_first=[ele for ele in canned_data if getattr(ele,'アレルゲン')=='F']

            moto_canned_data=can_A_first+can_B_first+can_C_first+can_D_first+can_F_first

            canned_data1=can_A_first+can_B_first+can_C_first+can_D_first+can_F_first
            canned_data1=allowable_in_same_group(canned_data1)
            canned_data1=arerugen_checker(canned_data1)

            moto_canned_data=[ele for ele in moto_canned_data if ele not in canned_data1]
            
            if eachline!='KO':

                highsoft=[ele for ele in subete_ikeru_task if ele.品名.startswith('ﾊｲｿﾌﾄ') and ele.納期_copy==elements and ele.get_used==0]
                ND_with_other=[]

                if len(highsoft)>0:
                    ND_with_other =[ele for ele in subete_ikeru_task if ele.品名.startswith('ｿﾌﾄﾌｱｲﾝ') or ele.品名.startswith('ｿﾌﾄｽﾍﾟｼｬﾙ') or ele.品名.startswith('ND10')  ]
                    ND_with_other =[ele for ele in ND_with_other if elements+timedelta(days=15)>=ele.納期_copy and ele.get_used==0]

                if len(ND_with_other)>0:
                    highsoft=highsoft+ND_with_other


                subete_ikeru_task=[ele for ele in subete_ikeru_task if ele not in highsoft]

                subete_ikeru_task=highsoft+subete_ikeru_task

                if elements.month==3 and elements.day==16 and eachline=='MK':
                    create_csv_from_objects(f'mk3_16_{elements.day_name()}_{elements.month}.csv', subete_ikeru_task)

               
                if eachline=='MK' and not premium_star:

                    subete_ikeru_task=allowable_in_same_group(subete_ikeru_task)
                    arerugen_check_list=arerugen_checker(subete_ikeru_task)


                elif eachline=='FK' and not flat_spread:
                    subete_ikeru_task=allowable_in_same_group(subete_ikeru_task)
                    arerugen_check_list=arerugen_checker(subete_ikeru_task)

                else:

                    arerugen_check_list=arerugen_checker_new(subete_ikeru_task)

                if elements.month==3 and elements.day==16 and eachline=='MK':
                    create_csv_from_objects(f'mk3_16_after{elements.day_name()}_{elements.month}.csv', arerugen_check_list)

                if elements.day_name()=='Monday' and eachline=='MK':# and MK_FK_selector%2==0:


                    deep_copies_list = [copy.deepcopy(obj) for obj in master_sunday_data]
                    for ele in deep_copies_list:
                        ele.納期_copy=elements
                        ele.納期=str(elements.year)+str(elements.month)+str(elements.day)

                    
                    subete_ikeru_task=deep_copies_list+subete_ikeru_task
                    arerugen_check_list=allowable_in_same_group(subete_ikeru_task)
                    arerugen_check_list=arerugen_checker(arerugen_check_list)
                    # print("IN MK")

            else:
                if not Magarin:
                    arerugen_check_list=salt_order_checker(ko_list+subete_ikeru_task)
                    arerugen_check_list=arerugen_checker(arerugen_check_list)                    
                    arerugen_check_list=[ele for ele in arerugen_check_list if ele not in ko_list]
                    if len (arerugen_check_list)==0 and len(subete_ikeru_task)!=0:

                        #the added code portion neglects the data which needs the cleaning time and performs the 
                        #allocation on magarin data the code remsembles same to the code above because we are doing same thing
                        #we could have used a function for the same purpose to reduce the code
                        if elements>KO.start_time:

                            ko_list=[]

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
                            # for ele in subete_ikeru_task:

                            total_data=[ele for ele in total_data1 if getattr(ele,'KOスライス製品')!='○' and getattr(ele,'窒素ガス')!='○']
                            far_future=[ele for ele in far_future1 if getattr(ele,'KOスライス製品')!='○' and getattr(ele,'窒素ガス')!='○']
                            # far_future=[]
                            Magarin=True
                            cleaning_time=20
                            KO=Line_select('KO',elements,cleaning_time,Magarin)
                            KO_line_total_time=840

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

                                
                            # if saisyu_value==0:
                            current_line_last=current_line_last+far_current_line_last
                            remaining_line_last=remaining_line_last+far_remaining_line_last
                            far_current_line_last=[]
                            far_remaining_line_last=[]

                            A_Group,B_Group,C_Group,D_Group,F_Group,E_Group=sequence(current_line_middle,current_line_last,remaining_line_middle,remaining_line_last,first_list)

                            current_group= A_Group+B_Group+C_Group+D_Group+F_Group
                            future_A_Group,future_B_Group,future_C_Group,future_D_Group,future_F_Group,future_E_Group=sequence(far_current_line_middle,far_current_line_last,far_remaining_line_middle,far_remaining_line_last,far_first_list)

                            future_groups=future_A_Group+future_B_Group+future_C_Group+future_D_Group+future_F_Group


                            subete_group=A_Group+B_Group+C_Group+D_Group+F_Group



                            subete_group,current_group,future_groups=yusen(subete_group,current_group,future_groups,elements,optimizer,eachline)
                            subete_ikeru_task=subete_group#A_Group+B_Group+C_Group+D_Group+F_Group


                            subete_ikeru_task=allowable_in_same_group(subete_ikeru_task)
                            arerugen_check_list=arerugen_checker(subete_ikeru_task)

                        else:
                            continue
                            

                else:
                    subete_ikeru_task=allowable_in_same_group(subete_ikeru_task)
                    arerugen_check_list=arerugen_checker(subete_ikeru_task)

            last_from_arerugen=[ele for ele in arerugen_check_list if getattr(ele,'last')==1]

            # today_last=[ele for ele in last_from_arerugen if getattr(ele,'納期_copy')==elements]
            last_found=False

            today_last=sorted(last_from_arerugen, key=lambda ele: (ele.納期_copy))
            

            if len(today_last)>0:

                first_last=today_last[0]

                today_last=[ele for ele in today_last if ele.品名.startswith(first_last.品名)]



            if len(today_last)>0:
                current_last,corresponding_type=last_checker(today_last)

                if len(today_last)>0 and len(current_last)==0:
                    current_last=[today_last[0]]
                    future_groups=[ele for ele in future_groups if getattr(ele,'last')!=1]
                    current_group=[ele for ele in current_group if getattr(ele,'last')!=1]
                    last_found=True


                else:

                    current_last,corresponding_type=last_checker_using_type(last_from_arerugen,corresponding_type)

            else:
                current_last,corresponding_type=last_checker(last_from_arerugen)

            if len(last_from_arerugen)>0 and len(current_last)==0 and not last_found:
                # last_from_arerugen=sorted(last_from_arerugen, key=lambda ele: (ele.納期_copy))
                current_last=[last_from_arerugen[0]]
                future_groups=[ele for ele in future_groups if getattr(ele,'last')!=1]
                current_group=[ele for ele in current_group if getattr(ele,'last')!=1]
                
            elif len(last_from_arerugen)>0 and len(current_last)>0 and not last_found:

                future_last=[ele for ele in future_groups if getattr(ele,'last')==1]
                last_future_group,corresponding_type=last_checker_using_type(future_last,corresponding_type)

                new_current_last=[ele for ele in current_group if getattr(ele,'last')==1]
                new_current_last,corresponding_type=last_checker_using_type(new_current_last,corresponding_type)
                current_group=[ele for ele in current_group if getattr(ele,'last')!=1]+new_current_last

                future_groups=[ele for ele in future_groups if getattr(ele,'last')!=1]+last_future_group
            else:
                future_groups=[ele for ele in future_groups if getattr(ele,'last')!=1]


            arerugen_check_list=[ele for ele in arerugen_check_list if getattr(ele,'last')!=1]+current_last

            arerugen_check_list=arerugen_check_list+no_limit_last


            s720K=[ele for ele in arerugen_check_list if getattr(ele,'品名')=='ﾆﾕ-YCS ｽﾄﾚﾂﾁ720K']
            s750k=[ele for ele in arerugen_check_list if getattr(ele,'品名')=='ﾆﾕ-YCS ｽﾄﾚﾂﾁ750K']

            if len(s720K)%2!=0:
                s720K=s720K[:-1]
                arerugen_check_list=[ele for ele in arerugen_check_list if getattr(ele,'品名')!='ﾆﾕ-YCS ｽﾄﾚﾂﾁ720K']
                arerugen_check_list=s720K+arerugen_check_list

                # arerugen_check_list=reorder_same_name(arerugen_check_list)

            
            if len(s750k)%2!=0:
                s750k=s750k[:-1]
                arerugen_check_list=[ele for ele in arerugen_check_list if getattr(ele,'品名')!='ﾆﾕ-YCS ｽﾄﾚﾂﾁ750K']
                arerugen_check_list=s750k+arerugen_check_list

                # arerugen_check_list=reorder_same_name(arerugen_check_list)

            
            current_group=[ele for ele in current_group if ele not in arerugen_check_list and ele.last==0]

            counter=1
            mk_list=[]                   
            fk_list=[]

            if eachline=='MK' and elements.day_name()!='Sunday':
                # if  not premium_star:
                
                allowable_time=elements+timedelta(minutes=440)
                e1_group=[]

                attribute_line='MK流量_time'
                Egroup_bool=[el for el in E_Group if getattr(el,'納期_copy')==elements]

                # if elements.month==4:
                #     if elements.day>=5 and len(E_Group)>0:
                #         e1_group,counter,MK_line_total_time,allowable_time=mk_tokusyouhin_handler(E_Group,MK,elements,attribute_line,counter,MK_line_total_time,allowable_time)

                # else:
                if len(E_Group)>0:
                    e1_group,counter,MK_line_total_time,allowable_time=mk_tokusyouhin_handler(E_Group,MK,elements,attribute_line,counter,MK_line_total_time,allowable_time)



                if len(e1_group)==0:
                    # mk_tokusyouhin=[el for el in arerugen_check_list if getattr(el,'MK特殊品')=='○' and getattr(el,'納期_copy')==elements]
                    mk_tokusyouhin=[el for el in arerugen_check_list if getattr(el,'MK特殊品')=='○']
                    if len(mk_tokusyouhin)==0:
                        mk_tokusyouhin=[el for el in current_group if getattr(el,'MK特殊品')=='○']
                    if len(mk_tokusyouhin):
                        e1_group,counter,MK_line_total_time,allowable_time=mk_tokusyouhin_handler([mk_tokusyouhin[0]],MK,elements,attribute_line,counter,MK_line_total_time,allowable_time)

                #         if getattr(mk_tokusyouhin[0],'new_creation')==0:

                        
                #         else:
                #             splitted_random=getattr(mk_tokusyouhin[0],'new_creation')
                #             same_split=[instance for instance in mk_tokusyouhin if getattr(instance,'new_creation')==splitted_random]
                #             e1_group,counter,MK_line_total_time,allowable_time=mk_tokusyouhin_handler(same_split,MK,elements,attribute_line,counter,MK_line_total_time,allowable_time)



                MK_LIST=MK_LIST+e1_group
                arerugen_check_list=[ele for ele in arerugen_check_list if getattr(ele,'MK特殊品')!='○']

                canned_list=[]

                if len(canned_data1)>0 and len(e1_group)>0:
                    canned_list,counter,MK_line_total_time=canned_data_allocation(MK_line_total_time,MK,canned_data1,counter,allowable_time,elements,moto_canned_data)
                    MK_LIST=MK_LIST+canned_list
                    continue


                else:
                    current_day_canned_data=[ele for ele in canned_data1 if getattr(ele,'納期_copy')==elements]
                    if len(current_day_canned_data):
                        canned_list,counter,MK_line_total_time=canned_data_allocation(MK_line_total_time,MK,canned_data1,counter,allowable_time,elements,moto_canned_data)
                        MK_LIST=MK_LIST+canned_list
                        continue


                highsoft_list=[]
                NDplusother=[]
                for ele in arerugen_check_list:
                    if ele.品名.startswith('ﾊｲｿﾌﾄ'):
                        highsoft_list.append(ele)
                
                    if ele.品名.startswith('ｿﾌﾄﾌｱｲﾝ') or ele.品名.startswith('ｿﾌﾄｽﾍﾟｼｬﾙ') or ele.品名.startswith('ND10'):
                        NDplusother.append(ele)

                

                

                high_list=[]
                if len(highsoft_list)>0:
                    highsoft_other=highsoft_list+NDplusother
                    

                    for ele in highsoft_other:

                        if MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')>0:
                            high_list.append(ele)   
                            MK_line_total_time=MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')
                            setattr(ele,'get_used',1)

                    for ele in high_list:

                        before_time=allowable_time
                        after_time=before_time+timedelta(minutes=getattr(ele,'MK流量_time'))
                        allowable_time=after_time+timedelta(minutes=MK.cleaning_time)

                        setattr(ele,'slot',f'{before_time}-->{after_time}')
                        setattr(ele,'順番',counter)
                        setattr(ele,'生産日',elements.date())
                        setattr(ele,'start',f'{before_time}')
                        setattr(ele,'end',f'{after_time}')
                        setattr(ele,'day',f'{after_time.day_name()}')


                        counter+=1

                    if len(NDplusother)==0:
                        allowable_time=allowable_time+timedelta(hours=3)
                        MK_line_total_time=MK_line_total_time-MK.cleaning_time-180

                    MK_LIST=MK_LIST+high_list
                
                current_batch_size=len(e1_group)+len(high_list)+len(canned_list)
                arerugen_check_list=[ele for ele in arerugen_check_list if ele not in high_list]

                mk_list_last=[]
                randi_counter=0

                for ele in arerugen_check_list:
                    if MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')>0 and getattr(ele,'last')==1 and current_batch_size+len(mk_list_last)<max_batch:

                        if getattr(ele,'ランディ')=='○':
                            randi_counter+=1
                        if randi_counter>5:
                            continue

                        mk_list_last.append(ele)   
                        MK_line_total_time=MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')
                        setattr(ele,'get_used',1)

                arerugen_check_list=[ele for ele in arerugen_check_list if getattr(ele,'last')!=1]

                newycs_count=0

                for ele in arerugen_check_list:

                    if not ele.品名.startswith('ﾆﾕ-YCS') and MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')>0 and current_batch_size+len(mk_list)+len(mk_list_last)<max_batch:

                    
                        mk_list.append(ele)   
                        MK_line_total_time=MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')
                        setattr(ele,'get_used',1)

                    elif ele.品名.startswith('ﾆﾕ-YCS') and newycs_count==0 and  MK_line_total_time-MK.cleaning_time*2-getattr(ele,'MK流量_time')*2>0 and current_batch_size+len(mk_list)+len(mk_list_last)<max_batch:

                        mk_list.append(ele)   
                        MK_line_total_time=MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')
                        setattr(ele,'get_used',1)
                        newycs_count+=1

                    elif ele.品名.startswith('ﾆﾕ-YCS') and newycs_count==1 and  MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')>0 and current_batch_size+len(mk_list)+len(mk_list_last)<max_batch:

                        mk_list.append(ele)   
                        MK_line_total_time=MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')
                        setattr(ele,'get_used',1)

                if len(no_limit_last)>0:

                    if len(NDplusother)==0:
                        mk_list=mk_list#+mk_list_last

                    elif len(NDplusother)>0 and len(high_list)>0:
                        mk_list=high_list+mk_list#+mk_list_last
                    #don't put mk list last right now put it at the end but change the batch size only here
                    max_batch=max_batch-len(mk_list_last)

                else:
                    if len(NDplusother)==0:

                        mk_list=mk_list+mk_list_last

                    elif len(NDplusother)>0 and len(high_list)>0:
                        mk_list=high_list+mk_list+mk_list_last



                


                current_group=[ele for ele in current_group if getattr(ele,'MK特殊品')!='○']

                current1=[ele for ele in current_group if ele.品名.startswith('ﾆﾕ-YCS')]
                if len (current1)%2!=0:
                    current1=current1[:-1]
                if len(current1)>2:
                    current1=current1[:2]

                if len(current1)==1:
                    current1=[]


                current_group=[ele for ele in current_group if getattr(ele,'get_used')==0]

                current_group=[ele for ele in current_group if ele not in current1]

                if len(current1)>0:

                    time_required_for_both_in_current1=MK.cleaning_time+getattr(current1[0],'MK流量_time')+MK.cleaning_time+getattr(current1[1],'MK流量_time')

                    if MK_line_total_time-time_required_for_both_in_current1<0:
                        current1=[]

                # current_group=current1+current_group
                current_group=[ele for ele in current_group if not ele.品名.startswith('ﾆﾕ-YCS')]
                current_group=current1+current_group

                length_of_newy=0

                
                current_group=[ele for ele in current_group if getattr(ele,'get_used')==0]
                for ele in current_group:
                    if MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')>0 and getattr(ele,'get_used')==0 and not ele.品名.startswith('ﾊｲｿﾌﾄ') and current_batch_size+len(mk_list)<max_batch:
                        # and not ele.品名.startswith('ﾆﾕ-YCS'):#and getattr(ele,'last')!=1:
                        
                        if getattr(ele,'ランディ')=='○':
                            randi_counter+=1
                            if randi_counter>5:
                                continue

                        if ele.品名.startswith('ﾆﾕ-YCS'):
                            length_of_newy+=1
                            if length_of_newy>2:
                                continue

                        mk_list_copy=mk_list.copy()
                        mk_length=len(mk_list)
                        for i in range (mk_length+1):
                            mk_list_copy.insert(i,ele)
                            if  not premium_star:
                                mk_list_copy=allowable_in_same_group(mk_list_copy)
                                mk_list_copy=arerugen_checker(mk_list_copy)
                            else:
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
                # future_groups=sorted(future_groups, key=lambda ele: ele.品名.startswith('ﾆﾕ-YCS'))


                for ele in future_groups:
                    if MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')>0 and not ele.品名.startswith('ﾆﾕ-YCS') and not ele.品名.startswith('ﾊｲｿﾌﾄ') and current_batch_size+len(mk_list)<max_batch:# and getattr(ele,'last')!=1:
                        # if elements.day==27 and elements.month==3:
                        #     print('futuregroup')
                        #     print(ele.品名)

                        if getattr(ele,'ランディ')=='○':
                            randi_counter+=1
                            if randi_counter>5:
                                continue

                        mk_list_copy=mk_list.copy()
                        mk_length=len(mk_list)
                        for i in range (mk_length+1):
                            mk_list_copy.insert(i,ele)
                            if  not premium_star:
                                mk_list_copy=allowable_in_same_group(mk_list_copy)
                                mk_list_copy=arerugen_checker(mk_list_copy)

                            else:
                                mk_list_copy=arerugen_checker_new(mk_list_copy)

                            if len(mk_list_copy)>len(mk_list):
                                mk_list=mk_list_copy.copy()
                                MK_line_total_time=MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')
                                setattr(ele,'get_used',1)
                                break

                            else:
                                mk_list_copy=mk_list.copy()

                if len(mk_list)==0 and len(mk_list_last)==0:
                    copy_future_groups=last_remaining_appender_second_part(copy_future_groups,premium_star)

                    s720K=[ele for ele in copy_future_groups if getattr(ele,'品名')=='ﾆﾕ-YCS ｽﾄﾚﾂﾁ720K']
                    s750k=[ele for ele in copy_future_groups if getattr(ele,'品名')=='ﾆﾕ-YCS ｽﾄﾚﾂﾁ750K']

                    if len(s720K)%2!=0:
                        s720K=s720K[:-1]
                    if len(s720K)>2:
                        s720K=s720K[:2]

                    copy_future_groups=[ele for ele in copy_future_groups if getattr(ele,'品名')!='ﾆﾕ-YCS ｽﾄﾚﾂﾁ720K']
                    copy_future_groups=s720K+copy_future_groups
                    
                    if len(s750k)%2!=0:
                        s750k=s750k[:-1]

                    if len(s750k)>2:
                        s750k=s750k[:2]

                    copy_future_groups=[ele for ele in copy_future_groups if getattr(ele,'品名')!='ﾆﾕ-YCS ｽﾄﾚﾂﾁ750K']
                    copy_future_groups=s750k+copy_future_groups

                    copy_future_groups=reorder_same_name(copy_future_groups)



                    for ele in copy_future_groups:

                        if MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')>0 and getattr(ele,'get_used')==0 and current_batch_size+len(mk_list)<max_batch:
                            if getattr(ele,'ランディ')=='○':
                                randi_counter+=1
                                if randi_counter>5:
                                    continue
                            mk_list.append(ele)   
                            MK_line_total_time=MK_line_total_time-MK.cleaning_time-getattr(ele,'MK流量_time')
                            setattr(ele,'get_used',1)

                premimum_group='ﾌﾟﾚﾐｱﾑｽﾀ-DX'
                mk_list=grouping(mk_list,premimum_group) #'ﾌﾟﾚﾐｱﾑｽﾀ-DX'
                mk_list=sorting_FHA6(mk_list)

                #for aroma fold
                groupname1='ｱﾛﾏ-ﾃﾞHTR'
                groupname2='ｱﾛﾏｺﾞ-ﾙﾄﾞ'

                mk_list=grouping_two_groups_consecutively(mk_list,groupname1,groupname2)


                mk_list=[ele for ele in mk_list if ele not in MK_LIST]
                if len(no_limit_last)>0:
                    mk_list=mk_list+mk_list_last
                MK_LIST=MK_LIST+mk_list#+mk_list+


                groupname_type1= ['ﾌﾟﾗｽﾞﾏAR', 'ﾌﾟﾗｽﾞﾏNFC', 'ﾌﾟﾚﾐｱﾑｽﾀｰDX', 'ﾌﾟﾗｽﾞﾏDX', 'ｱﾛﾏｽﾀ', 'ｴﾚﾊﾞｰﾙｿﾌﾄ']
                groupname_type2=['ﾌﾟﾚﾐｱﾑｽﾀｰ', 'ﾌﾟﾗｽﾞﾏNFC', 'ﾌﾟﾚﾐｱﾑｽﾀ-DX', 'ﾌﾟﾗｽﾞﾏDX', 'ｱﾛﾏｽﾀｰ', 'ﾛｰﾚﾙｽﾀｰ']

                groupname_type1 = [convert_fullwidth_to_halfwidth(name) for name in groupname_type1]
                groupname_type2 = [convert_fullwidth_to_halfwidth(name) for name in groupname_type2]

                mk_list=sequential_grouping(mk_list,groupname_type1)
                mk_list=sequential_grouping(mk_list,groupname_type2)


                mk_list=reorder_same_name(mk_list)

                
                
                # this_linetotal_time=960
                # fk_list=[ele for ele in fk_list if ele not in high_list ]
                mk_list=[ele for ele in mk_list if ele not in high_list]
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

                    setattr(ele,'day',f'{after_time.day_name()}')

                    counter+=1

            
            elif eachline=='FK' and elements.day_name()!='Sunday':#
                allowable_time=elements+timedelta(minutes=440)

                #for highsoft allocation after this has to be  ND10・ｿﾌﾄﾌｧｲﾝ・ｿﾌﾄｽﾍﾟｼｬﾙ    or を組めない場合洗浄
                highsoft_list=[]
                NDplusother=[]
                for ele in arerugen_check_list:
                    if ele.品名.startswith('ﾊｲｿﾌﾄ'):
                        highsoft_list.append(ele)
                
                    if ele.品名.startswith('ｿﾌﾄﾌｧｲﾝ') or ele.品名.startswith('ｿﾌﾄｽﾍﾟｼｬﾙ') or ele.品名.startswith('ND10'):
                        NDplusother.append(ele)

                

                high_list=[]
                if len(highsoft_list)>0:
                    highsoft_other=highsoft_list+NDplusother
                    

                    for ele in highsoft_other:

                        if FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')>0:
                            high_list.append(ele)   
                            FK_line_total_time=FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')
                            setattr(ele,'get_used',1)

                    for ele in high_list:

                        before_time=allowable_time
                        after_time=before_time+timedelta(minutes=getattr(ele,'FK流量_time'))
                        allowable_time=after_time+timedelta(minutes=FK.cleaning_time)

                        setattr(ele,'slot',f'{before_time}-->{after_time}')
                        setattr(ele,'順番',counter)
                        setattr(ele,'生産日',elements.date())
                        setattr(ele,'start',f'{before_time}')
                        setattr(ele,'end',f'{after_time}')
                        setattr(ele,'day',f'{after_time.day_name()}')


                        counter+=1

                    if len(NDplusother)==0:
                        allowable_time=allowable_time+timedelta(hours=3)
                        FK_line_total_time=FK_line_total_time-FK.cleaning_time-180

                    FK_LIST=FK_LIST+high_list


                    # print(" i am here ")
                    # print(f"the high soft list length {len(highsoft_list)}")
                    # print(f"the high soft other length {len(highsoft_other)}")
                    # print(f"the ND plus other length {len(NDplusother)}")

                    # exit()


                #lets prioritize the 最終限定
                current_batch_size=len(high_list)

                arerugen_check_list=[ele for ele in arerugen_check_list if ele not in high_list]


                fk_list_last=[]
                randi_counter=0
                for ele in arerugen_check_list:
                    if FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')>0 and getattr(ele,'last')==1 and current_batch_size+len(fk_list_last)<max_batch:
                        # FK_LIST.append(ele)

                        if getattr(ele,'ランディ')=='○':
                            randi_counter+=1
                        if randi_counter>5:
                            continue

                        fk_list_last.append(ele)
                        FK_line_total_time=FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time') 
                        setattr(ele,'get_used',1)
                arerugen_check_list=[ele for ele in arerugen_check_list if getattr(ele,'last')!=1]


                # current_batch_size=current_batch_size+len(fk_list_last)   and current_batch_size+len(fk_list)<max_batch



                newycs_count=0

                for ele in arerugen_check_list:

                    if not ele.品名.startswith('ﾆﾕ-YCS') and FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')>0 and current_batch_size+len(fk_list)+len(fk_list_last)<max_batch:

                    
                        fk_list.append(ele)   
                        FK_line_total_time=FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')
                        setattr(ele,'get_used',1)

                    elif ele.品名.startswith('ﾆﾕ-YCS') and newycs_count==0 and  FK_line_total_time-FK.cleaning_time*2-getattr(ele,'FK流量_time')*2>0 and current_batch_size+len(fk_list)+len(fk_list_last)<max_batch:

                        fk_list.append(ele)   
                        FK_line_total_time=FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')
                        setattr(ele,'get_used',1)
                        newycs_count+=1

                    elif ele.品名.startswith('ﾆﾕ-YCS') and newycs_count==1 and  FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')>0 and current_batch_size+len(fk_list)+len(fk_list_last)<max_batch:

                        fk_list.append(ele)   
                        FK_line_total_time=FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')
                        setattr(ele,'get_used',1)

                if len(no_limit_last)>0:

                    if len(NDplusother)==0:

                        fk_list=fk_list#+fk_list_last

                    elif len(NDplusother)>0 and len(high_list)>0:
                        fk_list=high_list+fk_list#+fk_list_last

                    #no need to add fk_list_last right now add it at last but reduce the batch size
                    max_batch=max_batch-len(fk_list_last)

                else:
                    if len(NDplusother)==0:

                        fk_list=fk_list+fk_list_last

                    elif len(NDplusother)>0 and len(high_list)>0:
                        fk_list=high_list+fk_list+fk_list_last


                current_group=[ele for ele in current_group if getattr(ele,'get_used')==0]
                current1=[ele for ele in current_group if ele.品名.startswith('ﾆﾕ-YCS')]

                if len (current1)%2!=0:
                    current1=current1[:-1]
                if len(current1)>2:
                    current1=current1[:2]
                if len(current1)==1:
                    current1=[]

                current_group=[ele for ele in current_group if ele not in current1]

                if len(current1)>0:

                    time_required_for_both_in_current1=FK.cleaning_time+getattr(current1[0],'FK流量_time')+FK.cleaning_time+getattr(current1[1],'FK流量_time')

                    if FK_line_total_time-time_required_for_both_in_current1<0:
                        current1=[]

                current_group=[ele for ele in current_group if not ele.品名.startswith('ﾆﾕ-YCS')]
                current_group=current1+current_group

                length_of_newy=0
                for ele in current_group:
                    if FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')>0 and getattr(ele,'get_used')==0 and not ele.品名.startswith('ﾊｲｿﾌﾄ') and current_batch_size+len(fk_list)<max_batch:# and not ele.品名.startswith('ﾆﾕ-YCS'):# and getattr(ele,'last')!=1:
                        # if len(fk_list)>0:
                        if getattr(ele,'ランディ')=='○':
                            randi_counter+=1
                            if randi_counter>5:
                                continue

                        if ele.品名.startswith('ﾆﾕ-YCS'):
                            length_of_newy+=1
                            if length_of_newy>2:
                                continue

                        fk_list_copy=fk_list.copy()
                        fk_length=len(fk_list)
                        for i in range (fk_length+1):
                            fk_list_copy.insert(i,ele)
                            if not flat_spread:
                                fk_list_copy=allowable_in_same_group(fk_list_copy)
                                fk_list_copy=arerugen_checker(fk_list_copy)

                            else:
                                fk_list_copy=arerugen_checker(fk_list_copy)


                            if len(fk_list_copy)>len(fk_list):
                                fk_list=fk_list_copy.copy()
                                FK_line_total_time=FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')
                                setattr(ele,'get_used',1)
                                break

                            else:
                                fk_list_copy=fk_list.copy()

                for ele in future_groups:
                    if FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')>0 and not ele.品名.startswith('ﾆﾕ-YCS') and not ele.品名.startswith('ﾊｲｿﾌﾄ') and current_batch_size+len(fk_list)<max_batch:#and getattr(ele,'last')!=1:
                        # if len(fk_list)>0:
                        if getattr(ele,'ランディ')=='○':
                            randi_counter+=1
                            if randi_counter>5:
                                continue
                        fk_list_copy=fk_list.copy()
                        fk_length=len(fk_list)
                        for i in range (fk_length+1):
                            fk_list_copy.insert(i,ele)
                            # if not flat_spread:
                            if not flat_spread:
                                fk_list_copy=allowable_in_same_group(fk_list_copy)
                                fk_list_copy=arerugen_checker(fk_list_copy)

                            else:
                                fk_list_copy=arerugen_checker(fk_list_copy)


                            # else:
                            #     fk_list_copy=arerugen_checker_new(fk_list_copy)

                            if len(fk_list_copy)>len(fk_list):
                                fk_list=fk_list_copy.copy()
                                FK_line_total_time=FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')
                                setattr(ele,'get_used',1)
                                break

                            else:
                                fk_list_copy=fk_list.copy()


                if len(fk_list)==0 and len(fk_list_last)==0:
                    copy_future_groups=last_remaining_appender_second_part(copy_future_groups,flat_spread)

                    s720K=[ele for ele in copy_future_groups if getattr(ele,'品名')=='ﾆﾕ-YCS ｽﾄﾚﾂﾁ720K']
                    s750k=[ele for ele in copy_future_groups if getattr(ele,'品名')=='ﾆﾕ-YCS ｽﾄﾚﾂﾁ750K']

                    if len(s720K)%2!=0:
                        s720K=s720K[:-1]
                    if len(s720K)>2:
                        s720K=s720K[:2]
                    copy_future_groups=[ele for ele in copy_future_groups if getattr(ele,'品名')!='ﾆﾕ-YCS ｽﾄﾚﾂﾁ720K']
                    copy_future_groups=s720K+copy_future_groups

                    
                    if len(s750k)%2!=0:
                        s750k=s750k[:-1]
                    if len(s750k)>2:
                        s750k=s750k[:2]

                    copy_future_groups=[ele for ele in copy_future_groups if getattr(ele,'品名')!='ﾆﾕ-YCS ｽﾄﾚﾂﾁ750K']
                    copy_future_groups=s750k+copy_future_groups


                    copy_future_groups=reorder_same_name(copy_future_groups)


                    for ele in copy_future_groups:
                        if FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time')>0 and getattr(ele,'get_used')==0 and not ele.品名.startswith('ﾊｲｿﾌﾄ') and current_batch_size+len(fk_list)<max_batch:
                            # FK_LIST.append(ele)
                            if getattr(ele,'ランディ')=='○':
                                randi_counter+=1
                                if randi_counter>5:
                                    continue
                            fk_list.append(ele)
                            FK_line_total_time=FK_line_total_time-FK.cleaning_time-getattr(ele,'FK流量_time') 
                            setattr(ele,'get_used',1)
                    


                # FK_LIST=FK_LIST+fk_prior_outer_list+e1_group+fk_list
                fk_list=[ele for ele in fk_list if ele not in MK_LIST]
                if len(no_limit_last)>0:
                    fk_list=fk_list+fk_list_last

                FK_LIST=FK_LIST+fk_list
                # this_linetotal_time=960
                premimum_group='ﾌﾟﾚﾐｱﾑｽﾀ-DX'
                fk_list=grouping(fk_list,premimum_group)
                fk_list=sorting_FHA6(fk_list)

                #for aroma gold
                groupname1='ｱﾛﾏ-ﾃﾞHTR'
                groupname2='ｱﾛﾏｺﾞ-ﾙﾄﾞ'

                fk_list=grouping_two_groups_consecutively(fk_list,groupname1,groupname2)


                groupname_type1= ['ﾌﾟﾗｽﾞﾏAR', 'ﾌﾟﾗｽﾞﾏNFC', 'ﾌﾟﾚﾐｱﾑｽﾀｰDX', 'ﾌﾟﾗｽﾞﾏDX', 'ｱﾛﾏｽﾀ', 'ｴﾚﾊﾞｰﾙｿﾌﾄ']
                groupname_type2=['ﾌﾟﾚﾐｱﾑｽﾀｰ', 'ﾌﾟﾗｽﾞﾏNFC', 'ﾌﾟﾚﾐｱﾑｽﾀ-DX', 'ﾌﾟﾗｽﾞﾏDX', 'ｱﾛﾏｽﾀｰ', 'ﾛｰﾚﾙｽﾀｰ']

                # groupname_type1 = ['プラズマAR','プラズマNFC','プレミアムスターDX','プラズマDX','アロマスタ','エレバールソフト']
                groupname_type1 = [convert_fullwidth_to_halfwidth(name) for name in groupname_type1]
                groupname_type2 = [convert_fullwidth_to_halfwidth(name) for name in groupname_type2]

                fk_list=sequential_grouping(fk_list,groupname_type1)
                fk_list=sequential_grouping(fk_list,groupname_type2)

                fk_list=reorder_same_name(fk_list)

                fk_list=sorting_soza(fk_list)

                fk_list=[ele for ele in fk_list if ele not in high_list ]

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
                    setattr(ele,'day',f'{after_time.day_name()}')
                    counter+=1

            
            elif eachline=='KO' and not Magarin and elements.day_name()!='Saturday':

                arerugen_check_list=reorder_same_name(arerugen_check_list)



                nouki_and_seisanbi_same=[ele for ele in arerugen_check_list if getattr(ele,'納期_copy').date()<=(elements+timedelta(days=1)).date()]

                #prioritizing those which has nouki as current date insted those which has future nouki
                if len(nouki_and_seisanbi_same)>0:
                    index=arerugen_check_list.index(nouki_and_seisanbi_same[0])
                    previous_elements=arerugen_check_list[:index]

                    previous_elements_backup=copy.deepcopy(previous_elements)


                    while (len(nouki_and_seisanbi_same) + len(previous_elements))> 6 and len(previous_elements)>0:
                        index=index-1
                        previous_elements=previous_elements[:index]


                    removed_elements= [ele for ele in previous_elements if ele not in previous_elements_backup]
                    arerugen_check_list= [ele for ele in arerugen_check_list if ele not in removed_elements]




                arerugen_check_list_copy=arerugen_check_list.copy()
                # MB_orimpia=[ele for ele in arerugen_check_list if ele.品名.startswith('MB-ｵﾘﾝﾋﾟｱ')]  荷姿
                MB_orimpia=[ele for ele in arerugen_check_list if ele.荷姿.startswith('コンテナ')]

                arerugen_check_list=[ele for ele in arerugen_check_list if ele not in MB_orimpia]

                 
                for ele in arerugen_check_list:
                    
                    MB_orimpia=[orimpia for orimpia in MB_orimpia if getattr(orimpia,'get_used')==0]

                    for dle in MB_orimpia:

                        new_type_list=[ele for ele in arerugen_check_list if getattr(ele,'アレルゲン')=='A' and getattr(ele,'get_used')==0]
                        new_type_low=[ele for ele in arerugen_check_list if getattr(ele,'アレルゲン')=='B' and getattr(ele,'塩')=='低' and getattr(ele,'get_used')==0]

                        T2=len(new_type_list)==0 and len(new_type_low)==0

                        restricted_time=KO.start_time+timedelta(minutes=getattr(dle,'KO流量_time'))
                        

                        #440
                        #1360
                        m1=KO.start_time.hour*60+KO.start_time.minute
                        m2=restricted_time.hour*60+restricted_time.minute
                        T1=(m1>=440 and m1<=1360) and (m2>=440 and m2<=1360)

                        # T1=((KO.start_time.hour<23 and KO.start_time.hour>=8) and (restricted_time.hour<23 and restricted_time.hour>=8))

                        if len(KO_LIST)>0:
                            T3=(getattr(KO_LIST[-1],'塩')=='普通') or (getattr(KO_LIST[-1],'塩')=='高')

                        else:
                            T3=True

                        if len(MB_orimpia)>0 and len(arerugen_check_list)==0 and len(KO_LIST)==0:
                            T1=True
                            KO.start_time=KO.start_time.replace(hour=7,minute=20)

                        
                        if  T1 and T2 and T3 :#and len(ko_list)<=max_kolist

                            KO_LIST.append(dle)
                            ko_list.append(dle)
                            before_time=KO.start_time
                            KO.start_time=KO.start_time+timedelta(minutes=getattr(dle,'KO流量_time'))
                            after_time=KO.start_time
                            KO.start_time=KO.start_time+timedelta(minutes=KO.cleaning_time)

                            after_after_time=KO.start_time
                            
                            attri=KO.start_time.day

                            if attri not in KO.day_breaktime_flag:
                                KO.day_breaktime_flag[attri]=0
                            if KO.start_time>=KO.start_time.replace(hour=2,minute=0) and KO.start_time<KO.start_time.replace(hour=5,minute=0) and KO.day_breaktime_flag[attri]==0:
                                # print("reached_true")
                                KO.start_time+=timedelta(hours=2)
                                KO.day_breaktime_flag[attri]=1

                            elif before_time<KO.start_time.replace(hour=2,minute=0) and after_time+timedelta(minutes=KO.cleaning_time)>KO.start_time.replace(hour=5,minute=0) and KO.day_breaktime_flag[attri]==0:
                                KO.start_time=KO.start_time-timedelta(minutes=getattr(dle,'KO流量_time'))-timedelta(minutes=KO.cleaning_time)
                                KO.start_time+=timedelta(hours=2)
                                before_time=KO.start_time
                                KO.start_time=KO.start_time+timedelta(minutes=getattr(dle,'KO流量_time'))
                                after_time=KO.start_time

                                KO.start_time=KO.start_time+timedelta(minutes=KO.cleaning_time)
                                KO.day_breaktime_flag[attri]=1

                            if before_time.hour<11 and after_after_time.hour>=11:
                                KO.start_time=KO.start_time+timedelta(minutes=20)

                            if before_time.hour<17 and after_after_time.hour>=17:
                                KO.start_time=KO.start_time+timedelta(minutes=20)
                                

                            setattr(dle,'get_used',1)
                            setattr(dle,'slot',f'{before_time}-->{after_time}')
                            setattr(dle,'順番',counter_type_KO)
                            counter_type_KO+=1
                            setattr(dle,'生産日',after_time.date())
                            setattr(dle,'start',f'{before_time}')
                            setattr(dle,'end',f'{after_time}')
                            setattr(dle,'day',f'{after_time.day_name()}')

                        else:
                            break


                    if len(KO_LIST)>0:
                        if (getattr(KO_LIST[-1],'塩')=='高'):
                            TT=(getattr(ele,'塩')=='普通') or (getattr(ele,'塩')=='高')
                        else:
                            TT=True
                    else:
                        TT=True
                    if  getattr(ele,'納期_copy').date()>=KO.start_time.date() and KO.start_time+timedelta(minutes=KO.cleaning_time)+timedelta(minutes=getattr(ele,'KO流量_time'))<=KO.end_time and  KO.start_time.date() not in dat2 and TT:#and len(ko_list)<=max_kolist
                        # print(KO.start_time.date(),dat2)

                        # if ele.ko_remark and len(KO_LIST):
                        #     if KO.start_time-timedelta(hours=3)<KO.start_time.replace(hour=2,minute=0) and KO.start_time<KO.start_time.replace(hour=5,minute=0):
                        #         KO.start_time+=timedelta(hours=2)

                        # if len(KO_LIST):
                        #     KO.start_time=KO.start_time+timedelta(minutes=KO.cleaning_time)

                        KO_LIST.append(ele)
                        ko_list.append(ele)
                        before_time=KO.start_time
                        KO.start_time=KO.start_time+timedelta(minutes=getattr(ele,'KO流量_time'))
                        after_time=KO.start_time
                        KO.start_time=KO.start_time+timedelta(minutes=KO.cleaning_time)

                        after_after_time=KO.start_time
                        attri=KO.start_time.day
                       
                        if attri not in KO.day_breaktime_flag:
                            KO.day_breaktime_flag[attri]=0
                        if KO.start_time>=KO.start_time.replace(hour=2,minute=0) and KO.start_time<KO.start_time.replace(hour=5,minute=0) and KO.day_breaktime_flag[attri]==0:
                            # print("reached_true")
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


                        if before_time.hour<11 and after_after_time.hour>=11:
                            KO.start_time=KO.start_time+timedelta(minutes=20)

                        if before_time.hour<17 and after_after_time.hour>=17:
                            KO.start_time=KO.start_time+timedelta(minutes=20)

                        
                        # print(before_time.hour)
                        # print(after_after_time.hour)

                           

                        



                        setattr(ele,'get_used',1)
                        setattr(ele,'slot',f'{before_time}-->{after_time}')
                        setattr(ele,'順番',counter_type_KO)
                        counter_type_KO+=1
                        setattr(ele,'生産日',after_time.date())
                        setattr(ele,'start',f'{before_time}')
                        setattr(ele,'end',f'{after_time}')
                        setattr(ele,'day',f'{after_time.day_name()}')
                # Magarin=True

                if KO.start_time<KO.start_time.replace(hour=23,minute=0) and  KO.start_time.date() not in dat2  :#and len(ko_list)<=max_kolist

                    # print('reached_in ko next part')

                    unused_arerugen_list=[ele for ele in arerugen_check_list_copy if getattr(ele,'get_used')==0]


                    

                    new_arerugen_check_list=salt_order_checker(ko_list+unused_arerugen_list+future_groups)

                    new_arerugen_check_list=arerugen_checker(new_arerugen_check_list)
                    new_arerugen_check_list=[ele for ele in new_arerugen_check_list if ele not in ko_list]

                    # MB_orimpia=[ele for ele in new_arerugen_check_list if ele.品名.startswith('MB-ｵﾘﾝﾋﾟｱ')]
                    MB_orimpia=[ele for ele in new_arerugen_check_list if ele.荷姿.startswith('コンテナ')]

                    new_arerugen_check_list=[ele for ele in new_arerugen_check_list if ele not in MB_orimpia]

                    for ele in new_arerugen_check_list:
                        #KO.start_time+timedelta(minutes=KO.cleaning_time)+timedelta(minutes=getattr(ele,'KO流量_time'))<=elements+timedelta(hours=24)
                        final_hour=KO.start_time.hour
                        minute=KO.start_time.minute
                        total_minutes = final_hour * 60 + minute
                        next_DaY=pd.to_datetime(KO.start_time.date()+timedelta(days=1))

                        MB_orimpia=[orimpia for orimpia in MB_orimpia if getattr(orimpia,'get_used')==0]
                        for dle in MB_orimpia:

                            final_hour=KO.start_time.hour
                            minute=KO.start_time.minute
                            total_minutes = final_hour * 60 + minute

                            new_type_list=[ele for ele in new_arerugen_check_list if getattr(ele,'アレルゲン')=='A' and getattr(ele,'get_used')==0]
                            new_type_low=[ele for ele in new_arerugen_check_list if getattr(ele,'アレルゲン')=='B' and getattr(ele,'塩')=='低' and getattr(ele,'get_used')==0]

                            
                            T2=len(new_type_list)==0 and len(new_type_low)==0

                            restricted_time=KO.start_time+timedelta(minutes=getattr(dle,'KO流量_time'))
                            # T1=((KO.start_time.hour<23 and KO.start_time.hour>7) and (restricted_time.hour<23 and restricted_time.hour>7))

                            m1=KO.start_time.hour*60+KO.start_time.minute
                            m2=restricted_time.hour*60+restricted_time.minute
                            T1=False
                            T1=(m1>=440 and m1<=1360) and (m2>=440 and m2<=1360)

                            if len(KO_LIST)>0:
                                T3=(getattr(KO_LIST[-1],'塩')=='普通') or (getattr(KO_LIST[-1],'塩')=='高')

                            else:
                                T3=True

                            
                            if  T1 and T2 and T3 and total_minutes+int(getattr(ele,'KO流量_time'))<1380 :#and len(ko_list)<=max_kolist
                                KO_LIST.append(dle)
                                ko_list.append(dle)
                                before_time=KO.start_time
                                KO.start_time=KO.start_time+timedelta(minutes=getattr(dle,'KO流量_time'))
                                after_time=KO.start_time
                                KO.start_time=KO.start_time+timedelta(minutes=KO.cleaning_time)
                                after_after_time=KO.start_time
                                attri=KO.start_time.day
                            
                                if attri not in KO.day_breaktime_flag:
                                    KO.day_breaktime_flag[attri]=0
                                if KO.start_time>=KO.start_time.replace(hour=2,minute=0) and KO.start_time<KO.start_time.replace(hour=5,minute=0) and KO.day_breaktime_flag[attri]==0:
                                    # print("reached_true")
                                    KO.start_time+=timedelta(hours=2)
                                    KO.day_breaktime_flag[attri]=1

                                elif before_time<KO.start_time.replace(hour=2,minute=0) and after_time+timedelta(minutes=KO.cleaning_time)>KO.start_time.replace(hour=5,minute=0) and KO.day_breaktime_flag[attri]==0:
                                    KO.start_time=KO.start_time-timedelta(minutes=getattr(dle,'KO流量_time'))-timedelta(minutes=KO.cleaning_time)
                                    KO.start_time+=timedelta(hours=2)
                                    before_time=KO.start_time
                                    KO.start_time=KO.start_time+timedelta(minutes=getattr(dle,'KO流量_time'))
                                    after_time=KO.start_time

                                    KO.start_time=KO.start_time+timedelta(minutes=KO.cleaning_time)
                                    KO.day_breaktime_flag[attri]=1


                                if before_time.hour<11 and after_after_time.hour>=11:
                                    KO.start_time=KO.start_time+timedelta(minutes=20)

                                if before_time.hour<17 and after_after_time.hour>=17:
                                    KO.start_time=KO.start_time+timedelta(minutes=20)

                                setattr(dle,'get_used',1)
                                setattr(dle,'slot',f'{before_time}-->{after_time}')
                                setattr(dle,'順番',counter_type_KO)
                                counter_type_KO+=1
                                setattr(dle,'生産日',after_time.date())
                                setattr(dle,'start',f'{before_time}')
                                setattr(dle,'end',f'{after_time}')
                                setattr(dle,'day',f'{after_time.day_name()}')

                            else:
                                break


                        next_DaY=pd.to_datetime(KO.start_time.date()+timedelta(days=1))

                        final_hour=KO.start_time.hour
                        minute=KO.start_time.minute
                        total_minutes = final_hour * 60 + minute


                        if len(KO_LIST)>0:
                            if (getattr(KO_LIST[-1],'塩')=='高'):
                                TT=(getattr(ele,'塩')=='普通') or (getattr(ele,'塩')=='高')
                            else:
                                TT=True
                        else:
                            TT=True
    
                        

                        if  total_minutes+60+int(getattr(ele,'KO流量_time'))<1380 and getattr(ele,'納期_copy').date()>=KO.start_time.date() and KO.start_time+timedelta(minutes=KO.cleaning_time)+timedelta(minutes=getattr(ele,'KO流量_time'))<=KO.end_time and  next_DaY not in dat2 and TT:#and len(ko_list)<=max_kolist


                            KO_LIST.append(ele)
                            ko_list.append(ele)
                            before_time=KO.start_time
                            KO.start_time=KO.start_time+timedelta(minutes=getattr(ele,'KO流量_time'))
                            after_time=KO.start_time
                            KO.start_time=KO.start_time+timedelta(minutes=KO.cleaning_time)

                            after_after_time=KO.start_time
                            attri=KO.start_time.day

                            if attri not in KO.day_breaktime_flag:
                                KO.day_breaktime_flag[attri]=0
                            if KO.start_time>=KO.start_time.replace(hour=2,minute=0) and KO.start_time<KO.start_time.replace(hour=5,minute=0) and KO.day_breaktime_flag[attri]==0:
                                # print("reached_true")
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


                            if before_time.hour<11 and after_after_time.hour>=11:
                                KO.start_time=KO.start_time+timedelta(minutes=20)

                            if before_time.hour<17 and after_after_time.hour>=17:
                                KO.start_time=KO.start_time+timedelta(minutes=20)
                                

                            setattr(ele,'get_used',1)
                            setattr(ele,'slot',f'{before_time}-->{after_time}')
                            setattr(ele,'順番',counter_type_KO)
                            counter_type_KO+=1
                            setattr(ele,'生産日',after_time.date())
                            setattr(ele,'start',f'{before_time}')
                            setattr(ele,'end',f'{after_time}')
                            setattr(ele,'day',f'{after_time.day_name()}')

                after_ko_list=len(KO_LIST)


                if len(ko_list)>0 and elements.month<=4 and elements.day<15:
                    if datetime.datetime.strptime(ko_list[-1].end, "%Y-%m-%d %H:%M:%S").hour<=12:


                        # print(f"ko list len {len(ko_list),len(KO_LIST)}")#荷姿


                        now_time=datetime.datetime.strptime(KO_LIST[-1].end, "%Y-%m-%d %H:%M:%S").replace(hour=0,minute=0)

                        convert_to_unused=[ele for ele in ko_list if ele.生産日==ko_list[-1].生産日]

                        previously_used_data_length=len(convert_to_unused)
                        counter_type_KO=counter_type_KO-previously_used_data_length


                        resetting_instances_attributes(convert_to_unused)
                        Magarin=True
                        KO_LIST=[ele for ele in KO_LIST if ele not in convert_to_unused]
                        KO.start_time=datetime.datetime.strptime(KO_LIST[-1].end, "%Y-%m-%d %H:%M:%S")+timedelta(minutes=KO.cleaning_time)
                        ko_list=[ele for ele in ko_list if ele not in convert_to_unused]


                        future_from_current_Day=[ele for ele in Class_Data if ele.get_used==0 and ele.納期_copy<=now_time+timedelta(days=14)  
                                                 and int(getattr(ele,'予定数量(㎏)'))<=4800  
                                                 and int(getattr(ele,'KO流量_time'))!=0 
                                                 and getattr(ele,'窒素ガス')!='○' and getattr(ele,'KOスライス製品')=='○']


                        A_first=[ele for ele in future_from_current_Day if getattr(ele,'アレルゲン')=='A']
                        B_first=[ele for ele in future_from_current_Day if getattr(ele,'アレルゲン')=='B']
                        C_first=[ele for ele in future_from_current_Day if getattr(ele,'アレルゲン')=='C']
                        D_first=[ele for ele in future_from_current_Day if getattr(ele,'アレルゲン')=='D']
                        F_first=[ele for ele in future_from_current_Day if getattr(ele,'アレルゲン')=='F']

                        E_first=[ele for ele in future_from_current_Day if getattr(ele,'アレルゲン')=='E']
                        future_from_current_Day=A_first+B_first+C_first+D_first+F_first

                        future_from_current_Day=[ele for ele in future_from_current_Day if ele not in convert_to_unused]
                        # exit()

                        if True:#KO.start_time<KO.start_time.replace(hour=23,minute=0) and  KO.start_time.date() not in dat2  :#and len(ko_list)<=max_kolist
                            # print('reached_in ko next part')
                            new_arerugen_check_list=salt_order_checker(ko_list+future_from_current_Day)

                            new_arerugen_check_list=arerugen_checker(new_arerugen_check_list)
                            new_arerugen_check_list=[ele for ele in new_arerugen_check_list if ele not in ko_list]

                            remaining_length=6-previously_used_data_length

                            if remaining_length>0:

                                new_arerugen_check_list=new_arerugen_check_list[:remaining_length]+convert_to_unused

                            else:
                                print("print i am in continue region ")
                                exit()
                                continue

                            # MB_orimpia=[ele for ele in new_arerugen_check_list if ele.品名.startswith('MB-ｵﾘﾝﾋﾟｱ')]
                            MB_orimpia=[ele for ele in new_arerugen_check_list if ele.荷姿.startswith('コンテナ')]

                            new_arerugen_check_list=[ele for ele in new_arerugen_check_list if ele not in MB_orimpia]


                            no=0
                            for ele in new_arerugen_check_list:
                                
                                if no<=1:
                                    total_minutes=0

                                else:
                                    final_hour=KO.start_time.hour
                                    minute=KO.start_time.minute
                                    total_minutes = final_hour * 60 + minute

                                next_DaY=pd.to_datetime(KO.start_time.date()+timedelta(days=1))

                                MB_orimpia=[orimpia for orimpia in MB_orimpia if getattr(orimpia,'get_used')==0]
                                for dle in MB_orimpia:

                                    final_hour=KO.start_time.hour
                                    minute=KO.start_time.minute
                                    total_minutes = final_hour * 60 + minute

                                    new_type_list=[ele for ele in new_arerugen_check_list if getattr(ele,'アレルゲン')=='A' and getattr(ele,'get_used')==0]
                                    new_type_low=[ele for ele in new_arerugen_check_list if getattr(ele,'アレルゲン')=='B' and getattr(ele,'塩')=='低' and getattr(ele,'get_used')==0]

                                    
                                    T2=len(new_type_list)==0 and len(new_type_low)==0

                                    restricted_time=KO.start_time+timedelta(minutes=KO.cleaning_time)+timedelta(minutes=getattr(dle,'KO流量_time'))

                                    m1=KO.start_time.hour*60+KO.start_time.minute
                                    m2=restricted_time.hour*60+restricted_time.minute
                                    T1=(m1>=440 and m1<=1360) and (m2>=440 and m2<=1360)
                                    # T1=((KO.start_time.hour<23 and KO.start_time.hour>7) and (restricted_time.hour<23 and restricted_time.hour>7))
                                    if len(KO_LIST)>0:
                                        T3=(getattr(KO_LIST[-1],'塩')=='普通') or (getattr(KO_LIST[-1],'塩')=='高')

                                    else:
                                        T3=True

                                    
                                    if  T1 and T2 and T3 and total_minutes+int(getattr(ele,'KO流量_time'))<1380  :#and len(ko_list)<=max_kolist


                                        KO_LIST.append(dle)
                                        ko_list.append(dle)
                                        before_time=KO.start_time
                                        KO.start_time=KO.start_time+timedelta(minutes=getattr(dle,'KO流量_time'))
                                        after_time=KO.start_time
                                        KO.start_time=KO.start_time+timedelta(minutes=KO.cleaning_time)
                                        after_after_time=KO.start_time
                                        attri=KO.start_time.day
                                    
                                        if attri not in KO.day_breaktime_flag:
                                            KO.day_breaktime_flag[attri]=0
                                        if KO.start_time>=KO.start_time.replace(hour=2,minute=0) and KO.start_time<KO.start_time.replace(hour=5,minute=0) and KO.day_breaktime_flag[attri]==0:
                                            # print("reached_true")
                                            KO.start_time+=timedelta(hours=2)
                                            KO.day_breaktime_flag[attri]=1

                                        elif before_time<KO.start_time.replace(hour=2,minute=0) and after_time+timedelta(minutes=KO.cleaning_time)>KO.start_time.replace(hour=5,minute=0) and KO.day_breaktime_flag[attri]==0:
                                            KO.start_time=KO.start_time-timedelta(minutes=getattr(dle,'KO流量_time'))-timedelta(minutes=KO.cleaning_time)
                                            KO.start_time+=timedelta(hours=2)
                                            before_time=KO.start_time
                                            KO.start_time=KO.start_time+timedelta(minutes=getattr(dle,'KO流量_time'))
                                            after_time=KO.start_time

                                            KO.start_time=KO.start_time+timedelta(minutes=KO.cleaning_time)
                                            KO.day_breaktime_flag[attri]=1


                                        if before_time.hour<11 and after_after_time.hour>=11:
                                            KO.start_time=KO.start_time+timedelta(minutes=20)

                                        if before_time.hour<17 and after_after_time.hour>=17:
                                            KO.start_time=KO.start_time+timedelta(minutes=20)
                                        
                                        

                                        setattr(dle,'get_used',1)
                                        setattr(dle,'slot',f'{before_time}-->{after_time}')
                                        setattr(dle,'順番',counter_type_KO)
                                        counter_type_KO+=1
                                        setattr(dle,'生産日',after_time.date())
                                        setattr(dle,'start',f'{before_time}')
                                        setattr(dle,'end',f'{after_time}')
                                        setattr(dle,'day',f'{after_time.day_name()}')

                                    else:
                                        break


                                next_DaY=pd.to_datetime(KO.start_time.date()+timedelta(days=1))

                                if no<=1:
                                    total_minutes=0

                                else:
                                    final_hour=KO.start_time.hour
                                    minute=KO.start_time.minute
                                    total_minutes = final_hour * 60 + minute

                                # print(f'i am new arerugen {total_minutes}')
                                # print(total_minutes+60+int(getattr(ele,'KO流量_time')))
                                # print(getattr(ele,'納期_copy').date(),KO.start_time.date())
                                # print(KO.start_time+timedelta(minutes=KO.cleaning_time)+timedelta(minutes=getattr(ele,'KO流量_time')),KO.end_time)
                                # print(next_DaY not in dat2)
                                # exit()
                                if len(KO_LIST)>0:
                                    if (getattr(KO_LIST[-1],'塩')=='高'):
                                        TT=(getattr(ele,'塩')=='普通') or (getattr(ele,'塩')=='高')
                                    else:
                                        TT=True
                                else:
                                    TT=True
            
                                

                                if  total_minutes+60+int(getattr(ele,'KO流量_time'))<1490 and getattr(ele,'納期_copy').date()>=KO.start_time.date() and KO.start_time+timedelta(minutes=KO.cleaning_time)+timedelta(minutes=getattr(ele,'KO流量_time'))<=KO.end_time and  next_DaY not in dat2 and TT:#and len(ko_list)<=max_kolist
                                    

                                    # print("i reached in allocation")
                                    KO_LIST.append(ele)
                                    ko_list.append(ele)
                                    before_time=KO.start_time
                                    KO.start_time=KO.start_time+timedelta(minutes=getattr(ele,'KO流量_time'))
                                    after_time=KO.start_time
                                    KO.start_time=KO.start_time+timedelta(minutes=KO.cleaning_time)

                                    after_after_time=KO.start_time
                                    attri=KO.start_time.day

                                    # if attri not in KO.day_breaktime_flag:
                                    KO.day_breaktime_flag[attri]=0
                                    if KO.start_time>=KO.start_time.replace(hour=2,minute=0) and KO.start_time<KO.start_time.replace(hour=5,minute=0) and KO.day_breaktime_flag[attri]==0:
                                        # print("reached_true")
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


                                    if before_time.hour<11 and after_after_time.hour>=11:
                                        KO.start_time=KO.start_time+timedelta(minutes=20)

                                    if before_time.hour<17 and after_after_time.hour>=17:
                                        KO.start_time=KO.start_time+timedelta(minutes=20)
                                        
                                    # print(after_time)
                                    day_name=after_time.strftime('%A')
                                    setattr(ele,'get_used',1)
                                    setattr(ele,'slot',f'{before_time}-->{after_time}')
                                    setattr(ele,'順番',counter_type_KO)
                                    counter_type_KO+=1
                                    setattr(ele,'生産日',after_time.date())
                                    setattr(ele,'start',f'{before_time}')
                                    setattr(ele,'end',f'{after_time}')
                                    setattr(ele,'day',f'{day_name}')

                                no=no+1
                        # print(f"ko list len  after {len(ko_list),len(KO_LIST)}")


                if len(ko_list)>0:
                    
                    if datetime.datetime.strptime(ko_list[-1].end, "%Y-%m-%d %H:%M:%S").hour<=12:
                        convert_to_unused=[ele for ele in ko_list if ele.生産日==ko_list[-1].生産日]
                        
                        Magarin=True

                        # print(f'the convert to be unused is: {convert_to_unused}')
                        # print(f'the KO_LIST is: {KO_LIST}')

                        KO_LIST=[ele for ele in KO_LIST if ele not in convert_to_unused]

                        # print(KO.start_time)


                        # KO.start_time=datetime.datetime.strptime(KO_LIST[-1].end, "%Y-%m-%d %H:%M:%S")

                        
                        
                        
                        if len(KO_LIST):
                            KO.start_time=datetime.datetime.strptime(KO_LIST[-1].end, "%Y-%m-%d %H:%M:%S")
                            resetting_instances_attributes(convert_to_unused)



            elif (eachline=='KO' and Magarin ):
                allowable_time=elements+timedelta(minutes=440)
                ko_magarin=[]
                randi_counter=0


                #first allocate last:
                last_group=[ele for ele in arerugen_check_list if getattr(ele,'last')==1]
                last_list=[]

                for ele in last_group:
                    if KO_line_total_time-KO.cleaning_time-getattr(ele,'KO流量_time')>0 and len(ko_magarin)<=7:
                        if getattr(ele,'ランディ')=='○':
                            randi_counter+=1
                            if randi_counter>5:
                                continue
                        
                        KO_LIST.append(ele)
                        last_list.append(ele)

                        KO_line_total_time=KO_line_total_time-KO.cleaning_time-getattr(ele,'KO流量_time')
                        setattr(ele,'get_used',1)



                arerugen_check_list=[ele for ele in arerugen_check_list if ele not in last_group]

                allowable_length=7-len(last_list)

                for ele in arerugen_check_list:
                    if KO_line_total_time-KO.cleaning_time-getattr(ele,'KO流量_time')>0 and len(ko_magarin)<=allowable_length:
                        if getattr(ele,'ランディ')=='○':
                            randi_counter+=1
                            if randi_counter>5:
                                continue
                        
                        KO_LIST.append(ele)
                        ko_magarin.append(ele)

                        KO_line_total_time=KO_line_total_time-KO.cleaning_time-getattr(ele,'KO流量_time')
                        setattr(ele,'get_used',1)


                if KO_line_total_time>0 and len(ko_magarin)<=allowable_length:
                    groups=[current_group,future_groups]

                    for eachgroup in groups:

                        for ele in eachgroup:
                            if KO_line_total_time-KO.cleaning_time-getattr(ele,'KO流量_time')>0 and getattr(ele,'get_used')==0 and len(ko_magarin)<=allowable_length:

                                if getattr(ele,'ランディ')=='○':
                                    randi_counter+=1
                                    if randi_counter>5:
                                        continue

                                # if len(ko_magarin)>0:
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

                                        

                                        break
                                    else:
                                        ko_list_copy=ko_magarin.copy()


                ko_magarin=ko_magarin+last_list


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
                    setattr(ele,'day',f'{after_time.day_name()}')
                    counter+=1

                    if before_time.hour<11 and allowable_time.hour>=11:
                        allowable_time=allowable_time+timedelta(hours=1)

                    if before_time.hour<17 and allowable_time.hour>=17:
                        allowable_time=allowable_time+timedelta(hours=1)
                                


          

    # print(f'the length of class data{len(Class_Data)}')
    non_used_data=[ele for ele in Class_Data if getattr(ele,'get_used')==0]
    used_Data=[ele for ele in Class_Data if getattr(ele,'get_used')==1]
    MK_LIST=sorted(MK_LIST, key=lambda ele: (ele.生産日, ele.順番))
    FK_LIST=sorted(FK_LIST, key=lambda ele: (ele.生産日, ele.順番))
    KO_LIST=sorted(KO_LIST, key=lambda ele: (ele.生産日, ele.順番))

    # create_csv_from_objects(f'MK_{arg}.csv', MK_LIST)
    # create_csv_from_objects(f'FK_{arg}.csv', FK_LIST)
    # create_csv_from_objects(f'KO_{arg}.csv', KO_LIST)

    # create_csv_from_objects(f'unused_data_{arg}.csv', non_used_data)

    # print(f'the length of non-used-data {len(non_used_data)} the length of used-data {len(used_Data)}')

    return non_used_data,MK_LIST,FK_LIST,KO_LIST


    # ganttchart.ganttchart_creator(MK_LIST,FK_LIST,KO_LIST)
    # return fig
    