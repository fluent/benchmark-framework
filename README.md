# Log Processor Benchmark

This is a generic benchmark to measure the performance of log processors for given scenarios.

Each scenario has its own folder inside the scenarios folder.
The scenario.py file describes the scenarios and its sub scenarios (i.e. run the same scenario with different data sets).
The config folder contains the scenario specific configuration file for each log processor.
The name of the folder has to be one of these: fluent-bit, stanza, fluentd, vector

## Prerequisitesd

The log processor requires python 3 (tested with 3.9.10) and the python dependencies listed in the ([requirements.txt](requirements.txt)) file (i.e pip3 install -r requirements.txt).

In addition you need to have the log processor executables on your path.
For the HTTP scenarios you need the ([https-benchmark-server](https://raw.githubusercontent.com/calyptia/https-benchmark-server/)) on your path as well.

Please ensure you have PYTHONPYCACHEPREFIX environment variable set (i.e. /tmp/.pycache) to avoid __pycache__ in the project.

## Run the Benchmark

`
python benchmark.py
`

If you would like to limit the scenarios or log processors then you can specify that:

`
python benchmark.py --scenarios tail_null,tail_http --logprocessors fluent-bit,vector,stanza,fluentd
`

## Benchmark Results

The results for each scenario are stored in the results folder.
The data is kept in csv files and there are graphs in png format.

Inforomation about the system where the benchmark was executed is persisted in the system_info.txt.

In addition you can start a dashboard server to view the results:

`
python dashboard.py
`

Then go to ([http://localhost:8050](http://localhost:8050)) to see the results per scenario.