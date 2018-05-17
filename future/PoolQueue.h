#pragma once

#include <functional>

namespace NAsync {
    class IPoolQueue {
    public:
        virtual bool TryEnqueue(std::function<void()> task) = 0;
        virtual std::function<void()>& Task(int threadId) = 0;
        virtual bool HasTask(int threadId) = 0;
        virtual void ReleaseThread(int threadId) = 0;
        virtual void WaitTask(int threadId, std::function<bool()> predicate) = 0;
        virtual void NotifyThread(int threadId) = 0;

        virtual ~IPoolQueue() = default;
    };
}