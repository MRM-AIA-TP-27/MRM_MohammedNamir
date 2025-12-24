#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include <iostream>
#include <string>
#include <thread>

using namespace std;

class ChatNode : public rclcpp::Node {
public:
    ChatNode() : Node("chat_user") {
        // FIXED: Changed string to String
        pub_ = this->create_publisher<std_msgs::msg::String>("/chat_topic", 10);

        // FIXED: Changed string to String
        sub_ = this->create_subscription<std_msgs::msg::String>(
            "/chat_topic", 10, std::bind(&ChatNode::on_message, this, std::placeholders::_1));

        cout << "Enter Username: ";
        getline(cin, user_name_);

        input_thread_ = std::thread(&ChatNode::send_loop, this);
    }

private:
    // FIXED: Changed string to String
    void on_message(const std_msgs::msg::String::SharedPtr msg) {
        if (msg->data.find(user_name_ + ":") != 0) {
            cout << "\n" << msg->data << "\n> " << flush;
        }
    }

    void send_loop() {
        while (rclcpp::ok()) {
            string input;
            cout << "> ";
            getline(cin, input);
            if (!input.empty()) {
                // FIXED: Changed string to String
                auto msg = std_msgs::msg::String();
                msg.data = user_name_ + ": " + input;
                pub_->publish(msg);
            }
        }
    }

    string user_name_;
    std::thread input_thread_;
    // FIXED: Changed string to String
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_;
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr sub_;
};

int main(int argc, char ** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<ChatNode>());
    rclcpp::shutdown();
    return 0;
}
