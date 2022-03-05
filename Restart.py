'''
This module is to be used in conjunction with PArFlow-CLM. It is still very
much under constrcution and should NOT be fully trusted yet. It's purpose is
to restart ParFlow using the CLM restart files. 
'''

#------------------------------------------------------------------------------
# Read in impportant libraries
#------------------------------------------------------------------------------

import os
import numpy as np
import pandas as pd
from os.path import exists
from datetime import datetime


#------------------------------------------------------------------------------
# Create an object for all intents and purposes; some evil, some good 
#------------------------------------------------------------------------------

class RestartObject:
    def __init__(self, \
        start_time, end_time, \
        restart_interval = 2190, \
        restart_path = '../restart-files/', \
        parflow_path = '../pf-output/', \
        clm_path = '../clm-output/'):


        #----------------------------------------------------------------------
        # Check date datetime inputs
        #----------------------------------------------------------------------
        
        if(isinstance(start_time, str) and isinstance(end_time, str)):
            self.start = datetime.strptime(start_time, '%YYYY-MM-DD HH:MM')
            self.end = datetime.strptime(end_time, '%YYYY-MM-DD HH:MM')

        else: 
            raise RuntimeError('Starting time and ending time must be '\
            'individual strings formatted (UTC): %Y-%M-%D %H:%M')

        
        #----------------------------------------------------------------------
        # Assign restart interval
        #----------------------------------------------------------------------
        
        self.restart_interval = restart_interval


        #----------------------------------------------------------------------
        # Check path inputs
        #----------------------------------------------------------------------

        if(isinstance(restart_path, str)):
            if(exists(restart_path)):
                self.restart_path = restart_path

            else: 
                os.makedirs(restart_path)
                self.restart_path = restart_path

        else: 
            raise RuntimeError('restart_path must be a string')

        if(isinstance(parflow_path, str)):
            if(exists(parflow_path)):
                self.parflow_path = parflow_path

            else: 
                os.makedirs(parflow_path)
                self.parflow_path = parflow_path

        else: 
            raise RuntimeError('parflow_path must be a string')
        
        if(isinstance(clm_path, str)):
            if(exists(clm_path)):
                self.clm_path = clm_path

            else: 
                os.makedirs(clm_path)
                self.clm_path = clm_path

        else: 
            raise RuntimeError('clm_path must be a string')


    #--------------------------------------------------------------------------
    # Restart method: checks for log, cropies restart files, updates log etc.
    #--------------------------------------------------------------------------
    def RestartSimulations(self):

        if(exists(self.restart_path+'/clm-restart-log.csv')):
           dataframe = pd.read_csv(self.restart_path+'/clm-restart-log.csv')

        else:
            dataframe = pd.DataFrame()
            first_step = True
            wallclock = datetime.now()
            parflow_step = 0


        #----------------------------------------------------------------------
        # copy restart files for posterity
        #----------------------------------------------------------------------


