# TCP &rarr; NULL Scenario

## Description

This scenario sends JSON log lines via tcp/socket requests to the log processor.
The output of the log processor is pointing to NULL.
The scenario is done once all the tcp/socket requests are sent.

## Sub Scenarios

The scenario is run twice with two different data sets:

* 1000 log-lines, each 100 characters long

* 1000 log-lines, each 1000 characters long

## Input

TCP/SOCKET, JSON

## Output

NULL
