#!/usr/bin/env python3

import argparse
import psutil
from datetime import datetime
import pandas as pd
import time
import os
import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as py
import scenarios.common

chartlabels = {
    'mpc': 'Measuring Point',
    'cpu': 'CPU Usage in %',
    'disk_io': 'Disk I/O in MB',
    'mem': 'Memory Usage in MB',
    'name': 'Log Processor',
    'subset': 'Sub Scenario'
    }

def createcharts(csvfile, desc=None, export_to_disk=False):
    if(not os.path.exists(csvfile) ):
        print('File not found: ' + csvfile)
        return

    try:
        figs = []
        # read the data
        df = pd.read_csv(csvfile, sep=';')

        # plotly does not support a subtitle but html is a workaround
        title = desc.get_name()
        subtitle = desc.get_subtitle()
        prefix = desc.get_file_prefix()
        if(prefix is None):
            prefix = ''
        else:
            prefix = prefix + '_'

        if( not subtitle is None ):
            title += '<br><sup>' + subtitle + '</sup>'

        metric_unit = desc.get_metric_unit()

        if(metric_unit is None):
            # cpu
            fig = px.line(df, x='mpc', y='cpu', color = 'name',
                title='CPU Usage: ' + title,
                labels=chartlabels
            )
            figs.append(fig)
            if( export_to_disk ):
                fig.write_image(os.path.join(os.path.dirname(csvfile) , prefix+'cpu.png'))

            # disk
            fig = px.line(df, x='mpc', y='disk_io', color = 'name',
                title='Disk I/O: ' + title,
                labels=chartlabels
            )
            figs.append(fig)
            if( export_to_disk ):
                fig.write_image(os.path.join(os.path.dirname(csvfile) , prefix+'disk.png'))

            # memory
            fig = px.line(df, x='mpc', y='mem', color = 'name',
                title='Memory Usage: ' + title,
                labels=chartlabels
            )
            figs.append(fig)
            if( export_to_disk ):
                fig.write_image(os.path.join(os.path.dirname(csvfile),prefix+'memory.png'))

        else:
            # metric output
            chartlabels['metric'] = metric_unit
            fig = px.bar(df, x='subset', y='metric', color = 'name',
                title=title,
                labels=chartlabels,
                barmode="group"
            )
            figs.append(fig)
            if('input' in csvfile):
                prefix = 'input_'
            else:
                prefix = 'output_'

            if( export_to_disk ):
                fig.write_image(os.path.join(os.path.dirname(csvfile) , prefix+'metric.png'))

        return figs

    except KeyboardInterrupt:  # pragma: no cover
        pass
