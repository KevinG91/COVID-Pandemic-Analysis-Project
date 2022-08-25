import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt


#functions to calculate based on two columns
def calculate_percentage_icu_beds_total(row):
    if row['total_staffed_icu_beds_occupancy'] == 0:
        return 0
    if row['total_staffed_icu_beds'] == 0:
        return 0
    return row['total_staffed_icu_beds_occupancy'] * 100 / row['total_staffed_icu_beds']


def calculate_percentage_icu_beds_pediatric(row):
    if row['total_staffed_pediatric_icu_beds'] == 0:
        return 0
    if row['staffed_pediatric_icu_bed_occupancy'] == 0:
        return 0
    return row['staffed_pediatric_icu_bed_occupancy'] * 100 / row['total_staffed_pediatric_icu_beds']


def total_staffed_icu_beds_covid_confirmed_percentage(row):
    return row['total_staffed_icu_beds_covid_confirmed'] * 100 / row['total_staffed_icu_beds_occupancy']


#Loading the CSV
df_covid = pd.read_csv('COVID-19_Reported_Patient_Impact_and_Hospital_Capacity_by_State_Timeseries.csv').sort_values(by= 'date')
df_covid.reset_index(drop=True, inplace=True)


#saving the first 6 months of 2020
df_covid_first_six_months_2020 = df_covid.loc[(df_covid['date'] >= '2020/01/01') & (df_covid['date'] <= '2020/06/30')].sort_values(by= 'date')


#getting the 5 states with the highest amount of onset covid cases in the first 6 months of 2020
#loc to slice off the columns named "state" and "hospital_onset_covid"
#then group by state --> 
#--> sum all the values in hospital_onset_covid-->
#--> use nlargest to get the top 5
top_5_states_onset_covid_first_six_months_2020 = df_covid_first_six_months_2020.loc[:, ['state', 'hospital_onset_covid']].groupby('state').sum().nlargest(5, 'hospital_onset_covid')
top_5_states_onset_covid_first_six_months_2020.reset_index(inplace=True)


#making a new dataframe using only new york's related rows
covid_new_york = df_covid.loc[df_covid['state'] == 'NY']
covid_new_york.reset_index(drop= True, inplace=True)


#making a new dataframe in case i need to use the complete one later
covid_new_york_used_beds = covid_new_york[['state', 'date', 'inpatient_beds_used']]


#making new york's dataframe, i take the previous day patients and the current day ones
#and get the difference, if it's higher than 0 increased and if not then it decreased
#then i keep the maximum and minimum amount of beds used in a day
covid_new_york_used_beds['difference_previous_day'] = covid_new_york_used_beds['inpatient_beds_used'].diff()
covid_new_york_used_beds.difference_previous_day.fillna(0, inplace=True)
max_beds = 0
min_beds = 0
min_beds = covid_new_york_used_beds.loc[covid_new_york_used_beds.inpatient_beds_used.idxmin()]
max_beds = covid_new_york_used_beds.loc[covid_new_york_used_beds.inpatient_beds_used.idxmax()]
min_beds = min_beds[:3]
max_beds = max_beds[:3]
covid_new_york_used_beds['growth'] = covid_new_york_used_beds.difference_previous_day > 0.0
covid_new_york_used_beds.growth.replace([True, False], ['increase', 'decrease'], inplace= True)


#here i save the indexes of the rows with a date between 2020/01/01 and 2020/12/31
#then i slice off everything except the columns state and adult_icu_bed_utilization
#after that i group the data by state and sum up everything and keep the 5 with the highest percentage values
top_5_icu = df_covid.loc[(df_covid['date'] >= '2020/01/01') & (df_covid['date'] <= '2020/12/31')]
top_5_icu = df_covid.loc[:, ['state', 'adult_icu_bed_utilization']].groupby('state').mean().nlargest(5, 'adult_icu_bed_utilization')
top_5_icu.reset_index(inplace=True)
top_5_icu.adult_icu_bed_utilization = (top_5_icu.adult_icu_bed_utilization * 100).round()
top_5_icu.rename(columns= {'adult_icu_bed_utilization': 'adult_icu_bed_utilization_percentage'}, inplace= True)


