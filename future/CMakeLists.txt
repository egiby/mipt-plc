cmake_minimum_required(VERSION 3.10)
project(future)

set(CMAKE_C_COMPILER /usr/bin/clang)
set(CMAKE_CXX_COMPILER /usr/bin/clang++)

FIND_PACKAGE(Threads)

set(CMAKE_CXX_STANDARD 11)

set(FUTURE_PROMICE
        AsyncData.h
        Future.h
        Exception.h
        ThreadPool.h)

add_executable(future ${FUTURE_PROMICE} main.cpp)

target_link_libraries(future ${CMAKE_THREAD_LIBS_INIT})