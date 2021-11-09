import rospy
from geometry_msgs.msg import Pose
from beginner_tutorials.msg import cord2D
import tf
import math
def talker():
    pub = rospy.Publisher('turtlebot/goal_pose', Pose, queue_size=10)
    rospy.init_node('kb_input', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        msg = Pose()
        x = input("X:")
        if x == "q":
        	break
        y = input("Y:")
        if y == "q":
        	break
        a = input("angle:")
        if a == "q":
        	break
        print (f"sending robot to {x}, {y}.")
        
        try:
            msg.position.x = float(x)
            msg.position.y = float(y)
            quat = tf.transformations.quaternion_from_euler(0,0,math.radians(int(a)))
            msg.orientation.x = quat[0]
            msg.orientation.y = quat[1]
            msg.orientation.z = quat[2]
            msg.orientation.w = quat[3]
            print(msg)
            pub.publish(msg)
        except Exception as e:
            print(e)
        rate.sleep()
talker()