#calculating the amount of beds used for pediatric patients in 2020
#same as the previous one but i keep the data related to pediatric patients
top_5_icu_pediatric = df_covid.loc[(df_covid['date'] >= '2020/01/01') & (df_covid['date'] <= '2020/12/31')].sort_values(by= 'date')
top_5_icu_pediatric = top_5_icu_pediatric[['state', 'total_staffed_pediatric_icu_beds', 'staffed_pediatric_icu_bed_occupancy']]
top_5_icu_pediatric = top_5_icu_pediatric.loc[:, ['state', 'total_staffed_pediatric_icu_beds', 'staffed_pediatric_icu_bed_occupancy']].groupby('state').sum().sort_values(by= 'staffed_pediatric_icu_bed_occupancy', ascending= False)
top_5_icu_pediatric.reset_index(inplace= True)
top_5_icu_pediatric['total_staffed_pediatric_icu_beds_percentage'] = top_5_icu_pediatric.apply(lambda row: calculate_percentage_icu_beds_pediatric(row), axis= 1)
top_5_icu_pediatric.sort_values(by= 'total_staffed_pediatric_icu_beds_percentage', ascending=False, inplace=True)
top_5_icu_pediatric.reset_index(drop= True, inplace= True)


#making a new dataframe for confirmed cases keeping the relevant columns
#then i group the data by state
#and make new columns by adding up the values of two others
#and then a new one by calculating the percentage based on other columns
#at the end i dropped the columns that aren't relevant anymore
df_covid_icu_beds_confirmed = df_covid[['state', 'total_staffed_adult_icu_beds', 'staffed_adult_icu_bed_occupancy', 'adult_icu_bed_covid_utilization_numerator', 'total_staffed_pediatric_icu_beds', 'staffed_pediatric_icu_bed_occupancy', 'staffed_icu_pediatric_patients_confirmed_covid']]
df_covid_icu_beds_confirmed = df_covid_icu_beds_confirmed.groupby('state').sum()
df_covid_icu_beds_confirmed.reset_index(inplace= True)
df_covid_icu_beds_confirmed['total_staffed_icu_beds'] = df_covid_icu_beds_confirmed.apply(lambda row: row.total_staffed_adult_icu_beds + row.total_staffed_pediatric_icu_beds, axis= 1)
df_covid_icu_beds_confirmed['total_staffed_icu_beds_occupancy'] = df_covid_icu_beds_confirmed.apply(lambda row: row.staffed_adult_icu_bed_occupancy + row.staffed_pediatric_icu_bed_occupancy, axis= 1)
df_covid_icu_beds_confirmed['total_staffed_icu_beds_covid_confirmed'] = df_covid_icu_beds_confirmed.apply(lambda row: row.adult_icu_bed_covid_utilization_numerator + row.staffed_icu_pediatric_patients_confirmed_covid, axis= 1)
df_covid_icu_beds_confirmed.drop(columns= ['total_staffed_adult_icu_beds','staffed_adult_icu_bed_occupancy', 'total_staffed_pediatric_icu_beds', 'staffed_pediatric_icu_bed_occupancy', 'adult_icu_bed_covid_utilization_numerator', 'staffed_icu_pediatric_patients_confirmed_covid'], inplace= True)
df_covid_icu_beds_confirmed['total_staffed_icu_beds_covid_confirmed_percentage'] = df_covid_icu_beds_confirmed.apply(lambda row: total_staffed_icu_beds_covid_confirmed_percentage(row), axis= 1).round()


