from collections import defaultdict
from Box2D import *

import random

from .framework import FrameworkBase, Framework, Keys
import time
import math


class rigidPhysics(framework):
  """docstring for rigidPhysics"""
  def __init__(self, verbose=False, max_steps=200, renderer=None):
    super(rigidPhysics, self).__init__()
    self.damping = .3
    self.max_steps = max_steps
    self.verbose = verbose

    self.node_body = dict()
    self.next_id = 0

    # Non static bodies
    self.bodies = []
    # self.edges = set()
    self.joints = []
    self.contacts = []

    self.destroy_joints = []

  def create_static_box(self, position, dimensions):
    self.world.CreateStaticBody(
      position=position,
      shapes=b2PolygonShape(box=dimensions),
    )

  def run(self):
    if self.verbose:
      print('Physics: starting.')
    self.running = True
    self.stepCount = 0
    start = time.time()
    super(rigidPhysics, self).run()
    for node, body in self.node_body.items():
      node.px = body.position[0]
      node.py = body.position[1]
      node.angle = body.angle

    if self.verbose:
      print('Physics: finished after %i.' % self.stepCount)

  def finished(self):
    if self.stepCount > self.max_steps:
      return True
    if sum(b.awake for b in self.bodies) == 0:
      return True
    return False


  # def edges(self):
  #   for joint in self.joints:
  #     yield (bodyA, bodyB)

  def neighbors(self, body):
    for jointEdge in body.joints:
      yield jointEdge.other

  def remove_body(self, body):
    self.bodies.remove(body)
    self.world.DestroyBody(body)

  def add_body(self, position, size):
    friction = .1
    density = 10

    body = self.world.CreateBody(
      type=b2_dynamicBody,
      linearDamping=.5,
      position=(position[0], position[1]), # Copy object.
      userData={'name': 'node', 'id': self.next_id},
    )
    self.next_id += 1

    if len(size) == 1: # Circle
      body.CreateCircleFixture(
        shape=b2CircleShape(radius=size[0]),
        density=density, friction=friction
      )
    else: # Rectangle
      body.CreatePolygonFixture(
        box=(size[0]/2, size[1]/2),
        density=density, friction=friction
      )
      self.bodies.append(body)

    return body

  def add_edge(self, bodyA, bodyB):
    for jointEdge in bodyA.joints:
      if jointEdge.other == bodyB:
        return

    # self.edges.add((bodyA, bodyB))
    d = bodyA.position - bodyB.position
    djd = b2DistanceJointDef(
        frequencyHz=4.,
        dampingRatio=0.5,
        # length = 4,
        bodyA=bodyA,
        bodyB=bodyB,
        # anchorA=bodyA.worldCenter-d/4,
        # anchorB=bodyB.worldCenter+d/4,
        localAnchorA=(0,0),
        localAnchorB=(0,0),
        collideConnected=True
    )
    self.joints.append(self.world.CreateJoint(djd))

  def set_size(self, body, axis0, axis1):
    # print('set_size', (axis0, axis1))
    fixt = body.fixtures[0]
    body.DestroyFixture(fixt)
    body.CreateFixture(b2FixtureDef(
      shape=b2PolygonShape(box=(axis0/2, axis1/2)),
      density=4,
      friction=2
    ))
    body.awake = True

  # def neighbors(self, node):
  #   body_node = { v:k for k, v in self.node_body.items() }
  #   result = []
  #   for joint in self.world.joints:
  #     if body_node[joint.bodyA] == node:
  #       result.append(joint.bodyB.userData)
  #     elif body_node[joint.bodyB] == node:
  #       result.append(joint.bodyA.userData)

  #   return result

  # def edges(self):
  #   # body_node = { v:k for k, v in self.node_body.items() }
  #   result = []
  #   for joint in self.joints:
  #     result.append((joint.bodyA, joint.bodyB))
  #   return result

  def BeginContact(self, contact):
    self.contacts.append(contact)

  def clear_edges(self, body):
    for jointEdge in body.joints:
      self.destroy_joints.append(jointEdge.joint)
      self.joints.remove(jointEdge.joint)


  def split(self, body):
    fixt = body.fixtures[0]
    oldw = 2*abs(fixt.shape.vertices[0][0])
    oldh = 2*abs(fixt.shape.vertices[0][1])

    axis = 0
    if oldh > oldw:
      axis = 1

    angle   = body.angle - (math.radians(90) * (axis))
    angvect = b2Vec2(math.cos(angle), math.sin(angle))

    w = oldw
    h = oldh

    if axis == 0:
      w/=2
    else:
      h/=2

    self.set_size(body, w, h)
    daughter = self.add_body(body.position[0], body.position[1], [w, h])
    daughter.angle = body.angle

    if axis == 1:
      body.position -= angvect * (oldh/4)
      daughter.position += angvect * (oldh/4)
    else:
      body.position -= angvect * (oldw/4)
      daughter.position += angvect * (oldw/4)

    self.add_edge(body, daughter)
    return daughter

  def Keyboard(self, key):
    if key == Keys.K_g:
      grow = random.choice(self.bodies)
      fixt = grow.fixtures[0]
      x = abs(fixt.shape.vertices[0][0])
      y = abs(fixt.shape.vertices[0][1])

      grow.DestroyFixture(fixt)
      grow.CreateFixture(b2FixtureDef(
        shape=b2PolygonShape(box=(x, y+.3)),
        density=4,
        friction=2
      ))
    # if key == Keys.K_s:
    #   self.split(self.bodies[0])

  # Functions used by simulation
  def grow(self, body, g0, g1):
    fixt = body.fixtures[0]
    d0 = 2*abs(fixt.shape.vertices[0][0])
    d1 = 2*abs(fixt.shape.vertices[0][1])
    self.set_size(body, d0+g0, d1+g1)

  def area(self, body):
    fixt = body.fixtures[0]
    w = 2*abs(fixt.shape.vertices[0][0])
    h = 2*abs(fixt.shape.vertices[0][1])
    return w*h

  def Step(self, settings):
    for contact in self.contacts:
      bodyA, bodyB = (contact.fixtureA.body, contact.fixtureB.body)
      if bodyA.userData and bodyB.userData:
        # print(contact)
        self.add_edge(bodyA, bodyB)

    for joint in self.joints:
      f = joint.GetReactionForce(60.).Normalize()
      if f > 80000:
        self.world.DestroyJoint(joint)
        self.joints.remove(joint)
        joint = None

    for joint in self.destroy_joints:
      self.world.DestroyJoint(joint)
      joint = None

    self.contacts = []
    self.destroy_joints = []
    self.running = not self.finished()
    super(rigidPhysics, self).Step(settings)

    # vel = sum(b.linearVelocity.Normalize() for b in self.world.bodies)
    # print(vel)
    # for body in self.world.bodies:
    #   if body.linearVelocity.Normalize() < .01:
    #     body.awake = False
    # print(foo, iner)

    # for bodyA, bodyB in self.edges():
    #   d = bodyA.position - bodyB.position
    #   if d.Normalize() > 40:
    #     self.remove_edge(bodyA, bodyB)
      # d = (bodyA.position.x - bodyB.position.x)**2
