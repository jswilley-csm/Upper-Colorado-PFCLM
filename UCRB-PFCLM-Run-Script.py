'''
PF-CLM run script

Upper Colorado River Basin

Note to modelers:
This is a python-wrapped version of the PF-CLM run script for the Upper Colorado River
Basin Model. This model represents a subdomain of the CONUS 2.0 PF-CLM model. The default
inputs are clipped from CONUS 2.0 inputs – see CONUS 2.0 documentation for the methods
used in their development. An aside, you will an initial condition file and meteorological
forcing data; neither has a default. To access the original set of input parameters, login 
to Verde and navigate to: /hydrodata/PFCLM/UCRB_Baseline. If you are not a group member, 
reach out and have one of us share the files with you – we'd be happy to. On Verde, make 
sure you have the original files by confirming they are dated as follows:

         hydrodata  41M Feb 28 09:57 UCRB.final.drv_vegm.dat
         hydrodata 4.2M Feb 28 09:57 UCRB.final.mannings.pfb
         hydrodata  42M Feb 28 09:57 UCRB.final.subsurface.pfb
         hydrodata  42M Feb 28 09:57 UCRB.final.flow_barrier.pfb
         hydrodata 4.2M Feb 28 09:57 UCRB.final.slope_y.pfb
         hydrodata 4.2M Feb 28 09:57 UCRB.final.slope_x.pfb
         hydrodata 4.2M Feb 28 09:57 UCRB.final.landcover_IGBP.pfb
         hydrodata 4.3K Feb 28 09:57 UCRB.final.drv_vegp.dat
         hydrodata 9.4K Feb 28 09:57 UCRB.final.drv_clmin.dat
         hydrodata 876K Feb 28 09:57 UCRB.final.domain.pfsol
         
Recommended directory structure:
    UCRB-run-001         <- parent directory to hold all files for documentation
        scripts          <- holds this script and others, i.e. your job script
        inputs           <- to hold your official UCRB run inputs
        pf-output        <- to hold pressure files and other values you choose to print
        clm-output       <- to hold CLM output files
        restart-files    <- to contain copies of CLM restart files and last pressure files
        forcing          <- forcing parent directory to hold meteorological inputs
            YYYY         <- if running multiple years, add subfolders with years as names
            YYYY
            ...

Things you should change:
    1.) the start and stop times - you won't finish in 8760 timesteps 12 hours; try 2000
    2.) the initial pressure file - use the last pressure file from your spinup
    3.) the clm driver file's start time based on the forcing you give it
    4.) probably the run name, your call though
    5.) which parameters you want printed - check the solvers settings at the bottom
    
Differences from CONUS 2.0:
    1.) the extent
    2.) boundary conditions - CONUS has several, UCRB only has no-flow and overland-flow
            patches: top, bottom, land
    3.) initialization - unless you clip the CONUS 2.0 initial pressure and use that
    4.) the number of processors required

Version history:
Jackson Swilley | Jan 30, 2022 | js2834@princeton.edu or jackson.swilley5@gmail.com 
    Comment: original transcription
    
Jackson Swilley | Feb 12, 2022 | js2834@princeton.edu or jackson.swilley5@gmail.com 
    Comment: adding clipped CONUS 2.0 inputs

Jackson Swilley | Feb 21, 2022 | js2834@princeton.edu or jackson.swilley5@gmail.com 
    Comment: final inputs - now runs
    
Jackson Swilley | Feb 28, 2022 | js2834@princeton.edu or jackson.swilley5@gmail.com 
    Comment: updating documentation
    
Jackson Swilley | Feb 28, 2022 | js2834@princeton.edu or jackson.swilley5@gmail.com 
    Comment: same day - new update, adding the G.D. flow barrier (should have earlier)
'''


#-----------------------------------------------------------------------------------------
# Import libraries
#-----------------------------------------------------------------------------------------

import sys
import os
import numpy as np
from datetime import datetime
from parflow.tools import Run
from parflow.tools.fs import mkdir, cp, get_absolute_path, exists
from parflow.tools.settings import set_working_directory
import shutil


#-----------------------------------------------------------------------------------------
# User-defined local variables
#-----------------------------------------------------------------------------------------

run_name               = 'UCRB-run-001'

script_path            = get_absolute_path('.') + '/'
input_path             = '../inputs/'
forcing_path           = '../forcing'
clm_output_path        = '../clm-output/'
pf_output_path         = '../pf-output/'
restart_output_path    = '../restart-files/'

