from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))
    from sumolib import checkBinary
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci


def generate_routefile():
    random.seed(42)  # make tests reproducible
    N = 3600  # number of time steps
    # demand per second from different directions
    pWE = 1. / 25
    pEW = 1. / 11
    pNS = 1. / 20
    pSN = 1. / 20
    with open("cross.rou.xml", "w") as routes:
        print("""<routes>
        <vType id="type_1" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger"/>
        <vType id="type_2" accel="0.8" decel="4.5" sigma="0.5" length="7" minGap="3" maxSpeed="25" guiShape="bus"/>
        <vType id="type_3" accel="0.8" decel="4.5" sigma="0.5" length="4" minGap="3" maxSpeed="25" guiShape="emergency"/>
        <vType id="type_4" accel="0.8" decel="4.5" sigma="0.5" length="6" minGap="3" maxSpeed="25" guiShape="passenger/sedan"/>
        <route id="right" edges="51o 1i 2o 52i" />
        <route id="left" edges="52o 2i 1o 51i" />
        <route id="down" edges="54o 4i 3o 53i" />
        <route id="up" edges="53o 3i 4o 54i" />
        <route id="mixed_1" edges="51o 1i 2o 52i 52o 2i 1o 51i" />
        <route id="mixed_2" edges="54o 4i 3o 53i 53o 3i 4o 54i" />""", file=routes)
        lastVeh = 0
        vehNr = 0
        c=0
        for i in range(N):
            c+=1
            if random.uniform(0, 1) < pWE:
                if(c%3==0):
                    print('    <vehicle id="%i" route="mixed_1" depart="%i" color="1,0,0" />' % (
                        vehNr, i), file=routes)
                else:
                    print('    <vehicle id="%i" route="mixed_1" depart="%i" />' % (
                        vehNr, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pEW:
                if(c%5==0):
                    print('    <vehicle id="%i" route="mixed_2" depart="%i" color="1,0,0" />' % (
                        vehNr, i), file=routes)
                else:
                    print('    <vehicle id="%i" route="mixed_2" depart="%i" />' % (
                        vehNr, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pNS:
                if(c%7==0):
                    print('    <vehicle id="%i" route="right" depart="%i" color="1,0,0" />' % (
                        vehNr, i), file=routes)
                else:
                    print('    <vehicle id="%i" route="right" depart="%i" />' % (
                        vehNr, i), file=routes)
                vehNr += 1
                lastVeh = i
        print("</routes>", file=routes)

"""def run():
    step = 0
    # we start with phase 2 where EW has green
    traci.trafficlight.setPhase("0", 2)
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        if traci.trafficlight.getPhase("0") == 2:
            # we are not already switching
            if traci.inductionloop.getLastStepVehicleNumber("0") > 0 :
                # there is a vehicle from the north, switch
                traci.trafficlight.setPhase("0", 3)
            else:
                # otherwise try to keep green for EW
                traci.trafficlight.setPhase("0", 2)
        step += 1
    traci.close()
    sys.stdout.flush()"""

def run() :
    step=0
    traci.trafficlight.setPhase("0", 2)
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        if traci.trafficlight.getPhase("0") == 2:
            if traci.inductionloop.getLastStepVehicleNumber("0") > traci.inductionloop.getLastStepVehicleNumber("1") :
                traci.trafficlight.setPhase("0", 3)
            elif traci.inductionloop.getLastStepVehicleNumber("1") > traci.inductionloop.getLastStepVehicleNumber("0") :
                traci.trafficlight.setPhase("0", 2)
        step += 1
    traci.close()
    sys.stdout.flush()
            


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "cross.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()
