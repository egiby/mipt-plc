#pragma once

#include <thread>
#include <vector>
#include <functional>
#include <future>

#include "Future.h"
#include "SimplePoolQueue.h"

namespace NAsync {
    class ThreadPool {
    public:
        explicit ThreadPool(int numThreads = std::thread::hardware_concurrency(), IPoolQueue *customQueue = nullptr)
                : numThreads(numThreads),
                  queue(customQueue ? customQueue : new SimplePoolQueue(numThreads)),
                  stop(new bool(false)) {
            for (int i = 0; i < numThreads; ++i) {
                queue->ReleaseThread(i);
                workers.emplace_back(threadFunction, std::ref(*queue), std::cref(*stop), i);
            }
        }

        template<class TResult>
        NAsync::Future<TResult> TryEnqueueSimple(std::function<TResult()> task);

        template<class TResult, class... Args>
        NAsync::Future<TResult> TryEnqueue(std::function<TResult(Args...)> task, Args... args);

        ~ThreadPool();

    private:
        static void threadFunction(NAsync::IPoolQueue& queue, const bool &stop, int idx);

        std::vector<std::thread> workers;
        std::unique_ptr<IPoolQueue> queue;
        std::unique_ptr<bool> stop;
        int numThreads;
    };

    // TODO: need atomic bool
    inline void ThreadPool::threadFunction(NAsync::IPoolQueue &queue, const bool &stop, int idx) {
        while (!stop) {
            queue.WaitTask(idx, [&]() {return stop;});

            if (stop) {
                return;
            }

            queue.Task(idx)();
            queue.ReleaseThread(idx);
        }
    }

    template<class TResult>
    NAsync::Future<TResult> ThreadPool::TryEnqueueSimple(std::function<TResult()> task) {
        std::shared_ptr<NAsync::Promise<TResult>> result(new NAsync::Promise<TResult>());

        std::function<void()> workerTask = [result, task] () {
            try {
                result->SetData(new TResult(task()));
            } catch (AsyncException* e) {
                result->SetException(e);
            } catch (std::runtime_error &e) {
                auto error = new AsyncException(e.what());
                result->SetException(error);
            } catch (...) {
                auto error = new AsyncException("unknown error");
                result->SetException(error);
            }
        };

        if (queue->TryEnqueue(workerTask)) {
            return result->GetFuture();
        }

        return NAsync::Future<TResult>();
    }

    inline ThreadPool::~ThreadPool() {
        *stop = true;
        for (int i = 0; i < numThreads; ++i) {
            queue->NotifyThread(i);
            workers[i].join();
        }
    }

    template<class TResult, class... Args>
    NAsync::Future<TResult> ThreadPool::TryEnqueue(std::function<TResult(Args...)> task, Args... args) {
        return TryEnqueueSimple<TResult>(std::bind(task, args...));
    }
}
