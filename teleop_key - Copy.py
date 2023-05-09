#!/usr/bin/env python

import rospy
import tty
import termios
import sys
import atexit
from select import select
from geometry_msgs.msg import Twist

def move_robot(lin_vel, ang_vel, pub):
    vel = Twist()
    vel.linear.x = lin_vel
    vel.linear.y = 0
    vel.linear.z = 0

    vel.angular.x = 0
    vel.angular.y = 0
    vel.angular.z = ang_vel

    rospy.loginfo("Linear Vel = %f: Angular Vel = %f", lin_vel, ang_vel)
    pub.publish(vel)

class TeleOp:
    def __init__(self):
        rospy.init_node('robot_teleop', anonymous=True)
        rospy.loginfo("To stop TurtleBot CTRL + C")
        rospy.on_shutdown(self.shutdown)
        self.pub = rospy.Publisher('cmd_vel', Twist, queue_size=5)
        self.orig_settings = termios.tcgetattr(sys.stdin)
        atexit.register(self.reset_terminal)

    def get_key(self):
        self.set_terminal()
        select([sys.stdin], [], [], 0)
        key = sys.stdin.read(1)
        self.reset_terminal()
        return key

    @staticmethod
    def set_terminal():
        tty.setraw(sys.stdin.fileno())

    def reset_terminal(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.orig_settings)

    def run(self):
        rate = rospy.Rate(10)
        s = 0.7
        print("Reading from keyboard\n---------------------------\nUse 'w a s d' to move the robot. 'u'increas speed and 'i' decreas speed 'esc' to quit.")
        while not rospy.is_shutdown():
            key = self.get_key()
            ord_key = ord(key)
            if ord_key == 3 or ord_key == 27:
                rospy.loginfo("Shutdown")
                break
            elif ord_key == 119: # w
                move_robot(s, 0.0, self.pub)
            elif ord_key == 115: # s
                move_robot(-s, 0.0, self.pub)
            elif ord_key == 97: # a
                move_robot(0.0, s , self.pub)
            elif ord_key == 100: # d
                move_robot(0.0, -s, self.pub)
            elif ord_key == 117: # u
                s = s+1
            elif ord_key == 105: # i
                s = s-1
            rate.sleep()

if __name__ == '__main__':
    teleop = TeleOp()
    teleop.run()
