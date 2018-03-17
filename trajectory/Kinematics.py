import sys
import traceback
from MotorClient import MotorClient
from fabrik.FabrikSolver import FabrikSolver
from fabrik.JointChain import JointChain
from fabrik.Joint import Joint
from fabrik.ConformalGeometricAlgebra import ConformalGeometricAlgebra
import math
import json

class Kinematics():

    def __init__(self):
        self.cga = ConformalGeometricAlgebra(1e-11)
        self.fabrik_solver = FabrikSolver()

    def get_joint_chain(self):
        first_joint = Joint(2 * math.pi, 50.0)
        second_joint = Joint(2 *math.pi, 50.0)
        joint_chain = JointChain([first_joint, second_joint])
        return joint_chain

    def get_angles_from_path(self, path):
        return [self.get_angles_from_coordinate(coordinate[0], coordinate[1], coordinate[2]) for coordinate in path]

    def get_angles_from_coordinate(self, x, y, z):
        joint_chain = self.get_joint_chain()
        target_point = self.cga.point(x, y, z)
        positions = self.fabrik_solver.solve(joint_chain, target_point)
        rotors = self.fabrik_solver.toRotors(positions)
        angles = [self.cga.angleFromRotor(rotor) for rotor in rotors]
        return angles
