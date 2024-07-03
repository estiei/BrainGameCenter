from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, Http404
from django.conf import settings
from scipy.stats import ttest_ind, linregress, pearsonr
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import json
import os

def generate_combined_figure(art_data):
    # Sort the data
    df = art_data

    df['temp_mean'] = df['temp_mean'] / 1000
    df_sorted_time = df.sort_values(by='temp_mean', ascending=False)
    df_sorted_mistakes = df.sort_values(by='answ_mean', ascending=False)

    # Create the combined figure
    fig = go.Figure()

    # Add traces for time spent and average mistakes

    fig.add_trace(go.Bar(x=df_sorted_time['words'], y=df_sorted_time['answ_mean'], name='Average Mistakes', 
                        marker=dict(color='lightgreen'), opacity=0.5, yaxis='y2', offsetgroup=2))
    fig.add_trace(go.Bar(x=df_sorted_time['words'], y=df_sorted_time['temp_mean'], name='Time Spent (seconds)',
                        marker=dict(color='blue'), opacity=1, yaxis='y1', offsetgroup=1))


    fig.add_trace(go.Bar(x=df_sorted_mistakes['words'], y=df_sorted_mistakes['answ_mean'], name='Average Mistakes', 
                        marker=dict(color='lightgreen'), yaxis='y2', opacity=1, offsetgroup=2, visible=False))
    fig.add_trace(go.Bar(x=df_sorted_mistakes['words'], y=df_sorted_mistakes['temp_mean'], name='Time Spent (seconds)', 
                        marker=dict(color='blue'), yaxis='y1', opacity=0.45, offsetgroup=1, visible=False))

    # Update layout with dropdown and secondary y-axis
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=[
                    dict(label='Time Spent',
                         method='update',
                         args=[{'visible': [True, True, False, False]},
                               {'title': 'Time Spent on Each Question'}]),
                    dict(label='Average Mistakes',
                         method='update',
                         args=[{'visible': [False, False, True, True]},
                               {'title': 'Average Mistakes per Question'}])
                ],
                direction='down',
                showactive=True,
                x=.77,
                xanchor='left',
                y=1.33,
                yanchor='top'
            )
        ],
        # set the x-axis titles and tick font size and set tick orientation to 45 degrees
        xaxis=dict(title='Questions', titlefont=dict(size=19), tickfont=dict(size=15), tickangle=45),
        # seet the y-axis titles and font size
        yaxis=dict(title='Time Spent (seconds)', side='left', titlefont=dict(size=19), tickfont=dict(size=18)),
        yaxis2=dict(title='Average Mistakes', overlaying='y', side='right',  titlefont=dict(size=19), tickfont=dict(size=18)),
        barmode='group',
        # set the title of the graph and it font size
        title= dict(text='Time Spent on Each Question', font=dict(size=22)),
        legend=dict( x=1, y=1.13, xanchor='left', yanchor='bottom', font=dict(size=16))
    )

    return fig.to_html(config={'displayModeBar': False}, full_html=False, include_plotlyjs=False)

def generate_scatter_plot(art_data):
    # Normalize temp_mean (if needed)
    df = art_data

    df['temp_mean'] = df['temp_mean'] / 1000

    # Calculate Pearson correlation coefficient and p-value
    correlation, p_value = pearsonr(df['temp_mean'], df['difficulty'])

    # Calculate slope and intercept for the regression line using linregress
    slope, intercept, r_value, p_value, std_err = linregress(df['temp_mean'], df['difficulty'])

    # Create scatter plot and set the size of the dots
    fig_scatter = px.scatter(df, x='temp_mean', y='difficulty', 
                             labels={'temp_mean': 'Time Spent (s)', 'difficulty': 'IRT difficulty'},
                             title=f'Correlation between Item Difficulty (IRT) and Average Time Spent per item')

    # Set font `size` for x and y axes and title
    fig_scatter.update_traces(marker_size=15, marker_color='blue', marker_opacity=0.5)
    fig_scatter.update_xaxes(tickfont=dict(size=19), title_font_size=22)
    fig_scatter.update_yaxes(tickfont=dict(size=19), title_font_size=22)
    fig_scatter.update_layout(title_font_size=22)

    # Add a line where the slope is calculated and the intercept is adjusted
    x = np.linspace(df['temp_mean'].min(), df['temp_mean'].max(), 100)
    y = slope * x + intercept

    fig_scatter.add_trace(go.Scatter(x=x, y=y, mode='lines', 
                                     name=f'corcoeff = {correlation:.2f}, p = {p_value:.4f}', 
                                     line=dict(color='red', width=1.5)))
    # Add the legend to the plot and set its font size and position
    fig_scatter.update_layout(showlegend=True, legend=dict(x=0.65, y=1, font=dict(size=18)))
    
    # Set the figure size
    fig_scatter.update_layout(width=1000, height=550)

    return fig_scatter.to_html(config={'displayModeBar': False}, full_html=False, include_plotlyjs=False)

def categorize_correct_answers(value):
    if value < 10:
        return 'Q1'
    elif 10 <= value < 20:
        return 'Q2'
    elif 20 <= value < 30:
        return 'Q3'
    else:
        return 'Q4'

