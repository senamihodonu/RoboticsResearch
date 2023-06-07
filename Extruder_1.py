# This macro allows simulating a 3D printing extruder
# The macro will output spray gun statistics
#
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# For more information visit:
# http://www.robodk.com/doc/en/PythonAPI/robolink.html
#
# Define the default action (0 to deactivate, +1 to activate, -1 to clear any spray gun simulation)
# Setting it to None will display a message
ACTION = None
# Check if we are running this program inside another program and passing arguments
import sys
if len(sys.argv) > 1:
    ACTION = float(sys.argv[1])
    # For faster speed: igone values greater than 0
    if ACTION > 0:
        quit()

from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
RDK = Robolink()

# quit if we are not in simulation mode
if RDK.RunMode() != RUNMODE_SIMULATE:
    quit()

# Get any previously added spray gun simulations and display statistics (spray on the part vs spray falling out of the part)
existing_material_simulation = False
info, stats_data = RDK.Spray_GetStats()
if stats_data.size(1) > 0:
    print("Spray gun statistics:")
    print(info)
    print(stats_data.tr())
    existing_material_simulation = True
    # # Diplay statistics
    # RDK.ShowMessage("Material used: %.1f%%<br>Material waisted: %.1f%%<br>Total particles: %.1f" % (data[1,0],data[2,0],data[3,0]), True)
    # # Clear previous spray
    # RDK.Spray_Clear() 

# If the default ACTION is None, display a message to activate/deactivate the spray gun
if ACTION is None:
    print('Note: This macro can be called as Extruder(0) to turn it ON or Extruder(-1) to turn it OFF')
    entry = mbox('Turn Extruder ON or OFF', ('On', '0'), ('Off', '-1'))
    if not entry:
        quit()
    ACTION = int(entry)    

if ACTION < 0:
    # Turn material deposition off
    # Select Escape to delete existing material simulations
    #RDK.Spray_Clear() 
    RDK.Spray_SetState(SPRAY_OFF)
    
elif ACTION >= 0:
    
    if existing_material_simulation:
        # Select Esc key to delete existing material simulations and force a new type of spray gun simulation
        RDK.Spray_SetState(SPRAY_ON)
        exit()
    
    
    # Create a new spray gun object in RoboDK for material deposition (3D printing simulation)
    # by using RDK.Spray_Add(tool, object, options_command, volume, geometry)
    # tool: tool item (TCP) to use
    # object: object to project the particles
    # options_command (optional): string to specify options. Example:
    #     STEP=AxB: Defines the grid to be projected 1x1 means only one line of particle projection (for example, for welding)
    #     PARTICLE: Defines the shape and size of particle (sphere or particle), unless a specific geometry is provided:
    #       a- SPHERE(radius, facets)
    #       b- SPHERE(radius, facets, scalex, scaley, scalez)
    #       b- CUBE(sizex, sizey, sizez)
    #     RAND=factor: Defines a random factor factor 0 means that the particles are not deposited randomly
    #     ELLYPSE: defines the volume as an ellypse (default)
    #     RECTANGLE: defines the volume as a rectangle
    #     PROJECT: project the particles to the surface (default) (for welding, painting or scanning)
    #     NO_PROJECT: does not project the particles to the surface (for example, for 3D printing)
    #
    # volume (optional): Matrix of parameters defining the volume of the spray gun
    # geometry (optional): Matrix of vertices defining the triangles.

    
    diameter = 22.225 # in mm
    detail = 8 # number of rings of detail to display the sphere
    scale = '1,1,0.5' # scale the particle in 0.5 along the tool Z axis (simulating gravity effect)
    options_command = "ELLYPSE NO_PROJECT PARTICLE=SPHERE(%.3f,%.0f,%s)" % (diameter, detail, scale) # simulate 
    #options_command = "PARTICLE=CUBE(10,10,2) STEP=8x8"
    #options_command = "PARTICLE=SPHERE(4,8) STEP=8x8"
    #options_command = "PARTICLE=SPHERE(4,8,1,1,0.1) STEP=8x8 RAND=3"

    # Example commands for welding:
    # options_command = "PROJECT PARTICLE=SPHERE(4,8)"
    # options_command = PARTICLE=SPHERE(4,8) STEP=1x0   

    tool = 0    # auto detect active tool
    obj = 0     # auto detect object in active reference frame

    # Material is deposited at 0,0,0 with respect to the TCP coordinates
    close_param = [0,0,0,  0,0,0,  0,0,0,     0.7,0.5,0.8,1] # color as RGBA
    far_param   = [0,0,0,  0,0,0,  0,0,0,     0.7,0.5,0.8,1] # color as RGBA
    volume = Mat([close_param, far_param])
    RDK.Spray_Add(tool, obj, options_command, volume.tr())
    RDK.Spray_SetState(SPRAY_ON)

    