pf_run_file            = 'UCRB-PFCLM-Run-Script.py'
domain_file            = 'UCRB.final.domain.pfsol'  
mannings_file          = 'UCRB.final.mannings.pfb'
subsurface_file        = 'UCRB.final.subsurface.pfb'
slope_x_file           = 'UCRB.final.slope_x.pfb'
slope_y_file           = 'UCRB.final.slope_y.pfb'
flow_barrier_file      = 'UCRB.final.flow_barrier.pfb'
initial_file           = 'UCRB-run-001.initial_press.pfb'

start_time             = 0
stop_time              = 8760


#-----------------------------------------------------------------------------------------
# Create ParFlow run object 'model'
#-----------------------------------------------------------------------------------------

model = Run(run_name, __file__)
model.FileVersion = 4


#-----------------------------------------------------------------------------------------
# Setting up directories for run
#-----------------------------------------------------------------------------------------

set_working_directory( pf_output_path )

cp( input_path + domain_file )
cp( input_path + subsurface_file )
cp( input_path + flow_barrier_file )
cp( input_path + slope_x_file )
cp( input_path + slope_y_file )
cp( input_path + initial_file )
cp( input_path + mannings_file )
cp( script_path + pf_run_file )


#-----------------------------------------------------------------------------------------
# Setup timing info
#-----------------------------------------------------------------------------------------

istep      = start_time
clmstep    = start_time

model.TimingInfo.BaseUnit        = 1.0
model.TimingInfo.DumpInterval    = 1.0
model.TimingInfo.StartCount      = start_time
model.TimingInfo.StartTime       = start_time
model.TimingInfo.StopTime        = stop_time

model.TimeStep.Type     = 'Constant'
model.TimeStep.Value    =  1.0


#-----------------------------------------------------------------------------------------
# Set processor topology
#-----------------------------------------------------------------------------------------

model.Process.Topology.P    = 16
model.Process.Topology.Q    = 16
model.Process.Topology.R    = 1

nproc = model.Process.Topology.P * model.Process.Topology.Q * model.Process.Topology.R


#-----------------------------------------------------------------------------------------
# Computational grid
#-----------------------------------------------------------------------------------------

model.ComputationalGrid.Lower.X    = 0.0
model.ComputationalGrid.Lower.Y    = 0.0
model.ComputationalGrid.Lower.Z    = 0.0

model.ComputationalGrid.NX    = 608
model.ComputationalGrid.NY    = 896
model.ComputationalGrid.NZ    = 10   

model.ComputationalGrid.DX    = 1000.0
model.ComputationalGrid.DY    = 1000.0
model.ComputationalGrid.DZ    = 200.0


#-----------------------------------------------------------------------------------------
# Name GeomInputs
#-----------------------------------------------------------------------------------------

model.Domain.GeomName                    = 'domain'
model.GeomInput.Names                    = 'domaininput indi_input'
model.GeomInput.domaininput.InputType    = 'SolidFile'
model.GeomInput.domaininput.GeomNames    = 'domain'
model.GeomInput.domaininput.FileName     = domain_file
model.Geom.domain.Patches                = 'top bottom land'


#-----------------------------------------------------------------------------------------
# Indicator Geometry Input
#-----------------------------------------------------------------------------------------

model.GeomInput.indi_input.InputType    = 'IndicatorField'
model.GeomInput.indi_input.GeomNames    = 's1 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 s12 s13 g1 g2 g3 g4 g5 g6 g7 g8 b1 b2'
model.Geom.indi_input.FileName          = subsurface_file
model.dist(subsurface_file)

model.GeomInput.s1.Value     = 1
model.GeomInput.s2.Value     = 2
model.GeomInput.s3.Value     = 3
model.GeomInput.s4.Value     = 4
model.GeomInput.s5.Value     = 5
model.GeomInput.s6.Value     = 6
model.GeomInput.s7.Value     = 7
model.GeomInput.s8.Value     = 8
model.GeomInput.s9.Value     = 9
model.GeomInput.s10.Value    = 10
model.GeomInput.s11.Value    = 11
model.GeomInput.s12.Value    = 12
model.GeomInput.s13.Value    = 13
model.GeomInput.g1.Value     = 21
model.GeomInput.g2.Value     = 22
model.GeomInput.g3.Value     = 23
model.GeomInput.g4.Value     = 24
model.GeomInput.g5.Value     = 25
model.GeomInput.g6.Value     = 26
model.GeomInput.g7.Value     = 27
model.GeomInput.g8.Value     = 28
model.GeomInput.b1.Value     = 19
model.GeomInput.b2.Value     = 20


