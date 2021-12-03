#! /usr/bin/env python2.7
import rospy
from visualization_msgs.msg import Marker
from tf.transformations import euler_from_quaternion, quaternion_from_euler


def marker_callback(data):
	
	print("pose")
	print(data.pose.position)
	print("rotation")
	orientation = list(euler_from_quaternion([data.pose.orientation.w,data.pose.orientation.x,data.pose.orientation.y,data.pose.orientation.z]))
	print("X: ", orientation[0])
	print("Y: ", orientation[1])
	print("Z: ", orientation[2])
	#c_rot = list(euler_from_quaternion (orientation_list))
		
	#print(c_pose, c_rot)
	
	pass
	

if __name__ == "__main__":
	rospy.init_node('m_printer', anonymous=True)
	rospy.Subscriber("/visualization_marker", Marker , marker_callback)
	while not rospy.is_shutdown():
		pass
