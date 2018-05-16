#include <iostream>
#include <thread>

#include <unistd.h>

#include "Future.h"
#include "Async.h"

int main() {
    SimpleThreadPool pool;
    pool.Init();

    srand(501);

    std::function<int()> task = [] {
        int time = rand() % 10;
        std::this_thread::sleep_for(std::chrono::seconds(time));
        return time;
    };
    std::vector<NAsync::Future<int>> tasks;
    for (int i = 0; i < 8; ++i) {
        tasks.push_back(NAsync::Async(task, NAsync::LaunchPolicy::Async, &pool));
    }

    for (auto &value: tasks)
        std::cout << *value.Get() << std::endl;

    return 0;
}