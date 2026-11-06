# turtlebot3-maze

터틀봇3가 **오른쪽 벽을 따라** 움직이는 ROS 2 예제 패키지입니다.
오른쪽 손을 벽에 대고 걷는 것처럼, 오른쪽 벽과의 거리를 일정하게 유지하며 나아갑니다.

## 환경

- Ubuntu 24.04
- ROS 2 Jazzy
- TurtleBot3 (burger 기준), 또는 TurtleBot3 Gazebo 시뮬레이션

## 빌드

```bash
mkdir -p ~/maze_ws/src && cd ~/maze_ws/src
git clone <이 저장소 주소>
cd ~/maze_ws
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
```

## 실행

### 시뮬레이션 (Gazebo)

터미널 1 — Gazebo 실행:

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

터미널 2 — 벽 따라가기 실행:

```bash
source ~/maze_ws/install/setup.bash
ros2 launch wall_follower wall_follower.launch.py
```

### 실제 로봇

로봇에서 bringup을 먼저 실행한 뒤, PC에서 위의 터미널 2 명령을 실행합니다.

```bash
# 로봇(라즈베리파이)에서
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_bringup robot.launch.py
```

로봇과 PC의 `ROS_DOMAIN_ID`가 같아야 합니다.

### 멈추기

`Ctrl+C`를 누르면 노드가 종료되기 직전에 정지 명령을 보내 로봇이 멈춥니다.

## 동작 원리

라이다(`/scan`)에서 두 구역의 가장 가까운 거리를 구합니다.

| 구역 | 각도 | 의미 |
|---|---|---|
| 앞 | -10° ~ 10° | 정면 장애물 |
| 오른쪽 | -40° ~ -10° | 오른쪽 앞 대각선의 벽 |

(0°가 정면, 음수가 오른쪽입니다.)

그 값에 따라 `/cmd_vel`로 아래 명령을 보냅니다. 위에서부터 먼저 맞는 조건 하나만 실행합니다.

| 상황 | 동작 | 직진 (m/s) | 회전 (rad/s) |
|---|---|---|---|
| 앞이 0.5 m 안으로 막힘 | 제자리 좌회전 | 0.0 | 0.4 |
| 오른쪽 벽이 0.7 m보다 멀거나 없음 | 오른쪽으로 붙기 | 0.1 | -0.2 |
| 오른쪽 벽이 0.5 m보다 가까움 | 왼쪽으로 벌리기 | 0.1 | 0.2 |
| 오른쪽 벽이 0.5 ~ 0.7 m | 직진 | 0.2 | 0.0 |

라이다가 측정에 실패해 보내는 값(0 또는 `inf`)은 `range_min` ~ `range_max` 범위로 걸러서 무시합니다.

## 바꿔 볼 만한 값

모두 `wall_follower/src/wall_follower.cpp`에 있습니다. 바꾼 뒤에는 `colcon build`를 다시 해야 합니다.

- `min_distance_`, `max_distance_` — 오른쪽 벽과 유지할 거리 범위
- `on_scan()` 안의 `front < 0.5` — 앞이 막혔다고 판단하는 거리
- `send(직진, 회전)` 값 — 속도. burger의 최고 직진 속도는 약 0.22 m/s입니다.

## 토픽

| 토픽 | 타입 | 방향 |
|---|---|---|
| `/scan` | `sensor_msgs/msg/LaserScan` | 구독 |
| `/cmd_vel` | `geometry_msgs/msg/TwistStamped` | 발행 |

## 라이선스

Apache-2.0
