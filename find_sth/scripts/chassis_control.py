#!/usr/bin/env python
#coding:UTF-8

import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist

def main():
    # 初始化 Twist 控制消息
    global twist, enable_
    twist = Twist()
    twist.linear.x = 0
    twist.linear.y = 0
    twist.linear.z = 0
    twist.angular.x = 0
    twist.angular.y = 0
    twist.angular.z = 0
    enable_ = 0

    # 初始化 ros 节点
    rospy.init_node("chassis_control", anonymous=False)

    # 初始化控制命令订阅者
    cmd_vel_sub = rospy.Subscriber("base_cmd", String, cmd_vel_callback)

    # 初始化控制命令发布者
    cmd_vel_pub = rospy.Publisher("cmd_vel_mux/input/teleop", Twist, queue_size=1)

    # 初始化 ros主循环
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        if enable_ == 1:
            cmd_vel_pub.publish(twist)
        rate.sleep()

def cmd_vel_callback(msg):
    global enable_
    if msg.data.find("whirl") > -1:
        twist.linear.x = 0
        twist.linear.y = 0
        twist.linear.z = 0
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = 0.2
        enable_ = 1
    elif msg.data.find("forward") > -1:
        twist.linear.x = 0.2
        twist.linear.y = 0
        twist.linear.z = 0
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = 0
        enable_ = 1
    else:
        twist.linear.x = 0
        twist.linear.y = 0
        twist.linear.z = 0
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = 0
        enable_ = 0

if __name__ == "__main__":
    main()
