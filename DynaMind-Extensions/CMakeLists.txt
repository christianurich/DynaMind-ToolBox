CMAKE_MINIMUM_REQUIRED(VERSION 2.8.7)
PROJECT(dynamind-extensions )

FIND_PATH(DYNAMINDDEV DynaMindDevCmake.txt
	    PATHS   $ENV{DYNAMIND_DIR}/include
	    PATH_SUFFIXES dynamindcore/CMake)

IF(DYNAMIND_INCLUDE_DIR)
	MESSAGE(STATUS "Compiled from toolbox")
	MESSAGE(STATUS "DYNAMIND_INCLUDE_DIR ${DYNAMIND_INCLUDE_DIR}")
	SET (DYNAMIND_CORE_LIBRARY dynamindcore)
	SET (DYNAMIND_TOOLBOX_LIBRARY dynamindtoolbox)
	MESSAGE(STATUS "${DYNAMIND_CORE_LIBRARY}")
ELSE()
	MESSAGE(STATUS "Compiled from stand alone")
	FIND_PATH(DYNAMINDDEV DynaMindDevCmake.txt
	PATHS $ENV{DYNAMIND_DIR}/include
	PATH_SUFFIXES dynamindcore/CMake)

	IF(DYNAMINDDEV)
		INCLUDE(${DYNAMINDDEV}/DynaMindDevCmake.txt)
	ELSE()
		MESSAGE(FATAL_ERROR "Could not find dynamind. Maybe not installed ?")
	ENDIF()

ENDIF()

IF(USEQT5)
    MESSAGE(STATUS "Using Qt5 for extensions")
    SET(CMAKE_INCLUDE_CURRENT_DIR ON)
    FIND_PACKAGE(Qt5Core)
    FIND_PACKAGE(Qt5Concurrent)
    FIND_PACKAGE(Qt5Sql)
    FIND_PACKAGE(Qt5Xml)
    FIND_PACKAGE(Qt5Gui)
    FIND_PACKAGE(Qt5Test)
	INCLUDE_DIRECTORIES(BEFORE /usr/local/opt/qt5/include)
    INCLUDE_DIRECTORIES(${Qt5Core_INCLUDE_DIRS})
    INCLUDE_DIRECTORIES(${Qt5Concurrent_INCLUDE_DIRS})
    INCLUDE_DIRECTORIES(${Qt5Xml_INCLUDE_DIRS})
    INCLUDE_DIRECTORIES(${Qt5Sql_INCLUDE_DIRS})
    INCLUDE_DIRECTORIES(${Qt5Gui_INCLUDE_DIRS})
    INCLUDE_DIRECTORIES(${Qt5Test_INCLUDE_DIRS})
    ADD_DEFINITIONS(-DUSEQT5)
ELSE()
    MESSAGE(STATUS "Using Qt4 for extensions")
    FIND_PACKAGE(Qt4 COMPONENTS QtCore QtGui QtXml QtTest REQUIRED)
    SET(QT_USE_QTXML TRUE)
    SET(QT_USE_QTTEST TRUE)
    SET(QT_USE_QTSQL TRUE)
    SET(QT_USE_QTGUI TRUE)
    SET(QT_USE_QTCORE TRUE)
    INCLUDE(${QT_USE_FILE})
ENDIF()

SET(CGAL_DONT_OVERRIDE_CMAKE_FLAGS "ON" CACHE BOOL "")
find_package(CGAL QUIET COMPONENTS Core REQUIRED)
include(${CGAL_USE_FILE})

FIND_PACKAGE(PythonLibs 3.5 REQUIRED)
INCLUDE_DIRECTORIES(src/python-swig ${PYTHON_INCLUDE_PATH})
FIND_PACKAGE(SWIG REQUIRED)
INCLUDE_DIRECTORIES(${PYTHON_INCLUDE_PATH})

FIND_PACKAGE(Boost COMPONENTS system thread REQUIRED)

INCLUDE_DIRECTORIES( ${DYNAMIND_INCLUDE_DIR} ${QT_QTCORE_INCLUDE_DIR})

IF(CMAKE_BUILD_TYPE STREQUAL Debug)
	MESSAGE(STATUS "Build Type = Debug")
	ADD_DEFINITIONS(-DDEBUG)
ELSE()
	MESSAGE(STATUS "Build Type = Release")
ENDIF()
IF(DYNAMIND_TOOLBOX_BUILD_DIR)
    SET(LIBRARY_OUTPUT_PATH ${DYNAMIND_TOOLBOX_BUILD_DIR})
    SET(EXECUTABLE_OUTPUT_PATH ${DYNAMIND_TOOLBOX_BUILD_DIR})
    SET(SCRIPT_PATH ${DYNAMIND_TOOLBOX_BUILD_DIR}/PythonModules )
    SET(OUTPUT_DIR ${DYNAMIND_TOOLBOX_BUILD_DIR})
ELSE()
    SET(LIBRARY_OUTPUT_PATH ${dynamind-extensions _BINARY_DIR})
    SET(EXECUTABLE_OUTPUT_PATH ${dynamind-extensions _BINARY_DIR})
    SET(SCRIPT_PATH ${dynamind-extensions_BINARY_DIR}/PythonModules )
ENDIF()

ADD_SUBDIRECTORY(src)
ADD_SUBDIRECTORY(python-swig)

IF(WITH_UNIT_TESTS)
    ADD_SUBDIRECTORY(unit-tests)
ENDIF(WITH_UNIT_TESTS)

