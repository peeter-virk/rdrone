import rospy
import math
from geometry_msgs.msg import Pose
from tf.transformations import euler_from_quaternion, quaternion_from_euler
import time

from beginner_tutorials.msg import cord2D
from beginner_tutorials.msg import plotdata
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from beginner_tutorials.msg import pid_values
import tf

target = [0,0,0]
target_x = 0
target_y = 0
target_a = 0

c_pose = [0,0,0]
c_rot = [0,0,0]

state = 0

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


def pid_callback(data):
	global Kp
	global Ki
	global Kd
	
	Kp = float(data.Kp)
	Ki = float(data.Ki)
	Kd = float(data.Kd)
	
	print("pid vals:", Kp, Ki, Kd)
	
	pass

def kb_callback(data):
	global target
	
	print(data)
	target[0] = data.position.x
	target[1] = data.position.y
	quat = [0,0,0,0]
	quat[0] = data.orientation.x
	quat[1] = data.orientation.y
	quat[2] = data.orientation.z
	quat[3] = data.orientation.w
	rot = list(tf.transformations.euler_from_quaternion(quat))
	print(rot)
	target[2] = rot[2]
	print(target)
	
	
	pass

def odom_callback(data):
	global c_pose
	global c_rot
	
	c_pose =[
	data.pose.pose.position.x,
	data.pose.pose.position.y,
	data.pose.pose.position.z	
	]
	
	orientation_q = data.pose.pose.orientation
	orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
	c_rot = list(euler_from_quaternion (orientation_list))
		
	#print(c_pose, c_rot)
	
	pass

def get_rotation_prop(current_angle, target_angle, max_speed):
	v = min(abs(current_angle-target_angle), max_speed)
	rotate_right = True
	if current_angle > target_angle:
		if target_angle + math.pi < current_angle:
			rotate_right = False
	else:
		if target_angle - math.pi < current_angle:
			rotate_right = False
	if rotate_right:
		v=v*-1
	return v



if __name__ == "__main__":

	pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
	plot = rospy.Publisher('/plot', plotdata, queue_size=10)
	rospy.init_node('goto', anonymous=True)
	rospy.Subscriber("/turtlebot/goal_pose", Pose , kb_callback)
	rospy.Subscriber("/odom", Odometry , odom_callback)
	rospy.Subscriber("/pid", pid_values , pid_callback)

	rate = rospy.Rate(10) # 10hz
	
	slope = 0
	integ = 0
	
	last_time = 0
	timen = 0
	delta = 0
	last_e = 0
	z_prop = 0
	
	integ_a = 0
	slope_a = 0
	last_a = 0
	
	vel_msg = Twist()
	vel_msg.linear.x = 0
	vel_msg.linear.y = 0
	vel_msg.linear.z = 0
	vel_msg.angular.x = 0
	vel_msg.angular.y = 0
	vel_msg.angular.z = 0
	pub.publish(vel_msg)
	time.sleep(5)
	
	integ_turning = 0
	integ_moving = 0
	
	while not rospy.is_shutdown():
		timen = time.time()
		delta = timen-last_time
		last_time = timen
		
		
		heading_x = target[0] - c_pose[0]
		heading_y = target[1] - c_pose[1]
		heading_angle = math.atan2(heading_y, heading_x)
		#print(target)
		
		current_angle = c_rot[2]
		#print(current_angle)
		
		
		distance = math.sqrt((target[0]-c_pose[0])**2 + (target[1]-c_pose[1])**2)
		
		#print(distance, rotspeed)
		
		plot_msg = plotdata()
		
		vel_msg = Twist()
		vel_msg.angular.x = 0
		vel_msg.angular.y = 0
		
		if distance < 0.08 and state == 0:
			state = 1
			print("stopped")
			integ_moving = integ_a
			integ_a = integ_turning
		if distance > 0.2 and state == 1:
			state = 0
			print("moving")
			integ_turning = integ_a
			integ_a = integ_moving
		
		if state == 1:
			
			vel_msg.linear.x = 0
			z_prop = get_rotation_prop(current_angle, target[2], 0.2)
			#print("ca:", current_angle, "ha:", target[2])
			plot_msg.set = target[2]
			state = 1
		elif state == 0:
			
			#print(distance)
			
			z_prop = get_rotation_prop(current_angle, heading_angle, 2)
			plot_msg.set = heading_angle
			
			vel_msg.linear.x = min(distance*0.5, 0.5)
		
		# angular pid controller
		
		if abs(integ_a)> 1000:
			integ_a = 0
		
		#derivetive
		slope_a = (z_prop-last_a)/(delta)
		last_a = z_prop

		#integral
		integ_a += z_prop*(delta)
		#print("zprop", z_prop, "delta", delta)
		
		vel_msg.angular.z = z_prop * Kp + integ_a * Ki + slope_a * Kd
		#print(z_prop * 0.6, integ_a * 0.01, slope_a * 0.2)
		vel_msg.linear.y = 0
		vel_msg.linear.z = 0
		
		plot_msg.response = current_angle
		
		plot.publish(plot_msg)
		
		pub.publish(vel_msg)
		#print("distance:",distance, "\n" ,vel_msg)

		
	f = open("pid.txt", "w")
	f.write(str(Kp)+"\n"+str(Ki)+"\n"+str(Kd))
	f.close()
