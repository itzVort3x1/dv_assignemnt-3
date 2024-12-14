from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np

worldometer_data = pd.read_csv('./worldometer_data.csv')
employment_data = pd.read_csv('./employment_data.csv')
covid_data = pd.read_csv('./owid-covid-data.csv')

worldometer_data['Country/Region'] = worldometer_data['Country/Region'].replace({'USA': 'United States'})
employment_data['country'] = employment_data['country'].replace({'United States': 'United States'})

merged_data = pd.merge(
    worldometer_data, employment_data, 
    left_on="Country/Region", right_on="country", 
    how="inner"
)

continent_mapping = {
    "USA": "North America",
    "Brazil": "South America",
    "India": "Asia",
    "Russia": "Europe",
    "South Africa": "Africa"
}

covid_data['date'] = pd.to_datetime(covid_data['date'])

covid_data['month_start_date'] = covid_data['date'].dt.to_period('M').dt.to_timestamp()

monthly_data = covid_data.groupby(['location', 'month_start_date']).agg(
    monthly_cases=('new_cases', 'sum')  
).reset_index()

if 'date' in monthly_data.columns:
    monthly_data = monthly_data.drop(columns=['date'])

monthly_data = monthly_data.sort_values(['location', 'month_start_date'])

print(monthly_data.tail())

merged_data["continent"] = merged_data["Country/Region"].map(continent_mapping)
merged_data = merged_data.sort_values('TotalDeaths', ascending=False)
merged_data['frame'] = np.arange(len(merged_data)) // 10

merged_data["Population_Scaled"] = merged_data["Population"] / 1e6

merged_data["gender_employment_ratio"] = (
    merged_data["employed_female_25+_2019"] / 
    merged_data["employed_male_25+_2019"]
)

merged_data['employment_impact'] = (
    merged_data['percentage_of_working_hrs_lost'] * merged_data['Population'] / 100
)

app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

