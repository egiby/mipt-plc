#include <thread>
#include <vector>
#include <functional>

#include "Future.h"

class SimpleThreadPool {
public:
    explicit SimpleThreadPool(int numThreads = std::thread::hardware_concurrency())
        : numThreads(numThreads),
          taskGuards(numThreads),
          notifiers(numThreads),
          isFree(numThreads),
          tasks(numThreads) {
    }

    void Init();

    template<class TResult>
    NAsync::Future<TResult> TryEnqueue(std::function<TResult()> task);

    ~SimpleThreadPool();

private:
    static void threadFunction(SimpleThreadPool& _this, int idx);

    std::vector<std::thread> workers;
    std::vector<std::mutex> taskGuards;
    std::vector<std::condition_variable> notifiers;
    std::vector<bool> isFree;
    std::vector<std::function<void()>> tasks;
    int numThreads;
};

void SimpleThreadPool::threadFunction(SimpleThreadPool& _this, int idx) {
    while (true) {
        std::unique_lock<std::mutex> lock(_this.taskGuards[idx]);
        _this.notifiers[idx].wait(lock, [&] {
            return !_this.isFree[idx];
        });

        _this.tasks[idx]();
        _this.isFree[idx] = true;
    }
}

template<class TResult>
NAsync::Future<TResult> SimpleThreadPool::TryEnqueue(std::function<TResult()> task) {
    auto* result = new NAsync::Promise<TResult>();

    std::function<void()> workerTask = [result, task] () {
        try {
            result->SetData(new TResult(task()));
        } catch (NAsync::AsyncException* e) {
            result->SetException(e);
        }
        delete result;
    };

    for (int i = 0; i < numThreads; ++i) {
        if (isFree[i]) {
            std::lock_guard<std::mutex> guard(taskGuards[i]);
            isFree[i] = false;
            tasks[i] = workerTask;
            notifiers[i].notify_all();

            return result->GetFuture();
        }
    }

    delete result;
    return NAsync::Future<TResult>();
}

void SimpleThreadPool::Init() {
    for (int i = 0; i < numThreads; ++i) {
        isFree[i] = true;
        workers.emplace_back(threadFunction, std::ref(*this), i);
        workers.back().detach();
    }
}

SimpleThreadPool::~SimpleThreadPool() {
    std::cerr << "destroy thread pool" << std::endl;
}
