#######################
# Import libraries

import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from vega_datasets import data

#######################
# Page configuration
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 25px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 40%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 40%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}


</style>
""", unsafe_allow_html=True)

# Load data
df_reshaped = pd.read_csv('data/us-population-2010-2019-reshaped.csv')


# Sidebar
with st.sidebar:
    st.title('🏂 US Population Dashboard')
    
    year_list = list(df_reshaped.year.unique())
    
    selected_year = st.selectbox('Select a year', year_list, index=len(year_list)-1)
    df_selected_year = df_reshaped[df_reshaped.year == selected_year]
    # df_selected_year['states_code'] = [states_abbreviation[x] for x in df_selected_year.states]
    df_selected_year_sorted = df_selected_year.sort_values(by="population", ascending=False)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)
    

# Plots

# Heatmap
heatmap = alt.Chart(df_reshaped).mark_rect().encode(
        y=alt.Y('year:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
        x=alt.X('states:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
        color=alt.Color('max(population):Q',
                         legend=alt.Legend(title=" "),
                         scale=alt.Scale(scheme=selected_color_theme)),
        stroke=alt.value('black'),
        strokeWidth=alt.value(0.25),
        #tooltip=[
        #    alt.Tooltip('year:O', title='Year'),
        #    alt.Tooltip('population:Q', title='Population')
        #]
    ).properties(height=300
    #).configure_legend(orient='bottom', titleFontSize=16, labelFontSize=14, titlePadding=0
    #).configure_axisX(labelFontSize=14)
    ).configure_axis(
    labelFontSize=12,
    titleFontSize=12
    )

# Choropleth map
choropleth = px.choropleth(df_selected_year, locations='states_code', color='population', locationmode="USA-states",
                           color_continuous_scale=selected_color_theme,
                           range_color=(0, max(df_selected_year.population)),
                           scope="usa",
                           labels={'population':'Population'}
                          )

choropleth.update_layout(
    template='plotly_dark',
    plot_bgcolor='rgba(0, 0, 0, 0)',
    paper_bgcolor='rgba(0, 0, 0, 0)',
    margin=dict(l=0, r=0, t=0, b=0),
    height=350,
    legend=dict(
        title_font_family='Courier New',
        font=dict(
        size=16
    ))
)

# Donut chart
def make_donut(input_response, input_text, input_color):
  if input_color == 'blue':
      chart_color = ['#29b5e8', '#155F7A']
  if input_color == 'green':
      chart_color = ['#27AE60', '#12783D']
  if input_color == 'orange':
      chart_color = ['#F39C12', '#875A12']
  if input_color == 'red':
      chart_color = ['#E74C3C', '#781F16']
    
  source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
  })
  source_bg = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100, 0]
  })
    
  plot = alt.Chart(source).mark_arc(innerRadius=55, cornerRadius=25).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          #domain=['A', 'B'],
                          domain=[input_text, ''],
                          # range=['#29b5e8', '#155F7A']),  # 31333F
                          range=chart_color),
                      legend=None),
  ).properties(width=140)
    
  text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=38, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
  plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=55, cornerRadius=20).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          # domain=['A', 'B'],
                          domain=[input_text, ''],
                          range=chart_color),  # 31333F
                      legend=None),
  ).properties(width=140)
  return plot_bg + plot + text

# Convert population to text 
def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

# Calculation year-over-year population migrations
def calculate_population_difference(input_df, input_year):
  selected_year_data = input_df[input_df['year'] == input_year].reset_index()
  previous_year_data = input_df[input_df['year'] == input_year - 1].reset_index()
  selected_year_data['population_difference'] = selected_year_data.population.sub(previous_year_data.population, fill_value=0)
  selected_year_data['population_difference_absolute'] = abs(selected_year_data['population_difference'])
  return pd.concat([selected_year_data.states, selected_year_data.id, selected_year_data.population, selected_year_data.population_difference, selected_year_data.population_difference_absolute], axis=1).sort_values(by="population_difference", ascending=False)


#######################
# Dashboard Main Panel
row_1_col = st.columns((1, 4, 2))

with row_1_col[0]:
    st.markdown('#### Gains/Losses')

    df_population_difference_sorted = calculate_population_difference(df_reshaped, selected_year)

    if selected_year > 2010:
        first_state_name = df_population_difference_sorted.states.iloc[0]
        first_state_population = format_number(df_population_difference_sorted.population.iloc[0])
        first_state_delta = format_number(df_population_difference_sorted.population_difference.iloc[0])
    else:
        first_state_name = '-'
        first_state_population = '-'
        first_state_delta = ''

    st.metric(label=first_state_name, value=first_state_population, delta=first_state_delta)

    if selected_year > 2010:
        last_state_name = df_population_difference_sorted.states.iloc[-1]
        last_state_population = format_number(df_population_difference_sorted.population.iloc[-1])   
        last_state_delta = format_number(df_population_difference_sorted.population_difference.iloc[-1])   
    else:
        last_state_name = '-'
        last_state_population = '-'
        last_state_delta = ''
    
    st.metric(label=last_state_name, value=last_state_population, delta=last_state_delta)

    st.markdown('#### States Migration')
    # Filter states with population difference > 50000
    df_greater_50000 = df_population_difference_sorted[df_population_difference_sorted.population_difference_absolute > 50000]
    # % of States with population difference > 50000
    states_migration = int((len(df_greater_50000)/df_population_difference_sorted.states.nunique())*100)

    st.altair_chart(make_donut(states_migration, 'States Migration', 'orange'))


with row_1_col[1]:
    st.plotly_chart(choropleth, use_container_width=True)
    
    st.markdown('#### Total Population')
    st.altair_chart(heatmap, use_container_width=True)
    

with row_1_col[2]:
    st.markdown('#### Top States')

    st.dataframe(df_selected_year_sorted,
                 column_order=("states", "population"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "states": st.column_config.TextColumn(
                        "States",
                    ),
                    "population": st.column_config.ProgressColumn(
                        "Population",
                        width="medium",
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_year_sorted.population),
                     )}
                 )
    with st.expander('About'):
        st.write('''
            - Data obtained from the [U.S. Census Bureau](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html).
            - :orange[**Gains/Losses**] refers to states with high inbound and outbound migration in the selected year
            - :orange[**States Migration**] refers to the percentage of states with annual migration > 50,000
            ''')

# Notes
# 6rem 1rem 10rem
