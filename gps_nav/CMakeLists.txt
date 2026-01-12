cmake_minimum_required(VERSION 3.8)
project(gps_nav)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(std_srvs REQUIRED)

# 1. Define the executable
add_executable(gps_navigator src/gps_navigator.cpp)

# 2. Add dependencies
ament_target_dependencies(gps_navigator 
  rclcpp 
  sensor_msgs 
  geometry_msgs 
  tf2 
  tf2_geometry_msgs
  std_srvs
)

# 3. Install targets
install(TARGETS
  gps_navigator
  DESTINATION lib/${PROJECT_NAME}
)

# 4. Install directories (URDF and Launch)
install(DIRECTORY urdf launch
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
