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

    # wait till the scenario is doen (i.e. sleep)
    # this is called after the monitoring and the log processor has been started
    # can be used to start/stop input if you want to ensure they only start after the processor is up
    def wait(self):
        print("Waiting till scenario is done: " + self.name)                    
        # ensure the port is ready
        common.wait_for_port_available("localhost", 8099, 10)
        self.input_metric = common.send_http_requests("http://localhost:8099/", self.json, self.expected_count)
        # Now wait for number of received records on http benchmark server       
        self.output_metric = common.waitfor_http_benchmark_server(self.httpserver, self.expected_count, self.max_time)

    # cleanup resources (i.e. stop input and output)
    def cleanup(self):
        print("Scenario cleanup: " + self.name)
                
        common.stop_http_benchmark_server(self.httpserver)

        # increment for next subscenario
        self.subscenario_count+=1        

    def start_input(self):
        self.desc = common.ScenarioDescription("HTTP --> Log Proc --> HTTP")
        #create the log for static input
        if( self.subscenario_count == 1):
            # 100 char per request
            self.sleep = 10
            self.max_time = 15
            self.expected_count = 1000                                    
            self.desc.set_subtitle("HTTP Requests, JSON, 100 characters per request")
            # for each iteration/sub-scenario a dedicated prefix can be shared
            self.desc.set_file_prefix("1Kx100chars") 
            self.json = common.create_json_logline(100)

        elif( self.subscenario_count == 2):
            # 1000 char per line
            self.sleep = 10
            self.max_time = 30
            self.expected_count = 1000
            self.desc.set_subtitle("HTTP Requests, JSON, 1000 characters per request")
            self.desc.set_file_prefix("1Kx1000chars")            
            self.json = common.create_json_logline(1000)            
            # this is the final sub-scenario
            self.complete = True
        self.input_metric = -1
        print("Sub-Scenario: " + self.desc.get_subtitle())

    def start_output(self):   
        # http server has to be on path but also needs to be run from that location
        self.httpserver = common.start_http_benchmark_server()        
        common.wait_for_port_available("localhost", 8443, 10)
    
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
        outdesc = copy.deepcopy(self.desc)
        outdesc.set_subtitle("Output")
        outdesc.set_metric_unit("Seconds Till Complete")        
        return outdesc