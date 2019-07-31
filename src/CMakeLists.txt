
cmake_minimum_required(VERSION 3.8)

project(MultiTau CXX)
set(MDScatter_VERSION_MAJOR 1)
set(MDScatter_VERSION_MINOR 0)


# C++11 Stuff
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set(SRC
    cpu_multitau.cpp
    pyMultiTau.cpp
)

# python d
find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})

# pybind11
find_package(pybind11 REQUIRED)
set(LIBS pybind11::module)

find_package(OpenMP)
if(OpenMP_FOUND)
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
endif(OpenMP_FOUND)

add_library(cMultitau MODULE ${SRC})
target_link_libraries(cMultitau PRIVATE ${LIBS})
set_target_properties(cMultitau PROPERTIES PREFIX "${PYTHON_MODULE_PREFIX}"
                                         SUFFIX "${PYTHON_MODULE_EXTENSION}")
                                        
