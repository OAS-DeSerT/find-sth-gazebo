#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Basic Modules
import os
import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sound_play.libsoundplay import SoundClient
from robot_vision_msgs.msg import BoundingBoxes

obj = ""
target = ""

class MissionDemo(object):

	def __init__(self):
		# Flags
		self._FLAG_EXECUTE = None
		self._FLAG_FOUND = None
		self._FLAG_NAVI = None
		self._FLAG_CMD = None
		# Soundplay parameter
		self.voice = rospy.get_param("~voice", "voice_kal_diphone")
		self.speaker = SoundClient(blocking=True)
		rospy.sleep(1)
		rospy.init_node("mission_demo", disable_signals=True)

	def main_loop(self):
		# Initial
		self.base_cmd_pub = rospy.Publisher("base_cmd", String, queue_size=1)
		self.take_photo = rospy.Publisher("take_photo", String, queue_size=10)
		rospy.Subscriber("nav_cmd", String, self._navi_callback)
		rospy.Subscriber("lm_data", String, self._voice_callback)
		rospy.Subscriber("yolo_ros/bounding_boxes", BoundingBoxes, self._vision_callback)
		rospy.sleep(1)
		# Set arm to rest-state
		rospy.loginfo("Waiting for command")
		self.speaker.say("I'm ready for commands", self.voice)
		# Navigating to finding-point
		while (True):
			if self._FLAG_CMD == 1:
				os.system("gnome-terminal -- bash -c 'rosrun rchomeedu_navigation nav1.py'")
				self.speaker.say("Going to the dining room", self.voice)
				self._FLAG_NAVI = 1
				break
		# Reached the point then shut naving
		while (True):
			if self._FLAG_NAVI == 10:
				break
			elif self._FLAG_NAVI == 0:
				self.speaker.say("Reached the dining room.", self.voice)
				rospy.sleep(1)
				rospy.loginfo("I am seeking the {}".format(target))
				self.speaker.say("I am seeking the {}".format(target), self.voice)
				self._FLAG_EXECUTE = 1
				self.base_cmd_pub.publish("whirl")
				for x in range(0, 33):
					if self._FLAG_EXECUTE == 0:
						break
					rospy.sleep(1)
				self.base_cmd_pub.publish("stop")
				self._FLAG_EXECUTE = 0
				rospy.sleep(1)
				if self._FLAG_FOUND != 1:
					rospy.loginfo("Not found")
					self.speaker.say("Not found", self.voice)
					os.system("gnome-terminal -- bash -c 'rosrun rchomeedu_navigation nav2.py'")
					rospy.loginfo("Go on finding")
					self.speaker.say("Go on finding", self.voice)
					self._FLAG_NAVI = 2
				break
		# Reached home and that's all
		while (True):
			if self._FLAG_FOUND == 1:
				break
			elif self._FLAG_NAVI == 0:
				rospy.loginfo("One more try")
				self.speaker.say("One more try", self.voice)
				self.base_cmd_pub.publish("whirl")
				self._FLAG_EXECUTE = 1
				for x in range(0, 33):
					if self._FLAG_EXECUTE == 0:
						break
					rospy.sleep(1)
				self.base_cmd_pub.publish("stop")
				self._FLAG_EXECUTE = 0
				rospy.sleep(1)
				if self._FLAG_FOUND != 1:
					rospy.loginfo("Not found. There is no {} in the dining room".format(target))
					self.speaker.say("Not found. There is no {} in the dining room".format(target), self.voice)
				rospy.sleep(1)
				break

		if self._FLAG_FOUND == 1:
			self.found_it()
			rospy.sleep(1)
		self.go_home()

		while (True):
			if self._FLAG_NAVI == 30:
				rospy.loginfo("Oops! Did I miss it? Ha ha ha!")
				self.speaker.say("Oops! Did I miss it? Ha ha ha!", self.voice)
				self.found_it()
				rospy.sleep(1)
				self.go_home()
			elif self._FLAG_NAVI == 0:
				if self._FLAG_FOUND == 1:
					self.take_photo.publish("show photo")
					rospy.loginfo("I've found the target object {}, please check the photo".format(target))
					self.speaker.say("I have found the target object {}, please check the photo".format(target), self.voice)
				else:
					rospy.loginfo("Sorry, I can't find the {} in the dining room".format(target))
					self.speaker.say("Sorry, I can't find the {} in the dining room".format(target), self.voice)
				break

	def found_it(self):
		rospy.loginfo("I have found the target object {}".format(target))
		self.speaker.say("I have found the target object {}".format(target), self.voice)
		rospy.loginfo("OK, take a photo")
		self.speaker.say("OK, take a photo", self.voice)
		self.take_photo.publish("take photo")
		return True

	def go_home(self):
		os.system("gnome-terminal -- bash -c 'rosrun rchomeedu_navigation nav3.py'")
		rospy.loginfo("Go back to Master!")
		self.speaker.say("Go back to Master!", self.voice)
		self._FLAG_NAVI = 3

	def _navi_callback(self, msg):
		if msg.data.find("done") > -1:
			os.system("rosnode kill /navi_point")
			self._FLAG_NAVI = 0

	def _voice_callback(self, msg):
		global target
		if msg.data.find("DINING") > -1 or msg.data.find("FIRE-HYDRANT") > -1:
			target = "fire hydrant"
			self._FLAG_CMD = 1

	def _vision_callback(self, msg):
		global obj
		for box in msg.bounding_boxes:
			obj = box.Class
			if obj == target:
				if self._FLAG_NAVI == 1:
					os.system("rosnode kill /navi_point")
					rospy.sleep(1)
					self._FLAG_NAVI = 10
				elif self._FLAG_NAVI == 2:
					os.system("rosnode kill /navi_point")
					rospy.sleep(1)
					self._FLAG_NAVI = 20
				elif self._FLAG_NAVI == 3 and self._FLAG_FOUND != 1:
					os.system("rosnode kill /navi_point")
					rospy.sleep(1)
					self._FLAG_NAVI = 30
				elif self._FLAG_NAVI == 0 and self._FLAG_EXECUTE == 1:
					self._FLAG_EXECUTE = 0
				self._FLAG_FOUND = 1

if __name__ == "__main__":
	controller = MissionDemo()
	controller.main_loop()
