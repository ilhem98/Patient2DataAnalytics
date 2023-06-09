import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
import requests
from io import BytesIO



st.set_page_config(page_title='2nd Patient Data Analytics Dashboard', layout='wide', initial_sidebar_state='collapsed')



header_left, header_mid, header_right = st.columns([1, 2, 1], gap='large')

with header_mid:
    st.title('2nd Patient Data Analytics Dashboard')

    st.write("""
    **Credit:** Meryem Kacimi & Ilhem Kacimi
---
""")


@st.cache_resource
def get_data():
    # Download the file from GitHub and save it locally
   

    url = 'https://raw.githubusercontent.com/ilhem98/Patient2DataAnalytics/main/diabete%20data.csv'



    response = requests.get(url)
    content = response.content
    with open('diabete data', 'wb') as f:
        f.write(content)
    
    # Read the file from disk using pandas
    df = pd.read_csv('diabete data', sep=',')
    
    df['basal rate (U/h)'] = df['basal rate (U/h)'].interpolate(limit_direction='both')
    df['bolus'] = df['bolus'].interpolate(limit_direction='both')
    df['glycemia(g/l)'] = df['glycemia(g/l)'].interpolate(limit_direction='both')
    glucose = df[['date','time' ,'glycemia(g/l)', 'bolus', 'basal rate (U/h)']]
    return glucose


# Call the function to get the data
df = get_data()

# Print the first 5 rows of the DataFrame
st.write("""

# Data Pre-Processing  
The first step is to pull the data. In our case, We have an Omnipod Dash. Omnipod Dash provides easy access to our data which can be downloaded as a CSV file through Their Omnipod DISPLAY App.

The important data for us to look at are the glycemia(g/l), bolus and basal rate (U/h) columns.  Overall, the Omnipod Dash acquires a data point, stores it, and displays it to the user.


---
""")
# Create a Styler object
styler = df.head(5).style

# Change the font size of the header
styler.set_table_styles([
  {'selector': 'th', 'props': [('font-size', '20px')]}
])

st.table(styler)


st.write("""

# Mean Glucose Value  

The mean glucose value over a given period is a straightforward descriptor of overall glycemic control. 

The target range for diabetics is between 70 and 180 mg/dL, with normal (non-diabetic) mean glucose between 90 and 110 mg/dL.

---
""")

st.write("""

# Interquartile Range of Blood Glucose Values  

The plot below is a visual representation of my IQR.

Values range from ~40 (minimum detectable by the CGM) to 200, with points above 200 being classified as outliers as determined by the IQR.

---
""")


styler2 = df.describe().transpose().style

# Change the font size of the header
styler2.set_table_styles([
  {'selector': 'th', 'props': [('font-size', '20px')]}
])

st.table(styler2)




fig = plt.figure(figsize=(10,2))
sns.boxplot(x=df['bolus'])
plt.title('Blood Glucose Interquartile Range, mu=3');
st.pyplot(fig)


st.write("""

# Percentage of Time in Range (TIR)  

It’s useful to know the percentage of time in various ranges as an indication of the general behavior of CGM variations. As mentioned earlier in the study, the relevant ranges are:

hypoglycemia (BG < 0.7 g/L)

target range ( 0.7 g/L < BG < 1.8 g/L)

hyperglycemia (BG > 1.8 g/L)

---
""")


ranges= [0,0.7,1.8,3.5]
df['ranges'] = pd.cut(df['glycemia(g/l)'], bins= ranges)
result = (df.groupby([pd.Grouper(key="time"),"ranges"])["ranges"].count().unstack(0).T.fillna(0))
summed_results= result.sum()
st.table(summed_results.reset_index())


st.write("""

We can summarize these results by calculating a simple percentage of the total for each discrete time period. 

In this example, I used f-string formatting to create a nicely spaced tabular output:

---
""")
# Define the variables
less70 = 'Time<70:'
in_range = 'Time in range:'
greater180 = 'Time>180:'
var_percent = '%'

# Get the summed results
summed_results = result.sum()

# Create the table
st.table([
    [less70, str(round(summed_results.iloc[0]/summed_results.sum()*100,2))+var_percent],
    [in_range, str(round(summed_results.iloc[1]/summed_results.sum()*100,2))+var_percent],
    [greater180, str(round(summed_results.iloc[2]/summed_results.sum()*100,2))+var_percent]
])

st.write("""

Over this 30 day period,  BG values were in range ~90% of the time. We would prefer this number to be higher, but it will never be perfect. 

Ultimately, a higher TIR correlates to a lower risk for microvascular complications .

 TIR should be considered in combination with lab-derived A1C values to accurately assess the day-to-day glucose variations.

We  have only been able to find a few examples for TIR goals. Diabetes.org specifies a goal of at least 70% TIR, but We personally feel that is too low. 

Suffice to say, the higher the TIR, the better.


---
""")


df['Aggregate'] = [180 if glucose_val >= 180 else 70 if glucose_val <= 70 else 110 for glucose_val 
                        in df['bolus']]


st.write("""

# Glucose Trace
The glucose trace graph is simply a time series of BG values.

 It’s useful to visualize the fluctuations in BG levels over time, to determine if there are any trends throughout the day.

I wrote the following code to create a Plotly interactive graph that has buttons to change the display region.

 For example, clicking “1d” will change the window to display only one days worth of data. Similarly, “1m” will change the view to encompass one month of data. 
 
 From there, you can scrub back and forth to see how the BG values fluctuate over time:


---
""")



# Create the figure
fig = px.line(df, x="date", y=["glycemia(g/l)"], 
              title='Glucose Value Vs. Time', labels={'bolus':'Glucose Fluctuation'})

# Update the x-axis
fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1d", step="day", stepmode="backward"),
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")
        ])
    )
)

# Update the layout
fig.update_layout(xaxis_title='Time', yaxis_title='Glucose Value (mg/dL)')

# Convert the figure to a Streamlit plot

st.plotly_chart(fig, use_container_width=True)                    
