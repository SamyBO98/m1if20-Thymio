import dbus
import dbus.mainloop.glib
import gobject
from optparse import OptionParser
from pynput import keyboard as kb

speed = 150
lowSpeed = speed - 50
detectMin = 200
detectMax = 275

minCaptor = 400
maxCaptor = 600

minBlack = 1000
maxBlack = 750
keyPressed = 0

# KEY EVENTS
'''
def press(key):
    if keyPressed == 0:
        keyPressed = 1
    else:
        keyPressed = 1

with kb.Listener(press) as listener:
    listener.join()
'''


# ROBOT EVENTS 
def move_linear():
    #get the values of the sensors
    deltaR = network.GetVariable("thymio-II", "prox.ground.delta")[1]
    deltaL = network.GetVariable("thymio-II", "prox.ground.delta")[0]

    #print(delta)

    if delta < detectMin:
        print("too much on right")
        network.SetVariable("thymio-II", "motor.right.target", [speed])
        network.SetVariable("thymio-II", "motor.left.target", [lowSpeed])
    elif delta > detectMax:
        print("too much on left")
        network.SetVariable("thymio-II", "motor.right.target", [lowSpeed])
        network.SetVariable("thymio-II", "motor.left.target", [speed])
    else:
        network.SetVariable("thymio-II", "motor.right.target", [speed])
        network.SetVariable("thymio-II", "motor.left.target", [speed]) 
 
    return True

def move_right(normal_speed, low_speed):
    #get the values of the sensors
    deltaR = network.GetVariable("thymio-II", "prox.ground.delta")[1]
    deltaL = network.GetVariable("thymio-II", "prox.ground.delta")[0]

    #print("Delta Right:", deltaR)
    #print("Delta Left:", deltaL)

    #print(delta)

    if keyPressed == 0:
        if deltaR < minCaptor:
            print("too much on left")
            network.SetVariable("thymio-II", "motor.left.target", [normal_speed + 75])
            network.SetVariable("thymio-II", "motor.right.target", [low_speed])
        elif deltaR > maxCaptor:
            if deltaL > maxCaptor:
                print("too much on left")
                network.SetVariable("thymio-II", "motor.left.target", [normal_speed + 75])
                network.SetVariable("thymio-II", "motor.right.target", [low_speed])
            else:
                print("too much on left")
                network.SetVariable("thymio-II", "motor.left.target", [low_speed])
                network.SetVariable("thymio-II", "motor.right.target", [normal_speed + 75])
        else:
            network.SetVariable("thymio-II", "motor.right.target", [normal_speed])
            network.SetVariable("thymio-II", "motor.left.target", [low_speed])
 
    return True

def move_left(normal_speed, low_speed):
    #get the values of the sensors
    deltaR = network.GetVariable("thymio-II", "prox.ground.delta")[1]
    deltaL = network.GetVariable("thymio-II", "prox.ground.delta")[0]

    #print("Delta Right:", deltaR)
    #print("Delta Left:", deltaL)

    #print(delta)

    if keyPressed == 0:
        if deltaR < minCaptor:
            print("too much on left")
            network.SetVariable("thymio-II", "motor.right.target", [normal_speed + 75])
            network.SetVariable("thymio-II", "motor.left.target", [low_speed])
        elif deltaR > maxCaptor:
            if deltaL > maxCaptor:
                print("too much on left")
                network.SetVariable("thymio-II", "motor.right.target", [normal_speed + 75])
                network.SetVariable("thymio-II", "motor.left.target", [low_speed])
            else:
                print("too much on left")
                network.SetVariable("thymio-II", "motor.right.target", [low_speed])
                network.SetVariable("thymio-II", "motor.left.target", [normal_speed + 75])
        else:
            network.SetVariable("thymio-II", "motor.left.target", [normal_speed])
            network.SetVariable("thymio-II", "motor.right.target", [low_speed])
 
    return True

def debug():
    #get the values of the sensors
    deltaR = network.GetVariable("thymio-II", "prox.ground.delta")[1]
    deltaL = network.GetVariable("thymio-II", "prox.ground.delta")[0]

    print("Delta Right:", deltaR)
    print("Delta Left:", deltaL)

    return True
 
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-s", "--system", action="store_true", dest="system", default=False,help="use the system bus instead of the session bus")
 
    (options, args) = parser.parse_args()
 
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
 
    if options.system:
        bus = dbus.SystemBus()
        print("option system")
    else:
        bus = dbus.SessionBus()
        print("not option system")
 
    # Create Aseba network 
    network = dbus.Interface(bus.get_object('ch.epfl.mobots.Aseba', '/'), dbus_interface='ch.epfl.mobots.AsebaNetwork')
 
    #print in the terminal the name of each Aseba NOde
    #print network.GetNodesList()
 
    #GObject loop
    print 'starting loop'
    loop = gobject.MainLoop()
    network.SetVariable("thymio-II", "motor.right.target", [0])
    network.SetVariable("thymio-II", "motor.left.target", [0])
    # Functions called every 0.1 seconds
    #handle = gobject.timeout_add(100, move_linear)
    #handle = gobject.timeout_add(100, move_left, 140, 115)
    #handle = gobject.timeout_add(100, move_right, 140, 115)


    # DEBUG
    handle = gobject.timeout_add(1000, debug)
    loop.run()