from copyreg import pickle
import os, sys
import pickle
from click import Path
#import dash
#import dash_html_components as html
from dash import Dash, html, dcc, dash_table, Output, Input
import pandas as pd
import plotly.graph_objects as go
#import dash_core_components as dcc
import plotly.express as px
#from dash.dependencies import Input, Output
import chart

app = Dash()

try:
    contents = os.listdir("results")
    if contents:
        rootdir = os.path.join("results", sorted(contents)[0])
    else:
        print("No results found to display. Please run benchmark.py before creating the dashboard")
        sys.exit(1)
except FileNotFoundError:
    print("Results directory not found")
    sys.exit(1)

scenarios = {}

# get all scenarios and data
for scenario in os.listdir(rootdir):
    csvlist = []
    descdict = {}
    scenario_dir = os.path.join(rootdir, scenario)
    if os.path.isdir(scenario_dir):
        scenario_results = os.listdir(scenario_dir)
        for file in scenario_results:
            if file.endswith(".csv"):
                #only process csv files
                csvlist.append(os.path.abspath(os.path.join(scenario_dir, file)))
            elif file.endswith(".pkl"):
                descpath = os.path.abspath(os.path.join(scenario_dir, file))
                descfile = open(descpath,'rb')
                desc = pickle.load(descfile)
                descfile.close()
                desc_name = file.split('.')[0]
                descdict[desc_name] = desc

        metadata = {}
        metadata['csv'] = csvlist
        metadata['desc'] = descdict
        print(metadata)
        scenarios[scenario] = metadata

scenarios_opt = []
default_value = None

for key in scenarios:
    option = {}
    metadata = scenarios[key]
    # the main title is same across sub scenarios, pick first
    desc = metadata['desc']
    scenario_desc = None
    for k in desc.keys():
        if('scenario_desc' in k):
            scenario_desc = k
            break

    if( not scenario_desc is None):
        option['label'] = desc[scenario_desc].get_name()
        option['value'] = key
        if(default_value is None):
            default_value = key
        scenarios_opt.append(option)


app.layout = html.Div(id = 'parent', children = [
    html.H1(id = 'H1', children = 'Log Processor Benchmark Results', style = {'textAlign':'center',\
                                            'marginTop':40,'marginBottom':40}),

        dcc.Dropdown( id = 'dropdown', options = scenarios_opt, value = default_value),
        html.Div(id='container'),
        html.Div(dcc.Graph(id='empty', figure={'data': []}), style={'display': 'none'})

    ])


@app.callback(Output('container', 'children'),
            [Input(component_id='dropdown', component_property= 'value')])
def display_graphs(dropdown_value):
    # first read the dataset for this scenario
    metadata = scenarios[dropdown_value]

    graphs = []
    # process available datasets
    csvcounter = 3  # start at 3 to show after input and output
    for csv in metadata['csv']:
        graphs.extend(graphs_from_csv(csv,dropdown_value,csvcounter))
        csvcounter += 1

    # ensure if we have input/output that these show up first
    graphs.sort(key=sort_graph)

    return html.Div(graphs)

def sort_graph(entry):
    return entry.id

def graphs_from_csv(csvfile, dropdown_value, csvcounter):
    graphs = []
    # there can be the following CSVs
    # input - for input metrics
    # output - for input metrics
    # *_result - results of a sub scenario
    metadata = scenarios[dropdown_value]
    desc = None
    idstr = None
    if(csvfile.endswith('input.csv')):
        print('Adding input graph')
        desc = metadata['desc']['input_desc']
        idstr = "1_input"
    elif(csvfile.endswith('output.csv')):
        print('Adding output graph')
        desc = metadata['desc']['output_desc']
        idstr = "2_output"
    else:
        print('Adding (sub)scenario graphs')
        prefix = os.path.basename(csvfile).split("_")[0]
        desc = metadata['desc'][prefix +'_scenario_desc']

    figs =  chart.createcharts(csvfile, desc)

    counter = 1
    for fig in figs:
        if(idstr is None):
            idstr = str(csvcounter) + "_" + str(counter) + "_result"
        counter += 1
        graph = dcc.Graph(
            id='graph-{}'.format(idstr),
            figure=fig
        )
        graphs.append(graph)
        idstr = None

    return graphs


if __name__ == '__main__':
    app.run_server()
