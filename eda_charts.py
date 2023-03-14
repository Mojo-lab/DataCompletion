import pandas as pd
import seaborn as sns

# todo:
#1.eda on dataset:




def null_value_graphs(filepath,filename,session):
    '''chart types in null values page:
    1. overall null values in the dataset - bar chart
    2. Missing values in each columns - pie chart
    3. Missing values & non null values in each column - horizontal bar chart
    '''

    if 'csv' in filename:
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath, engine="openpyxl")

    null_values = pd.DataFrame(df.isnull().sum(), columns=['values'])
    null_values = null_values[null_values['values'] != 0]
    xValues = list(null_values.index)
    yValues = list(null_values['values'])
    converted_values = [round((val / len(df)) * 100) for val in yValues]
    session["Column_names"] = str(xValues)
    palette = sns.color_palette("tab10", len(xValues)).as_hex()

    df_total_rows = df.shape[0] * df.shape[1]

    #1. overall null values in the dataset - bar chart
    overall_null_values_title = "Overall presence of null values in dataset"
    overall_null_values_xvalues = ["Non Null Values","Null Values"]
    overall_null_values_yvalues = [round(((df_total_rows - sum(yValues))/df_total_rows)*100), round((sum(yValues)/df_total_rows)*100)]
    overall_null_values_yvalues_content = f"The dataset consists of {sum(yValues)} null values and {(df.shape[0] * df.shape[1]) - sum(yValues)} non null values."
    overall_null_values = {"xValues": overall_null_values_xvalues,
                            "yValues": overall_null_values_yvalues,
                            "barColors": palette,
                           "title": overall_null_values_title,
                            "content":overall_null_values_yvalues_content}


    #2. Missing values in each columns - pie chart
    column_null_values_title = 'Proportion of missing values in each columns'
    column_null_values_content = 'The table below shows the proportion of missing values in each column'

    grouptable = []
    pietable = []
    for idx in range(len(xValues)):
        pietable.append({"ColumnName":xValues[idx],"MissingValues":yValues[idx],"MissingValuePercent":converted_values[idx]})
        if converted_values[idx] <= 8:
            filldecision = "Impute missing data"
        elif (converted_values[idx] > 76):
            filldecision = "Drop Attribute"
        else:
            filldecision = "Don't impute"
        grouptable.append({"ColumnName":xValues[idx],"MissingValuePercent":converted_values[idx],"Recommendation":filldecision})
    piedata = {"xValues": xValues,
               "yValues": converted_values,
                "barColors": palette,
               "title": column_null_values_title,
               "content":column_null_values_content,
               "datatable":pietable}

    #3. Missing values & non null values in each column - horizontal bar chart
    group_not_null_values = [100 - idx for idx in converted_values]

    groupedbardata = [
        {
            "label": 'Non Null Values',
            "data": group_not_null_values,
            "borderColor": palette[0],
            "backgroundColor": palette[0]
        },
        {
            "label": 'Null Values',
            "data": yValues,
            "borderColor": palette[1],
            "backgroundColor": palette[1]
        }]
    groupedbartitle = 'Comparision of null & non null values in each column'
    groupedbarcontent = 'EasyFill has analyzed the data and the recommendations are given in the table'
    groupedbar_meta_data = {"title":groupedbartitle,"content":groupedbarcontent,"grouptable":grouptable}
    data = {"bardata": overall_null_values, "piedata": piedata, 'groupedbardata': groupedbardata, 'grouplabels': xValues ,'groupedmetadata':groupedbar_meta_data}
    return data


def eda_report(filepath):
    if 'csv' in filepath:
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath, engine="openpyxl")

    describe_tab = df.describe()
    stats_table = []
    stats_table_headers = ['']+list(describe_tab.columns)
    for idx in range(len(describe_tab)):
        stats_table.append({"index":describe_tab.index[idx],'valuess':list(describe_tab.iloc[idx])})
    data = {"shape":{"rows":df.shape[0],"columns":df.shape[1]},"stats":stats_table,"statsHeader":stats_table_headers}
    print(stats_table)
    print(stats_table_headers)
    session = {}
    filename = 'xlsx'
    data1 = null_value_graphs(filepath,filename,session)
    data2 = chart_imputer(df)
    return data,data1,data2



def chart_type(dataType,unique_values):
    if dataType == 'object':
        if unique_values < 3:
            return 'bar chart'
        elif unique_values > 3 and unique_values <= 15:
            return 'pie chart'
        else:
            return 'unknown'
    else:
        pass



