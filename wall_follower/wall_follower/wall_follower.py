#!/usr/bin/env python3
"""오른쪽 벽만 따라간다.

원본 wall_follower.py 에서 벽 따라가기만 남겼다.
Bug2, 가제보 런치는 빼 두었다.
https://github.com/CodeName-Detective/TurtleBot3-Navigation-Wall-Following-Bug2-Algorithm

버거 브링업(Jazzy)은 /cmd_vel 을 TwistStamped 로 받는다.
"""

import math

import rclpy
from geometry_msgs.msg import TwistStamped
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


def wrap_pi(angle):
    """각도를 -pi~pi 로 접는다. 0이 정면이고 오른쪽이 음수다."""
    return math.atan2(math.sin(angle), math.cos(angle))


def sector_min(scan, start_deg, end_deg):
    """start_deg~end_deg 사이 거리의 최솟값. 유효한 점이 없으면 inf."""
    start = math.radians(start_deg)
    end = math.radians(end_deg)
    best = math.inf
    angle = scan.angle_min
    for dist in scan.ranges:
        wrapped = wrap_pi(angle)
        if start <= wrapped <= end and math.isfinite(dist):
            best = min(best, dist)
        angle += scan.angle_increment
    return best


class WallFollow(Node):
    def __init__(self):
        super().__init__('wall_follower')
        # 오른쪽 벽을 이 거리 사이에 두고 간다.
        self.min_distance = 0.5
        self.max_distance = 0.7
        # 라이다는 best effort 라 구독 QoS 를 맞춘다.
        self.create_subscription(
            LaserScan, 'scan', self.on_scan, qos_profile_sensor_data)
        self.cmd_pub = self.create_publisher(TwistStamped, 'cmd_vel', 10)

    def send(self, linear_x, angular_z):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.twist.linear.x = linear_x
        msg.twist.angular.z = angular_z
        self.cmd_pub.publish(msg)

    def on_scan(self, scan):
        front = sector_min(scan, -10.0, 10.0)
        right = sector_min(scan, -40.0, -10.0)

        if front < 0.5:
            # 앞이 막히면 제자리 좌회전.
            self.send(0.0, 0.4)
        elif right > self.max_distance:
            # 오른쪽 벽이 멀거나 없으면 오른쪽으로 붙는다.
            self.send(0.1, -0.2)
        elif right < self.min_distance:
            # 오른쪽 벽이 가까우면 왼쪽으로 벌린다.
            self.send(0.1, 0.2)
        else:
            # 0.5~0.7 m 이면 직진. 미로에서 빠르면 0.5 를 낮춘다.
            self.send(0.5, 0.0)

    def stop(self):
        self.send(0.0, 0.0)


def main():
    rclpy.init()
    node = WallFollow()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
