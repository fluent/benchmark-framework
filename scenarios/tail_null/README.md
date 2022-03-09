# TAIL &rarr; NULL Scenario

## Description

This scenario creates a log file in the data folder.
Once the log processor is started it processes this pre-existing file.
The output of the log processor is pointing to NULL.
The scenario is considered done once the configured scenario time has elapsed.

## Sub Scenarios

The scenario is run twice with two different data sets:

* 1000 log-lines, each 100 characters long

* 1000 log-lines, each 1000 characters long

## Input

File, JSON

## Output

NULL
