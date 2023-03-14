import pandas as pd
import seaborn as sns


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

