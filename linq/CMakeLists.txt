cmake_minimum_required(VERSION 3.10)
project(linq)

set(CMAKE_CXX_STANDARD 17)

set(LINQ_LIB
        common.h
        Collection.h
        )

add_executable(linq ${LINQ_LIB} main.cpp)