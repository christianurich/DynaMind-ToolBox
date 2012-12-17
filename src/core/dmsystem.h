/**
 * @file
 * @author  Chrisitan Urich <christian.urich@gmail.com>
 * @author  Michael Mair <abroxos@gmail.com>
 * @version 1.0
 * @section LICENSE
 * This file is part of DynaMite
 *
 * Copyright (C) 2011  Christian Urich, Michael Mair, Markus Sengthaler

 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.

 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.

 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 *
 */

#ifndef DMSYSTEM_H
#define DMSYSTEM_H
#include <dmcompilersettings.h>
#include <map>
#include <vector>
#include <dmview.h>
#include <dmcomponent.h>

#ifdef SWIG
#define DM_HELPER_DLL_EXPORT
#endif

namespace DM {

class Node;
class Edge;
class Face;
class RasterData;
class Module;



typedef std::pair<std::string, Component*> ComponentPair;
typedef std::pair<std::string, Attribute*> AttributePair;
typedef std::pair<std::string, RasterData*> RasterDataPair;
typedef std::pair<std::string, Edge*> EdgePair;
typedef std::pair<std::string, Node*> NodePair;
typedef std::pair<std::string, Face*> FacePair;

/** @ingroup DynaMind-Core
      * @brief The system class provides a description for complex objects.
      *
      * Systems can be described with nodes, edges, faces, rasterdata. Systems can contain sub systems.
      * Systems are used to describe urban environment - water infrastructure, streets, houses ...
      *
      * The System class is derived from the Component class. Therefore every system has a UUID and can hold Attributes.
      *
      * To use the System class in a dynamic environment it is possible to create a successor state. Successor states hold a new list of pointer to
      * the objects stored in the system. If a Object is added, removed or changed only the successor system is altered.
      */
class  DM_HELPER_DLL_EXPORT System : public Component
{
private:
    //QMutex * mutex;
    std::map<QUuid, Node* > nodes;
    std::map<QUuid, Edge* > edges;
    std::map<QUuid, Face* > faces;
    std::map<QUuid, RasterData *> rasterdata;
    std::map<QUuid, System*> subsystems;
    std::map<QUuid, Component* > components;

    std::map<QUuid, Component*> ownedchilds;

    std::map<std::string, View*> viewdefinitions;
    std::map<std::string, std::map<std::string, Component*> > views;   

    std::vector<DM::System*> predecessors;
    std::vector<DM::System*> sucessors;
    std::vector<DM::View *> ownedView;

    //Get Edge Based on map otherwise takes ages
    std::map<std::pair<std::string ,std::string>,DM::Edge*> EdgeNodeMap;

    void updateViews (Component * c);

    DM::Module * lastModule;

    void SQLInsert();
    void SQLUpdateStates();

