#pragma once

#include "Exception.h"

#include <memory>
#include <exception>
#include <mutex>
#include <condition_variable>


namespace NAsync {
    template<class TData>
    class Promise;

    template<class TData>
    class Future;

    template<class TData>
    class AsyncData {
    public:
        AsyncData() : exception(nullptr), data(nullptr) {
        }

        AsyncData(AsyncData<TData>&&) noexcept;
        AsyncData(const AsyncData<TData>&) = delete;

        void SetData(TData* newData);
        void SetException(AsyncException* newException);
        std::shared_ptr<TData> GetData() const;
        AsyncException* GetException() const;

        friend class Promise<TData>;
        friend class Future<TData>;
    private:

        std::shared_ptr<TData> data;
        AsyncException* exception;
        mutable std::mutex dataGuard;
        mutable std::condition_variable notifier;
    };

    template<class TData>
    void AsyncData<TData>::SetData(TData* newData) {
        std::cerr << "SetData: " << *newData << std::endl;
        data.reset(newData);
        notifier.notify_all();
        std::cerr << "SetData completed: " << *newData << std::endl;
    }

    template<class TData>
    void AsyncData<TData>::SetException(AsyncException *newException) {
        exception = newException;
        notifier.notify_all();
    }

    template<class TData>
    std::shared_ptr<TData> AsyncData<TData>::GetData() const {
        return data;
    }

    template<class TData>
    AsyncException *AsyncData<TData>::GetException() const {
        return exception;
    }

    template<class TData>
    AsyncData<TData>::AsyncData(AsyncData<TData>&& asyncData) noexcept {
        data = std::move(asyncData.data);
        exception = std::move(asyncData.exception);
        std::swap(dataGuard, asyncData.dataGuard);
        std::swap(notifier, asyncData.notifier);
    }
}