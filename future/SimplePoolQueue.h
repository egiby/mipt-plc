#pragma once

#include "PoolQueue.h"

#include <mutex>
#include <vector>
#include <condition_variable>

namespace NAsync {
    class SimplePoolQueue: public NAsync::IPoolQueue {
    public:
        explicit SimplePoolQueue(int numThreads) :
                numThreads(numThreads),
                isFree(numThreads),
                tasks(numThreads),
                taskGuards(numThreads),
                notifiers(numThreads) {
        }

        bool TryEnqueue(std::function<void()> task) override;

        std::function<void()>& Task(int threadId) override;
        bool HasTask(int threadId) override;
        void ReleaseThread(int threadId) override;
        void WaitTask(int threadId, std::function<bool()> predicate) override;
        void NotifyThread(int threadId) override;

    private:
        int numThreads;
        std::mutex queueGuard;

        std::vector<bool> isFree;
        std::vector<std::function<void()>> tasks;
        std::vector<std::mutex> taskGuards;
        std::vector<std::condition_variable> notifiers;
    };
}