import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

hd = 0.3

distance = 10000
distance0 = 10000
distance270 = 10000
distance280 = 10000
state = 0
mem1 = 0



def ls_callback(data):
	global distance
	distance = min(data.ranges)
	global distance0

	distance0 = data.ranges[0]

	global distance270

	distance270 = data.ranges[270]
	
	global distance280
	
	distance270 = data.ranges[280]
	
	print ('-----')

def node():
	global distance0
	global distance270
	global distance280
	global distance
	global state
	global hd
	global mem1
	
	pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
	rospy.init_node('obstical_avoider', anonymous=True)
	rospy.Subscriber("/scan", LaserScan , ls_callback)

	rate = rospy.Rate(10) # 10hz

	
	while not rospy.is_shutdown():
		vel_msg = Twist()
		
		if state == 0:
			vel_msg.linear.x = 0
			vel_msg.linear.y = 0
			vel_msg.linear.z = 0
			vel_msg.angular.x = 0
			vel_msg.angular.y = 0
			vel_msg.angular.z = 0
			state = 1
			print("state:" + str(state))
		elif state == 1:
			if distance0 > hd:
				vel_msg.linear.x = min([distance/2, 1])
				vel_msg.angular.z = 0
				if distance<hd:
					vel_msg.angular.z = 0.05
			elif distance0 <= hd or distance <= hd:
				vel_msg.linear.x = 0
				vel_msg.angular.z = 0.001
				state = 2
				mem1 = 10
				print("state:" + str(state))
		elif state == 2:
			vel_msg.angular.z = 1
			vel_msg.linear.x = 0
			if distance270 < hd and distance280 > hd and mem1 <= 0 :
				state = 1
			mem1 -=1
		elif state == 3:
	
			mem1 = distance - mem1
			print(distance)
			vel_msg.linear.x = 0.1
			vel_msg.linear.y = 0
			vel_msg.linear.z = 0
			vel_msg.angular.x = 0
			vel_msg.angular.y = 0
			vel_msg.angular.z = (hd-distance)*5
			'''
			if distance > hd+0.1:
				print("greater")
				if mem1 < 0.02:
					vel_msg.angular.z = -0.2
				else:
					vel_msg.angular.z = 0.2
			elif distance < hd<-0.1:
				print("lesser")
				if mem1 > 0.02:
					vel_msg.angular.z = -0.2
				else:
					vel_msg.angular.z = 0.2
			else:	
				print("in range")
				'''
			mem1 = distance

		pub.publish(vel_msg)
		
		rate.sleep()
	 
node()  
        
