# HTTP &rarr; NULL Scenario

## Description

This scenario sends JSON log lines via HTTP requests to the log processor.
The output of the log processor is pointing to NULL.
The scenario is done once all http requests are sent to the log processor.
This means it measures how fast a log processor can consume/buffer the log requests.

## Sub Scenarios

The scenario is run twice with two different data sets:

* 1000 log-lines/http-requests, each 100 characters long

* 1000 log-lines/http-requests, each 1000 characters long

## Input

HTTP request, JSON

## Output

NULL
