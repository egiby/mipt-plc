#pragma once

#include <common.h>

#include <data/Data.h>
#include <pipeline/Pipeline.h>

#include <vector>
#include <functional>

namespace NLINQ {
    template<class TData, class TValue>
    class Sequence {
    public:
        using ValueType = TValue;
        using DataType = TData;

        explicit Sequence(std::shared_ptr<IDataGenerator<const TData>> generator
                , Pipeline<TData, TValue> pipeline = Pipeline<TData, TValue>())
            : generator(std::move(generator)), pipeline(pipeline) {
        }

        std::vector<TValue> ToList();
        Sequence<TValue, TValue> Take(int k);

        template<class TKey>
        Sequence<std::pair<TKey, Sequence<TValue, TValue>>, std::pair<TKey, Sequence<TValue, TValue>>> GroupBy(std::function<TKey(TValue)> key);

        template<class TKey>
        Sequence<TValue, TValue> OrderBy(std::function<TKey(TValue)> key);

        Sequence<TData, TValue> Where(std::function<bool(TValue)> filter);

        template<class TResult>
        Sequence<TData, TResult> Select(std::function<TResult(TValue)> mapper);

        Sequence<DataType, ValueType::ValueType> Flatten();
    private:
        std::shared_ptr<IDataGenerator<const TData>> generator;
        Pipeline<TData, TValue> pipeline;
    };

    template<class TData, class TValue>
    Sequence<TValue, TValue> Sequence<TData, TValue>::Take(int k) {
        auto newGenerator = pipeline.Apply(*generator, k);
        return Sequence<TValue, TValue>(std::move(newGenerator));
    }

    template<class TData, class TValue>
    std::vector<TValue> Sequence<TData, TValue>::ToList() {
        auto result = pipeline.Apply(*generator);
        return std::vector<TValue>(result->begin(), result->end());
    }
}