app.layout = html.Div(
    [
        html.Div([
            html.H5('Global COVID-19 and Employment Stats Dashboard', className='text-center text-white')
        ], className='bg-dark'),

        html.Div([
            # Left Panel: Country-based Stats
            html.Div([
                html.H5('Country-based Stats', className='text-center pb-3 text-dark'),
                html.Div([
                    dcc.Graph(id='country-bar-chart')
                ], className='p-3 bg-light shadow rounded'),
                html.Div([
                    dcc.Dropdown(
                        id='country-dropdown',
                        options=[{'label': country, 'value': country} for country in merged_data['country'].unique()],
                        value=None,
                        placeholder="Highlight a Country",
                        className='btn w-75 mb-3'
                    )
                ], className='col-12 col-xl-6 p-2')
            ], className='col-12 col-xl-4 px-5'),

            html.Div([
                html.H5('Global COVID-19 Cases', className='text-center pb-3 text-dark'),
                html.Div([
                    dcc.Graph(
                        id='global-scatter-geo',
                        figure=px.scatter_geo(
                            merged_data,
                            locations="Country/Region", 
                            locationmode="country names",
                            size="Population_Scaled",
                            color="TotalCases",
                            hover_name="Country/Region",
                            hover_data={
                                "Population": ":,.0f",
                                "TotalCases": ":,.0f",
                                "TotalDeaths": ":,.0f"
                            },
                            color_continuous_scale=px.colors.sequential.Viridis,
                            size_max=50,
                            title="COVID-19 Cases vs Population Distribution",
                            projection="natural earth"
                        )
                    ),
                ], className='bg-light shadow rounded'),
            ], className='col-12 col-xl-4 px-5'),

            # Right Panel: Correlation Analysis
            html.Div([
                html.H5('Correlation Analysis', className='text-center pb-3 text-dark'),
                html.Div([
                    dcc.Graph(id='correlation-scatter-plot'),
                    html.Div([
                        html.Div([
                            dcc.Dropdown(
                                id='scatter-x-stat-dropdown',
                                options=[
                                    {'label': 'Total Cases', 'value': 'TotalCases'},
                                    {'label': 'Total Deaths', 'value': 'TotalDeaths'},
                                    {'label': 'Tests per Million', 'value': 'Tests/1M pop'},
                                    {'label': 'Labour Dependency Ratio', 'value': 'labour_dependency_ratio'}
                                ],
                                value='TotalCases',
                                className='btn w-100'
                            ),
                        ], className='col-12 col-xl-6 p-2'),
                        html.Div([
                            dcc.Dropdown(
                                id='scatter-y-stat-dropdown',
                                options=[
                                    {'label': 'Total Cases', 'value': 'TotalCases'},
                                    {'label': 'Total Deaths', 'value': 'TotalDeaths'},
                                    {'label': 'Tests per Million', 'value': 'Tests/1M pop'},
                                    {'label': 'Labour Dependency Ratio', 'value': 'labour_dependency_ratio'}
                                ],
                                value='TotalDeaths',
                                className='btn w-100'
                            ),
                        ], className='col-12 col-xl-6 py-2 px-5'),
                    ], className='row w-100')
                ], className='p-3 bg-light shadow rounded')
            ], className='col-12 col-xl-4 px-5')
        ], className='row'),

        # Row 2: Top Gender Metrics and Bubble Chart
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='employment-choropleth', figure=px.choropleth(
                            merged_data,
                            locations="Country/Region",
                            locationmode="country names",
                            color="percentage_of_working_hrs_lost",
                            hover_name="Country/Region",
                            title="Employment Impact by Percentage of Working Hours Lost",
                            projection="orthographic"
                        ))
                    ],
                    style={
                        "width": "48%",
                        "background-color": "#ffffff",
                        "border-radius": "10px",
                        "box-shadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
                        "display": "inline-block",
                        "vertical-align": "top",
                    },
                ),
                html.Div(
                    [
                        dcc.Graph(
                            id='line-chart-employment-impact',
                            figure=px.line(
                                merged_data.nlargest(10, 'TotalCases'),
                                x="Population",
                                y="employment_impact",
                                color="Country/Region",
                                hover_name="Country/Region",
                                title="Top 10 Countries: Employment Impact vs Population",
                                labels={
                                    "Population": "Population",
                                    "employment_impact": "Employment Impact (Number of People)"
                                },
                                markers=True
                            ).update_traces(line=dict(width=2))
                        )
                    ],
                    style={
                        "width": "48%",
                        "background-color": "#ffffff",
                        "border-radius": "10px",
                        "box-shadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
                        "display": "inline-block",
                        "vertical-align": "top",
                    },
                ),
            ],
            style={"display": "flex", "justify-content": "space-between"},
        ),

        # Footer
        html.Div([
            html.A('Data Source: Worldometer and Custom Employment Data', href='#'),
            html.Span(' | '),
            html.A('GitHub Repository', href='https://github.com/')
        ], className='bg-dark text-white text-center py-3 fs-5')
    ],
    style={
        "font-family": "Arial, sans-serif",
        "background-color": "#f5f7fa",
    },
)

@app.callback(
    Output('country-bar-chart', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_country_bar_chart(selected_country):
    fig = px.bar(
        merged_data,
        x='country',
        y='TotalDeaths',
        animation_frame='frame',
        title='Top 10 Countries by Total Deaths',
        color='country',
        hover_data=['Population', 'TotalCases', 'TotalDeaths'],
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    if selected_country and selected_country in merged_data['country'].values:
        selected_country_data = merged_data[merged_data['country'] == selected_country]
        fig.add_trace(
            px.bar(
                selected_country_data,
                x='country',
                y='TotalDeaths',
                color_discrete_sequence=['#EF553B']
            ).data[0]
        )

    fig.update_layout(
        showlegend=False,
        transition_duration=2000,
        xaxis_title="Country",
        yaxis_title="Total Deaths",
        xaxis={'categoryorder': 'total descending'}
    )

    fig.frames = fig.frames + fig.frames[:1]

    return fig

@app.callback(
    Output('correlation-scatter-plot', 'figure'),
    [Input('scatter-x-stat-dropdown', 'value'),
     Input('scatter-y-stat-dropdown', 'value')]
)
def update_scatter_plot(x_stat, y_stat):
    fig = px.scatter(
        merged_data,
        x=x_stat,
        y=y_stat,
        color='country',
        hover_data=['Population', 'TotalCases', 'TotalDeaths'],
        title=f'{x_stat} vs. {y_stat} Correlation Analysis'
    )
    fig.update_traces(marker_size=15)
    fig.update_layout(xaxis_title=x_stat, yaxis_title=y_stat)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