def chart_imputer(df):
    decision_factor = {}
    for col in df.columns:
        if df[col].dtype == object:
            unique_values = len(df[col].dropna().unique())
            if unique_values <= 15 and unique_values != 1:
                unigraph = True
                ch_type = chart_type('object', unique_values)
            else:
                unigraph = False
                ch_type = None
            decision_factor[col] = {'dtype':'object','unique_values':unique_values,'unigraph':unigraph,'chart':ch_type}
        else:
            print("some other dtype")
    chart_data = chart_generator(decision_factor,df)
    return chart_data

def chart_generator(decision_factor,df):
    consolidated_graph_data = []
    for col_name in df.columns:
        if decision_factor[col_name]['unigraph'] == True:
            if decision_factor[col_name]['chart'] == 'bar chart':
                consolidated_graph_data.append(bar_chart(col_name,df))
            elif decision_factor[col_name]['chart'] == 'pie chart':
                consolidated_graph_data.append(pie_chart(col_name,df))
            else:
                pass
        else:
            pass
    html_cont = ''
    idx = 4
    for val in consolidated_graph_data:
        idx += 1
        if val['chart'] == 'barchart':
            html_txt = f'''<div class ="col-sm-6">
                            <div class ="well">
                            <h4> {val['title']} </h4>
                    <canvas id = "myChart{idx}" style = "width:100%;max-width:600px;"> </canvas>
                    <br>
                <script>
                var xValues = {val['xValues']};
                var yValues = {val['yValues']};
                var barColors = {val['barColors']};
                new Chart("myChart{idx}",'''

            html_txt_2 = ''' {type: "bar", data: {
                    labels: xValues,
                    datasets: [{
                        backgroundColor: barColors,
                        data: yValues,
                        borderWidth: 1
                    }]
                },
                options: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: false
                    }
                }
            });
            </script>
            </div>
            </div>'''
            html_txt = html_txt+html_txt_2
            html_cont = html_cont+html_txt
        elif val['chart'] == "piechart":
            html_txt = f'''<div class="col-sm-6">
                          <div class="well">
                              <h4>{val['title']}</h4>
                                <br>
                            <canvas id="myChart{idx}" style="width:100%;max-width:600px;"></canvas>
                              <script>
                                var xValues = {val['xValues']};
                                var yValues = {val['yValues']};
                                var barColors = {val['barColors']};
                                
                                new Chart("myChart{idx}",'''
            html_txt_2 = '''{
                                  type: "doughnut",
                                  data: {
                                labels: xValues,
                                datasets: [{
                                  backgroundColor: barColors,
                                  data: yValues
                                }]
                              },
                              options: {
                              legend: {
                                    display: true,
                                    position: 'right'
                                },
                                title: {
                                  display: false
                                },
                              }
                            });
                            </script>
                                      </div>
                                    </div>
                            '''
            html_txt = html_txt + html_txt_2
            html_cont = html_cont + html_txt
    return html_cont


def bar_chart(col_name,df):
    uniq_vals = df[col_name].dropna().value_counts()
    xValues = list(uniq_vals.keys())
    yValues = [uniq_vals[i] for i in uniq_vals.keys()]
    palette = sns.color_palette("tab10", len(xValues)).as_hex()
    overall_values_title = f"Distribution of categories in {col_name}"
    overall_values = {"xValues": xValues,
                           "yValues": yValues,
                           "barColors": palette,
                           "title": overall_values_title,
                      "chart":"barchart"}
    return overall_values

def pie_chart(col_name,df):
    uniq_vals = df[col_name].dropna().value_counts()
    xValues = list(uniq_vals.keys())
    yValues = [uniq_vals[i] for i in uniq_vals.keys()]
    palette = sns.color_palette("tab10", len(xValues)).as_hex()
    column_null_values_title = f"Distribution of categories in {col_name}"

    piedata = {"xValues": xValues,
               "yValues": yValues,
               "barColors": palette,
               "title": column_null_values_title,
               "chart":"piechart"}
    return piedata

# filepath = r'static\file_uploads\CollectionMonitoringReport20220121101935.xlsx'
# filename = 'CollectionMonitoringReport20220121101935.xlsx'
# df = pd.read_excel(filepath,engine='openpyxl')
# z = chart_imputer(df)
# print(z)
# eda_report(filepath,filename)



'''
1.rows and columns
2.basic stats
3.corr'''