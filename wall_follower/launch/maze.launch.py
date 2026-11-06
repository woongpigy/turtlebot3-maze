import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    # 터틀봇3 런치 파일들이 이 값을 읽는다. 지정하지 않았으면 burger.
    os.environ.setdefault('TURTLEBOT3_MODEL', 'burger')

    tb3_launch = os.path.join(get_package_share_directory('turtlebot3_gazebo'), 'launch')
    ros_gz_sim = get_package_share_directory('ros_gz_sim')
    world = os.path.join(get_package_share_directory('wall_follower'), 'worlds', 'maze.sdf')

    def include(path, args):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(path), launch_arguments=args.items())

    return LaunchDescription([
        AppendEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            os.path.join(get_package_share_directory('turtlebot3_gazebo'), 'models')),
        # Gazebo 서버와 화면
        include(os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py'),
                {'gz_args': f'-r -s -v2 {world}', 'on_exit_shutdown': 'true'}),
        include(os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py'),
                {'gz_args': '-g -v2', 'on_exit_shutdown': 'true'}),
        include(os.path.join(tb3_launch, 'robot_state_publisher.launch.py'),
                {'use_sim_time': 'true'}),
        # 로봇은 입구 칸(S)에서 동쪽(+x)을 보고 시작한다.
        include(os.path.join(tb3_launch, 'spawn_turtlebot3.launch.py'),
                {'x_pose': '-2.0', 'y_pose': '-2.0'}),
    ])
