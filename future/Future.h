#pragma once

#include "AsyncData.h"
#include "Exception.h"

#include <memory>
#include <exception>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <functional>

#include <cassert>


namespace NAsync {
    template<class TData>
    class Promise;

    template<class TResult>
    class Future {
    public:
        Future() = default;

        std::shared_ptr<TResult> Get() const;
        std::shared_ptr<TResult> TryGet() const noexcept;

        // TODO: some way not to do this?
        void SetInitializer(std::function<void()> init);

        friend class Promise<TResult>;

        Future(const Future& future) = delete;
        Future(Future&& future) noexcept = default;
        Future& operator = (const Future&) = delete;
        Future& operator = (Future&&) noexcept = default;
        ~Future() = default;

        explicit operator bool();

    private:
        explicit Future(std::shared_ptr<AsyncData<TResult>> data) : data(data) {
        }

        std::shared_ptr<AsyncData<TResult>> data;
        std::function<void()> initializer;
    };

    template<class TData>
    class Promise {
    public:
        void SetData(TData* newData);
        void SetException(AsyncException* newException);

        Future<TData> GetFuture();

        Promise() : data(new AsyncData<TData>()) {
        }

        Promise(const Promise&) = delete;
        Promise& operator = (const Promise&) = delete;

        Promise(Promise&&) noexcept = default;
        Promise& operator = (Promise&&) noexcept = default;

        ~Promise() = default;

        friend class Future<TData>;
    private:
        std::shared_ptr<AsyncData<TData>> data;
    };

    template<class TData>
    void NAsync::Promise<TData>::SetData(TData* newData) {
        data->SetData(newData);
    }

    template<class TData>
    void NAsync::Promise<TData>::SetException(AsyncException* newException) {
        data->SetException(newException);
    }

    template<class TData>
    Future<TData> Promise<TData>::GetFuture() {
        return Future<TData>(data);
    }

    template<class TResult>
    std::shared_ptr<TResult> Future<TResult>::Get() const {
        {
            assert(data);
            if (initializer)
                initializer();

            std::unique_lock<std::mutex> lock(data->dataGuard);

            data->notifier.wait(lock, [this]() {
                return !data->Empty();
            });
        }

        if (data->GetException()) {
            throw data->GetException();
        }
        return data->GetData();
    }

    template<class TResult>
    std::shared_ptr<TResult> Future<TResult>::TryGet() const noexcept {
        return data->GetData();
    }

    template<class TResult>
    Future<TResult>::operator bool() {
        return data != nullptr;
    }

    template<class TResult>
    void Future<TResult>::SetInitializer(std::function<void()> init) {
        initializer = init;
    }
}
