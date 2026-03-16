from os import times
import random
import numpy as np
import sys
import rospy
from qt_robot_interface.srv import *
from qt_motors_controller.srv import *
from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState

rospy.init_node('qt_motors_command')
rospy.loginfo("This is when random movements start!")

head_pub   = rospy.Publisher('/qt_robot/head_position/command',       Float64MultiArray, queue_size=10)
right_pub  = rospy.Publisher('/qt_robot/right_arm_position/command',  Float64MultiArray, queue_size=10)
left_pub   = rospy.Publisher('/qt_robot/left_arm_position/command',   Float64MultiArray, queue_size=10)

setVelocity = rospy.ServiceProxy('/qt_robot/motors/setVelocity', set_velocity)


class randomClassAbstract:
    def __init__(self, joints, jointParallel, velMin, velMax, angleMin, angleMax, jerkMin, jerkMax, selectZero):
        self.joints        = joints
        self.jointParallel = jointParallel
        self.velMin        = velMin
        self.velMax        = velMax
        self.angleMin      = angleMin
        self.angleMax      = angleMax
        self.jerkMin       = jerkMin
        self.jerkMax       = jerkMax
        self.selectZero    = selectZero

    def create_movement_vel(self):
        jointVelocities = dict.fromkeys(self.joints, False)

        for joint in jointVelocities:
            if joint in self.jointParallel:
                if jointVelocities[joint] == False:
                    jointMove = random.choice([False, True])

                    if jointMove:
                        jointVelocities[joint] = random.randint(self.velMin, self.velMax)
                        jointVelocities[self.jointParallel[joint]] = jointVelocities[joint]
                    else:
                        options = [joint, self.jointParallel[joint]]
                        whichJointMove = random.choice(options)
                        jointVelocities[whichJointMove] = random.randint(0, self.velMax)
                        otherJoint = options[1] if whichJointMove == options[0] else options[0]
                        jointVelocities[otherJoint] = 0
            else:
                jointVelocities[joint] = random.randint(self.velMin, self.velMax)

        print("Velocities:", jointVelocities)
        return jointVelocities

    def create_movement_angle(self):
        jointAngles = dict.fromkeys(self.joints, False)

        for joint in self.jointParallel:
            if jointAngles[joint] == False:
                jointMove = random.choice([False, True])

                if jointMove:
                    jointAngles[joint] = random.uniform(self.angleMin, self.angleMax)
                    jointAngles[self.jointParallel[joint]] = jointAngles[joint]
                else:
                    options = [joint, self.jointParallel[joint]]
                    whichJointMove = random.choice(options)
                    jointAngles[whichJointMove] = random.uniform(self.angleMin, self.angleMax)
                    otherJoint = options[1] if whichJointMove == options[0] else options[0]
                    jointAngles[otherJoint] = 0

        for joint in self.joints:
            if jointAngles[joint] == False:
                jointAngles[joint] = random.uniform(self.angleMin, self.angleMax)

        print("Angles:", jointAngles)
        return jointAngles

    def create_movement_jerk(self, initial_velocities=None, duration=5.0, dt=0.05):
        if initial_velocities is None:
            initial_velocities = self.create_movement_vel()

        times_arr = list(np.arange(0, duration + dt, dt))
        movement_profiles = {}

        for joint in self.joints:
            v0   = initial_velocities.get(joint, 0) or 0
            jerk = random.uniform(self.jerkMin, self.jerkMax)
            velocities = []
            v = v0
            a = 0.0

            for i, t in enumerate(times_arr):
                a += jerk * dt
                v += a * dt

                if v >= self.velMax:
                    v    = self.velMax
                    a    = -abs(a)
                    jerk = -abs(jerk)
                elif v <= 0 and a < 0:
                    v = 0
                    a = 0

                if i >= len(times_arr) - 1:
                    v = 0
                    a = 0
                velocities.append(v)

            movement_profiles[joint] = {
                'times':      times_arr,
                'velocities': velocities,
                'jerk':       jerk
            }

        return movement_profiles

    def run_full(self, time, sequence):
        v_seq = []
        for _ in range(sequence):
            v_seq.append(self.create_movement_vel())
        return v_seq

    def apply_movement(self):
        pass


if __name__ == "__main__":
    print("hello!")

    ALL_JOINTS = [
        'RightShoulderPitch', 'RightShoulderRoll', 'RightElbowRoll',
        'LeftShoulderPitch',  'LeftShoulderRoll',  'LeftElbowRoll',
        'HeadYaw',            'HeadPitch',
    ]

    PARALLEL = {
        'RightShoulderPitch': 'LeftShoulderPitch',
        'RightShoulderRoll':  'LeftShoulderRoll',
        'RightElbowRoll':     'LeftElbowRoll',
    }

    test1 = randomClassAbstract(
        joints        = ALL_JOINTS,
        jointParallel = PARALLEL,
        #might need to update these ranges based on what the robot can actually do - these are just placeholders for now
        velMin   = random.randint(-100, 50),
        velMax   = random.randint(50, 100),
        angleMin = random.randint(-100, 50),
        angleMax = random.randint(50, 100),
        jerkMin  = 0.5,
        jerkMax  = 0.8,
        selectZero = None
    )

    jointVelocities = test1.create_movement_vel()
    jointAngles     = test1.create_movement_angle()

    for j in ALL_JOINTS:
        print(f"  {j:30s}  angle={jointAngles.get(j):.2f}  vel={jointVelocities.get(j)}")

    while not rospy.is_shutdown():
        rospy.wait_for_service('/qt_robot/motors/setVelocity')
        try:
            print('Publishing movement commands...')
            rospy.sleep(5)

            rref = Float64MultiArray()
            rref.data = [
                jointAngles['RightShoulderPitch'],
                jointAngles['RightShoulderRoll'],
                jointAngles['RightElbowRoll'],
            ]
            right_pub.publish(rref)

            lref = Float64MultiArray()
            lref.data = [
                jointAngles['LeftShoulderPitch'],
                jointAngles['LeftShoulderRoll'],
                jointAngles['LeftElbowRoll'],
            ]
            left_pub.publish(lref)

            href = Float64MultiArray()
            href.data = [
                jointAngles['HeadYaw'],
                jointAngles['HeadPitch'],
            ]
            head_pub.publish(href)

            jointVelocities = test1.create_movement_vel()
            jointAngles     = test1.create_movement_angle()

        except KeyboardInterrupt:
            pass

    rospy.loginfo("finished!")
    rospy.loginfo("No more random moves!")