#-----------------------------------------------------------------------------------------
# variable dz assignments
#-----------------------------------------------------------------------------------------

model.Solver.Nonlinear.VariableDz    = True 
model.dzScale.GeomNames              = 'domain'
model.dzScale.Type                   = 'nzList'
model.dzScale.nzListNumber           = 10

model.Cell._0.dzScale.Value    = 1.0
model.Cell._1.dzScale.Value    = 0.5
model.Cell._2.dzScale.Value    = 0.25
model.Cell._3.dzScale.Value    = 0.125
model.Cell._4.dzScale.Value    = 0.050
model.Cell._5.dzScale.Value    = 0.025
model.Cell._6.dzScale.Value    = 0.005
model.Cell._7.dzScale.Value    = 0.003
model.Cell._8.dzScale.Value    = 0.0015
model.Cell._9.dzScale.Value    = 0.0005


#-----------------------------------------------------------------------------------------
# Permeability (values in m/hr)
#-----------------------------------------------------------------------------------------

model.Geom.Perm.Names           = 'domain s1 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 s12 s13 g1 g2 g3 g4 g5 g6 g7 g8 b1 b2'

model.Geom.domain.Perm.Type     = 'Constant'
model.Geom.domain.Perm.Value    = 0.02

model.Geom.s1.Perm.Type         = 'Constant'
model.Geom.s1.Perm.Value        = 0.269022595

model.Geom.s2.Perm.Type         = 'Constant'
model.Geom.s2.Perm.Value        = 0.043630356

model.Geom.s3.Perm.Type         = 'Constant'
model.Geom.s3.Perm.Value        = 0.015841225

model.Geom.s4.Perm.Type         = 'Constant'
model.Geom.s4.Perm.Value        = 0.007582087

model.Geom.s5.Perm.Type         = 'Constant'
model.Geom.s5.Perm.Value        = 0.01818816

model.Geom.s6.Perm.Type         = 'Constant'
model.Geom.s6.Perm.Value        = 0.005009435

model.Geom.s7.Perm.Type         = 'Constant'
model.Geom.s7.Perm.Value        = 0.005492736

model.Geom.s8.Perm.Type         = 'Constant'
model.Geom.s8.Perm.Value        = 0.004675077

model.Geom.s9.Perm.Type         = 'Constant'
model.Geom.s9.Perm.Value        = 0.003386794

model.Geom.s10.Perm.Type        = 'Constant'
model.Geom.s10.Perm.Value       = 0.004783973

model.Geom.s11.Perm.Type        = 'Constant'
model.Geom.s11.Perm.Value       = 0.003979136

model.Geom.s12.Perm.Type        = 'Constant'
model.Geom.s12.Perm.Value       = 0.006162952

model.Geom.s13.Perm.Type        = 'Constant'
model.Geom.s13.Perm.Value       = 0.005009435

model.Geom.b1.Perm.Type         = 'Constant'
model.Geom.b1.Perm.Value        = 0.005

model.Geom.b2.Perm.Type         = 'Constant'
model.Geom.b2.Perm.Value        = 0.01

model.Geom.g1.Perm.Type         = 'Constant'
model.Geom.g1.Perm.Value        = 0.02

model.Geom.g2.Perm.Type         = 'Constant'
model.Geom.g2.Perm.Value        = 0.03

model.Geom.g3.Perm.Type         = 'Constant'
model.Geom.g3.Perm.Value        = 0.04

model.Geom.g4.Perm.Type         = 'Constant'
model.Geom.g4.Perm.Value        = 0.05

model.Geom.g5.Perm.Type         = 'Constant'
model.Geom.g5.Perm.Value        = 0.06

model.Geom.g6.Perm.Type         = 'Constant'
model.Geom.g6.Perm.Value        = 0.08

model.Geom.g7.Perm.Type         = 'Constant'
model.Geom.g7.Perm.Value        = 0.1

model.Geom.g8.Perm.Type         = 'Constant'
model.Geom.g8.Perm.Value        = 0.2


#-----------------------------------------------------------------------------------------
# Permeability tensor
#-----------------------------------------------------------------------------------------

model.Perm.TensorType                 = 'TensorByGeom'
model.Geom.Perm.TensorByGeom.Names    = 'domain b1 b2 g1 g2 g4 g5 g6 g7'

