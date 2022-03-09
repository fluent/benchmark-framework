from .. import common

class Scenario:

    def __init__(self, name):
        self.name = name
        self.complete = False

    # initialize the scenrio (i.e. start input and output)
    def init(self):
        print("Scenario initialization: " + self.name)

    # wait till the scenario is doen (i.e. sleep)	
    # this is called after the monitoring and the log processor has been started
    # can be used to start/stop input if you want to ensure they only start after the processor is up
    def wait(self):
        print("Waiting till scenario is done: " + self.name)

    # cleanup resources (i.e. stop input and output)
    def cleanup(self):
        print("Scenario cleanup: " + self.name)
        self.complete = True
	
    # while this returns true, init/get_description/cleanup functions are called in a loop
    def has_next(self):
        return self.complete

    # provide a description for each scenario/iteration
	def get_description(self):
        desc = common.ScenarioDescription("Tail --> Log Proc --> HTTP")
        desc.set_subtitle("Static input file, JSON, x bytes per line")
		return desc
    
    # ------ below functions can return None if there is no input/output metric for this scenario ------

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
