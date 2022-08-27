#!/usr/bin/env python3
import os
import re
from time import sleep
from pprint import pprint
import yaml
import json
from yaml.loader import BaseLoader
import logging


from prometheus_client import start_http_server, Counter

APP_CONFIG = '/etc/authlog_exporter.yml'

## read yaml config
with open(APP_CONFIG,"r") as f:
    config = yaml.load(f, Loader=BaseLoader)


APP_NAME = os.path.basename(__file__)

FOLLOW_LOG_SLEEP_SEC = int(config["follow_log_sleep_sec"])
RSYSLOG_CONFIG = config["rsyslog_config"]
PORT = int(config["port"])
AUTHLOG_FILE = config["authlog_file"]
IS_DEBUG = json.loads(config["debug"].lower())

# other parameters
PROMETHEUS_LABELS = ["user"]
COUNTERS = [
            { "name": "authlog_login_successful_total",
            "description": "Number of successful logins",            
            "regex": r"\w{3} \d{2} \d{2}:\d{2}:\d{2} \w* .*pam_unix.*: session opened for user (\w*).*",
            "counter": None
            },

            { "name": "authlog_logout_total",
            "description": "Number of logouts",
            "regex": r"\w{3} \d{2} \d{2}:\d{2}:\d{2} \w* .*pam_unix.*: session closed for user (\w*).*",
            "counter": None
            },

            { "name": "authlog_login_failed_total",
            "description": "Number of failed logins",
            "regex": r"\w{3} \d{2} \d{2}:\d{2}:\d{2} \w* .*pam_unix.*: authentication failure.*user=(\w*)",
            "counter": None
            }
]

def main():    
    if IS_DEBUG:
        logging.basicConfig(level=logging.DEBUG)
    else:        
        logging.basicConfig(level=logging.ERROR)    
    if not check_logfile_format():
        print(f"This exporter works only with RSYSLOG_TraditionalFileFormat template. See $ActionFileDefaultTemplate in {RSYSLOG_CONFIG}")
        exit(1)
    start_http_server(PORT)
    gather_metrics()


def check_logfile_format():    
    """
    Check if rsync template is RSYSLOG_TraditionalFileFormat
    Line in config:
    cat /etc/rsyslog.conf | grep $ActionFileDefaultTemplate RSYSLOG_TraditionalFileFormat
    """
    is_traditional = False
    with open(RSYSLOG_CONFIG, 'r') as f:
        regex = r'\s*\$ActionFileDefaultTemplate\s*RSYSLOG_TraditionalFileFormat\s*'
        for line in f.readlines():
            match = re.match(regex, line)
            if match:
                is_traditional = True
                break;    
    return is_traditional   


def gather_metrics():
    """
    Parse metrics and update Prometheus counters
    """    
    logging.debug( f"collecting auth metrics run" ) 
    # create Prometheus counters
    for c in COUNTERS:
        c["counter"] = Counter(c["name"], c["description"], PROMETHEUS_LABELS)

    # parse log and update counters
    for line in follow_log(AUTHLOG_FILE):
        for c in COUNTERS:
            match = re.match(c["regex"], line)
            if match:                
                user = match.group(1)                              
                logging.debug( f"parse matched: {c.get('counter')} user: { user }" )
                c["counter"].labels(user=user).inc()   


def follow_log(file):    
    """
    retrieve lines loop
    """
    with open(file, 'r') as f:
        f.seek(0, os.SEEK_END)        
        while True:      
            logging.debug('log reading loop')            
            line = f.readline()
            if not line:
                sleep(FOLLOW_LOG_SLEEP_SEC)
                continue
            yield line


if __name__ == '__main__':
    main()