model.Geom.domain.Perm.TensorValX     = 1.0
model.Geom.domain.Perm.TensorValY     = 1.0
model.Geom.domain.Perm.TensorValZ     = 1.0

model.Geom.b1.Perm.TensorValX         = 1.0
model.Geom.b1.Perm.TensorValY         = 1.0
model.Geom.b1.Perm.TensorValZ         = 0.1

model.Geom.b2.Perm.TensorValX         = 1.0
model.Geom.b2.Perm.TensorValY         = 1.0
model.Geom.b2.Perm.TensorValZ         = 0.1

model.Geom.g1.Perm.TensorValX         = 1.0
model.Geom.g1.Perm.TensorValY         = 1.0
model.Geom.g1.Perm.TensorValZ         = 0.1

model.Geom.g2.Perm.TensorValX         = 1.0
model.Geom.g2.Perm.TensorValY         = 1.0
model.Geom.g2.Perm.TensorValZ         = 0.1

model.Geom.g4.Perm.TensorValX         = 1.0
model.Geom.g4.Perm.TensorValY         = 1.0
model.Geom.g4.Perm.TensorValZ         = 0.1

model.Geom.g5.Perm.TensorValX         = 1.0
model.Geom.g5.Perm.TensorValY         = 1.0
model.Geom.g5.Perm.TensorValZ         = 0.1

model.Geom.g6.Perm.TensorValX         = 1.0
model.Geom.g6.Perm.TensorValY         = 1.0
model.Geom.g6.Perm.TensorValZ         = 0.1

model.Geom.g7.Perm.TensorValX         = 1.0
model.Geom.g7.Perm.TensorValY         = 1.0
model.Geom.g7.Perm.TensorValZ         = 0.1


#-----------------------------------------------------------------------------------------
# Vertical flow Barrier
#-----------------------------------------------------------------------------------------

model.Solver.Nonlinear.FlowBarrierZ    = True
model.FBz.Type                         = 'PFBFile'
model.Geom.domain.FBz.FileName         = flow_barrier_file
model.dist(flow_barrier_file)


#-----------------------------------------------------------------------------------------
# Porosity
#-----------------------------------------------------------------------------------------

model.Geom.Porosity.GeomNames       = "domain s1 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 s12 s13 g1 g2 g3 g4 g5 g6 g7 g8"

model.Geom.domain.Porosity.Type     = 'Constant'
model.Geom.domain.Porosity.Value    = 0.33

model.Geom.s1.Porosity.Type         = 'Constant'
model.Geom.s1.Porosity.Value        = 0.375

model.Geom.s2.Porosity.Type         = 'Constant'
model.Geom.s2.Porosity.Value        = 0.39

model.Geom.s3.Porosity.Type         = 'Constant'
model.Geom.s3.Porosity.Value        = 0.387

model.Geom.s4.Porosity.Type         = 'Constant'
model.Geom.s4.Porosity.Value        = 0.439

model.Geom.s5.Porosity.Type         = 'Constant'
model.Geom.s5.Porosity.Value        = 0.489

model.Geom.s6.Porosity.Type         = 'Constant'
model.Geom.s6.Porosity.Value        = 0.399

model.Geom.s7.Porosity.Type         = 'Constant'
model.Geom.s7.Porosity.Value        = 0.384

model.Geom.s8.Porosity.Type         = 'Constant'
model.Geom.s8.Porosity.Value        = 0.482

model.Geom.s9.Porosity.Type         = 'Constant'
model.Geom.s9.Porosity.Value        = 0.442

model.Geom.s10.Porosity.Type        = 'Constant'
model.Geom.s10.Porosity.Value       = 0.385

model.Geom.s11.Porosity.Type        = 'Constant'
model.Geom.s11.Porosity.Value       = 0.481

model.Geom.s12.Porosity.Type        = 'Constant'
model.Geom.s12.Porosity.Value       = 0.459

model.Geom.s13.Porosity.Type        = 'Constant'
model.Geom.s13.Porosity.Value       = 0.399

model.Geom.g1.Porosity.Type         = 'Constant'
model.Geom.g1.Porosity.Value        = 0.33

model.Geom.g2.Porosity.Type         = 'Constant'
model.Geom.g2.Porosity.Value        = 0.33

model.Geom.g3.Porosity.Type         = 'Constant'
model.Geom.g3.Porosity.Value        = 0.33

