#!/usr/bin/env python3

from http.server import executable
import signal
import sys
import argparse
import importlib
import json
import os
import pickle
import platform
import shutil
import yaml
import logging.config

if(sys.platform == "win32"):
    from signal import CTRL_BREAK_EVENT, CTRL_C_EVENT
else:
    from signal import SIGINT

import subprocess
import threading

from datetime import datetime
import pandas as pd
import time

from psutil import cpu_freq
import monitor_pid
import psutil
import chart
from tabulate import tabulate

# constants
FLUENTBIT = "Fluent Bit"
VECTOR = "Vector"
STANZA = "Stanza"
FLUENTD = "Fluentd"

logproc = None

def preexec_function():
    if(not sys.platform == "win32"):
        logging.info("---> PREEXEC_FUNCTION")
        # Ignore the SIGCON signal by setting the handler to the standard
        # signal handler SIG_IGN.
        #signal.signal(signal.SIGCONT, signal.SIG_IGN)
        os.setpgrp()

kwargs = {}
if sys.platform == "win32":
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    kwargs.update(creationflags=CREATE_NEW_PROCESS_GROUP)
else:
    kwargs.update(preexec_fn=preexec_function)

"""
Config for Benchmark framework
File for config : log-processor.yaml
"""
def setup_benchmark(config_file, log_file=None):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    if log_file:
        config['logging']['handlers']['file']['filename'] = log_file
        if 'file' not in config['logging']['root']['handlers']:
            config['logging']['root']['handlers'].append('file')
    else:
        config['logging']['root']['handlers'] = ['console']

    config['logging']['handlers']['console']['class'] = 'logging.StreamHandler'
    config['logging']['handlers']['file']['class'] = 'logging.FileHandler'

    config['logging']['formatters'] = {
        'simple': {
            'format': '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - Line:%(lineno)d - %(message)s'
        }
    }

    # formatter for handlr
    config['logging']['handlers']['console']['formatter'] = 'simple'
    config['logging']['handlers']['file']['formatter'] = 'simple'

    # Configure logger
    logging.config.dictConfig(config['logging'])

    # Obtain scenarios and agents
    scenarios = config.get('scenarios', {})

    type_values = scenarios.get('type', [])
    agents_scenarios_values = scenarios.get('agents_scenarios', [])

    return type_values, agents_scenarios_values


def run_fluentbit(dir, location):
    logging.info("Starting Fluent Bit")
    if(sys.platform == "win32"):
        executable = "fluent-bit"
    else:
        executable = "fluent-bit"

    if not location:
        location = shutil.which(executable)

    if( location is None ):
        return None
    configpath = os.path.abspath(os.path.join(dir, "config", "fluent-bit", "fluent-bit.conf"))
    logging.info(f'configPath: {configpath}')
    proc = ensure_proc_alive(subprocess.Popen([location, "-c", configpath],stdout=sys.stdout, stderr=sys.stderr, **kwargs))
    logging.info(f'proc: {proc}')
    time.sleep(1) # got crashes sometimes without this on linux
    return proc

def run_vector(dir, location):
    logging.info("Starting Vector")

    if not location:
        location = shutil.which("vector")

    if( location is None ):
        return None

    # note vector by default uses as many threads as CPU cores are available
    # see https://vector.dev/docs/reference/cli/#vector_threads
    configpath = os.path.abspath(os.path.join(dir, "config", "vector", "vector.toml"))
    logging.info(f'configPath: {configpath}')
    proc = ensure_proc_alive(subprocess.Popen([location, "-c", configpath],stdout=sys.stdout, stderr=sys.stderr, **kwargs))
    logging.info(f'proc: {proc}')

    return proc

def run_stanza(dir, location):
    logging.info("Starting Stanza")

    if not location:
        location = shutil.which("stanza")

    if( location is None ):
        return None

    configpath = os.path.abspath(os.path.join(dir, "config", "stanza", "config.yaml"))
    logging.info(f'configPath: {configpath}')
    proc = ensure_proc_alive(subprocess.Popen([location, "-c", configpath],stdout=sys.stdout, stderr=sys.stderr, **kwargs))
    logging.info(f'proc: {proc}')

    return proc

