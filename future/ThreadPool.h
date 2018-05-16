#pragma once

#include <thread>
#include <vector>
#include <functional>
#include <future>

#include "Future.h"

class SimpleThreadPool {
public:
    explicit SimpleThreadPool(int numThreads = std::thread::hardware_concurrency())
        : numThreads(numThreads),
          taskGuards(numThreads),
          notifiers(numThreads),
          isFree(numThreads),
          tasks(numThreads),
          stop(false) {
    }

    void Init();

    template<class TResult>
    NAsync::Future<TResult> TryEnqueueSimple(std::function<TResult()> task);

    template<class TResult, class... Args>
    NAsync::Future<TResult> TryEnqueue(std::function<TResult(Args...)> task, Args... args);

    ~SimpleThreadPool();

private:
    static void threadFunction(SimpleThreadPool& _this, int idx);

    std::vector<std::thread> workers;
    std::vector<std::mutex> taskGuards;
    std::vector<std::condition_variable> notifiers;
    std::vector<bool> isFree;
    std::vector<std::function<void()>> tasks;
    int numThreads;
    bool stop;
};

inline void SimpleThreadPool::threadFunction(SimpleThreadPool& _this, int idx) {
    while (!_this.stop) {
        std::unique_lock<std::mutex> lock(_this.taskGuards[idx]);
        _this.notifiers[idx].wait(lock, [&] {
            return !_this.isFree[idx] || _this.stop;
        });

        if (_this.stop) {
            return;
        }

        _this.tasks[idx]();
        _this.isFree[idx] = true;
    }
}

template<class TResult>
NAsync::Future<TResult> SimpleThreadPool::TryEnqueueSimple(std::function<TResult()> task) {
    std::shared_ptr<NAsync::Promise<TResult>> result(new NAsync::Promise<TResult>());

    std::function<void()> workerTask = [result, task] () {
        try {
            result->SetData(new TResult(task()));
        } catch (NAsync::AsyncException* e) {
            result->SetException(e);
        } catch (std::runtime_error &e) {
            auto error = new NAsync::AsyncException(e.what());
            result->SetException(error);
        } catch (...) {
            auto error = new NAsync::AsyncException("unknown error");
            result->SetException(error);
        }
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

    return NAsync::Future<TResult>();
}

inline void SimpleThreadPool::Init() {
    for (int i = 0; i < numThreads; ++i) {
        isFree[i] = true;
        workers.emplace_back(threadFunction, std::ref(*this), i);
    }
}

inline SimpleThreadPool::~SimpleThreadPool() {
    stop = true;
    for (int i = 0; i < numThreads; ++i) {
        notifiers[i].notify_one();
        workers[i].join();
    }
}

template<class TResult, class... Args>
NAsync::Future<TResult> SimpleThreadPool::TryEnqueue(std::function<TResult(Args...)> task, Args... args) {
    return TryEnqueueSimple<TResult>(std::bind(task, args...));
}
