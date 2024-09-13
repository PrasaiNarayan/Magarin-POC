import pandas as pd
import plotly.figure_factory as ff
from datetime import timedelta
import plotly.subplots as sp


import plotly.graph_objects as go



import numpy as np
import math

def calculate_markers(start, finish, gap_hours):
    symbols_per_hour = 10
    num_symbols = int(gap_hours * symbols_per_hour)
    start_time = start.timestamp()
    finish_time = finish.timestamp()
    return pd.to_datetime(np.linspace(start_time, finish_time, num_symbols), unit='s')


def plot_gantt(df):
    df['Start'] = pd.to_datetime(df['start'], format='%Y/%m/%d %H:%M')
    df['Finish'] = pd.to_datetime(df['end'], format='%Y/%m/%d %H:%M')

    start_date = df['Start'].min()
    end_date = df['Finish'].max()

    df = df[['品目コード','品名','アレルゲン','塩','色','香料','乳化剤','納期_copy','Start','Finish','Task','last']]
    df.rename(columns={'納期_copy': '納期'}, inplace=True)

    num_weeks = math.ceil((end_date - start_date).days / 7)
    # Ensure num_weeks is at least 1
    num_weeks = max(num_weeks, 1)
    
    df.sort_values(["Task", "Start"], inplace=True)
    weeks = [start_date + timedelta(weeks=week) for week in range(num_weeks+1)]
    df['Week'] = pd.cut(df['Start'], bins=pd.to_datetime(weeks), labels=[f"Week {i+1}" for i in range(num_weeks)], include_lowest=True)

    task_dict = {"MK": 0, "FK": 1, "KO": 2}
    gap_symbols = {"MK": {3: ("square", "black"), 5.5: ("square", "darkblue")},
                   "FK": {3: ("square", "black"), 5.5: ("square", "darkblue")},
                   "KO": {2: ("square", "gray"), 3: ("square", "black"), 5.5: ("square", "darkblue")}}

    color_legend = {2: ("square", "gray"), 3: ("square", "black"), 5.5: ("square", "darkblue")}

    fig = sp.make_subplots(rows=num_weeks, cols=1, subplot_titles=[f"Week {i+1}" for i in range(num_weeks)])

    for task in ["MK", "FK", "KO"]:
        for week in range(num_weeks):
            start_week = start_date + timedelta(weeks=week)
            end_week = start_week + timedelta(weeks=1)
            weekly_df = df[(df['Week'] == f"Week {week+1}") & (df["Task"] == task)]
            for i in range(1, len(weekly_df)):
                prev_row = weekly_df.iloc[i-1]
                curr_row = weekly_df.iloc[i]
                gap = (curr_row["Start"] - prev_row["Finish"]).total_seconds() / 3600  

                for gap_hours, (symbol, color) in reversed(list(gap_symbols[task].items())):
                    if gap_hours == 5.5 and gap == gap_hours: 
                        marker_times = calculate_markers(prev_row['Finish'], curr_row["Start"], gap)
                        marker_trace = go.Scatter(
                            x=marker_times,
                            y=[task_dict[task]] * len(marker_times),
                            mode='markers',
                            marker=dict(
                                symbol=symbol,
                                color=color,
                                size=10
                            ),
                            showlegend=False
                        )
                        fig.add_trace(marker_trace, row=week+1, col=1)
                    elif gap >= gap_hours and gap <= 4.5: 
                        marker_times = calculate_markers(prev_row['Finish'], curr_row["Start"], gap)
                        marker_trace = go.Scatter(
                            x=marker_times,
                            y=[task_dict[task]] * len(marker_times),
                            mode='markers',
                            marker=dict(
                                symbol=symbol,
                                color=color,
                                size=10
                            ),
                            showlegend=False
                        )
                        fig.add_trace(marker_trace, row=week+1, col=1)
                        break

            for _, row in weekly_df.iterrows():
                fig.add_trace(
                    go.Scatter(
                        x=[row['Start'], row['Finish']],
                        y=[task_dict[row['Task']]]*2,
                        name=row['Task'],
                        hovertext='<br>'.join([f'{k}: {v}' for k, v in row.items()]),
                        hoverinfo='text',
                        mode='lines',
                        line=dict(width=14), 
                        showlegend=False
                    ),
                    row=week+1, 
                    col=1
                )

            fig.update_xaxes(range=[start_week, end_week], row=week+1, col=1)

    # Add a dummy trace for each unique color
    for hours, (symbol, color) in color_legend.items():
        if hours==2:
            name_required=f'resting_time'
        elif hours==4:
            name_required=f'cleaning_time'
        if hours==5.5 or hours==5:
            name_required=f'resting and cleaning_time'
        
        fig.add_trace(
            go.Scatter(
                x=[None],  # these lines won't show up
                y=[None],
                mode='markers',
                marker=dict(symbol=symbol, color=color, size=10),  
                showlegend=True,  # show these traces in the legend
                name=f'{name_required}',  # description of the color
            )
        )

    fig.update_yaxes(tickvals=list(task_dict.values()), ticktext=list(task_dict.keys()))
    fig.update_layout(showlegend=True)
    fig.show()
    fig.write_html("gantt_chart.html")






