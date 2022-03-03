import datetime
import itertools
import os
from random import choice
import shutil
import socket
from socketserver import ThreadingMixIn
from string import ascii_lowercase
import subprocess
import sys
from datetime import datetime
import threading
import time
from typing import final
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3

# allow scenarios to describe the display of results
class ScenarioDescription:

    def __init__(self, name):
        self.displayname = name
        self.metric_unit = None

    def get_name(self):
        return self.displayname

    def set_subtitle(self, subtitle):
        self.subtitle = subtitle

    def get_subtitle(self):
        return self.subtitle

    def set_file_prefix(self, prefix):
        self.prefix = prefix

    def get_file_prefix(self):
        return self.prefix

    def set_metric_unit(self, unit):
        self.metric_unit = unit

    def get_metric_unit(self):
        return self.metric_unit

def start_http_benchmark_server():
    location = shutil.which("https-benchmark-server")
    httpcwd = os.path.dirname(os.path.abspath(location))
    cwd = os.getcwd()
    os.chdir(httpcwd)

    # start the server and redirect stdout to pipe
    httpserver = subprocess.Popen(["https-benchmark-server","-printmetrics=true","-printrecords=false"]
        ,stderr=subprocess.PIPE, bufsize=1,
        universal_newlines=True)

    os.chdir(cwd)
    poll = httpserver.poll()
    # process still alive?
    if poll is not None:
        sys.exit("Failed to start process: " + httpserver.cmd)
    return httpserver

# stop the benchmark server
# minruntime - defines how long it was running it seconds, that many counts are ignored as the server logs one count line per second
def stop_http_benchmark_server(httpserver, minruntime=-1):
    _ensure_http_server_alive(httpserver)
    ret = -1
    if(minruntime > -1 ):
        ret = _get_max_http_count(httpserver,minruntime)

    httpserver.terminate()
    while httpserver.poll() == None:
        print("waiting for httpserver process to terminate")
        time.sleep(1)

    return ret

def waitfor_http_benchmark_server(httpserver, expected_count, max_time):
    _ensure_http_server_alive(httpserver)
    return _wait_for_http_count(httpserver, max_time, expected_count)


def _ensure_http_server_alive(httpserver):
    poll = httpserver.poll()
    # process still alive?
    if poll is not None:
        sys.exit("Http server no longer running")

# get the http count from stderr
# minruntime - defines how many count entries have to be expected at least,
#   only then it returns (once the count remains static)
def _get_max_http_count(httpserver, minruntime):
    ret = None
    counts_found = 0
    static_result_count = 0
    while(static_result_count < 3):
        # the server prints the count to stderr
        line = httpserver.stderr.readline()
        prefix, success, result = line.partition("count:")
        if success:
            counts_found += 1
            previous = ret
            ret = int(result)
            if((counts_found > minruntime) and (ret == previous)):
                # count has not changed
                static_result_count += 1
    return ret

def _wait_for_http_count(httpserver, maxtime, expected_count):
    start_time = time.perf_counter()
    elapsed_time = 0
    lastresult = 0
    while(elapsed_time < maxtime):
        # the server prints the count to stderr
        line = httpserver.stderr.readline()
        prefix, success, result = line.partition("count:")
        elapsed_time = time.perf_counter() - start_time
        if success:
            print("count found: " + result)
            lastresult = int(result)
            if( lastresult >= expected_count):
                print("Expected count has been reached: " + result )
                return elapsed_time

    return -1

# create a data log file with a defined number of records and record length
def create_json_log(filepath, recordcount, recordbytes=10, scenario=None):
    scenario_file = None
    # do not create the input file again and again
    if(not scenario is None):
        scenario_file = os.path.join( os.path.dirname(filepath) ,scenario)
        if( os.path.exists(scenario_file) ):
            shutil.copyfile(scenario_file,filepath)
            print("Using JSON file from previous run")
            return

    print("Creating JSON log: " + filepath)

    # ensure the input data directory exists
    datadir = os.path.dirname(filepath)
    if(not os.path.exists(datadir)):
        os.mkdir(datadir)

    # delete previous file if exists
    if( os.path.exists(filepath) ):
        os.remove(filepath)

    #do this outside the loop
    data = _get_logline_random_chars(recordbytes)
    with open(filepath, 'a') as log_file:
        for counter in range(1,recordcount+1):
            logline =  create_json_logline(recordbytes, counter, data)
            log_file.write(logline)

    print("Creating JSON log - done")
    # preserve a copy for future runs
    if(not scenario is None):
        shutil.copyfile(filepath,scenario_file)

def _get_logline_random_chars(recordbytes):
    non_data_char_count = 94
    data = "".join(choice(ascii_lowercase) for i in range(recordbytes-non_data_char_count))
    return data

