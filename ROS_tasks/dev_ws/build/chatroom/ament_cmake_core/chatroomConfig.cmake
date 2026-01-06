# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_chatroom_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED chatroom_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(chatroom_FOUND FALSE)
  elseif(NOT chatroom_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(chatroom_FOUND FALSE)
  endif()
  return()
endif()
set(_chatroom_CONFIG_INCLUDED TRUE)

# output package information
if(NOT chatroom_FIND_QUIETLY)
  message(STATUS "Found chatroom: 0.0.0 (${chatroom_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'chatroom' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT ${chatroom_DEPRECATED_QUIET})
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(chatroom_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${chatroom_DIR}/${_extra}")
endforeach()
