#pragma once

#include "Exception.h"

#include <memory>
#include <exception>
#include <mutex>
#include <condition_variable>
#include <atomic>


namespace NAsync {
    template<class TData>
    class Promise;

    template<class TData>
    class Future;

    template<class TData>
    class AsyncData {
    public:
        AsyncData() : exception(nullptr), data(nullptr), empty(true) {
        }

        AsyncData(AsyncData<TData>&&) noexcept = delete;
        AsyncData(const AsyncData<TData>&) = delete;

        void SetData(TData* newData);
        void SetException(AsyncException* newException);
        bool Empty() const;
        std::shared_ptr<TData> GetData() const;
        AsyncException* GetException() const;

        friend class Promise<TData>;
        friend class Future<TData>;
    private:
        std::shared_ptr<TData> data;
        std::atomic<bool> empty;
        AsyncException* exception;
        mutable std::mutex dataGuard;
        mutable std::condition_variable notifier;
    };

    template<class TData>
    void AsyncData<TData>::SetData(TData* newData) {
        std::lock_guard<std::mutex> guard(dataGuard);
        data.reset(newData);
        empty = false;
        notifier.notify_all();
    }

    template<class TData>
    void AsyncData<TData>::SetException(AsyncException *newException) {
        std::lock_guard<std::mutex> guard(dataGuard);
        exception = newException;
        empty = false;
        notifier.notify_all();
    }

    template<class TData>
    bool AsyncData<TData>::Empty() const {
        return bool(empty);
    }

    template<class TData>
    std::shared_ptr<TData> AsyncData<TData>::GetData() const {
        return data;
    }

    template<class TData>
    AsyncException *AsyncData<TData>::GetException() const {
        return exception;
    }
}