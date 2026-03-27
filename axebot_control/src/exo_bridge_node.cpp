#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/joint_state.hpp>

#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <atomic>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

class ExoBridgeNode : public rclcpp::Node {
public:
  ExoBridgeNode() : Node("exo_bridge_node") {

    this->declare_parameter<int>("listen_port", 5005);
    this->declare_parameter<int>("joint_count", 1);

    int port = this->get_parameter("listen_port").as_int();
    joint_count_ = this->get_parameter("joint_count").as_int();

    for (int i = 0; i < joint_count_; ++i) {
      joint_names_.push_back("joint_" + std::to_string(i + 1));
    }

    pub_ = this->create_publisher<sensor_msgs::msg::JointState>(
        "real_robot/joint_states", 10);

    sockfd_ = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd_ < 0) {
      RCLCPP_FATAL(this->get_logger(), "Failed to create socket");
      rclcpp::shutdown();
      return;
    }

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(static_cast<uint16_t>(port));

    if (bind(sockfd_, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
      RCLCPP_FATAL(this->get_logger(), "Failed to bind socket");
      close(sockfd_);
      rclcpp::shutdown();
      return;
    }

    // Receive timeout for clean shutdown
    timeval tv{};
    tv.tv_sec = 0;
    tv.tv_usec = 500000;
    setsockopt(sockfd_, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    RCLCPP_INFO(this->get_logger(), "Listening on UDP port %d", port);

    recv_thread_ = std::thread(&ExoBridgeNode::receiveLoop, this);
  }

  ~ExoBridgeNode() {
    running_ = false;
    if (recv_thread_.joinable()) {
      recv_thread_.join();
    }
    close(sockfd_);
  }

private:
  void receiveLoop() {
    char buffer[4096];

    while (rclcpp::ok() && running_) {
      ssize_t len = recv(sockfd_, buffer, sizeof(buffer) - 1, 0);
      if (len <= 0) {
        continue;
      }

      buffer[len] = '\0';
      std::string data(buffer);

      // Parse CSV
      std::vector<double> values;
      std::stringstream ss(data);
      std::string token;

      while (std::getline(ss, token, ',')) {
        try {
          values.push_back(std::stod(token));
        } catch (...) {
        }
      }

      const size_t expected_size = joint_count_ * 2;
      if (values.size() != expected_size) {
        RCLCPP_WARN(this->get_logger(), "Received %zu values, expected %zu",
                    values.size(), expected_size);
        continue;
      }

      auto msg = sensor_msgs::msg::JointState();
      msg.header.stamp = this->now();
      msg.name = joint_names_;
      msg.position.resize(joint_count_);
      msg.velocity.resize(joint_count_);

      // First N values → position
      // Next N values → velocity
      for (int i = 0; i < joint_count_; ++i) {
        msg.position[i] = values[i];
        msg.velocity[i] = values[i + joint_count_];
      }

      pub_->publish(msg);
    }
  }

  rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr pub_;
  std::vector<std::string> joint_names_;

  int joint_count_{14};
  int sockfd_{-1};

  std::thread recv_thread_;
  std::atomic<bool> running_{true};
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ExoBridgeNode>());
  rclcpp::shutdown();
  return 0;
}