#i take the important columns and group the data by state to sum up the deaths
df_covid_deaths_2021 = df_covid[['state', 'date', 'deaths_covid']]
df_covid_deaths_2021 = df_covid_deaths_2021.loc[(df_covid_deaths_2021['date'] >= '2021/01/01') & (df_covid_deaths_2021['date'] <= '2021/12/31')]
df_covid_deaths_2021.drop(columns= ['date'], inplace= True)
df_covid_deaths_2021 = df_covid_deaths_2021.groupby('state').sum()
df_covid_deaths_2021.reset_index(inplace= True)


#i simply make 3 dataframes, one for each year and then group the death counts by month
#i slice off the months in a single year then convert the date column to datetime
#after that i group by month using grouper and rename the date column no month
#finally i reformat the date column to only show month and year
df_covid_deaths_2020_by_month = df_covid.loc[(df_covid['date'] >= '2020/01/01') & (df_covid['date'] <= '2020/12/31')]
df_covid_deaths_2020_by_month = df_covid_deaths_2020_by_month.loc[:, ['date', 'deaths_covid']]
df_covid_deaths_2020_by_month['date'] = pd.to_datetime(df_covid_deaths_2020_by_month['date'])
df_covid_deaths_2020_by_month = df_covid_deaths_2020_by_month.groupby(pd.Grouper(key='date', axis=0, freq='M')).sum()
df_covid_deaths_2020_by_month.reset_index(inplace= True)
df_covid_deaths_2020_by_month.rename(columns= {'date': 'Month', 'deaths_covid': 'Deaths'}, inplace= True)
df_covid_deaths_2020_by_month['Month'] = df_covid_deaths_2020_by_month['Month'].dt.strftime('%m/%Y')
# df_covid_deaths_2020_by_month['Month'] = pd.to_datetime(df_covid_deaths_2020_by_month['Month'])
#i slice off the months in a single year then convert the date column to datetime
#after that i group by month using grouper and rename the date column no month
#finally i reformat the date column to only show month and year
df_covid_deaths_2021_by_month = df_covid.loc[(df_covid['date'] >= '2021/01/01') & (df_covid['date'] <= '2021/12/31')]
df_covid_deaths_2021_by_month = df_covid_deaths_2021_by_month.loc[:, ['date', 'deaths_covid']]
df_covid_deaths_2021_by_month['date'] = pd.to_datetime(df_covid_deaths_2021_by_month['date'])
df_covid_deaths_2021_by_month = df_covid_deaths_2021_by_month.groupby(pd.Grouper(key='date', axis=0, freq='M')).sum()
df_covid_deaths_2021_by_month.reset_index(inplace= True)
df_covid_deaths_2021_by_month.rename(columns= {'date': 'Month', 'deaths_covid': 'Deaths'}, inplace= True)
df_covid_deaths_2021_by_month['Month'] = df_covid_deaths_2021_by_month['Month'].dt.strftime('%m/%Y')
# df_covid_deaths_2021_by_month['Month'] = pd.to_datetime(df_covid_deaths_2021_by_month['Month'])
#i slice off the months in a single year then convert the date column to datetime
#after that i group by month using grouper and rename the date column no month
#finally i reformat the date column to only show month and year
df_covid_deaths_2022_by_month = df_covid.loc[(df_covid['date'] >= '2022/01/01') & (df_covid['date'] <= '2022/12/31')]
df_covid_deaths_2022_by_month = df_covid_deaths_2022_by_month.loc[:, ['date', 'deaths_covid']]
df_covid_deaths_2022_by_month['date'] = pd.to_datetime(df_covid_deaths_2022_by_month['date'])
df_covid_deaths_2022_by_month = df_covid_deaths_2022_by_month.groupby(pd.Grouper(key='date', axis=0, freq='M')).sum()
df_covid_deaths_2022_by_month.reset_index(inplace= True)
df_covid_deaths_2022_by_month.rename(columns= {'date': 'Month', 'deaths_covid': 'Deaths'}, inplace= True)
df_covid_deaths_2022_by_month['Month'] = df_covid_deaths_2022_by_month['Month'].dt.strftime('%m/%Y')
# df_covid_deaths_2022_by_month['Month'] = pd.to_datetime(df_covid_deaths_2022_by_month['Month'])


