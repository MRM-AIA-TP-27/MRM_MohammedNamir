#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/nav_sat_fix.hpp>
#include <sensor_msgs/msg/imu.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <std_srvs/srv/set_bool.hpp>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2/LinearMath/Matrix3x3.h>
#include <cmath>
#include <algorithm>

class GpsNavigator : public rclcpp::Node {
public:
    GpsNavigator() : Node("gps_navigator") {
        // --- Parameters ---
        this->declare_parameter<double>("target_x", 0.0);
        this->declare_parameter<double>("target_y", 0.0);

        // --- Publishers & Subscribers ---
        cmd_vel_pub_ = this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);

        gps_sub_ = this->create_subscription<sensor_msgs::msg::NavSatFix>(
            "/gps_plugin/out", 10,
            std::bind(&GpsNavigator::gps_callback, this, std::placeholders::_1));

        imu_sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
            "/imu", 10,
            std::bind(&GpsNavigator::imu_callback, this, std::placeholders::_1));

        // --- Services & Timers ---
        start_service_ = this->create_service<std_srvs::srv::SetBool>(
            "start_navigation",
            std::bind(&GpsNavigator::handle_start_nav, this, std::placeholders::_1, std::placeholders::_2));

        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(100),
            std::bind(&GpsNavigator::navigate, this));

        RCLCPP_INFO(this->get_logger(), "GPS Navigator Ready.");
    }

private:
    void handle_start_nav(const std::shared_ptr<std_srvs::srv::SetBool::Request> request,
                          std::shared_ptr<std_srvs::srv::SetBool::Response> response) 
    {
        this->get_parameter("target_x", target_x_);
        this->get_parameter("target_y", target_y_);

        is_active_ = request->data;
        goal_reached_ = false; 
        
        response->success = true;
        if (is_active_) {
            response->message = "Heading to X: " + std::to_string(target_x_) + " Y: " + std::to_string(target_y_);
        } else {
            response->message = "Rover STOPPED";
            stop_robot();
        }
        
        RCLCPP_INFO(this->get_logger(), "%s", response->message.c_str());
    }

    void gps_callback(const sensor_msgs::msg::NavSatFix::SharedPtr msg) {
        if (!origin_set_) {
            origin_lat_ = msg->latitude;
            origin_lon_ = msg->longitude;
            origin_set_ = true;
            RCLCPP_INFO(this->get_logger(), "GPS ORIGIN SET: Lat %.6f, Lon %.6f", origin_lat_, origin_lon_);
        }

        // Convert Lat/Lon to Meters using Equirectangular projection
        // X = Easting, Y = Northing
        double dlat = (msg->latitude - origin_lat_) * M_PI / 180.0;
        double dlon = (msg->longitude - origin_lon_) * M_PI / 180.0;

        current_x_ = dlon * std::cos(origin_lat_ * M_PI / 180.0) * EARTH_RADIUS;
        current_y_ = dlat * EARTH_RADIUS;
        gps_received_ = true;
    }

    void imu_callback(const sensor_msgs::msg::Imu::SharedPtr msg) {
        tf2::Quaternion q(
            msg->orientation.x, 
            msg->orientation.y, 
            msg->orientation.z, 
            msg->orientation.w
        );
        tf2::Matrix3x3 m(q);
        double r, p, y;
        m.getRPY(r, p, y);
        current_yaw_ = y; // Typically 0 is East in ENU
        imu_received_ = true;
    }

void navigate() {
    if (!is_active_ || !gps_received_ || !imu_received_ || !origin_set_ || goal_reached_) {
        return;
    }

    // --- 1. Calculate Error ---
    double dx = target_x_ - current_x_;
    double dy = target_y_ - current_y_;
    double distance = std::hypot(dx, dy);
    
    // Target heading in Radians
    double target_heading = std::atan2(dy, dx);
    double angle_error = target_heading - current_yaw_;

    // Normalize angle to [-PI, PI]
    while (angle_error > M_PI)  angle_error -= 2.0 * M_PI;
    while (angle_error < -M_PI) angle_error += 2.0 * M_PI;

    geometry_msgs::msg::Twist cmd;

    // --- 2. State Machine Logic ---
    if (distance < STOP_TOL) {
        RCLCPP_INFO(this->get_logger(), "GOAL REACHED! Distance: %.2f", distance);
        stop_robot();
        goal_reached_ = true;
        is_active_ = false;
        return;
    }

    if (std::abs(angle_error) > ALIGN_TOL) {
        // High angle error: Rotate in place until aligned
        cmd.linear.x = 0.0;
        // Corrected clamp: -0.8 to 0.8
        cmd.angular.z = std::clamp(1.5 * angle_error, -0.8, 0.8);
    } else {
        // Aligned: Move forward and adjust heading slightly
        // Increased min linear speed to 0.2 to ensure movement
        cmd.linear.x = std::clamp(0.5 * distance, 0.2, 0.8);
        // Corrected clamp: -0.5 to 0.5 (was -0.4 to -0.4)
        cmd.angular.z = std::clamp(0.8 * angle_error, -0.5, 0.5);
    }

    cmd_vel_pub_->publish(cmd);
}

    void stop_robot() {
        geometry_msgs::msg::Twist stop_cmd;
        cmd_vel_pub_->publish(stop_cmd);
    }

    // --- Configuration ---
    static constexpr double EARTH_RADIUS = 6371000.0; // Meters
    const double STOP_TOL = 0.5;   // Stop within 0.5m of goal
    const double ALIGN_TOL = 0.15; // Start moving when within ~8 degrees

    // --- State Variables ---
    double origin_lat_{0.0}, origin_lon_{0.0};
    double current_x_{0.0}, current_y_{0.0}, current_yaw_{0.0};
    double target_x_{0.0}, target_y_{0.0};
    
    bool is_active_{false}, origin_set_{false};
    bool gps_received_{false}, imu_received_{false}, goal_reached_{false};

    // --- ROS Objects ---
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_pub_;
    rclcpp::Subscription<sensor_msgs::msg::NavSatFix>::SharedPtr gps_sub_;
    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
    rclcpp::Service<std_srvs::srv::SetBool>::SharedPtr start_service_;
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<GpsNavigator>());
    rclcpp::shutdown();
    return 0;
}