def run_fluentd(dir, location):
    logging.info("Starting Fluentd")
    configpath = os.path.abspath(os.path.join(dir, "config", "fluentd", "fluentd.conf"))
    logging.info(f'configPath: {configpath}')
    executeable = "td-agent"

    # on Windows td-agent works from console but Popen needs .bat added
    if(sys.platform == "win32"):
        executeable = executeable + ".bat"

    if not location:
        location = shutil.which(executeable)

    if( location is None ):
        return None

    proc = ensure_proc_alive(subprocess.Popen([location, "-c", configpath],stdout=sys.stdout, stderr=sys.stderr, **kwargs))
    logging.info(f'proc: {proc}')
    return proc


def ensure_proc_alive(proc):
    poll = proc.poll()
    # process still alive?
    if poll is not None:
        strExit='Failed to start process'
        logging.error(strExit)
        sys.exit(strExit)
    return proc

def clear_dir(basedir, folder ):
    try:
        dir = os.path.join(basedir,folder)
        if(os.path.exists(dir)):
            shutil.rmtree(dir)
        os.mkdir(dir)
    except OSError as e:
        logging.error('cwd: ' + os.getcwd())
        logging.error("\t" + e.strerror)
        pass

# dynamically load the python class for the given scenario
def get_scenario_instance(name):
    module = importlib.import_module('scenarios.'+name+'.scenario')
    cls = getattr(module, 'Scenario')
    scenario = cls(str(name))
    return scenario

monitor_called_back = False
stop_monitor_thread = False

def monitor_callback():
    global monitor_called_back
    global stop_monitor_thread

    monitor_called_back = True
    return stop_monitor_thread

def start_monitoring(pidstr, logprocessor, csvresult):
    global monitor_called_back
    global stop_monitor_thread
    monitor_called_back = False
    stop_monitor_thread = False

    monitor_thread = threading.Thread(target=monitor_pid.monitor, name="Monitoring", args=[pidstr, logprocessor, csvresult, monitor_callback])
    monitor_thread.start()

    while(not monitor_called_back):
        time.sleep(0.5)

    return monitor_thread

def stop_monitoring(monitor_thread):
    global stop_monitor_thread
    stop_monitor_thread = True

    time.sleep(1)
    monitor_thread.join()


# run one scenrio

<<<<<<< HEAD
def run_scenario(scenario_name, scenario_dir, logprocessor, path_scenario, **kwargs):
    version = kwargs.get("version","")
    location = kwargs.get("location","")
    abs_scenario_path = os.path.abspath(scenario_dir)
    results_path = os.path.join(path_scenario,'results')

    os.makedirs(results_path, exist_ok=True)

    logging.info("\nRunning scenario: " + abs_scenario_path)

=======
def run_scenario(scenario_name, scenario_dir, logprocessor, results_path=None, **kwargs):
    version = kwargs.get("version","")
    location = kwargs.get("location","")
    abs_scenario_path = os.path.abspath(scenario_dir)
    results_path = os.path.join(abs_scenario_path,'results')
    print("\nRunning scenario: " + abs_scenario_path)