model.Geom.g4.Porosity.Type         = 'Constant'
model.Geom.g4.Porosity.Value        = 0.33

model.Geom.g5.Porosity.Type         = 'Constant'
model.Geom.g5.Porosity.Value        =  0.33

model.Geom.g6.Porosity.Type         = 'Constant'
model.Geom.g6.Porosity.Value        = 0.33

model.Geom.g7.Porosity.Type         = 'Constant'
model.Geom.g7.Porosity.Value        = 0.33

model.Geom.g8.Porosity.Type         = 'Constant'
model.Geom.g8.Porosity.Value        = 0.33


#-----------------------------------------------------------------------------------------
# Relative permeability
#-----------------------------------------------------------------------------------------

model.Phase.RelPerm.Type         = 'VanGenuchten'
model.Phase.RelPerm.GeomNames    = "domain s1 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 s12 s13"

model.Geom.domain.RelPerm.Alpha                  = 0.5
model.Geom.domain.RelPerm.N                      = 2.5
model.Geom.domain.RelPerm.NumSamplePoints        = 20000
model.Geom.domain.RelPerm.MinPressureHead        = -300
model.Geom.domain.RelPerm.InterpolationMethod    = 'Linear'

model.Geom.s1.RelPerm.Alpha                      = 3.548
model.Geom.s1.RelPerm.N                          = 4.162
model.Geom.s1.RelPerm.NumSamplePoints            = 20000
model.Geom.s1.RelPerm.MinPressureHead            = -300
model.Geom.s1.RelPerm.InterpolationMethod        = 'Linear'

model.Geom.s2.RelPerm.Alpha                      = 3.467
model.Geom.s2.RelPerm.N                          = 2.738
model.Geom.s2.RelPerm.NumSamplePoints            = 20000
model.Geom.s2.RelPerm.MinPressureHead            = -300
model.Geom.s2.RelPerm.InterpolationMethod        = 'Linear'

model.Geom.s3.RelPerm.Alpha                      = 2.692
model.Geom.s3.RelPerm.N                          = 2.445
model.Geom.s3.RelPerm.NumSamplePoints            = 20000
model.Geom.s3.RelPerm.MinPressureHead            = -300
model.Geom.s3.RelPerm.InterpolationMethod        = 'Linear'

model.Geom.s4.RelPerm.Alpha                      = 0.501
model.Geom.s4.RelPerm.N                          = 2.659
model.Geom.s4.RelPerm.NumSamplePoints            = 20000
model.Geom.s4.RelPerm.MinPressureHead            = -300
model.Geom.s4.RelPerm.InterpolationMethod        = 'Linear'

model.Geom.s5.RelPerm.Alpha                      = 0.661
model.Geom.s5.RelPerm.N                          = 2.659
model.Geom.s5.RelPerm.NumSamplePoints            = 20000
model.Geom.s5.RelPerm.MinPressureHead            = -300
model.Geom.s5.RelPerm.InterpolationMethod        = 'Linear'

model.Geom.s6.RelPerm.Alpha                      = 1.122
model.Geom.s6.RelPerm.N                          = 2.479
model.Geom.s6.RelPerm.NumSamplePoints            = 20000
model.Geom.s6.RelPerm.MinPressureHead            = -300
model.Geom.s6.RelPerm.InterpolationMethod        = 'Linear'

model.Geom.s7.RelPerm.Alpha                      = 2.089
model.Geom.s7.RelPerm.N                          = 2.318
model.Geom.s7.RelPerm.NumSamplePoints            = 20000
model.Geom.s7.RelPerm.MinPressureHead            = -300
model.Geom.s7.RelPerm.InterpolationMethod        = 'Linear'

model.Geom.s8.RelPerm.Alpha                      = 0.832
model.Geom.s8.RelPerm.N                          = 2.514
model.Geom.s8.RelPerm.NumSamplePoints            = 20000
model.Geom.s8.RelPerm.MinPressureHead            = -300
model.Geom.s8.RelPerm.InterpolationMethod        = 'Linear'

model.Geom.s9.RelPerm.Alpha                      = 1.585
model.Geom.s9.RelPerm.N                          = 2.413
model.Geom.s9.RelPerm.NumSamplePoints            = 20000
model.Geom.s9.RelPerm.MinPressureHead            = -300
model.Geom.s9.RelPerm.InterpolationMethod        = 'Linear'

