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
        self.logpath =  os.path.abspath("data/input.log")
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
        # this sceario has a static input log file
        
        # wait a few seconds to let the log processor finish
        time.sleep(self.sleep)    

    # cleanup resources (i.e. stop input and output)
    def cleanup(self):
        print("Scenario cleanup: " + self.name)
        
        if os.path.exists(self.logpath):
            try:
                os.remove(self.logpath)
            except:
                # sometimes a log processor migh still use it
                time.sleep(5)
                os.remove(self.logpath)

        # increment for next subscenario
        self.subscenario_count+=1        

    def start_input(self):
        self.desc = common.ScenarioDescription("Tail --> Log Proc --> NULL")
        #create the log for static input
        if( self.subscenario_count == 1):
            # 100 char per line
            self.sleep = 10
            self.max_time = 30
            self.expected_count = 1000000                                    
            self.desc.set_subtitle("Static input file, JSON, 100 characters per line")
            # for each iteration/sub-scenario a dedicated prefix can be shared
            self.desc.set_file_prefix("1Mx100chars") 
            common.create_json_log(self.logpath, self.expected_count,100,self.desc.get_file_prefix())            

        elif( self.subscenario_count == 2):
            # 1000 char per line
            self.sleep = 10
            self.max_time = 60
            self.expected_count = 1000000
            self.desc.set_subtitle("Static input file, JSON, 1000 characters per line")
            self.desc.set_file_prefix("1Mx1000chars")            
            common.create_json_log(self.logpath, self.expected_count, 1000,self.desc.get_file_prefix()) 
            
            # this is the final sub-scenario
            self.complete = True

        print("Sub-Scenario: " + self.desc.get_subtitle())

    def start_output(self):   
        print("Using null output")
    
    # provides a description for the chart output 
    def get_description(self):        
        return self.desc
    
    # return True as long as there are further sub-scenarios/iterations
    def has_next(self):
        return not self.complete
    
    # return the value of the input metric or None
    def get_input_metric(self):
        return None
    
    # descripe the input metric
    def get_input_description(self):
        return None

    # return the value of the output metric or None
    def get_output_metric(self):
        return None
    
    # descripe the output metric
    def get_output_description(self):
        return None