    bool addChild(Component *newcomponent);
    /*@deprecated*/
    bool removeChild(std::string name);
    bool removeChild(QUuid uuid);
    /*@deprecated*/
    Component* getChild(std::string name);
    Component* getChild(QUuid uuid);
    Component* findChild(QUuid uuid) const;
    /** @brief return table name */
    QString getTableName();
    Component* getComponent(QUuid uuid);
    Node* getNode(QUuid uuid);
    Edge* getEdge(QUuid uuid);
    System* getSubSystem(QUuid uuid);
protected:
    //std::string getStateUuid();
public:
    bool removeChild(Component* c);
    /*@deprecated*/
    std::map<std::string, Component*> getAllChilds();
    std::vector<Component*> getChilds();
    /** @brief Copies a System  */
    System(const System& s);
    /** @brief creates a new System */
    System();
    /** @brief Destructor
     *
     * The destructor also deletes all successor states */
    ~System();
    /** @brief setUUID */
    //virtual void setUUID(std::string uuid);
	/** @brief return Type */
	virtual Components getType();
    /** @brief Adds an existing component to the system. The ownership of the component goes to the system*/
    Component * addComponent(Component* c, const DM::View & view = DM::View());
    /** @brief Adds an existing node to the system. The ownership of the node goes to the system.
     *  If the node already exists 0 it returns 0, if not the pointer to the node (same as the input)
     */
    Node * addNode(Node* node);
    /** @brief Adds a new node to the system and returns a pointer to the node.*/
    Node * addNode(double x, double y, double z, const DM::View & view = DM::View());
    /** @brief Copies xyz in a new Node, attaches it to the system, returning a pointer*/
    Node * addNode(const Node &n,  const DM::View & view = DM::View());
    /** @brief Adds a new Edge to the system, the system class takes ownership of the edge */
    Edge* addEdge(Edge* edge);
    /** @brief Creates a new Edge, based on the UUID of the start and end node */
    Edge* addEdge(Node * start, Node * end, const DM::View & view = DM::View());
    /** @brief Adds a new Face to the system, the system class takes ownership of the face  */
    Face * addFace(Face * f);
    /** @brief Creates a new Face, based on the UUID of the nodes stored in the vector */
    Face * addFace(std::vector<Node*> nodes,  const DM::View & view = DM::View());
    /** @brief Returns a pointer to the component. Returns 0 if Component doesn't exist
        @deprecated*/
    Component* getComponent(std::string uuid);
    /** @brief Returns a pointer to the node. Returns 0 if Node doesn't exis
        @deprecated*/
    Node* getNode(std::string uuid);
    /** @brief Returns a pointer to the edge. Returns 0 if Edge doesn't exis
        @deprecated*/
    Edge* getEdge(std::string uuid);
    /** @brief Returns a pointer to the edge. Returns 0 if Edge doesn't exist
        @deprecated*/
    Edge* getEdge(const std::string &startnodeuuid, const std::string &endnodeuuid);
    /** @brief Returns a pointer to the face. Returns 0 if Face doesn't exist
        @deprecated*/
    Face * getFace(std::string uuid);
    /** @brief Removes an Edge. Returns false if the edge doesn't exist */
    bool removeEdge(std::string uuid);
    /** @brief Removes a Node. Returns false if the node doesn't exist
        @deprecated*/
    bool removeNode(std::string uuid);
    /** @brief Removes a Component. Returns false if the component doesn't exist
        @deprecated*/
    bool removeComponent(std::string uuid);
    /** @brief Removes a Face. Returns false if the face doesn't exist */
    bool removeFace(std::string uuid);
    /** @brief Returns a map of nodes stored in the system
        @deprecated*/
    std::map<std::string, Component*> getAllComponents();
    /** @brief Returns a map of nodes stored in the system
        @deprecated*/
    std::map<std::string, Node*> getAllNodes();
    /** @brief Returns a map of edges stored in the system
        @deprecated*/
    std::map<std::string, Edge*> getAllEdges();
    /** @brief Returns a map of faces stored in the system
        @deprecated*/
    std::map<std::string, Face*> getAllFaces();
    /** @brief Returns a map of subsystems stored in the system
        @deprecated*/
    std::map<std::string, System*> getAllSubSystems();
    /** @brief Returns a map of rasterdata stored in the system
        @deprecated*/
    std::map<std::string, RasterData*> getAllRasterData();
    /** @brief Returns the predecessor of the system */
    std::vector<System*> getPredecessors();
    /** @brief Returns the sucessor of the system */
    std::vector<System*> getSucessors();
    /** @brief adds a new subsystem, the system class takes ownership of the subsystem*/
    System * addSubSystem(System *newsystem, const DM::View & view = DM::View());
    /** @brief Removes a Subsystem. Returns false if the subsystem doesn't exist */
    bool removeSubSystem(std::string uuid);
    /** @brief Returns Subsystem. Returns 0 if Subsystem doesn't exist
        @deprecated*/
    System* getSubSystem(std::string uuid);
    /** @brief Creates a new Successor state
       *
       * @todo add a more detailed description here
       */
    System* createSuccessor();
    /** @brief Adds a new view to the system. At the moment always returns true */
    bool addView(DM::View view);
    /** @brief return a vector of the names of the views avalible in the system */
    std::vector<std::string> getNamesOfViews();
    /** @brief return a vector of views avalible in the system */
    const std::vector<DM::View> getViews();
    /** @brief Retruns View */
    View * getViewDefinition(std::string name);
    /** @brief Creates a clone of the System. UUID and Attributes stay the same as its origin */
    Component* clone();
    /** @brief add a component to a view */
    bool addComponentToView(Component * comp, const DM::View & view);
    /** @brief remove a component from a view */
    bool removeComponentFromView(Component * comp, const DM::View & view);
    /** @brief retrun all components related to a view */
    std::map<std::string, Component*> getAllComponentsInView(const View &view);
    /** @brief Returns a vector of all uuids stored in a view */
    std::vector<std::string> getUUIDsOfComponentsInView(DM::View  view);
    /** @brief Returns a vector of all uuids stored in a view, calls getUUIDsOfComponentsInView but it's much shorter*/
    std::vector<std::string> getUUIDs(const DM::View &view);
    /** @brief Adds raster data to the system. The owner ship of the raster data is taken by the system */
    RasterData * addRasterData(RasterData * r,  const DM::View & view = DM::View());
    /** @brief add Predecessor **/
    void addPredecessors(DM::System * s);

