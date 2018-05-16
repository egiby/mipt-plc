#include <iostream>
#include <thread>

#include <unistd.h>

#include "Future.h"
#include "Async.h"

int main() {
    SimpleThreadPool pool;
    pool.Init();

    srand(501);

    std::function<int(int, int)> task = [](int time, int result) {
        std::this_thread::sleep_for(std::chrono::seconds(time));
        return result;
    };

    std::vector<NAsync::Future<int>> tasks;
    for (int i = 0; i < 8; ++i) {
        tasks.push_back(NAsync::Async(NAsync::LaunchPolicy::Async, &pool, task, 1, 8 - i));
    }

    for (auto &value: tasks)
        std::cout << *value.Get() << std::endl;

    return 0;
}