>>>>>>> f5499dd (Understanding modifications and benchmark-framework dependencies)
    cwd = os.getcwd()
    logging.info(f'Working Directory: {cwd}')
    os.chdir(abs_scenario_path)
    logging.info(f'Path: {abs_scenario_path}')

    # load the scenario implementation
    logging.info(f'load the scenario : {scenario_name}')
    scenario = get_scenario_instance(scenario_name)

    while scenario.has_next():
        # clear any temp files
        clear_dir(abs_scenario_path, 'tmp')

        # ensure we are in the right folder on each iteration, no matter what the scenario does
        os.chdir(abs_scenario_path)

        # initialize the scenario, usually starts input and output
        scenario.init()
        # get the description of this scenario iteration
        sdesc = scenario.get_description()
        prefix = sdesc.get_file_prefix()
        if( prefix is None):
            prefix = ''

        # start log processor
        logproc = None
        sendctrlbrk = False
        if( logprocessor == FLUENTBIT):
            logproc = run_fluentbit(abs_scenario_path, location)
        elif( logprocessor == VECTOR):
            logproc = run_vector(abs_scenario_path, location)
        elif( logprocessor == STANZA):
            logproc = run_stanza(abs_scenario_path, location)
        elif( logprocessor == FLUENTD):
            logproc = run_fluentd(abs_scenario_path, location)
        else:
            logging.error("Unknown log processor: " + logprocessor)
            return

        if( logproc is None):
            logging.info(logprocessor + " log processor not found, skipping.")
            break

        # avoid a super quick process to be gone before we can monitor it
        pslogproc = psutil.Process(logproc.pid)
        pslogproc.suspend()

        # start monitoring
        csvresult = os.path.join(path_scenario,"results",prefix + "_result.csv")
        logging.info(f'results at: {csvresult}')

        monitor_thread = start_monitoring(str(logproc.pid), logprocessor+f" {version}", csvresult)

        # by now the monitoring should be ready
        pslogproc.resume()

        # wait till the scenario is done
        scenario.wait()

        # stop monitoring as the scenario is done
        stop_monitoring(monitor_thread)

        # kill the log processor if it is still around
        if(sys.platform == "win32"):
                os.kill(logproc.pid,CTRL_C_EVENT )
                os.kill(logproc.pid,CTRL_BREAK_EVENT)
        else:
            os.kill(logproc.pid,SIGINT)

        retries = 0
        while logproc.poll() == None and retries <3:
            logging.info("waiting for log processor process to shutdown")
            retries += 1
            time.sleep(1)

        logproc.terminate()
        logproc.wait()

        while logproc.poll() == None:
            logging.info("waiting for log processor process to terminate")
            time.sleep(1)

        # stop input, output and do cleanup
        scenario.cleanup()

        # create the charts
        chart.createcharts(csvresult, sdesc, True)

        # create the input chart
        inputdesc = scenario.get_input_description()
        if( not inputdesc is  None):
            input_csvresult = os.path.join(results_path, "input.csv")
            metric = scenario.get_input_metric()
            write_metric(metric, input_csvresult, logprocessor, prefix)
            chart.createcharts(input_csvresult, inputdesc, True)

        # create the output chart
        outputdesc = scenario.get_output_description()
        if( not outputdesc is  None):
            output_csvresult = os.path.join(results_path, "output.csv")
            metric = scenario.get_output_metric()
            write_metric(metric, output_csvresult, logprocessor, prefix)
            chart.createcharts(output_csvresult, outputdesc, True)

        # serialize the description objects as well
        # per subscenario as the subtitle may change
        pickle.dump(sdesc, open(os.path.join(results_path, prefix + "_scenario_desc.pkl"), 'wb'))
        # no prefix as these should contain all scenarios
        pickle.dump(inputdesc, open(os.path.join(results_path, "input_desc.pkl"), 'wb'))
        pickle.dump(outputdesc, open(os.path.join(results_path, "output_desc.pkl"), 'wb'))

    os.chdir(cwd)

def write_system_info(filepath):
    info={}
    info['platform']=platform.system()
    info['platform-release']=platform.release()
    info['platform-version']=platform.version()
    info['architecture']=platform.machine()
    info['processor']=platform.processor()
    info['physical_cores']=psutil.cpu_count(logical=False)
    info['total_cores']=psutil.cpu_count(logical=True)
    info['cpu_frequency_max']=f"{cpu_freq().max:.2f}Mhz"
    info['memory_ram']=str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"
    info['memory_swap']=str(round(psutil.swap_memory().total / (1024.0 **3)))+" GB"

    with open(filepath, 'w') as file:
        json_string = json.dump(info,file, indent=4)
        logging.info(f'system info json_string: {json_string}')

def write_metric(metric, csvfile, name, subset):
    data = {
                'name': [name], # name of the dataset
                'metric': [metric], # metric value
                'subset': [subset] # name of sub dataset
            }
    df = pd.DataFrame(data)
    if( os.path.exists(csvfile) ):
        df.to_csv(csvfile, sep=';', mode='a', index=False, header=None) # append to the csv
        logging.info(df.info)
    else:
        df.to_csv(csvfile, sep=';', mode='a', index=False) # append to the csv with header
        logging.info(df.info)

def main():
    # runs all the scenarios by default
    # this script assumes that local processors and https-benchmark-server are on PATH
    parser = argparse.ArgumentParser(description='Run benchmark scenarios with different log processors')

    parser.add_argument('-s', '--scenarios',
                        help='the comma separated list of scenarios to run, default is to run all', required=False,
                        type=lambda s: [item for item in s.split(',')])

    parser.add_argument('-lps', '--logprocessors',
                        help='the comma separated list of log processors to run, default is to run all (fluent-bit,vector,stanza,fluentd)', required=False,
                        type=lambda s: [{item:{}} for item in s.split(',')])

    parser.add_argument('-c', '--config',
                        help='yaml file specifying the log processors to run, default is to run all (fluent-bit,vector,stanza,fluentd). This option overrides --logprocessors', required=False)

    parser.add_argument('-f', '--logfile',type=str,
                        help='the file logger output.',
                        required=False)

    args = parser.parse_args()

    # call logger config

    log_file = args.logfile
    scenarios_type_values, agents_scenarios_values = setup_benchmark('log-processors.yaml', log_file)

    if scenarios_type_values:
        args.scenarios = scenarios_type_values
    if agents_scenarios_values:
        args.logprocessors = [{item: {}} for item in agents_scenarios_values]

    # dev test
    #args.scenarios = ['tcp_tcp','tcp_null']
    #args.logprocessors = ['fluent-bit'] #,'stanza','fluentd']
    #args.logprocessors = ['vector','stanza','fluentd']

    # Log the arguments for verification
    logging.info("Scenarios: " + str(args.scenarios))
    logging.info("Log Processors: " + str(args.logprocessors))

    run_benchmark(args.scenarios, args.logprocessors, args.config)