    void setAccessedByModule(Module * m);
    Module * getLastModule();
};

typedef std::map<std::string, DM::System*> SystemMap;
}


// mforeach

struct ForeachBaseBase {};

template <typename T1, typename T2>
class ForeachBase: public ForeachBaseBase
{
public:
    inline ForeachBase(const std::map<T1,T2>& t): c(t), brk(0), i(c.begin()), e(c.end()){}
    const std::map<T1,T2> c;
    mutable int brk;
    mutable typename std::map<T1,T2>::const_iterator i, e;
    inline bool condition() const { return (!brk++ && i != e);}
};

template <typename T1, typename T2> inline std::map<T1,T2> *pMForeachPointer(const std::map<T1,T2> &) { return 0; }

template <typename T1, typename T2> inline ForeachBase<T1,T2> pMForeachBaseNew(const std::map<T1,T2>& t)
{ return ForeachBase<T1,T2>(t); }

template <typename T1, typename T2>
inline const ForeachBase<T1,T2> *pMForeachBase(const ForeachBaseBase *base, const std::map<T1,T2> *)
{ return static_cast<const ForeachBase<T1,T2> *>(base); }


#if defined(Q_CC_MIPS)
/*
   Proper for-scoping in MIPSpro CC
*/
#  define MAP_FOREACH(variable,container)                                                             \
    if(0){}else                                                                                     \
    for (const ForeachBaseBase &_container_ = pMForeachBaseNew(container);                \
         pMForeachBase(&_container_, true ? 0 : pMForeachPointer(container))->condition();       \
         ++pMForeachBase(&_container_, true ? 0 : pMForeachPointer(container))->i)               \
        for (variable = pMForeachBase(&_container_, true ? 0 : pMForeachPointer(container))->i->second; \
             pMForeachBase(&_container_, true ? 0 : pMForeachPointer(container))->brk;           \
             --pMForeachBase(&_container_, true ? 0 : pMForeachPointer(container))->brk)

#elif defined(Q_CC_DIAB)
// VxWorks DIAB generates unresolvable symbols, if container is a function call
#  define MAP_FOREACH(variable,container)                                                             \
    if(0){}else                                                                                     \
    for (const ForeachBaseBase &_container_ = pMForeachBaseNew(container);                \
         pMForeachBase(&_container_, (__typeof__(container) *) 0)->condition();       \
         ++pMForeachBase(&_container_, (__typeof__(container) *) 0)->i)               \
        for (variable = pMForeachBase(&_container_, (__typeof__(container) *) 0)->i->second; \
             pMForeachBase(&_container_, (__typeof__(container) *) 0)->brk;           \
             --pMForeachBase(&_container_, (__typeof__(container) *) 0)->brk)

#else
#  define MAP_FOREACH(variable, container) \
    for (const ForeachBaseBase &_container_ = pMForeachBaseNew(container); \
         pMForeachBase(&_container_, true ? 0 : pMForeachPointer(container))->condition();       \
         ++pMForeachBase(&_container_, true ? 0 : pMForeachPointer(container))->i)               \
        for (variable = pMForeachBase(&_container_, true ? 0 : pMForeachPointer(container))->i->second; \
             pMForeachBase(&_container_, true ? 0 : pMForeachPointer(container))->brk;           \
             --pMForeachBase(&_container_, true ? 0 : pMForeachPointer(container))->brk)
#endif // MSVC6 || MIPSpro

#define mforeach MAP_FOREACH


#endif // SYSTEM_H
