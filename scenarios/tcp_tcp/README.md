# TCP &rarr; TCP Scenario

## Description

This scenario sends JSON log lines via tcp/socket requests to the log processor.
The output of the log processor is pointing to tcp/socket as well.
For the tcp/socket output a socket server instance is started by the scenario.
The scenario is done once all sent requests are received by the backend or the maximum scenario time has elapsed.

## Sub Scenarios

The scenario is run twice with two different data sets:

* 1000 log-lines/tcp-requests, each 100 characters long

* 1000 log-lines/tcp-requests, each 1000 characters long

## Input

TCP request, JSON

## Output

TCP request, JSON
