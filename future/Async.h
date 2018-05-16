#pragma once

#include "ThreadPool.h"

namespace NAsync {
    enum class LaunchPolicy {
        Async,
        Deferred
    };

    template<class TResult, class... Args>
    Future<TResult> Async(LaunchPolicy policy,
                          SimpleThreadPool *pool,
                          std::function<TResult(Args...)> task,
                          Args ...args) {
        switch (policy) {
            case LaunchPolicy::Async:
            {
                assert(pool);
                auto future = pool->TryEnqueue<TResult, Args...>(task, args...);
                if (future)
                    return future;
            }
            case LaunchPolicy::Deferred:
            {
                std::shared_ptr<Promise<TResult>> result(new NAsync::Promise<TResult>());

                auto simpleTask = std::bind(task, args...);

                auto init = [result, simpleTask]() {
                    result->SetData(new TResult(simpleTask()));
                };

                auto future = result->GetFuture();
                future.SetInitializer(init);

                return future;
            }
        }
    }
}