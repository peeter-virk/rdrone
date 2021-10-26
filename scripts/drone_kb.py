from pynput import keyboard
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
import rospy

#              w,a,s,d,i,j,k,l,z,x,h
controllmap = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
keymap = ['w','a','s','d','i','j','k','l','z','x','t','f','g','h']

def on_press(key):
    global controllmap, keymap
    try:
        #print('alphanumeric key {0} pressed'.format(key.char))
        for i, v in enumerate(keymap):
            if v == str(key.char):
            	controllmap[i] = 1
            	
    except AttributeError:
        pass
        #print('special key {0} pressed'.format(key))

def on_release(key):
    global controllmap, keymap
    #print('{0} released'.format(key))
    for i, v in enumerate(keymap):
            if v == str(key.char):
            	controllmap[i] = 0
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Collect events until released
#with keyboard.Listener(
#        on_press=on_press,
#        on_release=on_release) as listener:
#    listener.join()

# ...or, in a non-blocking fashion:
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()


pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
takeoff = rospy.Publisher('/drone/takeoff', Empty, queue_size=10)
land = rospy.Publisher('/drone/land', Empty, queue_size=10)
rospy.init_node('dronekb', anonymous=True)

rate = rospy.Rate(10) # 10hz

speed = 10
# w,a,s,d,i,j,k,l,z,x,h
while not rospy.is_shutdown():
    print(controllmap)
    
    vel_msg = Twist()
    empty = Empty()
    
    if controllmap[8]:
        takeoff.publish(empty)
    if controllmap[9]:
        land.publish(empty)
        
    vel_msg.linear.x = (controllmap[0] - controllmap[2]) * speed
    vel_msg.linear.y = (controllmap[1] - controllmap[3]) * speed
    vel_msg.linear.z = (controllmap[4] - controllmap[6]) * speed * 0.1
    vel_msg.angular.x = (controllmap[10] - controllmap[12]) * speed * 0.1
    vel_msg.angular.y = (controllmap[11] - controllmap[13]) * speed * 0.1
    vel_msg.angular.z = (controllmap[5] - controllmap[7]) * speed * 0.1
    pub.publish(vel_msg)
    rate.sleep()
    
