import rospy
from visualization_msgs.msg import Marker
from tf.transformations import euler_from_quaternion, quaternion_from_euler
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty


position = [0,0,0]
rotation = [0,0,0]

def marker_callback(data):
	
	global position
	global rotation
	
	#print("pose")
	#print(data.pose.position)
	#print("rotation")
	position = [data.pose.position.x,data.pose.position.y,data.pose.position.z]
	print(data.pose.orientation)
	rotation = list(euler_from_quaternion([data.pose.orientation.x,data.pose.orientation.y,data.pose.orientation.z,data.pose.orientation.w]))
	#print("X: ", orientation[0])
	#print("Y: ", orientation[1])
	#print("Z: ", orientation[2])
	#c_rot = list(euler_from_quaternion (orientation_list))
		
	#print(c_pose, c_rot)
	
	pass
	

if __name__ == "__main__":
	rospy.init_node('dst_keeper', anonymous=True)
	rospy.Subscriber("/visualization_marker", Marker , marker_callback)
	mov = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
	takeoff = rospy.Publisher('/drone/takeoff', Empty, queue_size=10)
	rate = rospy.Rate(10) # 10hz
	empty = Empty()
	takeoff.publish(empty)
	while not rospy.is_shutdown():
		takeoff.publish(empty)
		vel_msg = Twist()
		vel_msg.linear.x = (position[2]-1)*2
		vel_msg.linear.y = 0
		vel_msg.linear.z = (position[1]) * -0.5
		vel_msg.angular.x = 0
		vel_msg.angular.y = 0
		vel_msg.angular.z = (position[0])*-4
		mov.publish(vel_msg)
		rate.sleep()