model.Geom.s10.RelPerm.Alpha                     = 3.311
model.Geom.s10.RelPerm.N                         = 2.202
model.Geom.s10.RelPerm.NumSamplePoints           = 20000
model.Geom.s10.RelPerm.MinPressureHead           = -300
model.Geom.s10.RelPerm.InterpolationMethod       = 'Linear'

model.Geom.s11.RelPerm.Alpha                     = 1.622
model.Geom.s11.RelPerm.N                         = 2.318
model.Geom.s11.RelPerm.NumSamplePoints           = 20000
model.Geom.s11.RelPerm.MinPressureHead           = -300
model.Geom.s11.RelPerm.InterpolationMethod       = 'Linear'

model.Geom.s12.RelPerm.Alpha                     = 1.514
model.Geom.s12.RelPerm.N                         = 2.259
model.Geom.s12.RelPerm.NumSamplePoints           = 20000
model.Geom.s12.RelPerm.MinPressureHead           = -300
model.Geom.s12.RelPerm.InterpolationMethod       = 'Linear'

model.Geom.s13.RelPerm.Alpha                     = 1.122
model.Geom.s13.RelPerm.N                         = 2.479
model.Geom.s13.RelPerm.NumSamplePoints           = 20000
model.Geom.s13.RelPerm.MinPressureHead           = -300
model.Geom.s13.RelPerm.InterpolationMethod       = 'Linear'


#-----------------------------------------------------------------------------------------
# Saturation
#-----------------------------------------------------------------------------------------

model.Phase.Saturation.Type           = 'VanGenuchten'
model.Phase.Saturation.GeomNames      = 'domain s1 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 s12 s13'

model.Geom.domain.Saturation.Alpha    = 0.5
model.Geom.domain.Saturation.N        = 2.5
model.Geom.domain.Saturation.SRes     = 0.00001
model.Geom.domain.Saturation.SSat     = 1.0

model.Geom.s1.Saturation.Alpha        = 3.548
model.Geom.s1.Saturation.N            = 4.162
model.Geom.s1.Saturation.SRes         = 0.0001
model.Geom.s1.Saturation.SSat         = 1.0

model.Geom.s2.Saturation.Alpha        = 3.467
model.Geom.s2.Saturation.N            = 2.738
model.Geom.s2.Saturation.SRes         = 0.0001
model.Geom.s2.Saturation.SSat         = 1.0

model.Geom.s3.Saturation.Alpha        = 2.692
model.Geom.s3.Saturation.N            = 2.445
model.Geom.s3.Saturation.SRes         = 0.0001
model.Geom.s3.Saturation.SSat         = 1.0

model.Geom.s4.Saturation.Alpha        = 0.501
model.Geom.s4.Saturation.N            = 2.659
model.Geom.s4.Saturation.SRes         = 0.1
model.Geom.s4.Saturation.SSat         = 1.0

model.Geom.s5.Saturation.Alpha        = 0.661
model.Geom.s5.Saturation.N            = 2.659
model.Geom.s5.Saturation.SRes         = 0.0001
model.Geom.s5.Saturation.SSat         = 1.0

model.Geom.s6.Saturation.Alpha        = 1.122
model.Geom.s6.Saturation.N            = 2.479
model.Geom.s6.Saturation.SRes         = 0.0001
model.Geom.s6.Saturation.SSat         = 1.0

model.Geom.s7.Saturation.Alpha        = 2.089
model.Geom.s7.Saturation.N            = 2.318
model.Geom.s7.Saturation.SRes         = 0.0001
model.Geom.s7.Saturation.SSat         = 1.0

model.Geom.s8.Saturation.Alpha        = 0.832
model.Geom.s8.Saturation.N            = 2.514
model.Geom.s8.Saturation.SRes         = 0.0001
model.Geom.s8.Saturation.SSat         = 1.0

model.Geom.s9.Saturation.Alpha        = 1.585
model.Geom.s9.Saturation.N            = 2.413
model.Geom.s9.Saturation.SRes         = 0.0001
model.Geom.s9.Saturation.SSat         = 1.0

model.Geom.s10.Saturation.Alpha       = 3.311
model.Geom.s10.Saturation.N           = 2.202
model.Geom.s10.Saturation.SRes        = 0.0001
model.Geom.s10.Saturation.SSat        = 1.0

model.Geom.s11.Saturation.Alpha       = 1.622
model.Geom.s11.Saturation.N           = 2.318
model.Geom.s11.Saturation.SRes        = 0.0001
model.Geom.s11.Saturation.SSat        = 1.0