"### TOP 5 States with the highest amount of onset covid cases in the first six months"
display_code_top_5_states_onset_covid_first_six_months_2020 = st.checkbox('Show code for top 5 states for onset covid in the first half of 2020')

if display_code_top_5_states_onset_covid_first_six_months_2020:
     st.code(
        '''#saving the first 6 months of 2020
df_covid_first_six_months_2020 = df_covid.loc[(df_covid['date'] >= '2020/01/01') & (df_covid['date'] <= '2020/06/30')].sort_values(by= 'date')


#getting the 5 states with the highest amount of onset covid cases in the first 6 months of 2020
#loc to slice off the columns named "state" and "hospital_onset_covid"
#then group by state --> 
#--> sum all the values in hospital_onset_covid-->
#--> use nlargest to get the top 5
top_5_states_onset_covid_first_six_months_2020 = df_covid_first_six_months_2020.loc[:, ['state', 'hospital_onset_covid']].groupby('state').sum().nlargest(5, 'hospital_onset_covid')
top_5_states_onset_covid_first_six_months_2020.reset_index(inplace=True)'''
     , language= 'python')
st.dataframe(top_5_states_onset_covid_first_six_months_2020)


"### Bed occupancy New York throughout the pandemic"
display_code_covid_new_york_used_beds = st.checkbox('Show code for bed occupancy in New York')

if display_code_covid_new_york_used_beds:
    st.code(
        '''#making a new dataframe using only new york's related rows
covid_new_york = df_covid.loc[df_covid['state'] == 'NY']
covid_new_york.reset_index(drop= True, inplace=True)


#making a new dataframe in case i need to use the complete one later
covid_new_york_used_beds = covid_new_york[['state', 'date', 'inpatient_beds_used']]


#making new york's dataframe, i take the previous day patients and the current day ones
#and get the difference, if it's higher than 0 increased and if not then it decreased
#then i keep the maximum and minimum amount of beds used in a day
covid_new_york_used_beds['difference_previous_day'] = covid_new_york_used_beds['inpatient_beds_used'].diff()
covid_new_york_used_beds.difference_previous_day.fillna(0, inplace=True)
max_beds = 0
min_beds = 0
min_beds = covid_new_york_used_beds.loc[covid_new_york_used_beds.inpatient_beds_used.idxmin()]
max_beds = covid_new_york_used_beds.loc[covid_new_york_used_beds.inpatient_beds_used.idxmax()]
min_beds = min_beds[:3]
max_beds = max_beds[:3]
covid_new_york_used_beds['growth'] = covid_new_york_used_beds.difference_previous_day > 0.0
covid_new_york_used_beds.growth.replace([True, False], ['increase', 'decrease'], inplace= True)'''
    , language= 'python')
st.dataframe(covid_new_york_used_beds)


"### The 5 states with the biggest amount of beds used in intensive care units"

display_code_top_5_icu = st.checkbox('Show code for top 5 states for occupied beds in ICU')

if display_code_top_5_icu:
    st.code(
        '''#here i save the indexes of the rows with a date between 2020/01/01 and 2020/12/31
#then i slice off everything except the columns state and adult_icu_bed_utilization
#after that i group the data by state and sum up everything and keep the 5 with the highest percentage values
top_5_icu = df_covid.loc[(df_covid['date'] >= '2020/01/01') & (df_covid['date'] <= '2020/12/31')]
top_5_icu = df_covid.loc[:, ['state', 'adult_icu_bed_utilization']].groupby('state').mean().nlargest(5, 'adult_icu_bed_utilization')
top_5_icu.reset_index(inplace=True)
top_5_icu.adult_icu_bed_utilization = (top_5_icu.adult_icu_bed_utilization * 100).round()
top_5_icu.rename(columns= {'adult_icu_bed_utilization': 'adult_icu_bed_utilization_percentage'}, inplace= True)'''
    , language= 'python')
