#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <trajectory_msgs/msg/joint_trajectory.hpp>
#include <string>
#include <vector>

class ExoToJointTrajectoryNode : public rclcpp::Node
{
public:
  ExoToJointTrajectoryNode()
  : Node("exo_to_joint_trajectory_node")
  {
    // Declare parameters
    this->declare_parameter<std::string>("source_topic", "real_robot/joint_states");
    this->declare_parameter<std::string>("target_topic", "/vx300s_right_arm_controller/joint_trajectory");
    this->declare_parameter<std::string>("target_joint_name", "vx300s_right_elbow");
    this->declare_parameter<int>("source_joint_index", 0);

    // Get parameters
    std::string source_topic = this->get_parameter("source_topic").as_string();
    target_topic_ = this->get_parameter("target_topic").as_string();
    target_joint_name_ = this->get_parameter("target_joint_name").as_string();
    source_joint_index_ = this->get_parameter("source_joint_index").as_int();

    // Create publisher
    pub_ = this->create_publisher<trajectory_msgs::msg::JointTrajectory>(target_topic_, 10);

    // Create subscriber
    sub_ = this->create_subscription<sensor_msgs::msg::JointState>(
      source_topic, 10,
      std::bind(&ExoToJointTrajectoryNode::jointStateCallback, this, std::placeholders::_1));

    RCLCPP_INFO(this->get_logger(), "ExoToJointTrajectoryNode started.");
    RCLCPP_INFO(this->get_logger(), "Subscribing to: %s", source_topic.c_str());
    RCLCPP_INFO(this->get_logger(), "Publishing to: %s", target_topic_.c_str());
    RCLCPP_INFO(this->get_logger(), "Mapping index %d to joint %s", source_joint_index_, target_joint_name_.c_str());
  }

private:
  void jointStateCallback(const sensor_msgs::msg::JointState::SharedPtr msg)
  {
    if (source_joint_index_ < 0 || static_cast<size_t>(source_joint_index_) >= msg->position.size()) {
      RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 5000,
        "Source joint index %d out of range (msg size: %zu)", source_joint_index_, msg->position.size());
      return;
    }

    double position = msg->position[source_joint_index_];

    auto traj_msg = trajectory_msgs::msg::JointTrajectory();
    traj_msg.header.stamp = this->now();
    traj_msg.joint_names.push_back(target_joint_name_);

    trajectory_msgs::msg::JointTrajectoryPoint point;
    point.positions.push_back(position);
    point.time_from_start = rclcpp::Duration::from_seconds(0.1); // Small duration for immediate execution

    traj_msg.points.push_back(point);

    pub_->publish(traj_msg);
  }

  rclcpp::Publisher<trajectory_msgs::msg::JointTrajectory>::SharedPtr pub_;
  rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr sub_;

  std::string target_topic_;
  std::string target_joint_name_;
  int source_joint_index_;
};

int main(int argc, char **argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ExoToJointTrajectoryNode>());
  rclcpp::shutdown();
  return 0;
}
