# CMakeList.txt : CMake project for nix_http_sp0re, include source and define
# project specific logic here.
#
cmake_minimum_required (VERSION 3.8)

project ("nix_http_sp0re")

set(BOOST_ROOT "C:\\Users\\zathras\\Documents\\boost_1_75_0")
#set(BOOST_LIBRARY_DIR "C:\\Users\\zathras\\Documents\\boost_1_75_0\\libs")
#set(Boost_NO_BOOST_CMAKE ON)
#set(Boost_USE_STATIC_LIBS OFF) 
#set(Boost_USE_MULTITHREADED ON)  
#set(Boost_USE_STATIC_RUNTIME OFF) 
#option(BOOST_DEBUG ON)

#add_library(boost INTERFACE)
#add_dependencies(boost ${BOOST_TARGET})
#target_include_directories(boost INTERFACE ${BOOST_ROOT})

find_package(Boost 1.75.0 REQUIRED COMPONENTS system uuid property_tree filesystem) 
add_definitions(${Boost_LIB_DIAGNOSTIC_DEFINITIONS})

# Add source to this project's executable.
if(Boost_FOUND)
    include_directories(${Boost_INCLUDE_DIRS}) 
    add_executable(nix_http_sp0re "main.cpp" "implant.h" "implant.cpp" "tasks.h" "results.h" "results.cpp" "tasks.cpp") 
    target_link_libraries(nix_http_sp0re ${Boost_LIBRARIES})
endif()

# TODO: Add tests and install targets if needed.
