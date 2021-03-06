CMAKE_MINIMUM_REQUIRED(VERSION 2.6)
PROJECT(dynamind-performance-assessment)

FIND_PATH(DYNAMINDDEV DynaMindDevCmake.txt
            PATHS   $ENV{DYNAMIND_DIR}/include
            PATH_SUFFIXES dynamindcore/CMake)

IF(DYNAMIND_INCLUDE_DIR)
        MESSAGE("Compiled from toolbox")
        MESSAGE("DYNAMIND_INCLUDE_DIR ${DYNAMIND_INCLUDE_DIR}")
        SET (DYNAMIND_CORE_LIBRARY dynamindcore)
        SET (DYNAMIND_TOOLBOX_LIBRARY dynamindtoolbox)
        MESSAGE("${DYNAMIND_CORE_LIBRARY}")
ELSE()
        MESSAGE("Compiled from stand alone")
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
    MESSAGE(STATUS "Using Qt5 for performance assessment")
    FIND_PACKAGE(Qt5Core)
    FIND_PACKAGE(Qt5Xml)
	IF(APPLE)
	INCLUDE_DIRECTORIES(BEFORE /usr/local/opt/qt5/include)
	ENDIF()
    INCLUDE_DIRECTORIES(${Qt5Core_INCLUDE_DIRS})
    INCLUDE_DIRECTORIES(${Qt5Xml_INCLUDE_DIRS})
ELSE()
    MESSAGE(STATUS "Using Qt4 for performance assessment")
    FIND_PACKAGE(Qt4 COMPONENTS QtCore QtGui QtXml REQUIRED)
    FIND_PACKAGE(Git REQUIRED)
    FIND_PACKAGE(PythonLibs REQUIRED)
    SET(QT_USE_QTXML true)
    SET(QT_USE_QTGUI true)
    SET(QT_USE_QTSVG true)
    ADD_DEFINITIONS(-DQT_NO_KEYWORDS)
    INCLUDE(${QT_USE_FILE})
ENDIF()

SET(BOOST_COMPONENTS system program_options thread date_time filesystem)
SET(Boost_USE_STATIC_LIBS OFF)
FIND_PACKAGE(Boost 1.38.0 COMPONENTS ${BOOST_COMPONENTS} REQUIRED)
ADD_DEFINITIONS(${Boost_LIB_DIAGNOSTIC_DEFINITIONS} "-fPIC")
SET(Boost_USE_MULTITHREADED ON)
INCLUDE_DIRECTORIES(${Boost_INCLUDE_DIRS})
LINK_DIRECTORIES(${Boost_LIBRARY_DIRS})
INCLUDE_DIRECTORIES(${DYNAMIND_INCLUDE_DIR})

IF(CMAKE_BUILD_TYPE STREQUAL Debug)
        MESSAGE(STATUS "Build Type = Debug")
        ADD_DEFINITIONS(-DDEBUG)
ELSE()
        MESSAGE(STATUS "Build Type = Release")
ENDIF()
IF(DYNAMIND_TOOLBOX_BUILD_DIR)
    SET(LIBRARY_OUTPUT_PATH ${DYNAMIND_TOOLBOX_BUILD_DIR}/Modules)
    SET(EXECUTABLE_OUTPUT_PATH ${DYNAMIND_TOOLBOX_BUILD_DIR}/Modules)
    SET(SCRIPT_PATH ${DYNAMIND_TOOLBOX_BUILD_DIR}/PythonModules)
ELSE()
    SET(LIBRARY_OUTPUT_PATH ${dynamind-performance-assessment_BINARY_DIR})
    SET(EXECUTABLE_OUTPUT_PATH ${dynamind-performance-assessment_BINARY_DIR})
    SET(SCRIPT_PATH ${dynamind-performance-assessment_BINARY_DIR}/PythonModules)
ENDIF()

IF(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/cd3/src)
    MESSAGE(STATUS "CD3 dir exists")
ELSE()
    MESSAGE(STATUS "CD3 dir does not exist -- starting automatic download")
    EXECUTE_PROCESS(COMMAND ${GIT_EXECUTABLE} submodule init cd3 WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    EXECUTE_PROCESS(COMMAND ${GIT_EXECUTABLE} submodule update cd3 WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    EXECUTE_PROCESS(COMMAND ${GIT_EXECUTABLE} checkout master WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/cd3/)
ENDIF()

SET(OUTPUT_DIR ${DYNAMIND_TOOLBOX_BUILD_DIR})
SET(LIBRARY_OUTPUT_PATH ${DYNAMIND_TOOLBOX_BUILD_DIR}/Modules)
SET(EXECUTABLE_OUTPUT_PATH ${DYNAMIND_TOOLBOX_BUILD_DIR}/Modules)

ADD_SUBDIRECTORY(scripts)
ADD_SUBDIRECTORY(cd3)
INCLUDE_DIRECTORIES(cd3/src/cd3core)
#INCLUDE_DIRECTORIES(cd3/src/app)

ADD_SUBDIRECTORY(src/cd3-modules)
ADD_SUBDIRECTORY(src/DynaMind-Performance-Assessment)
ADD_SUBDIRECTORY(3rdparty)
IF(WITH_UNIT_TESTS)
    ADD_SUBDIRECTORY(src/unit-tests)
ENDIF(WITH_UNIT_TESTS)

