import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np



# Title of the dashboard
#st.set_page_config(page_title="Honda Data Dashboard", page_icon="honda.png", layout="wide")

st.set_page_config(page_title='Maersk Profitability Optimization', page_icon="maersk.png", layout='wide')

# Using columns to set the logo and title on the same line
col1, col2 = st.columns([1, 2])

# Setting the Maersk logo in the first column
with col1:
    st.image('maersk.png', width=100)

# Setting the title in the second column
with col2:
    st.title('Maersk Profitability Optimization')


# Optional: Add an introduction or description
st.markdown("""
This dashboard provides an analysis of the profitability optimization for Maersk by comparing the estimated and actual costs. 
Select a country and category to view the average monthly cost differences for the year 2023.
""")

# Function to load data (you may want to cache this function to improve performance)
@st.cache
def load_data():
    data = pd.read_excel('capstone_sample.xlsx')
    data['Activity Month Year'] = pd.to_datetime(data['Activity Month Year'])
    data['Difference'] = data['Actual Allocated Amount USD'] - data['Estimated Allocated Amount USD']
    return data

# Load data
df = load_data()

# Filter data for the year 2023
df_2023 = df[df['Activity Month Year'].dt.year == 2023]

# Sidebar filters
st.sidebar.header('Filters')
selected_country = st.sidebar.selectbox('Select a Country', df_2023['Location Activity Country Name'].unique())
selected_categories = st.sidebar.multiselect(
    'Select Categories',
    options=df_2023['Category'].unique(),
    default=df_2023['Category'].unique()[0]
)


# Filter the DataFrame based on the selected country and selected categories
df_filtered = df_2023[(df_2023['Location Activity Country Name'] == selected_country) &
                       (df_2023['Category'].isin(selected_categories))]

# Group by month and calculate the average difference
grouped_by_month = df_filtered.groupby(pd.Grouper(key='Activity Month Year', freq='M'))
avg_difference_by_month = grouped_by_month['Difference'].mean()

# Calculate summary statistics
summary_stats = df_filtered['Difference'].describe()

# Plotting
st.title('Average Monthly Cost Difference Analysis')
fig, ax = plt.subplots(figsize=(12, 6))  # You can adjust the figure size here

avg_difference_by_month.plot(marker='o', linestyle='-', ax=ax)
ax.set_title(f'Average Monthly Cost Difference for {selected_country} - Category: {selected_categories}')
ax.set_xlabel('Month')
ax.set_ylabel('Average Difference (USD)')
ax.grid(True)

# Label each data point with its value
for x, y in zip(avg_difference_by_month.index, avg_difference_by_month.values):
    label = "{:.2f}".format(y)
    ax.annotate(label, (x, y), textcoords="offset points", xytext=(0,10), ha='center')

st.pyplot(fig)

# Display summary statistics
st.subheader('Summary Statistics')
st.write(summary_stats)

# Histogram of differences
st.subheader('Histogram of Cost Differences')
fig, ax = plt.subplots()
df_filtered['Difference'].plot(kind='hist', bins=20, ax=ax)
ax.set_xlabel('Cost Difference (USD)')
st.pyplot(fig)

# Calculate month-over-month percentage change and display it
avg_difference_by_month_pct_change = avg_difference_by_month.pct_change().replace(np.inf, np.nan) * 100  # Convert to percentage
st.subheader('Month-over-Month Percentage Change in Average Cost Difference')
fig, ax = plt.subplots(figsize=(12, 6))
avg_difference_by_month_pct_change.plot(marker='o', linestyle='-', ax=ax)
ax.set_title(f'Month-over-Month Percentage Change for {selected_country} - Category: {selected_categories}')
ax.set_xlabel('Month')
ax.set_ylabel('Percentage Change (%)')
ax.grid(True)
st.pyplot(fig)

# Assuming 'top_10_countries' is a list of the top 10 countries by some metric
top_10_countries = df_2023['Location Activity Country Name'].value_counts().nlargest(10).index

# Prepare the grid of subplots
fig, axes = plt.subplots(nrows=5, ncols=2, figsize=(20, 15))  # Adjust the size as needed
axes = axes.flatten()  # Flatten the array of axes for easy iteration

for i, country in enumerate(top_10_countries):
    # Filter the DataFrame for the selected country
    df_country = df_2023[df_2023['Location Activity Country Name'] == country]

    # Group by month and calculate the average difference
    grouped_by_month = df_country.groupby(pd.Grouper(key='Activity Month Year', freq='M'))
    avg_difference_by_month = grouped_by_month['Difference'].mean()
    avg_difference_by_month.to_csv('avg_difference_by_month.csv')

    # Plotting the average monthly cost difference for the country
    axes[i].plot(avg_difference_by_month.index, avg_difference_by_month, marker='o', linestyle='-')
    axes[i].set_title(country)
    axes[i].set_xlabel('Month')
    axes[i].set_ylabel('Average Difference (USD)')
    axes[i].grid(True)

    # Label each data point with its value
    for x, y in zip(avg_difference_by_month.index, avg_difference_by_month):
        label = "{:.2f}".format(y)
        axes[i].annotate(label, (x, y), textcoords="offset points", xytext=(0,10), ha='center')

# Adjust the layout
plt.tight_layout()

# Display the plot in Streamlit
st.pyplot(fig)

# Add your inferences for the plot
st.header('Analysis and Inferences')
st.markdown("""

Here are some inferences that can be drawn from the plots:

Variability: There's a noticeable variability in the average differences for each country over time. No single country shows a consistent average difference across all months, indicating that there are fluctuations in how much the actual costs deviate from the estimated costs.

Extreme Values: Some countries show months with particularly high or low average differences, such as the United States in January 2023 or France in April 2023. These could indicate specific events or issues that led to unusually high costs or savings that month.

Trend Absence: There does not appear to be a clear upward or downward trend in the data for any of the countries, suggesting that the differences between estimated and actual costs do not consistently increase or decrease over the year.

Data Distribution: The average differences range from negative values, where actual costs were lower than estimated, to positive values, where actual costs were higher. This indicates a mix of overestimations and underestimations in the budgeting or costing process.

Comparative Analysis: Some countries, like Germany and the United Kingdom, generally have a narrower range of differences, implying more accurate estimations or stable costs. Others, like India and Canada, show wide swings, suggesting more volatile or less predictable cost behaviors.

Potential Outliers: There may be potential outliers, such as the data points for the United States in January or Canada in March, which are noticeably different from other months. These might warrant further investigation to understand the reasons behind such deviations.

Frequency of Over/Under Estimation: Certain countries, such as Italy and Poland, show a pattern where actual costs are frequently lower than estimated (negative values), which may indicate a trend of conservative estimations or efficiency in cost management.

Significant Changes: Some plots show significant changes from one month to the next, like the Netherlands from February to March, or Spain from June to July. Such changes could result from specific events, seasonal factors, or changes in operational efficiency or policy.


""")


st.cache_data 