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

## Adding Scenarios

In order to add new scenarios you can start by copying the scenarios/_scenario_template folder.
Name the scenario accoring to your scenario. For example based on the input and output used by the scenario.
There is also a README.md in each scenario that describes what the scenario does.

Each scenario consists of the following folders:

### config:
contains sub folders per log processor that should be executed for this scenario. Please note that the folder names and config file names are expected to be identical to the other scenarios.
i.e.: /config/fluent-bit/fluent-bit.conf, /config/fluentd/fluentd.conf, /config/vector/vector.toml, /config/stanza/config.yaml

### data:
if your scenario requires some input data then this should be placed into this folder

### tmp:
temporary folder that will be cleared before each scenario execution

### results:
results of the scenario run.

The benchmark framework will execute the scenario.py in the following order:

***scenario.init()*** &rarr; allows you to initialize the scenario i.e. start/prepare the input

***scenario.get_description()*** &rarr; provide scenario description to the framework

&rarr;&rarr; after the init the benchmark framework will tart the log processor and the monitoring

***scenario.wait()*** &rarr; wait till the scenario is done, you can start input/output also here if it makes sense for your scenario

&rarr;&rarr; log processor and monitoring will be stopped

***scenario.cleanup()*** &rarr; stop input, output and do cleanup

***scenario.get_input_description()*** &rarr; if there is an input metric the scenario has to provide a description with the metric
***scenario.get_input_metric()***
***scenario.get_output_description()*** &rarr; if there is an output metric the scenario has to provide a description with the metric
***scenario.get_output_metric()***


## General Info

- This project was originally started at calyptia/benchmark-framework
- Project was moved to chronosphereio/calyptia-benchmark-framework (archived)
- Project has been moved in full to fluent/benchmark-framework

