# TAIL &rarr; HTTP Scenario

## Description

This scenario creates a log file in the data folder.
Once the log processor is started it processes this pre-existing file.
The output of the log processor is pointing to HTTP.
For the HTTP output a https-benchmark-server instance is started by the scenario.
The scenario is done once all the log lines are received by the backend or the maximum scenario time has elapsed.

## Sub Scenarios

The scenario is run twice with two different data sets:

* 1000 log-lines, each 100 characters long

* 1000 log-lines, each 1000 characters long

## Input

File, JSON

## Output

HTTP request, JSON