model.Geom.s12.Saturation.Alpha       = 1.514
model.Geom.s12.Saturation.N           = 2.259
model.Geom.s12.Saturation.SRes        = 0.0001
model.Geom.s12.Saturation.SSat        = 1.0

model.Geom.s13.Saturation.Alpha       = 1.122
model.Geom.s13.Saturation.N           = 2.479
model.Geom.s13.Saturation.SRes        = 0.0001
model.Geom.s13.Saturation.SSat        = 1.0


#-----------------------------------------------------------------------------------------
# Specific Storage
#-----------------------------------------------------------------------------------------

model.SpecificStorage.Type                 = 'Constant'
model.SpecificStorage.GeomNames            = 'domain'
model.Geom.domain.SpecificStorage.Value    = 1.0e-4


#-----------------------------------------------------------------------------------------
# Manning's roughness
#-----------------------------------------------------------------------------------------

model.Mannings.Type        = 'PFBFile'
model.Mannings.FileName    = mannings_file
model.dist(mannings_file)


#-----------------------------------------------------------------------------------------
# Phases
#-----------------------------------------------------------------------------------------

model.Phase.Names                    = 'water'

model.Phase.water.Density.Type       = 'Constant'
model.Phase.water.Density.Value      = 1.0

model.Phase.water.Viscosity.Type     = 'Constant'
model.Phase.water.Viscosity.Value    = 1.0


#-----------------------------------------------------------------------------------------
# Phase sources:
#-----------------------------------------------------------------------------------------

model.PhaseSources.water.Type                 = 'Constant'
model.PhaseSources.water.GeomNames            = 'domain'
model.PhaseSources.water.Geom.domain.Value    = 0.0


#-----------------------------------------------------------------------------------------
# Contaminants
#-----------------------------------------------------------------------------------------

model.Contaminants.Names    = ''


#-----------------------------------------------------------------------------------------
# Retardation
#-----------------------------------------------------------------------------------------

model.Geom.Retardation.GeomNames    = ''


#-----------------------------------------------------------------------------------------
# Gravity
#-----------------------------------------------------------------------------------------

model.Gravity    = 1.0


#-----------------------------------------------------------------------------------------
# Mobility
#-----------------------------------------------------------------------------------------

model.Phase.water.Mobility.Type     = 'Constant'
model.Phase.water.Mobility.Value    = 1.0


#-----------------------------------------------------------------------------------------
# Wells
#-----------------------------------------------------------------------------------------

model.Wells.Names    = ''


#-----------------------------------------------------------------------------------------
# Time Cycles
#-----------------------------------------------------------------------------------------

model.Cycle.Names                      = 'constant'
model.Cycle.constant.Names             = 'alltime'
model.Cycle.constant.alltime.Length    = 10000000
model.Cycle.constant.Repeat            = -1


#-----------------------------------------------------------------------------------------
# Boundary Conditions: Pressure
#-----------------------------------------------------------------------------------------

model.BCPressure.PatchNames                    = 'top bottom land'

model.Patch.top.BCPressure.Type                = 'OverlandFlow'
model.Patch.top.BCPressure.Cycle               = 'constant'
model.Patch.top.BCPressure.alltime.Value       = 0.0

model.Patch.bottom.BCPressure.Type             = 'FluxConst'
model.Patch.bottom.BCPressure.Cycle            = 'constant'
model.Patch.bottom.BCPressure.alltime.Value    = 0.0

model.Patch.land.BCPressure.Type               = 'FluxConst'
model.Patch.land.BCPressure.Cycle              = 'constant'
model.Patch.land.BCPressure.alltime.Value      = 0.0


#-----------------------------------------------------------------------------------------
# Topo slopes in x-direction
#-----------------------------------------------------------------------------------------

model.TopoSlopesX.Type         = 'PFBFile'
model.TopoSlopesX.GeomNames    = 'domain'
model.TopoSlopesX.FileName     = slope_x_file
model.dist(slope_x_file)


#-----------------------------------------------------------------------------------------
# Topo slopes in y-direction
#-----------------------------------------------------------------------------------------

model.TopoSlopesY.Type         = 'PFBFile'
model.TopoSlopesY.GeomNames    = 'domain'
model.TopoSlopesY.FileName     = slope_y_file
model.dist(slope_y_file)


#-----------------------------------------------------------------------------------------
# Initial conditions: pressure head
#-----------------------------------------------------------------------------------------

