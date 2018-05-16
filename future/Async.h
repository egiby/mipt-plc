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
                    try {
                        result->SetData(new TResult(simpleTask()));
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

                auto future = result->GetFuture();
                future.SetInitializer(init);

                return future;
            }
        }
    }
}