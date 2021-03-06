cmake_minimum_required (VERSION 2.6)
project(cd3)

if (${CMAKE_CXX_COMPILER_ID} STREQUAL MSVC)
	message(STATUS "Using Visual C compilers")
	set(CMAKE_CXX_FLAGS "/EHsc")
endif()
if (${CMAKE_CXX_COMPILER_ID} STREQUAL GNU)
	message(STATUS "Using GNU compilers")
	set(CMAKE_CXX_FLAGS "-g -Wall")
	SET (CMAKE_CXX_FLAGS "-std=c++11 ${CMAKE_CXX_FLAGS}")
endif()


IF(USEQT5)
	MESSAGE(STATUS "Using Qt5 for cd3")
	SET(CMAKE_INCLUDE_CURRENT_DIR ON)
	SET(CMAKE_AUTOMOC ON)
	SET(CMAKE_PREFIX_PATH "C:/Qt/Qt5.4.1/5.4/msvc2013_64_opengl")
	FIND_PACKAGE(Qt5Core)
	FIND_PACKAGE(Qt5Concurrent)
	FIND_PACKAGE(Qt5Sql)
	FIND_PACKAGE(Qt5Xml)
	FIND_PACKAGE(Qt5Gui)
	FIND_PACKAGE(Qt5Test)
	FIND_PACKAGE(Qt5Svg)
	FIND_PACKAGE(Qt5Network)
	#FIND_PACKAGE(Qt5WebKitWidgets)
	FIND_PACKAGE(Qt5Widgets)
	FIND_PACKAGE(Qt5PrintSupport)
	FIND_PACKAGE(Qt5OpenGL)
	INCLUDE_DIRECTORIES(${Qt5Core_INCLUDE_DIRS})
	INCLUDE_DIRECTORIES(${Qt5Concurrent_INCLUDE_DIRS})
	INCLUDE_DIRECTORIES(${Qt5Xml_INCLUDE_DIRS})
	INCLUDE_DIRECTORIES(${Qt5Sql_INCLUDE_DIRS})
	INCLUDE_DIRECTORIES(${Qt5Gui_INCLUDE_DIRS})
	INCLUDE_DIRECTORIES(${Qt5Test_INCLUDE_DIRS})
	INCLUDE_DIRECTORIES(${Qt5Svg_INCLUDE_DIRS})
	INCLUDE_DIRECTORIES(${Qt5Network_INCLUDE_DIRS})
	#INCLUDE_DIRECTORIES(${Qt5WebKitWidgets_INCLUDE_DIRS})
	INCLUDE_DIRECTORIES(${Qt5Widgets_INCLUDE_DIRS})
	INCLUDE_DIRECTORIES(${Qt5PrintSupport_INCLUDE_DIRS})
	INCLUDE_DIRECTORIES(${Qt5OpenGL_INCLUDE_DIRS})
	ADD_DEFINITIONS(-DUSEQT5)
ELSE()
	MESSAGE(STATUS "Using Qt4 for gui")
	FIND_PACKAGE(Qt4 COMPONENTS QtCore QtGui QtOpenGL QtXml QtWebkit QtNetwork QtSvg QtTest REQUIRED)
	SET(QT_USE_QTXML TRUE)
	SET(QT_USE_QTTEST TRUE)
	SET(QT_USE_QTSQL TRUE)
	SET(QT_USE_QTGUI TRUE)
	SET(QT_USE_QTCORE TRUE)
	SET(QT_USE_QTWEBKIT TRUE)
	SET(QT_USE_QTSVG TRUE)
	SET(QT_USE_QTNETWORK TRUE)
	INCLUDE(${QT_USE_FILE})
ENDIF()

##check for Qt4 which is a definitive requirement for building cd3
#find_package(Qt4 REQUIRED)
#set(QT_USE_QTXML true)
#set(QT_USE_QTGUI true)
#set(QT_USE_QTSVG true)
#add_definitions(-DQT_NO_KEYWORDS)
#INCLUDE(${QT_USE_FILE})