st.dataframe(top_5_icu)


"### Amount of beds used by pediatric patients in 2020 by state"

display_code_top_5_icu_pediatric = st.checkbox('Show code for top 5 for occupied bed in pediatric ICUs')

if display_code_top_5_icu_pediatric:
    st.code(
        '''#calculating the amount of beds used for pediatric patients in 2020
#same as the previous one but i keep the data related to pediatric patients
top_5_icu_pediatric = df_covid.loc[(df_covid['date'] >= '2020/01/01') & (df_covid['date'] <= '2020/12/31')].sort_values(by= 'date')
top_5_icu_pediatric = top_5_icu_pediatric[['state', 'total_staffed_pediatric_icu_beds', 'staffed_pediatric_icu_bed_occupancy']]
top_5_icu_pediatric = top_5_icu_pediatric.loc[:, ['state', 'total_staffed_pediatric_icu_beds', 'staffed_pediatric_icu_bed_occupancy']].groupby('state').sum().sort_values(by= 'staffed_pediatric_icu_bed_occupancy', ascending= False)
top_5_icu_pediatric.reset_index(inplace= True)
top_5_icu_pediatric['total_staffed_pediatric_icu_beds_percentage'] = top_5_icu_pediatric.apply(lambda row: calculate_percentage_icu_beds_pediatric(row), axis= 1)
top_5_icu_pediatric.sort_values(by= 'total_staffed_pediatric_icu_beds_percentage', ascending=False, inplace=True)
top_5_icu_pediatric.reset_index(drop= True, inplace= True)'''
    , language= 'python')
st.dataframe(top_5_icu_pediatric)


"### Percentage of beds occupied by patients who have been confirmed to have contracted covid"

display_code_df_covid_icu_beds_confirmed = st.checkbox('Show code for confirmed cases of COVID')

if display_code_df_covid_icu_beds_confirmed:
    st.code(
        '''#making a new dataframe for confirmed cases keeping the relevant columns
#then i group the data by state
#and make new columns by adding up the values of two others
#and then a new one by calculating the percentage based on other columns
#at the end i dropped the columns that aren't relevant anymore
df_covid_icu_beds_confirmed = df_covid[['state', 'total_staffed_adult_icu_beds', 'staffed_adult_icu_bed_occupancy', 'adult_icu_bed_covid_utilization_numerator', 'total_staffed_pediatric_icu_beds', 'staffed_pediatric_icu_bed_occupancy', 'staffed_icu_pediatric_patients_confirmed_covid']]
df_covid_icu_beds_confirmed = df_covid_icu_beds_confirmed.groupby('state').sum()
df_covid_icu_beds_confirmed.reset_index(inplace= True)
df_covid_icu_beds_confirmed['total_staffed_icu_beds'] = df_covid_icu_beds_confirmed.apply(lambda row: row.total_staffed_adult_icu_beds + row.total_staffed_pediatric_icu_beds, axis= 1)
df_covid_icu_beds_confirmed['total_staffed_icu_beds_occupancy'] = df_covid_icu_beds_confirmed.apply(lambda row: row.staffed_adult_icu_bed_occupancy + row.staffed_pediatric_icu_bed_occupancy, axis= 1)
df_covid_icu_beds_confirmed['total_staffed_icu_beds_covid_confirmed'] = df_covid_icu_beds_confirmed.apply(lambda row: row.adult_icu_bed_covid_utilization_numerator + row.staffed_icu_pediatric_patients_confirmed_covid, axis= 1)
df_covid_icu_beds_confirmed.drop(columns= ['total_staffed_adult_icu_beds','staffed_adult_icu_bed_occupancy', 'total_staffed_pediatric_icu_beds', 'staffed_pediatric_icu_bed_occupancy', 'adult_icu_bed_covid_utilization_numerator', 'staffed_icu_pediatric_patients_confirmed_covid'], inplace= True)
df_covid_icu_beds_confirmed['total_staffed_icu_beds_covid_confirmed_percentage'] = df_covid_icu_beds_confirmed.apply(lambda row: total_staffed_icu_beds_covid_confirmed_percentage(row), axis= 1).round()'''
    , language= 'python')