def create_json_logline(recordbytes , counter=0, data=None):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    counter_str = '{0:010d}'.format(counter)

    # remove static count
    if(data == None):
        data = _get_logline_random_chars(recordbytes)

    logline = '{"host":"138.84.248.84", "datetime":"'+ dt_string + '", "counter":"'+counter_str+'", "data": "' + data + '"}\n '
    return logline

# source: https://stackoverflow.com/a/68583332/5994461
THREAD_POOL = 4

# This is how to create a reusable connection pool with python requests.
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_maxsize=THREAD_POOL,
                                  max_retries=3,
                                  pool_block=True)

for prefix in "http://", "https://":
    session.mount(prefix, adapter)

def _post(url, data, content_type, reqid):
    #print(reqid)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    session.verify = False
    headers = {'Content-type': content_type}
    resp = session.post(url,data, verify=False,headers=headers);
    return resp

def send_http_requests(url,content, count, content_type="application/json"):
    start_time = time.perf_counter()
    elapsed_time = 0
    with ThreadPoolExecutor(max_workers=THREAD_POOL) as executor:
        # wrap in a list() to wait for all requests to complete
        for response in list(executor.map(_post, itertools.repeat(url), itertools.repeat(content), itertools.repeat(content_type), range(count))):
            if not response.ok:
                print("Request faild: " + str(response.status_code))
                print(response.content)
                return -1

    elapsed_time = time.perf_counter() - start_time
    return elapsed_time

def send_socket_requests(host,port,data,count):
    start_time = time.perf_counter()
    elapsed_time = 0

    response =  _send_socket(host, port, data, count)
    if response != "ok":
        print("Request faild: " + str(response))
        return -1

    elapsed_time = time.perf_counter() - start_time
    return elapsed_time

def _send_socket(host, port, data, count):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            sock.connect((host, port))
            for reqid in range(count):
               # print(reqid+1)
                sock.send(data.encode())
    except OSError as e:
        if(e.strerror is None):
            return str(e)
        return e.strerror

    return "ok"

def wait_for_port_available(host,port,maxwait):
    print("Wait for port: " + host + ":" + str(port) )
    start_time = time.perf_counter()
    elapsed_time = 0
    success = False
    while not success and elapsed_time <= maxwait:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1) # try with a timeotu of 1 sec
            result = sock.connect_ex((host, port))
            if(result == 0):
                success = True

        elapsed_time = time.perf_counter() - start_time

    if(success):
        print("Time until port found: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
    else:
        print("Could not find host:port: " + host + ":" + str(port) )

    return success

def _socket_server(port, timelimit, expected, callback):
    received_lines=0
    start_time = time.perf_counter()
    elapsed_time = 0
    max_retries = 5
    retry = 0

    #if( wait_for_port_available("localhost", port, 1) ):
    #    print("Unable to start socket server as port is still in use")
    #    callback(-1)
    #    return

    # condition check in exception handler too
    while retry <= max_retries:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5) # timeout for the accept
                #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('127.0.0.1', port))
                s.listen()
                print("Socket server accepting connections on port: " + str(port))
                conn, addr = s.accept()
                with conn:
                    while True:
                        conn.settimeout(2) # timout for the receive
                        data = conn.recv(1024)

                        if data == b'':
                            # important as the port check opens a connection
                            print("Socket connection aborted (port check, if only seen once per scenario)")
                            break

                        received_lines += data.decode().count('\n')
                        #print('received_lines: ' + str(received_lines))
                        elapsed_time = time.perf_counter() - start_time
                        if(received_lines >= expected):
                            callback(elapsed_time)
                            return
                        if(elapsed_time >= timelimit):
                            callback(-1)
                            return
        except OSError as e:
            if(e.strerror is None):
                print("Socket server creation, error: " + str(e))
            else:
                print("Socket server creation, error: " + e.strerror)
            retry += 1
            if(retry > max_retries):
                callback(-1)
                return
            else:
                print("Socket server creation, retry after 1 sec")
                time.sleep(1)

def _start_thread(func, name=None, args = []):
    thread = threading.Thread(target=func, name=name, args=args)
    thread.start()
    return thread

def start_socket_server(port, timelimit, expected, callback):
    print("Starting socket server on port: " + str(port))
    return _start_thread(_socket_server, "socket server", args=[port,timelimit, expected, callback])

def _test_callback(elapsed):
    print(str(elapsed))

if __name__ == "__main__":
    # testing
    json = create_json_logline(100)

    #socket
    thread = start_socket_server(8433,5,10, _test_callback)
    #thread2 = start_socket_server(5171,5,11, _test_callback)   # will timeout
    #print( " port is up: " + str(wait_for_port_available("localhost", 5170, 10)))
    send_socket_requests("localhost",5170, json, 10)
    #print("before")
    thread.join()
    #thread2.join()
    #print("after")