if(NOT(OUTPUT_DIR))
    set(OUTPUT_DIR ${cd3_BINARY_DIR})
endif()

set(LIBRARY_OUTPUT_PATH ${OUTPUT_DIR})
set(EXECUTABLE_OUTPUT_PATH ${OUTPUT_DIR})

set(CD3_FRONTEND_LIBS cd3core)
set(BOOST_COMPONENTS system program_options thread date_time filesystem)


include_directories(src/cd3core)

#include python scripting capabilites
option(WITH_PYTHON "Include Python scripting capabilites" ON)
if (WITH_PYTHON)
    FIND_PACKAGE(PythonLibs 3.5 REQUIRED)
    FIND_PROGRAM(PYTHON_EXECUTABLE NAMES python)
    INCLUDE_DIRECTORIES(src/python-swig ${PYTHON_INCLUDE_PATH})
    FIND_PACKAGE(SWIG REQUIRED)
    INCLUDE_DIRECTORIES(${PYTHON_INCLUDE_PATH})
    execute_process(
      COMMAND "${PYTHON_EXECUTABLE}" -c "if True:
        from distutils import sysconfig as sc
	print(sc.get_python_lib(prefix='', plat_specific=True))"
      OUTPUT_VARIABLE PYTHON_SITE_PACKAGES
      OUTPUT_STRIP_TRAILING_WHITESPACE)
endif (WITH_PYTHON)
if (WITH_PYTHON AND PYTHONLIBS_FOUND AND SWIG_FOUND)
	message(STATUS "Python support enabled")
	include_directories(${PYTHON_INCLUDE_DIRS})
else()
	add_definitions(-DPYTHON_DISABLED)
	message(STATUS "Python support disabled")
endif()

#check for boost which is a definitive requirement for building cd3
#status makes problems when compiling in linux

if(WIN32)
	set(Boost_USE_STATIC_LIBS ON)
endif()
find_package(Boost 1.38.0 COMPONENTS ${BOOST_COMPONENTS} REQUIRED)
add_definitions(${Boost_LIB_DIAGNOSTIC_DEFINITIONS})
set(Boost_USE_MULTITHREADED ON)
include_directories(${Boost_INCLUDE_DIRS})
link_directories(${Boost_LIBRARY_DIRS})

#check for openmp. also disables the code using qt thread
option(WITH_PARALLEL "Enable parallel code. Needs a OpenMP compiler" ON)
find_package(OpenMP QUIET)
if (WITH_PARALLEL AND OPENMP_FOUND)
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
	message(STATUS "OpenMP is enabled")
else()
	add_definitions(-DOPENMP_DISABLED)
	message(STATUS "OpenMP is disabled. Consider using a compiler that supports OpenMP")
endif()

if (CMAKE_BUILD_TYPE STREQUAL Debug)
	message(STATUS Debug)
	add_definitions(-DDEBUG)
else ()
	message(STATUS Release)
endif()

#check for graphviz
find_package(PkgConfig)
if (PKG_CONFIG_FOUND)
	pkg_search_module(GRAPHVIZ libgvc)
	if (GRAPHVIZ_FOUND)
		message(STATUS "graphviz found enabling autolayout")
		set(WITH_AUTOLAYOUT TRUE)
	endif (GRAPHVIZ_FOUND)
endif (PKG_CONFIG_FOUND)

##'NOF CHECKING... BUILDING##
add_subdirectory(src/cd3core)

if (WITH_PYTHON)
	add_subdirectory(src/python-swig)
endif()

add_subdirectory(src/app)
#add_subdirectory(src/gui)
#add_subdirectory(src/plugindoc)

#option(WITH_PLUGINDOC "Build the plugindoc app" OFF)
#if (WITH_PLUGINDOC)
#	add_subdirectory(src/plugindoc)
#endif()

option(WITH_TESTS "Enable unit testing" OFF)

if (WITH_TESTS)
	find_package(GTest REQUIRED)
	message(STATUS "Tests enabled")
	enable_testing(true)
	add_subdirectory(src/tests)
endif()

INCLUDE(Cd3CPack.txt)
