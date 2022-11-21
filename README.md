# Upper-Colorado-PFCLM

Parflow-CLM model of the Upper Colorado River Basin 

<img width="294" alt="image" src="https://user-images.githubusercontent.com/55851528/203094169-847a3840-e0f1-4998-a647-66448a6b90e3.png">

ReadMe and gitignore coming soon

#### Note to modelers:
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
         
Recommended Directory Structure:  
    UCRB-run-001         <- parent directory to hold all files for documentation  
        scripts          <- holds this script and others i.e. your job script  
        inputs           <- to hold your official UCRB run inputs  
        pf-output        <- to hold pressure files and other values you choose to print  
        clm-output       <- to hold CLM output files  
        restart-files    <- to contain copies of CLM restart files and last pressure files  
        forcing          <- forcing parent directory to hold meteorological inputs  
            YYYY         <- if running multiple years, add subfolders with years as names  
            YYYY  
            ...  
   
Things You Should Change:  
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
