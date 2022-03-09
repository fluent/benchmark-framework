# HTTP &rarr; HTTP Scenario

## Description

This scenario sends JSON log lines via HTTP requests to the log processor.
The output of the log processor is pointing to HTTP as well.
For the HTTP output a https-benchmark-server instance is started by the scenario.
The scenario is done once all sent http requests are received by the backend or the maximum scenario time has elapsed.

## Sub Scenarios

The scenario is run twice with two different data sets:

* 1000 log-lines/http-requests, each 100 characters long

* 1000 log-lines/http-requests, each 1000 characters long

## Input

HTTP request, JSON

## Output

HTTP request, JSON
