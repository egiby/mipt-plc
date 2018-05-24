#pragma once

#include <exception>
#include <stdexcept>

namespace NAsync {
    class AsyncException : public std::runtime_error {
    public:
        explicit AsyncException(const std::string& message) : runtime_error(message) {
        }
    protected:
        using std::runtime_error::runtime_error;
    };
}