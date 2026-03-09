from os import times
import random
import numpy as np
import matplotlib.pyplot as plt
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
    
    def create_movement_jerk(self, initial_velocities=None, duration=5.0, dt=0.05):
    
        if initial_velocities is None:
            initial_velocities = self.create_movement_vel()
    
        times = list(np.arange(0, duration + dt, dt))
        movement_profiles = {}
    
        for joint in self.joints:                        
            v0 = initial_velocities.get(joint, 0) or 0
            jerk = random.uniform(self.jerkMin, self.jerkMax)
            velocities = []
            v = v0
            a = 0.0
    
            for i, t in enumerate(times):                              
                a += jerk * dt
                v += a * dt

                if v >= self.velMax:
                    v = self.velMax
                    a = -abs(a)
                    jerk = -abs(jerk)  
                elif v <= 0 and a < 0:
                    v = 0
                    a = 0

                if i >= len(times) - 1:  # duration reached, stop
                    v = 0
                    a = 0
                velocities.append(v)
            
    
            movement_profiles[joint] = {                   
                'times': times,
                'velocities': velocities,
                'jerk': jerk
            }
    
        return movement_profiles                        
    
    
   
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
                                random.uniform(0.1, 0.299), random.uniform(0.5, 0.9), None, None, 0.5, 0.8, None) 
    test1.create_movement_vel()
    profiles = test1.create_movement_jerk(duration=2.0, dt=0.05)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    for joint, data in profiles.items():
        line = ax1.plot(data['times'], data['velocities'], label=joint)
        color = line[0].get_color()
        ax2.axhline( y=data['jerk'],linestyle='--',color=color,label=joint)

        print(f"Joint {joint}: jerk = {data['jerk']}")
        print(f"Joint {joint}: velocities = {data['velocities']}")

    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Velocity')
    ax1.set_title('Joint Velocity Profiles via Euler Integration')
    ax1.legend(loc='upper right', fontsize=7)

    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Jerk')
    ax2.set_title('Joint Jerk Values')
    ax2.legend(loc='upper right', fontsize=7)

    plt.tight_layout()
    plt.show()
    
if __name__ == "__main__":
    main()
