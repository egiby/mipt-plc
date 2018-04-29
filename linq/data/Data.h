#pragma once

#include <common.h>

namespace NLINQ {
    template <class TData>
    interface IDataGenerator {
        virtual const TData* begin() = 0;
        virtual const TData* end() = 0;
    };
}