#! /usr/bin/env python2.7
import rospy
import math
import time
from visualization_msgs.msg import Marker
from tf.transformations import euler_from_quaternion, quaternion_from_euler
from geometry_msgs.msg import Twist
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Empty

current_pos = [0,0,0,0,0,0,0]
marker_behind = [0,0,0,0,0,0,0]
marker_top = [0,0,0,0,0,0,0]
markertime = time.time()

path = []

def handle_marker(data, marker_loc):
	marker_loc[0] = data.pose.position.x
	marker_loc[1] = data.pose.position.y
	marker_loc[2] = data.pose.position.z
	rotation = list(euler_from_quaternion([data.pose.orientation.x,data.pose.orientation.y,data.pose.orientation.z,data.pose.orientation.w]))
	for i in range(3):	
		marker_loc[3+i] = rotation[0+i]
	marker_loc[6] = time.time()
	#print(marker_loc)

def marker_callback(data):
	global markertime
	markertime = time.time()
	#print(data)
	if data.id == 5:
		global marker_behind
		handle_marker(data, marker_behind)
	elif data.id == 4:
		global marker_top
		handle_marker(data, marker_top)	

def drone_odom_callback(data):
	global current_pos
	current_pos[0] = data.pose.position.x
	current_pos[1] = data.pose.position.y
	current_pos[2] = data.pose.position.z
	rotation = list(euler_from_quaternion([data.pose.orientation.x,data.pose.orientation.y,data.pose.orientation.z,data.pose.orientation.w]))
	
	for i in range(3):	
		current_pos[3+i] = rotation[0+i]
	current_pos[6] = time.time()



def target_odom_callback(data):
	target = [0,0,0]
	target[0] = data.pose.position.x
	target[1] = data.pose.position.y
	target[2] = data.pose.position.z
	global path
	path.append(target)
	
	global current_target
	current_target[0] = data.pose.position.x
	current_target[1] = data.pose.position.y
	current_target[2] = data.pose.position.z
	rotation = list(euler_from_quaternion([data.pose.orientation.x,data.pose.orientation.y,data.pose.orientation.z,data.pose.orientation.w]))
	for i in range(3):	
		current_target[3+i] = rotation[0+i]



def planar_distance(pt1, pt2):
	return math.sqrt((pt1[0]-pt2[0])**2 + (pt1[1]-pt2[1])**2)

def local_to_global_space(obj, tgt):
	out = [0,0]
	out[0] = (math.cos(obj[5]) * tgt[2] + obj[0] + math.sin(obj[5]) * tgt[0])
	out[1] = (math.sin(obj[5]) * tgt[2] + obj[1] - math.cos(obj[5]) * tgt[0])
	return out

if __name__ == "__main__":
	rospy.init_node('tracker', anonymous = True)
	mov = rospy.Publisher('/bebop/cmd_vel', Twist, queue_size=10)
	takeoff = rospy.Publisher('/bebop/takeoff', Empty, queue_size=10)
	land = rospy.Publisher('/bebop/land', Empty, queue_size=10)
	cam_c = rospy.Publisher('/bebop/camera_control', Twist, queue_size=10)

	rospy.Subscriber("/visualization_marker", Marker , marker_callback)
	rospy.Subscriber("/vrpn_client_node/drone_1/pose", PoseStamped , drone_odom_callback)

	rate = rospy.Rate(10) # 10hz
	empty = Empty()
	is_located = True
	robot_start_pose = [0,0,0,0,0,0]
	last_a_z = 0
	while not rospy.is_shutdown():
		if current_pos != [0,0,0,0,0,0,0] and not is_located:
			robot_start_pose = current_pos
			is_located = True
			stime = time.time() + 3
			while (time.time() < stime):
				takeoff.publish(empty)
			
			
		if not is_located:
			continue
		
		robots_loc = [0,0]
		if abs(marker_top[6]-current_pos[6]) < 0.5:
			if abs(marker_behind[6]-current_pos[6]) < 0.5:
				lt = local_to_global_space(current_pos, marker_top)
				lb = local_to_global_space(current_pos, marker_behind)
				robots_loc[0] = (lt[0] + lb[0]) / 2
				robots_loc[1] = (lt[1] + lb[1]) / 2
			else:
				robots_loc = local_to_global_space(current_pos, marker_top)
		elif abs(marker_behind[6]-current_pos[6]) < 0.5:
			robots_loc = local_to_global_space(current_pos, marker_behind)
		print(robots_loc)
		if len(path) < 1 or planar_distance(robots_loc, path[-1]) < 0.3 or robots_loc == [0,0]:
			pass
		else:
			path.append(robots_loc)
				
		
		#print ("behind", marker_behind)
		#print ("top   ", marker_top)
		print ("drone ", current_pos)
		
		
		vel_msg = Twist()
		vel_msg.angular.z = (marker_top[0]*-0.5) + ((marker_top[0] - last_a_z)*-0.5)
		vel_msg.linear.z = ((current_pos[2]-1.3 ) * -1)
		last_a_z = marker_top[0]
		#print(vel_msg)
		#mov.publish(vel_msg)
		

		rate.sleep()
		continue
















		rotpow = math.pi*1.5 - (marker_loc[5]+math.pi)
		if rotpow > 2*math.pi:
			rotpow -= 2*math.pi
		elif rotpow < 0:
			rotpow += 2*math.pi

		rotpow = rotpow / math.pi
		rotpow -= 1



		vel_msg = Twist()

		if ((time.time() - markertime) < 1):
			vel_msg.angular.z = rotpow * 2 + (rotpow - last_rotpow) * 0.5
			vel_msg.linear.y = (marker_loc[0] * marker_loc[2] * -3.5) + last_y * -0.5
			vel_msg.linear.x = (marker_loc[1] * marker_loc[2] * -3.5) + last_x * -0.5
			last_y = vel_msg.linear.y
			last_x = vel_msg.linear.x
			vel_msg.linear.z = (marker_loc[2] - 0.3) * -1.5
		else:
			vel_msg.angular.z = 0
		last_rotpow = rotpow
		print(vel_msg)
		

		mov.publish(vel_msg)
		rate.sleep()
		continue



		if current_pos == [0,0,0,0,0,0]:
			continue
		if current_target == [0,0,0,0,0,0]:
			continue
		if tgt == None and len(path) == 0:
			continue
		#path operations
		if tgt == None:
			if len(path)>0:
				tgt = path.pop(0)
		while (planar_distance(tgt,current_pos)< 0.2 and len(path) > 0):
			tgt = path.pop(0)
		#print(len(path))
		# output current distance to the target node on the path
		#print(planar_distance(tgt,current_pos))
		
		
		if planar_distance(current_pos,current_target) < 0.8:
			tgt = current_target
		
		# movement handling
		deltaX = tgt[0]-current_pos[0]
		deltaY = tgt[1]-current_pos[1]
		g_angle = math.atan2(deltaY,deltaX)

		l_angle = g_angle - current_pos[5]
		#print(math.cos(l_angle), math.sin(l_angle))
		vel_msg = Twist()
		vel_msg.linear.x = (math.cos(l_angle)*0.2)
		vel_msg.linear.y = (math.sin(l_angle)*0.2)
		hight = 2
		# hold drone at level height
		if abs(current_pos[2]-hight) > 0.02:
			if current_pos[2] > hight:
				vel_msg.linear.z = -0.1
			elif current_pos[2] < hight:
				vel_msg.linear.z = 0.1

		
		mov.publish(vel_msg)

		rate.sleep()