def generate_correct_answer_histogram(participants_df):
    df = participants_df
    df = df.sort_values(by='sum_answ')

    # Apply the categorization
    df['Quartile'] = df['sum_answ'].apply(categorize_correct_answers)

    color_scale = {
        'Q1': 'rgba(0, 0, 255, 0.2)',
        'Q2': 'rgba(0, 0, 255, 0.4)',
        'Q3': 'rgba(0, 0, 255, 0.55)',
        'Q4': 'rgba(0, 0, 255, 0.7)'
    }

    # Create histogram using Plotly
    fig = px.histogram(df, x='sum_answ', nbins=20, color='Quartile',
                       color_discrete_map=color_scale,
                       labels={'sum_answ': 'Correct Answers'},
                       title='Histogram of Correct Answers Distribution')
    # set font `size` for x and y axes and title
    fig.update_xaxes(tickfont=dict(size=19), title_font_size=23)
    fig.update_yaxes(tickfont=dict(size=19), title_font_size=23)
    fig.update_layout(title_font_size=22)

    fig.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGrey')))
    fig.update_layout(showlegend=True, legend=dict(font=dict(size=18)))

    # set the figure size
    fig.update_layout(width=1000, height=450)

    return fig.to_html(config={'displayModeBar': False}, full_html=False, include_plotlyjs=False)

def generate_correct_answers_vs_ability(participants_df):
    # Calculate mean and standard deviation for each unique value in 'sum_answ'
    df = participants_df

    stats = df.groupby('sum_answ')['ability'].agg(['mean', 'std']).reset_index()
    stats.columns = ['sum_answ', 'mean', 'std']

    # Replace NaN values with 0 in stats
    stats.fillna({'std': 0}, inplace=True)

    # Create the figure
    fig = go.Figure()

    # Add fill between lines for the range (-SD, +SD)
    fig.add_trace(go.Scatter(
        x=pd.concat([stats['sum_answ'], stats['sum_answ'][::-1]]),
        y=pd.concat([stats['mean'] + stats['std'], (stats['mean'] - stats['std'])[::-1]]),
        fill='toself',
        fillcolor='LightSkyBlue',
        line=dict(color='rgba(255,255,255,0)'),
        name='SD',
        showlegend=True
    ))

    # Add line representing mean value for each unique sum_answ
    fig.add_trace(go.Scatter(x=stats['sum_answ'], y=stats['mean'], mode='lines',
                             line=dict(width=2, color='blue'),
                             name='Mean Value'))

    # Update layout
    fig.update_layout(
        title='Correct Answers vs Ability',
        xaxis_title='Correct Answers',
        yaxis_title='Ability'
    )

    # set font size for x and y axes and title
    fig.update_xaxes(tickfont=dict(size=19), title_font_size=23)
    fig.update_yaxes(tickfont=dict(size=19), title_font_size=23)
    fig.update_layout(title_font_size=22)

    fig.update_layout(showlegend=True, legend=dict(font=dict(size=18)))

    # set the figure size
    fig.update_layout(width=1000, height=450)

    return fig.to_html(config={'displayModeBar': False}, full_html=False, include_plotlyjs=False)

def generate_participants_data(art_data):
    # Define the path to the JSON file
    json_file_path = os.path.join(settings.BASE_DIR, 'best_parameters.json')

    # Read the JSON file into a dictionary
    with open(json_file_path, 'r') as file:
        irt_param = json.load(file)

    # form a dataset with abilities of participants
    df = art_data

    PARTN_NUM = 120 # number of participants
    summary_data = {'id':[], 'sum_answ':[], 'mean_answ':[], 'sd_answ':[], 'sum_temp':[], 'mean_temp':[], 'sd_temp':[]}

    for id in range(PARTN_NUM):
        summary_data['id'].append(id)

        col = f'answ_{id}'   
        summary_data['sum_answ'].append(df[col].sum())
        summary_data['mean_answ'].append(df[col].mean())
        summary_data['sd_answ'].append(df[col].std())

        col = f'temp_{id}'
        summary_data['sum_temp'].append(df[col].sum())
        summary_data['mean_temp'].append(df[col].mean())
        summary_data['sd_temp'].append(df[col].std())

    # Create a new DataFrame with the summary data
    participants_df = pd.DataFrame(summary_data)
    participants_df['ability'] = irt_param['ability']

    return participants_df

# Handles requests for the index page
def index(request):
    # Load the artifical data
    art_data = pd.read_csv(os.path.join(settings.BASE_DIR, 'art_generated_data.csv'))
    participants_df = generate_participants_data(art_data)

    # Load the HTML template
    template = loader.get_template("myapp/index.html")

    # Create the context dictionary for the template
    context = {
        'combined_figure': generate_combined_figure(art_data),
        'scatter_plot': generate_scatter_plot(art_data),
        'correct_answer_histogram': generate_correct_answer_histogram(participants_df),
        'correct_answers_vs_ability': generate_correct_answers_vs_ability(participants_df)
    }

    return HttpResponse(template.render(context, request))

