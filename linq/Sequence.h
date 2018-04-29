#pragma once

#include "common.h"

#include <vector>
#include <functional>

namespace NLINQ {
    template<class T>
    class Collection {
    public:
        using valueType = T;

        std::vector<T> ToList();
        Collection<T> Take(int k);

        Collection<T> Where(std::function<bool(T)> filter);

        template<class TResult>
        Collection<TResult> Select(std::function<TResult(T)> mapper);

        template<class TKey>
        Collection<T> OrderBy(std::function<TKey(T)> key);

        template<class TKey>
        Collection<std::pair<TKey, Collection<T>>> GroupBy(std::function<TKey(T)> key);

        Collection<T::valueType> Flatten();

    private:

    };
}