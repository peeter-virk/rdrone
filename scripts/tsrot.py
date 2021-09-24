import rospy
from geometry_msgs.msg import Twist

def talker():
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rospy.init_node('turtlesim_motion_pose', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        vel_msg = Twist()
        vel_msg.angular.z = 1
        vel_msg.linear.x = 1
        pub.publish(vel_msg)
        rate.sleep()
talker()