def run_benchmark(scenarios, logprocessors, config):
    # if config file is passed, we get the log processors from the file
    # if config file is passed, we ignore --logprocessors
    if config:
        with open(config, 'r') as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)
        logprocessors = data["agents"]

    # if config file as well as --logprocessors is not passed we run the scenarios for all log processors
    if not logprocessors:
        logprocessors = [{"fluent-bit": {}}, {"vector": {}}, {"stanza": {}}, {"fluentd": {}}]

    start_time = time.perf_counter()
    dt = datetime.now().strftime("%Y%m%d_%H%M%S")
    rootdir = 'scenarios'
    scenario_elapsed = {}
    for file in os.listdir(rootdir):
        scenario_dir = os.path.join(rootdir, file)
        if os.path.isdir(scenario_dir):
            if('_scenario_template' in scenario_dir):
                continue # always ignore the template

            if(not scenarios is None and not file in scenarios):
                continue # skip scenario

            dir_path = os.path.dirname(os.path.realpath(__file__))
            result_dir = os.path.join(dir_path, f"results/scenario_{dt}", file)
            os.makedirs(result_dir, exist_ok=True)

            # persists system information
            write_system_info(os.path.join(result_dir, "system_info.txt"))

            # check which log processors the scenario supports
            log_processors = os.listdir( os.path.join(scenario_dir, 'config') )
            scenario_start_time = time.perf_counter()
            logging.info(f'Init time {scenario_start_time}')
            # iterate through all the log processors in mentioned in the config
            for dir in logprocessors:
                processor = list(dir.keys())[0]
                version = dir[processor].get("version", "")
                location = dir[processor].get("location", "")
                logging.info(f'Versión processor: {version} - location: {location}')
                if(not processor in log_processors):
                    continue # skip log processor

                if(processor in 'fluent-bit'):
                    logging.info('Init scenario fluent-bit')
                    run_scenario(str(file),scenario_dir,FLUENTBIT,result_dir,version=version,location=location)
                    scenario_elapsed[f"{file}_{processor} {version}"] = f"{time.perf_counter()-scenario_start_time:.2f}s"
                    scenario_start_time = time.perf_counter()
                elif(processor in 'vector'):
                    logging.info('Init scenario vector')
                    run_scenario(str(file),scenario_dir,VECTOR,version=version,location=location)
                    scenario_elapsed[f"{file}_{processor} {version}"] = f"{time.perf_counter()-scenario_start_time:.2f}s"
                    scenario_start_time = time.perf_counter()
                elif(processor in 'stanza'):
                    logging.info('Init scenario stanza')
                    run_scenario(str(file),scenario_dir,STANZA,version=version,location=location)
                    scenario_elapsed[f"{file}_{processor} {version}"] = f"{time.perf_counter()-scenario_start_time:.2f}s"
                    scenario_start_time = time.perf_counter()
                elif(processor in 'fluentd'):
                    logging.info('Init scenario fluentd')
                    run_scenario(str(file),scenario_dir,FLUENTD,version=version,location=location)
                    scenario_elapsed[f"{file}_{processor} {version}"] = f"{time.perf_counter()-scenario_start_time:.2f}s"
                    scenario_start_time = time.perf_counter()

    elapsed_time = time.perf_counter() - start_time

    logging.info("\n\n--------------------------------------------------------------------------")
    logging.info("\nSUCCESSFULLY FINISHED in " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
    logging.info("\nScenario Execution Times:\n")
    logging.info(tabulate(scenario_elapsed.items(), headers=['Name', 'Elapsed Time']))

    logging.info("\n--------------------------------------------------------------------------")


if __name__ == "__main__":
    main()
