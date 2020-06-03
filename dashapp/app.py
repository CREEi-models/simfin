import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

# Load data
data = {inf/10 : pd.read_csv('data/output_'+str(inf/10)+'.csv') for inf in range(10,40,5) }


# Initialise the app
app = dash.Dash(__name__)
def total(inf):
    output = data[inf]
    total2 = make_subplots(specs=[[{"secondary_y": True}]])
    total2.add_trace(go.Scatter(x=output["Years"], y=output.loc[:,'total revenue'],
                        mode='lines+markers',
                        name='Revenu total'),secondary_y=False)

    total2.add_trace(go.Scatter(x=output["Years"], y=output.loc[:,'total spending'],
                        mode='lines+markers',
                        name='Dépense total'),secondary_y=False)

    total2.add_trace(go.Scatter(x=output["Years"], y=output.loc[:,'net surplus'],
                        mode='lines+markers',
                        name='Surplus net'),secondary_y=True)
    total2.update_layout(
        title_text="Revenus et dépenses totales",
        #template="plotly_dark"
    )
    total2.update_yaxes(title_text="Millions de $", secondary_y=False)
    total2.update_yaxes(title_text="Millions de $", secondary_y=True)
    return total2
def missions(inf):
    output = data[inf]

    missions = make_subplots()
    missions.add_trace(go.Scatter(x=output["Years"], y=output.loc[:,'mission health'],
                        mode='lines+markers',
                        name='Mission Santé'),secondary_y=False)
    missions.add_trace(go.Scatter(x=output["Years"], y=output.loc[:,'mission education'],
                        mode='lines+markers',
                        name='Mission éducation'),secondary_y=False)
    missions.add_trace(go.Scatter(x=output["Years"], y=output.loc[:,'other missions'],
                        mode='lines+markers',
                        name='Autres missions'),secondary_y=False)
    missions.add_trace(go.Scatter(x=output["Years"], y=output.loc[:,'debt service'],
                        mode='lines+markers',
                        name='Paiment de la dette'),secondary_y=False)

    missions.update_layout(
        title_text="Missions")

    missions.update_yaxes(title_text="Missions en M$", secondary_y=False)
    return missions

def taxes(inf):
    output = data[inf]

    taxes = make_subplots()

    taxes.add_trace(go.Scatter(x=output["Years"], y=output.loc[:,'personal'],
                        mode='lines+markers',
                        name='Taxe revenu individu'),secondary_y=False)

    taxes.add_trace(go.Scatter(x=output["Years"], y=output.loc[:,'corporate'],
                        mode='lines+markers',
                        name='Taxe entreprise'),secondary_y=False)
    

    taxes.add_trace(go.Scatter(x=output["Years"], y=output.loc[:,'consumption'],
                        mode='lines+markers',
                        name='Taxe à la consommation'),secondary_y=False)

    taxes.add_trace(go.Scatter(x=output["Years"], y=output.loc[:,'other taxes'],
                        mode='lines+markers',
                        name='Autres taxes'),secondary_y=False)


    taxes.update_layout(
        title_text="Taxes")

    taxes.update_yaxes(title_text="Taxes en M$", secondary_y=False)
    return taxes
# Define the app
app.layout = html.Div(
    children= [
    html.Div([
        html.Div([html.H1('SIMFIN - COVID19')
                 ],className='eight columns'),
        html.Div([html.H2('LOGO')],className='four columns')
        ],className='twelve columns'),
    html.Hr(className='Twelve columns'),
    html.Div([
        html.Div([
            html.H2('Hypothèses'),
            html.P('Inflation'),
            dcc.Slider(
                id='inf--slider',
                min=1.0,
                max=3.5,
                value=2.0,
                marks={ (int(inf/10) if np.mod(inf/10,1) == 0 else inf/10) : str(inf/10) for inf in range(10,40,5)},
                step=None
            )
            ],className="four columns"),
        html.Div([      
            dcc.Graph(id='total', figure=total(2))
            ],className="eight columns")      
        ], className="twelve columns"),
    html.Div([
        html.Div([
            html.P(' ')    
            ], className="four columns"),

        html.Div([
            dcc.Graph(id='mission', figure=missions(2)),
            dcc.Graph(id='taxes', figure=taxes(2))
            ], className="eight columns")
        ], className="twelve columns"),
    ]
    )
@app.callback(
    [Output(component_id='total', component_property='figure'),
     Output(component_id='mission', component_property='figure'),
     Output(component_id='taxes', component_property='figure')],
    [Input(component_id='inf--slider', component_property='value')]
)

def update_figure(input_value):
    return total(input_value),missions(input_value),taxes(input_value)
#app.layout = html.Div(className='eight columns div-for-charts bg-grey',
   # children = [
   # dcc.Graph(figure={'data':total,
   #              'layout': go.Layout(
   #               colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
   #               template='plotly_dark',
   #               paper_bgcolor='rgba(0, 0, 0, 0)',
   #               plot_bgcolor='rgba(0, 0, 0, 0)')}),
   # dcc.Graph(figure=surplus),
#])


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)