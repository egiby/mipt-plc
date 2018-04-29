#pragma once

#include <common.h>

#include <data/Data.h>

#include <climits>

namespace NLINQ {
    template <class TInput, class TOutput>
    class Pipeline {
    public:
        shared_ptr<IDataGenerator<TOutput>> Apply(const IDataGenerator<TInput>& generator, int maxNumber = INT_MAX);
    private:
        std::function<TOutput*(TInput)> function;
    };

    template<class TInput, class TOutput>
    shared_ptr<IDataGenerator<TOutput>> Pipeline<TInput, TOutput>::Apply(const IDataGenerator <TInput> &generator, int maxNumber) {
        std::vector<TOutput> resultVector;
        for (const auto& x: generator) {
            if (resultVector.size() >= maxNumber) {
                break;
            }

            TOutput* result = function(x);
            if (result) {
                resultVector
            }
        }
    }
}