st.dataframe(df_covid_icu_beds_confirmed)


"### COVID deaths in 2021 by state"

display_code_df_covid_deaths_2021 = st.checkbox('Show code for deaths in 2021 by state')

if display_code_df_covid_deaths_2021:
    st.code(
        '''#i take the important columns and group the data by state to sum up the deaths
df_covid_deaths_2021 = df_covid[['state', 'date', 'deaths_covid']]
df_covid_deaths_2021 = df_covid_deaths_2021.loc[(df_covid_deaths_2021['date'] >= '2021/01/01') & (df_covid_deaths_2021['date'] <= '2021/12/31')]
df_covid_deaths_2021.drop(columns= ['date'], inplace= True)
df_covid_deaths_2021 = df_covid_deaths_2021.groupby('state').sum()
df_covid_deaths_2021.reset_index(inplace= True)'''
    , language= 'python')
st.dataframe(df_covid_deaths_2021)


"### COVID deaths per year, grouped by month"
"##### Deaths in 2020 by month"

display_code_df_covid_deaths_2020_by_month = st.checkbox('Show code for COVID deaths in 2020 by month')

if display_code_df_covid_deaths_2020_by_month:
    st.code(
        '''#i slice off the months in a single year then convert the date column to datetime
#after that i group by month using grouper and rename the date column no month
#finally i reformat the date column to only show month and year
df_covid_deaths_2020_by_month = df_covid.loc[(df_covid['date'] >= '2020/01/01') & (df_covid['date'] <= '2020/12/31')]
df_covid_deaths_2020_by_month = df_covid_deaths_2020_by_month.loc[:, ['date', 'deaths_covid']]
df_covid_deaths_2020_by_month['date'] = pd.to_datetime(df_covid_deaths_2020_by_month['date'])
df_covid_deaths_2020_by_month = df_covid_deaths_2020_by_month.groupby(pd.Grouper(key='date', axis=0, freq='M')).sum()
df_covid_deaths_2020_by_month.reset_index(inplace= True)
df_covid_deaths_2020_by_month.rename(columns= {'date': 'Month', 'deaths_covid': 'Deaths'}, inplace= True)
df_covid_deaths_2020_by_month['Month'] = df_covid_deaths_2020_by_month['Month'].dt.strftime('%m/%Y')
# df_covid_deaths_2020_by_month['Month'] = pd.to_datetime(df_covid_deaths_2020_by_month['Month'])'''
    , language= 'python')
st.table(df_covid_deaths_2020_by_month)
"##### Deaths in 2021 by month"

display_code_df_covid_deaths_2021_by_month = st.checkbox('Show code for COVID deaths in 2021 by month')

