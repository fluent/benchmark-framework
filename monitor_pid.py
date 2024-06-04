#!/usr/bin/env python3

import argparse
import logging

import psutil
from datetime import datetime
import pandas as pd
import time
import os
import platform


# need to keep global references to get cpu percent
_subprocesses = {}

def main():
    parser = argparse.ArgumentParser(description='Record performance information about a given process ID (pid)')

    parser.add_argument('pid', type=str,
                        help='the process id')
    
    parser.add_argument('name', type=str,
                        help='name of the dataset')

    parser.add_argument('csvfile', type=str,
                        help='path to the csv output')    

    args = parser.parse_args()

    monitor(pid=args.pid, name=args.name, csvfile=args.csvfile)



def monitor(pid, name, csvfile="monitor_output.csv", callback=None, interval="0.5", withchildren=True):
    logging.info("Output file: " + csvfile)
    logging.info("Monitoring PID: " + pid)
    proc = psutil.Process(int(pid))
    logging.info("Found process with pid: " + pid)
    
    df = None
    csvexists = False
    if os.path.exists(csvfile):
        csvexists = True
        
    count = 0

    try:

        # Start main event loop
        while True:
            # do the callback here to still allo run without callback
            if(not callback is None):
                if(callback()):
                    break

            # Find current time
            now = datetime.now()

            try:
                proc_status = proc.status()
            except psutil.NoSuchProcess:  # pragma: no cover
                break

            # process still alive?
            if proc_status in [psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD]:
                print("Process has already finished")
                break
                        
            count+=1

            # get metrics
            cpu = _get_cpu(proc, withchildren)
            rss = _get_mem_rss(proc, withchildren)
            vms = _get_mem_vms(proc, withchildren)
            if platform.system() != "Darwin":
                ioread = _get_io_read(proc, withchildren)
                iowrite = _get_io_write(proc, withchildren)
            else:
                ioread = 0
                iowrite = 0
            # we will report the main pid but sum all child process information if requested
            data = {
                'pid': [pid],
                'name': [name], # name of the dataset
                'mpc': [count], # count of measuring point
                'cpu': [cpu], # in % , 1.0 = 100% 
                'mem': [rss / 1024 ** 2  + vms / 1024 ** 2], # total, in MB                
                'rss_mem': [rss / 1024 ** 2], # in MB
                'virt_mem': [vms / 1024 ** 2], # in MB                
                'disk_io': [(ioread + iowrite)/ 1024 ** 2 ], # read_bytes + write_bytes in mb
                'disk_read': [ioread / 1024 ** 2 ], # read_bytes + write_bytes , in mb
                'disk_write': [iowrite / 1024 ** 2] # read_bytes + write_bytes, in mb
            }

            newdf = pd.DataFrame(data)
         
            if( csvexists ):
                newdf.to_csv(csvfile, sep=';', mode='a', index=False, header=None) # append to the csv
            else:
                newdf.to_csv(csvfile, sep=';', mode='a', index=False) # append to the csv with header
                csvexists =True

            if interval is not None:
                sleeptime=float(interval)
                time.sleep(sleeptime)

    except KeyboardInterrupt:  # pragma: no cover
        pass


def _get_cpu(proc, withchildren):
    ret = proc.cpu_percent()    
    if(withchildren):
        for child in proc.children(recursive=True):
            try:
                pid = child.pid
                cp =_subprocesses.get(pid)
                if(cp is None):
                    _subprocesses[pid] = child
                    cp = child
                child_cpu = cp.cpu_percent()                
                ret += child_cpu
            except psutil.NoSuchProcess:
                print("Child process no longer exists")
    return ret

def _get_mem_rss(proc, withchildren):
    ret = proc.memory_info().rss
    if(withchildren):
        for child in proc.children(recursive=True):
            try:
                ret += child.memory_info().rss
            except psutil.NoSuchProcess:
                print("Child process no longer exists")
    return ret

def _get_mem_vms(proc, withchildren):
    ret = proc.memory_info().vms
    if(withchildren):
        for child in proc.children(recursive=True):
            try:
                ret += child.memory_info().vms
            except psutil.NoSuchProcess:
                print("Child process no longer exists")
    return ret

def _get_io_read(proc, withchildren):
    ret = proc.io_counters().read_bytes
    if(withchildren):
        for child in proc.children(recursive=True):
            try:
                ret += child.io_counters().read_bytes
            except psutil.NoSuchProcess:
                print("Child process no longer exists")
    return ret

def _get_io_write(proc, withchildren):
    ret = proc.io_counters().write_bytes
    if(withchildren):
        for child in proc.children(recursive=True):
            try:
                ret += child.io_counters().write_bytes
            except psutil.NoSuchProcess:
                print("Child process no longer exists")
    return ret

if __name__ == "__main__":
    main()