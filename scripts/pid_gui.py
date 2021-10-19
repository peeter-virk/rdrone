import PySimpleGUI as sg
import rospy
from beginner_tutorials.msg import pid_values

Kp = 1
Ki = 1
Kd = 1

try:
	f = open("pid.txt", "r")
	vals = f.read().splitlines()
	Kp = float(vals[0])
	Ki = float(vals[1])
	Kd = float(vals[2])
	f.close()
except:
	f = open("pid.txt", "w")
	f.write("1\n1\n1")
	f.close()

rospy.init_node('input', anonymous=True)

layout = [  [sg.Text('My Window')],
            [sg.InputText(Kp)],
            [sg.InputText(Ki)],
            [sg.InputText(Kd)],
            [sg.Button('set'), sg.Button('exit')]]

# Create the window
window = sg.Window("Demo", layout)

# Create an event loop

pub = rospy.Publisher('/pid', pid_values, queue_size=10)

while True:
    event, values = window.read()
    if event == "set":
    	pid = pid_values()
    	pid.Kp = float(values[0])
    	pid.Ki = float(values[1])
    	pid.Kd = float(values[2])
    	pub.publish(pid)
    if event == "exit" or event == sg.WIN_CLOSED:
        break

window.close()