if display_code_df_covid_deaths_2021_by_month:
    st.code(
        '''#i slice off the months in a single year then convert the date column to datetime
#after that i group by month using grouper and rename the date column no month
#finally i reformat the date column to only show month and year
df_covid_deaths_2021_by_month = df_covid.loc[(df_covid['date'] >= '2021/01/01') & (df_covid['date'] <= '2021/12/31')]
df_covid_deaths_2021_by_month = df_covid_deaths_2021_by_month.loc[:, ['date', 'deaths_covid']]
df_covid_deaths_2021_by_month['date'] = pd.to_datetime(df_covid_deaths_2021_by_month['date'])
df_covid_deaths_2021_by_month = df_covid_deaths_2021_by_month.groupby(pd.Grouper(key='date', axis=0, freq='M')).sum()
df_covid_deaths_2021_by_month.reset_index(inplace= True)
df_covid_deaths_2021_by_month.rename(columns= {'date': 'Month', 'deaths_covid': 'Deaths'}, inplace= True)
df_covid_deaths_2021_by_month['Month'] = df_covid_deaths_2021_by_month['Month'].dt.strftime('%m/%Y')
# df_covid_deaths_2021_by_month['Month'] = pd.to_datetime(df_covid_deaths_2021_by_month['Month'])'''
    , language= 'python')
st.table(df_covid_deaths_2021_by_month)
"##### Deaths in 2022 by month"

display_code_df_covid_deaths_2022_by_month = st.checkbox('Show code for COVID deaths in 2022 by month')

if display_code_df_covid_deaths_2022_by_month:
    st.code(
        '''#i slice off the months in a single year then convert the date column to datetime
#after that i group by month using grouper and rename the date column no month
#finally i reformat the date column to only show month and year
df_covid_deaths_2022_by_month = df_covid.loc[(df_covid['date'] >= '2022/01/01') & (df_covid['date'] <= '2022/12/31')]
df_covid_deaths_2022_by_month = df_covid_deaths_2022_by_month.loc[:, ['date', 'deaths_covid']]
df_covid_deaths_2022_by_month['date'] = pd.to_datetime(df_covid_deaths_2022_by_month['date'])
df_covid_deaths_2022_by_month = df_covid_deaths_2022_by_month.groupby(pd.Grouper(key='date', axis=0, freq='M')).sum()
df_covid_deaths_2022_by_month.reset_index(inplace= True)
df_covid_deaths_2022_by_month.rename(columns= {'date': 'Month', 'deaths_covid': 'Deaths'}, inplace= True)
df_covid_deaths_2022_by_month['Month'] = df_covid_deaths_2022_by_month['Month'].dt.strftime('%m/%Y')
# df_covid_deaths_2022_by_month['Month'] = pd.to_datetime(df_covid_deaths_2022_by_month['Month'])'''
    , language= 'python')
st.table(df_covid_deaths_2022_by_month)
st.text('Here we can see that January 2021 was the month with the highest number of deaths')


"#### Final Thoughts"
st.markdown("""
    We can see there is a clear correlation between the amount of available beds in ICU units and the number of deaths, as well as a stable growth among new infections.
    That being said no one could have foreseen this virus would become a full on pandemic, mutate as fast as it did and generate so much fear in the population.
    Needless to say this fear was mostly brought on by news channels exaggerating every piece of new info they came across and the policticians who were all too quick to lock everyone up.
    Isolation was also an indirect cause of surging cases of mental issues, but that is not relevant to what we are studying here.
    Rather than developing a surefire way of handling a pandemic, which is borderline impossible since there is no way to know how a virus will behave every time, it is much more important to cultivate among the population health and safety related habits.
    Like japan's custom to wear masks when one is sick regardless of wether there is a pandemic going on or not, and staying home when the symptoms are specially bad.""")

#Uncomment to export the csv files
# df_covid_icu_beds_confirmed.to_csv('df_covid_icu_beds_confirmed.csv', index= False, encoding= 'utf-8')
# df_covid_deaths_2020_by_month.to_csv('df_covid_deaths_2020_by_month.csv', index= False, encoding= 'utf-8')
# df_covid_deaths_2021_by_month.to_csv('df_covid_deaths_2021_by_month.csv', index= False, encoding= 'utf-8')
# df_covid_deaths_2022_by_month.to_csv('df_covid_deaths_2022_by_month.csv', index= False, encoding= 'utf-8')
# covid_new_york_used_beds.to_csv('covid_new_york_used_beds.csv', index= False, encoding= 'utf-8')