model.Geom.domain.ICPressure.RefGeom     = 'domain'
model.Geom.domain.ICPressure.RefPatch    = 'bottom'

model.ICPressure.Type                    = 'PFBFile'
model.ICPressure.GeomNames               = 'domain'
model.Geom.domain.ICPressure.FileName    = initial_file
model.dist(initial_file)


#-----------------------------------------------------------------------------------------
# Exact solution specification for error calculations
#-----------------------------------------------------------------------------------------

model.KnownSolution    = 'NoKnownSolution'


#-----------------------------------------------------------------------------------------
# Set LSM parameters
#-----------------------------------------------------------------------------------------

model.Solver.LSM                    = 'CLM'
model.Solver.CLM.CLMFileDir         = clm_output_path
model.Solver.CLM.Print1dOut         = False
model.Solver.CLM.CLMDumpInterval    = 1
model.Solver.CLM.MetForcing         = '3D'
model.Solver.CLM.MetFileName        = 'NLDAS'
model.Solver.CLM.MetFilePath        = forcing_path
model.Solver.CLM.MetFileNT          = 24
model.Solver.CLM.IstepStart         = clmstep
model.Solver.CLM.EvapBeta           = 'Linear'
model.Solver.CLM.VegWaterStress     = 'Saturation'
model.Solver.CLM.ResSat             = 0.2
model.Solver.CLM.WiltingPoint       = 0.2
model.Solver.CLM.FieldCapacity      = 1.00
model.Solver.CLM.IrrigationType     = None
model.Solver.CLM.RootZoneNZ         = 4
model.Solver.CLM.SoiLayer           = 4
model.Solver.CLM.ReuseCount         = 1 
model.Solver.CLM.WriteLogs          = False
model.Solver.CLM.WriteLastRST       = True
model.Solver.CLM.DailyRST           = True
model.Solver.CLM.SingleFile         = True


#-----------------------------------------------------------------------------------------
# Set solver parameters
#-----------------------------------------------------------------------------------------

model.Solver                                                = 'Richards'
model.Solver.MaxIter                                        = 250000
model.Solver.MaxConvergenceFailures                         = 5
model.Solver.EvapTransFile                                  = False
model.Solver.BinaryOutDir                                   = False
model.Solver.TerrainFollowingGrid                           = True
model.Solver.TerrainFollowingGrid.SlopeUpwindFormulation    = 'Upwind'
model.Solver.Nonlinear.MaxIter                              = 250
model.Solver.Nonlinear.ResidualTol                          = 1e-2
model.Solver.Nonlinear.EtaChoice                            = 'EtaConstant'
model.Solver.Nonlinear.EtaValue                             = 1e-2 
model.Solver.Nonlinear.UseJacobian                          = True
model.Solver.Nonlinear.DerivativeEpsilon                    = 1e-16
model.Solver.Nonlinear.StepTol                              = 1e-15
model.Solver.Nonlinear.Globalization                        = 'LineSearch'
model.Solver.Linear.KrylovDimension                         = 500
model.Solver.Linear.MaxRestarts                             = 8
model.Solver.Linear.Preconditioner                          = 'PFMG'
model.Solver.Linear.Preconditioner.PCMatrixType             = 'PFSeymmetric'
model.Solver.Linear.Preconditioner.PFMG.NumPreRelax         = 3
model.Solver.Linear.Preconditioner.PFMG.NumPostRelax        = 2

model.Solver.PrintPressure               = True
model.Solver.PrintCLM                    = True
model.Solver.PrintSaturation             = False
model.Solver.PrintVelocities             = False
model.Solver.PrintSubsurfData            = False
model.Solver.PrintMask                   = False
model.Solver.WriteCLMBinary              = False
model.Solver.WriteSiloSpecificStorage    = False
model.Solver.WriteSiloMannings           = False
model.Solver.WriteSiloMask               = False
model.Solver.WriteSiloSlopes             = False
model.Solver.WriteSiloSubsurfData        = False
model.Solver.WriteSiloSaturation         = False
model.Solver.WriteSiloPressure           = False
model.Solver.WriteSiloEvapTrans          = False
model.Solver.WriteSiloEvapTransSum       = False
model.Solver.WriteSiloOverlandSum        = False
model.Solver.WriteSiloCLM                = False


#-----------------------------------------------------------------------------------------
# Run and Unload the ParFlow output files
#-----------------------------------------------------------------------------------------

model.run()