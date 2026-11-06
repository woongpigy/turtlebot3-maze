// SPDX-License-Identifier: Apache-2.0

#include <cmath>
#include <limits>
#include <memory>

#include "geometry_msgs/msg/twist_stamped.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"

namespace
{

double wrap_pi(double angle)
{
  // 0이 정면, 오른쪽이 음수.
  return std::atan2(std::sin(angle), std::cos(angle));
}

double sector_min(const sensor_msgs::msg::LaserScan & scan, double start_deg, double end_deg)
{
  const double start = start_deg * M_PI / 180.0;
  const double end = end_deg * M_PI / 180.0;
  double best = std::numeric_limits<double>::infinity();
  double angle = scan.angle_min;
  for (const float dist : scan.ranges) {
    const double wrapped = wrap_pi(angle);
    if (start <= wrapped && wrapped <= end && std::isfinite(dist)) {
      best = std::min(best, static_cast<double>(dist));
    }
    angle += scan.angle_increment;
  }
  return best;
}

}  // namespace

class WallFollower : public rclcpp::Node
{
public:
  WallFollower()
  : Node("wall_follower")
  {
    cmd_pub_ = create_publisher<geometry_msgs::msg::TwistStamped>("cmd_vel", 10);
    // 라이다는 best effort 라 구독 QoS 를 맞춘다.
    scan_sub_ = create_subscription<sensor_msgs::msg::LaserScan>(
      "scan", rclcpp::SensorDataQoS(),
      std::bind(&WallFollower::on_scan, this, std::placeholders::_1));
  }

  void stop()
  {
    send(0.0, 0.0);
  }

private:
  void send(double linear_x, double angular_z)
  {
    geometry_msgs::msg::TwistStamped msg;
    msg.header.stamp = now();
    msg.twist.linear.x = linear_x;
    msg.twist.angular.z = angular_z;
    cmd_pub_->publish(msg);
  }

  void on_scan(const sensor_msgs::msg::LaserScan::SharedPtr scan)
  {
    const double front = sector_min(*scan, -10.0, 10.0);
    const double right = sector_min(*scan, -40.0, -10.0);

    if (front < 0.5) {
      // 앞이 막히면 제자리 좌회전.
      send(0.0, 0.4);
    } else if (right > max_distance_) {
      // 오른쪽 벽이 멀거나 없으면 오른쪽으로 붙는다.
      send(0.1, -0.2);
    } else if (right < min_distance_) {
      // 오른쪽 벽이 가까우면 왼쪽으로 벌린다.
      send(0.1, 0.2);
    } else {
      // 0.5~0.7 m 이면 직진. 미로에서 빠르면 0.5 를 낮춘다.
      send(0.5, 0.0);
    }
  }

  static constexpr double min_distance_ = 0.5;
  static constexpr double max_distance_ = 0.7;

  rclcpp::Publisher<geometry_msgs::msg::TwistStamped>::SharedPtr cmd_pub_;
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr scan_sub_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<WallFollower>();
  rclcpp::spin(node);
  node->stop();
  rclcpp::shutdown();
  return 0;
}