def ganttchart_creator(MK_LIST,FK_LIST,KO_LIST):
    # all_task=MK_LIST+FK_LIST+KO_LIST

    mk=[instance.__dict__ for instance in MK_LIST]
    mk_df=pd.DataFrame(mk)
    mk_df['Task']='MK'

    fk=[instance.__dict__ for instance in FK_LIST]
    fk_df=pd.DataFrame(fk)
    fk_df['Task']='FK'

    ko=[instance.__dict__ for instance in KO_LIST]
    ko_df=pd.DataFrame(ko)
    ko_df['Task']='KO'

    df=pd.concat([mk_df, fk_df, ko_df])

    # instances_dict = [instance.__dict__ for instance in all_task]
    # df['Task']=None
    # df = pd.DataFrame(instances_dict)

    

    
    plot_gantt(df)
    cols = df.columns.tolist()
    cols.insert(0, cols.pop(cols.index('生産日')))
    cols.insert(1, cols.pop(cols.index('start')))
    cols.insert(2, cols.pop(cols.index('end')))
    cols.insert(3, cols.pop(cols.index('Task')))
    df = df[cols]
    df.to_csv('all_data.csv',index=False,encoding='utf_8_sig')

    # return fig


# import pandas as pd
# import plotly.figure_factory as ff
# from datetime import timedelta
# import plotly.subplots as sp
# import plotly.graph_objects as go
# import numpy as np
# import math

# def calculate_markers(start, finish, gap_hours):
#     symbols_per_hour = 10
#     num_symbols = int(gap_hours * symbols_per_hour)
#     start_time = start.timestamp()
#     finish_time = finish.timestamp()
#     return pd.to_datetime(np.linspace(start_time, finish_time, num_symbols), unit='s')

# def plot_gantt(df, height=1000, zoom_level=24):
#     df['Start'] = pd.to_datetime(df['start'], format='%Y/%m/%d %H:%M')
#     df['Finish'] = pd.to_datetime(df['end'], format='%Y/%m/%d %H:%M')

#     start_date = df['Start'].min()
#     end_date = df['Finish'].max()

#     df = df[['品目コード', '品名', 'アレルゲン', '塩', '色', '香料', '乳化剤', '納期_copy', 'Start', 'Finish', 'Task', 'last']]
#     df.rename(columns={'納期_copy': '納期'}, inplace=True)

#     num_weeks = math.ceil((end_date - start_date).days / 7)
#     df.sort_values(["Task", "Start"], inplace=True)
#     weeks = [start_date + timedelta(weeks=week) for week in range(num_weeks + 1)]
#     df['Week'] = pd.cut(df['Start'], bins=pd.to_datetime(weeks), labels=[f"Week {i + 1}" for i in range(num_weeks)], include_lowest=True)

#     task_dict = {"MK": 0, "FK": 1, "KO": 2}
#     gap_symbols = {"MK": {3: ("square", "black"), 5.5: ("square", "darkblue")},
#                    "FK": {3: ("square", "black"), 5.5: ("square", "darkblue")},
#                    "KO": {2: ("square", "gray"), 3: ("square", "black"), 5.5: ("square", "darkblue")}}

#     color_legend = {2: ("square", "gray"), 3: ("square", "black"), 5.5: ("square", "darkblue")}

#     fig = sp.make_subplots(rows=num_weeks * (len(task_dict) + 1), cols=1, subplot_titles=[f"Week {i + 1}" for i in range(num_weeks) for _ in range(len(task_dict) + 1)])

