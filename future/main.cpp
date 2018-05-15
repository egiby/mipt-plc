#include <iostream>
#include <thread>

#include <unistd.h>

#include "Future.h"
#include "ThreadPool.h"

int main() {
    SimpleThreadPool pool;
    pool.Init();

    std::function<int()> task = [] {
//        std::this_thread::sleep_for(std::chrono::seconds(3));
        return 5;
    };
    auto value = pool.TryEnqueue(task);

    assert(value);

    std::cout << *value.Get() << std::endl;

    return 0;
}