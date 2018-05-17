#include "SimplePoolQueue.h"

#include <cassert>

namespace NAsync {
    bool SimplePoolQueue::TryEnqueue(std::function<void()> task) {
        std::lock_guard<std::mutex> guard(queueGuard);

        for (int i = 0; i < numThreads; ++i) {
            if (isFree[i]) {
                tasks[i] = task;
                isFree[i] = false;
                NotifyThread(i);
                return true;
            }
        }

        return false;
    }

    std::function<void()>& SimplePoolQueue::Task(int threadId) {
        assert(threadId < numThreads);
        return tasks[threadId];
    }

    bool SimplePoolQueue::HasTask(int threadId) {
        assert(threadId < numThreads);
        return !isFree[threadId];
    }

    void SimplePoolQueue::ReleaseThread(int threadId) {
        assert(threadId < numThreads);
        isFree[threadId] = true;
    }

    void SimplePoolQueue::WaitTask(int threadId, std::function<bool()> predicate) {
        assert(threadId < numThreads);
        std::unique_lock<std::mutex> lock(taskGuards[threadId]);
        notifiers[threadId].wait(lock, [&] {
            return HasTask(threadId) || predicate();
        });
    }

    void SimplePoolQueue::NotifyThread(int threadId) {
        assert(threadId < numThreads);
        notifiers[threadId].notify_one();
    }
}
