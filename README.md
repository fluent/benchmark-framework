# Log Processor Benchmark

This is a generic benchmark to measure the performance of log processors for given scenarios.

A scenario is a particular test that can be configured and executed with fluent-bit, fluentd, 
stanza, and vector.

### Description of the directory structure

The scenario.py file describes the scenarios and its sub scenarios (i.e. run the same scenario with different data sets).
The config folder contains the scenario specific configuration file for each log processor.
The name of the folder has to be one of these: fluent-bit, stanza, fluentd, vector

Each scenario has its own folder inside the scenarios folder, under the structure:

### benchmark-framework > scenarios > http_http : 

This scenario sends JSON log lines via HTTP requests to the log processor.
The output of the log processor is pointing to HTTP as well.
For the HTTP output a https-benchmark-server instance is started by the scenario.
The scenario is done once all sent http requests are received by the backend or the maximum scenario time has elapsed.

### benchmark-framework > scenarios > http_null: 

This scenario sends JSON log lines via HTTP requests to the log processor.
The output of the log processor is pointing to NULL.
The scenario is done once all http requests are sent to the log processor.
This means it measures how fast a log processor can consume/buffer the log requests.

### benchmark-framework > scenarios > tail_http :

This scenario creates a log file in the data folder.
Once the log processor is started it processes this pre-existing file.
The output of the log processor is pointing to HTTP.
For the HTTP output a https-benchmark-server instance is started by the scenario.
The scenario is done once all the log lines are received by the backend or the maximum scenario time has elapsed.

### benchmark-framework > scenarios > tail_null :

This scenario creates a log file in the data folder.
Once the log processor is started it processes this pre-existing file.
The output of the log processor is pointing to NULL.
The scenario is considered done once the configured scenario time has elapsed.

### benchmark-framework > scenarios > tcp_null :

This scenario sends JSON log lines via tcp/socket requests to the log processor.
The output of the log processor is pointing to NULL.
The scenario is done once all the tcp/socket requests are sent.

### benchmark-framework > scenarios > tcp_tcp : 

This scenario sends JSON log lines via tcp/socket requests to the log processor.
The output of the log processor is pointing to tcp/socket as well.
For the tcp/socket output a socket server instance is started by the scenario.
The scenario is done once all sent requests are received by the backend or the maximum scenario time has elapsed.


## Prerequisites

1. Python Interpreter

The log processor requires python 3 (tested with 3.9.10, 3.10 and 3.12) and the python dependencies listed 
in the ([requirements.txt](requirements.txt)) file.

To do this, you must install the dependencies in your Python virtual environment by running the command: 
pip install -r requirements.txt (ideally within your virtual environment created for Python 3.x, or if 
it is not a Python virtual environment, use pip3 install -r requirements.txt).

2. Log Procesor

In addition you need to have the log processor executables on your path:

* [Download fluent-bit](https://docs.fluentbit.io/manual/installation/getting-started-with-fluent-bit)
* [Download stanza](https://github.com/observIQ/stanza)
* [Download fluentd](https://www.fluentd.org/download)
* [Download vector](https://github.com/vectordotdev/vector)

3. For the HTTP scenarios you need the ([https-benchmark-server](https://github.com/chronosphereio/calyptia-https-benchmark-server)) on your path as well.

The https-benchmark-server is a program written in Go. From the provided link, you can download the Docker 
images. However, the execution of the benchmark (via benchmark.py) will attempt to find the executable in 
your operating system's path, so it is necessary to provide an environment for compiling and building 
the https-benchmark-server executable. Once you have built it, copy it to your environment's path or modify 
your environment to add the directory where https-benchmark-server is located to the search path.

4. Environment variable

Please ensure you have PYTHONPYCACHEPREFIX environment variable set (i.e. /tmp/.pycache) to avoid __pycache__ in the project.

## Limitations on macOS

Limitations of psutil on macOS

I/O Counters Access (io_counters):
On macOS, the io_counters() function of psutil is not supported, resulting in an AttributeError when attempting to 
access this property for processes.

Alternative: There is no direct alternative in psutil for macOS to obtain I/O counters. 
For detailed I/O information, you may need OS-specific tools like dtrace.

Due to this limitation, all tests will fail when attempting to tally input/output operations, and obtaining 
such a metric in monitor_pid.py will fail, but it won't be blocking, and the program will continue.

The failure due to library limitation occurs in:

#### def _get_io_read(proc, withchildren)
#### def _get_io_write(proc, withchildren)

## Run the Benchmark

`python benchmark.py`

It will run all scenarios for all agents (fluent-bit, fluentd, stanza, and vector).

If you need to define a specific scenario or a set of them, you should specify the --scenarios parameter followed by the scenario names, separated by commas.

Example:

`python benchmark.py --scenarios tail_null,tail_http`

If you need to define a specific log processor or a set of them, you should specify the --logprocessors parameter followed by the log processor names, separated by commas.

Example:

`python benchmark.py --scenarios tail_null --logprocessors fluent-bit`

The available scenarios for --scenarios parameter are::

* http_http
* http_null
* tail_http
* tail_null
* tcp_null
* tcp_tcp

The available log processors for --logprocessors parameter are:

* fluent-bit
* fluentd
* stanza
* vector

## Benchmark Results

Information about the system where the benchmark was executed is persisted in the system_info.txt 
inside the benchmark-framework folder, in a folder generated during each run named: 

* scenario_<date>_<sequencenumber>

Example: 

###### benchmark_framework/results/scenario_20240520_103157

The results for each scenario are stored in the results folder under scenario name folder
The data is kept in csv files and there are graphs in png format.

Example:

###### benchmark_framework/scenarios_tcp_null/results

In addition you can start a dashboard server to view the results:

`
python dashboard.py
`

Then go to ([http://localhost:8050](http://localhost:8050)) to see the results per scenario.

## Adding Scenarios

In order to add new scenarios you can start by copying the scenarios/_scenario_template folder.
Name the scenario according to your scenario. For example based on the input and output used by the scenario.
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

## How it works

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

