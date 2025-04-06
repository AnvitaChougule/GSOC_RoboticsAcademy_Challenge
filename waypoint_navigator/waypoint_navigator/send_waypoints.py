import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from rclpy.action import ActionClient  
from nav2_msgs.action import FollowWaypoints 

class WaypointNavigator(Node):
    def __init__(self):
        super().__init__('waypoint_navigator')
        self.client = ActionClient(self, FollowWaypoints, '/follow_waypoints') 

        self.get_logger().info("Waiting for waypoint follower action server...")
        self.client.wait_for_server()

        self.send_waypoints()

    def send_waypoints(self):
        goal_msg = FollowWaypoints.Goal()  
        goal_msg.poses = []

        waypoints = [
            (1.0, 1.0),
            (2.0, 2.0),
            (3.0, 3.0)
        ]

        for x, y in waypoints:
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.orientation.w = 1.0 
            goal_msg.poses.append(pose)

        self.get_logger().info("Sending waypoints...")
        self.client.send_goal_async(goal_msg)
        
def main(args=None):
    rclpy.init(args=args)
    navigator = WaypointNavigator()
    rclpy.spin(navigator)
    navigator.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
