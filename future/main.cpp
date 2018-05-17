#include <iostream>
#include <thread>

#include <unistd.h>

#include "Future.h"
#include "Async.h"

int main() {
    NAsync::ThreadPool pool;

    srand(501);

    std::function<int(int, int)> task = [](int time, int result) {
//        std::this_thread::sleep_for(std::chrono::seconds(time));
//        throw 1;
        return result;
    };

    std::vector<NAsync::Future<int>> tasks;
    for (int i = 0; i < 10; ++i) {
        tasks.push_back(NAsync::Async(NAsync::LaunchPolicy::Async, &pool, task, 3, 10 - i));
    }

    for (auto &value: tasks) {
        try {
            std::cout << *value.Get() << std::endl;
        } catch (NAsync::AsyncException *e) {
            std::unique_ptr<NAsync::AsyncException> exception(e);
            std::cerr << exception->what() << std::endl;
        }
    }

    for (int i = 0; i < 10; ++i) {
        tasks[i] = NAsync::Async(NAsync::LaunchPolicy::Async, &pool, task, 3, 10 - i);
    }

    for (auto &value: tasks) {
        try {
            std::cout << *value.Get() << std::endl;
        } catch (NAsync::AsyncException *e) {
            std::unique_ptr<NAsync::AsyncException> exception(e);
            std::cerr << exception->what() << std::endl;
        }
    }

    return 0;
}