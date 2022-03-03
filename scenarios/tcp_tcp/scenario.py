import copy
import os
import shutil
import subprocess
import sys
import time
from .. import common


class Scenario:

    def __init__(self, name):
        self.name = name
        self.complete = False
        self.subscenario_count = 1

    # initialize the scenrio (i.e. start input and output)
    def init(self):
        print("\nScenario initialization: " + self.name)
        self.start_input()
        self.start_output()

    def servercallback(self,elapsed):
        self.output_metric = elapsed

    # wait till the scenario is doen (i.e. sleep)
    # this is called after the monitoring and the log processor has been started
    # can be used to start/stop input if you want to ensure they only start after the processor is up
    def wait(self):
        print("Waiting till scenario is done: " + self.name)
        self.output_metric = None
        common.wait_for_port_available("localhost", 5170, 10)
        self.input_metric = common.send_socket_requests("localhost",5170, self.json, self.expected_count)

        sleep = self.max_time
        while(sleep>0 and (self.output_metric is None)):
            time.sleep(1)
            sleep -= 1

    # cleanup resources (i.e. stop input and output)
    def cleanup(self):
        print("Scenario cleanup: " + self.name)
        self.sockt_server_thread.join()
        # increment for next subscenario
        self.subscenario_count+=1


    def start_input(self):
        self.desc = common.ScenarioDescription("TCP --> Log Proc --> TCP")
        #create the log for static input
        if( self.subscenario_count == 1):
            # 100 char per request
            self.sleep = 15
            self.max_time = 60
            self.expected_count = 1000000
            self.desc.set_subtitle("Lines written, JSON, 100 characters per line")
            # for each iteration/sub-scenario a dedicated prefix can be shared
            self.desc.set_file_prefix("1Mx100chars")
            self.json = common.create_json_logline(100)

        elif( self.subscenario_count == 2):
            # 1000 char per line
            self.sleep = 15
            self.max_time = 60
            self.expected_count = 1000000
            self.desc.set_subtitle("Lines written, JSON, 1000 characters per line")
            self.desc.set_file_prefix("1Mx1000chars")
            self.json = common.create_json_logline(1000)
            # this is the final sub-scenario
            self.complete = True

        self.input_metric = -1
        print("Sub-Scenario: " + self.desc.get_subtitle())

    def start_output(self):
        print("Starting output")
        self.sockt_server_thread = common.start_socket_server(8443,self.max_time,self.expected_count,self.servercallback)
        common.wait_for_port_available("localhost", 8443, 15)

    # provides a description for the chart output
    def get_description(self):
        return self.desc

    # return True as long as there are further sub-scenarios/iterations
    def has_next(self):
        return not self.complete

    # return the value of the input metric or None
    def get_input_metric(self):
        return self.input_metric

    # descripe the input metric
    def get_input_description(self):
        inputdesc = copy.deepcopy(self.desc)
        inputdesc.set_subtitle("Input")
        inputdesc.set_metric_unit("Seconds Till Complete")
        return inputdesc

    # return the value of the output metric or None
    def get_output_metric(self):
        return self.output_metric

    # descripe the output metric
    def get_output_description(self):
        outputdesc = copy.deepcopy(self.desc)
        outputdesc.set_subtitle("Output")
        outputdesc.set_metric_unit("Seconds Till Complete")
        return outputdesc

