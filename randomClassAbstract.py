import random
class randomClassAbstract:
    def __init__(self, joints, jointParallel, velMin, velMax, angleMin, angleMax, jerkMin, jerkMax, selectZero):
        self.joints = joints
        self.jointParallel = jointParallel
        self.velMin = velMin
        self.velMax = velMax
        self.angleMin = angleMin
        self.angleMax = angleMax
        self.jerkMin = jerkMin
        self.jerkMax = jerkMax  
        self.selectZero = selectZero
        
    def create_movement_vel(self):
        jointVelocities = dict.fromkeys(self.joints, False)
        
        for joint in jointVelocities:
            if joint in self.jointParallel:
                if jointVelocities[joint] == False:
                    jointMove = random.choice([False, True])
                    print(jointMove)
                    
                    if jointMove == True:
                        jointVelocities[joint] = random.uniform(self.velMin, self.velMax)
                        jointVelocities[self.jointParallel[joint]] = jointVelocities[joint]
                        
                    if jointMove == False:
                        options = [joint, self.jointParallel[joint]]
                        whichJointMove = random.choice(options)
                        jointVelocities[whichJointMove] = random.uniform(0, self.velMax)
                        otherJoint = options[1] if whichJointMove == options[0] else options[0] 
                        jointVelocities[otherJoint] = 0
                        
            else:
                jointVelocities[joint]=random.uniform(self.velMin, self.velMax)
        print(jointVelocities)
        return jointVelocities 
    
    def create_movement_angle(self):
        pass
        #head yaw
        #right shoulder pitch
        #left shoulder pitch
    
    def create_movement_jerk(self):
        pass
    
   
    def run_full(self, time, sequence):
        v_seq = []
        for _ in range(sequence):
            v_seq.append(self.create_movement())
        return v_seq
            
    
    def apply_movement(self):
        pass
    
def main():
    print("hello!")
    #update dictionary to have all of the joint DOF (right arm roll, etc etc)
    test1 = randomClassAbstract(['RightShoulderPitch', 'RightShoulderRoll', 'RightElbowRoll', 'LeftShoulderPitch', 'LeftShoulderRoll', 'LeftElbowRoll'], 
                                {'RightShoulderPitch': 'LeftShoulderPitch', 'RightShoulderRoll': 'LeftShoulderRoll', 'RightElbowRoll': 'LeftElbowRoll'},
                                0.1, 1, None, None, None, None, None) 
    test1.create_movement_vel()
    
if __name__ == "__main__":
    main()