#     for week in range(num_weeks):
#         start_week = start_date + timedelta(weeks=week)
#         end_week = start_week + timedelta(weeks=1)
#         for task in task_dict.keys():
#             row_index = week * (len(task_dict) + 1) + task_dict[task] + 1
#             weekly_df = df[(df['Week'] == f"Week {week + 1}") & (df["Task"] == task)]
#             for i in range(1, len(weekly_df)):
#                 prev_row = weekly_df.iloc[i - 1]
#                 curr_row = weekly_df.iloc[i]
#                 gap = (curr_row["Start"] - prev_row["Finish"]).total_seconds() / 3600

#                 for gap_hours, (symbol, color) in reversed(list(gap_symbols[task].items())):
#                     if gap_hours == 5.5 and gap == gap_hours:
#                         marker_times = calculate_markers(prev_row['Finish'], curr_row["Start"], gap)
#                         marker_trace = go.Scatter(
#                             x=marker_times,
#                             y=[0] * len(marker_times),
#                             mode='markers',
#                             marker=dict(
#                                 symbol=symbol,
#                                 color=color,
#                                 size=10
#                             ),
#                             showlegend=False
#                         )
#                         fig.add_trace(marker_trace, row=row_index, col=1)
#                     elif gap >= gap_hours and gap <= 4.5:
#                         marker_times = calculate_markers(prev_row['Finish'], curr_row["Start"], gap)
#                         marker_trace = go.Scatter(
#                             x=marker_times,
#                             y=[0] * len(marker_times),
#                             mode='markers',
#                             marker=dict(
#                                 symbol=symbol,
#                                 color=color,
#                                 size=10
#                             ),
#                             showlegend=False
#                         )
#                         fig.add_trace(marker_trace, row=row_index, col=1)
#                         break

#             for _, row in weekly_df.iterrows():
#                 fig.add_trace(
#                     go.Scatter(
#                         x=[row['Start'], row['Finish']],
#                         y=[0, 0],
#                         name=row['Task'],
#                         hovertext='<br>'.join([f'{k}: {v}' for k, v in row.items()]),
#                         hoverinfo='text',
#                         mode='lines',
#                         line=dict(width=14),
#                         showlegend=False
#                     ),
#                     row=row_index,
#                     col=1
#                 )

#             fig.update_xaxes(range=[start_week, end_week], row=row_index, col=1)

#     # Add a dummy trace for each unique color
#     for hours, (symbol, color) in color_legend.items():
#         if hours == 2:
#             name_required = 'resting_time'
#         elif hours == 4:
#             name_required = 'cleaning_time'
#         if hours == 5.5 or hours == 5:
#             name_required = 'resting and cleaning_time'

#         fig.add_trace(
#             go.Scatter(
#                 x=[None],  # these lines won't show up
#                 y=[None],
#                 mode='markers',
#                 marker=dict(symbol=symbol, color=color, size=10),
#                 showlegend=True,  # show these traces in the legend
#                 name=f'{name_required}',  # description of the color
#             )
#         )

#     fig.update_yaxes(tickvals=[0], ticktext=[""])
#     fig.update_layout(
#         showlegend=True,
#         height=height,
#         yaxis=dict(
#             autorange=True,
#             fixedrange=True
#         ),
#         xaxis=dict(
#             range=[start_date, start_date + timedelta(hours=zoom_level)],  # Adjust the range for zoom level
#             autorange=False
#         )
#     )
#     fig.show()
#     fig.write_html("gantt_chart.html")

# def ganttchart_creator(MK_LIST, FK_LIST, KO_LIST):
#     mk = [instance.__dict__ for instance in MK_LIST]
#     mk_df = pd.DataFrame(mk)
#     mk_df['Task'] = 'MK'

#     fk = [instance.__dict__ for instance in FK_LIST]
#     fk_df = pd.DataFrame(fk)
#     fk_df['Task'] = 'FK'

#     ko = [instance.__dict__ for instance in KO_LIST]
#     ko_df = pd.DataFrame(ko)
#     ko_df['Task'] = 'KO'

#     df = pd.concat([mk_df, fk_df, ko_df])

#     plot_gantt(df)
#     cols = df.columns.tolist()
#     cols.insert(0, cols.pop(cols.index('生産日')))
#     cols.insert(1, cols.pop(cols.index('start')))
#     cols.insert(2, cols.pop(cols.index('end')))
#     cols.insert(3, cols.pop(cols.index('Task')))
#     df = df[cols]
#     df.to_csv('all_data.csv', index=False, encoding='utf_8_sig')

