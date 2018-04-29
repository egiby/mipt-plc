cmake_minimum_required(VERSION 3.10)
project(linq)

set(CMAKE_CXX_STANDARD 17)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")

set(LINQ_LIB
        common.h
        Sequence.h
        Sequence.cpp pipeline/Pipeline.h)

include_directories(.)

add_executable(linq ${LINQ_LIB} main.cpp)