/**
 * @file
 * @author  Chrisitan Urich <christian.urich@gmail.com>
 * @version 1.0
 * @section LICENSE
 *
 * This file is part of DynaMind
 *
 * Copyright (C) 2014  Christian Urich

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

#include "dmgdalsystem.h"

#include <dmlogger.h>
#include <dmattribute.h>
#include <dmsystem.h>

#include <ogrsf_frmts.h>
#include <ogr_api.h>

#include <sstream>

#include <QUuid>
#include <QFile>
#include "../../3rdparty/sqlite3/sqlite3.h"
#include <dmviewcontainer.h>

namespace DM {

GDALSystem::GDALSystem(int EPSG, std::string workingDir, bool keepDatabaseFile) :
	EPSG(EPSG),
	workingDir(workingDir),
	keepDatabaseFile(keepDatabaseFile)
{
	//Init SpatialiteServer
	GDALAllRegister();

	if (EPSG == 0) {
		DM::Logger(DM::Warning) << "Please set EPSG code for simulation";
		EPSG = 0;
	}
	if (workingDir == "") {
		this->workingDir = QString(QDir::tempPath() + "/dynamind").toStdString();
	}
	poDrive = (GDALDriver*) GDALGetDriverByName("SQLite" );
	//poDrive = OGRSFDriverRegistrar::GetRegistrar()->GetDriverByName( "SQLite" );
	char ** options = NULL;
	options = CSLSetNameValue( options, "OGR_SQLITE_SYNCHRONOUS", "OFF" );
	options = CSLSetNameValue( options, "OGR_SQLITE_CACHE", "2048" );
	options = CSLSetNameValue( options, "OGR_SQLITE_PRAGMA", "temp_store=2" );
	if (EPSG != 0) {
		options = CSLSetNameValue( options, "SPATIALITE", "YES" );
	} else {
		DM::Logger(DM::Warning) << "No EPSG code defined, disable spatialite backend";
	}


	DBID = QUuid::createUuid().toString();

	QString dbname =  QString::fromStdString(this->getDBID());
	poDS = poDrive->Create( dbname.toStdString().c_str(), 0, 0, 0, GDT_Unknown, options );
	//poDS = poDrive->CreateDataSource(dbname.toStdString().c_str() , options );

	if( poDS == NULL ) {
		DM::Logger(DM::Error) << "couldn't create source";
	}


	int rc =  sqlite3_open(dbname.toStdString().c_str(), &db);
		if( rc ){
			std::cout <<  "Can't open database: " << sqlite3_errmsg(db) << std::endl; 
			DM::Logger(DM::Error) <<  "Can't open database: " << sqlite3_errmsg(db);
		} else{
			std::cout <<  "Open database"  << std::endl; 
		}



	//Create State ID
	this->state_ids.push_back(QUuid::createUuid().toString().toStdString());

	predecessor = NULL;
	this->EPSG = EPSG;

	


	OGRSpatialReference* oSourceSRS;
	oSourceSRS = new OGRSpatialReference();
	oSourceSRS->importFromEPSG(this->EPSG);
	OGRLayer * lyr_def = poDS->CreateLayer("dynamind_table_definitions", oSourceSRS, wkbUnknown, NULL );
	{
		OGRFieldDefn oField ( "view_name", OFTString );
		lyr_def->CreateField(&oField);
	}
	{
		OGRFieldDefn oField ( "attribute_name", OFTString );
		lyr_def->CreateField(&oField);
	}
	{
		OGRFieldDefn oField ( "data_type", OFTString );
		lyr_def->CreateField(&oField);
	}
}

void GDALSystem::setGDALDatabase(const string & database)
{
	GDALClose(poDS);
	if (db) {
		sqlite3_close(db);
		db = NULL;
	}

	DBID = QUuid::createUuid().toString();

	//Copy DB
	QString origin = QString::fromStdString(database);
	QString dest = QString::fromStdString(this->getDBID());
	QFile::copy(origin, dest);
	//poDS = poDrive->( dest.toStdString().c_str(), 0, 0, 0, GDT_Unknown, NULL );

	char ** options = NULL;
	options = CSLSetNameValue( options, "OGR_SQLITE_SYNCHRONOUS", "OFF" );
	options = CSLSetNameValue( options, "OGR_SQLITE_CACHE", "2048" );
	options = CSLSetNameValue( options, "OGR_SQLITE_PRAGMA", "temp_store=2" );
	if (EPSG != 0) {
		options = CSLSetNameValue( options, "SPATIALITE", "YES" );
	} else {
		DM::Logger(DM::Warning) << "No EPSG code defined, disable spatialite backend";
	}

	poDS = (GDALDataset*) GDALOpenEx( dest.toStdString().c_str(), GDAL_OF_VECTOR | GDAL_OF_UPDATE,NULL, options, NULL );
	//poDS = poDrive->GDALOpenEx(dest.toStdString().c_str(), true);


	int rc =  sqlite3_open(dest.toStdString().c_str(), &db);
		if( rc ){
			std::cout <<  "Can't open database: " << sqlite3_errmsg(db) << std::endl; 
			DM::Logger(DM::Error) <<  "Can't open database: " << sqlite3_errmsg(db);
		} else{
			std::cout <<  "Ooen database"  << std::endl; 
		}

	

	//Create new state
	state_ids.push_back(QUuid::createUuid().toString().toStdString());

	//RebuildViewLayer
	for (std::map<std::string, OGRLayer *>::const_iterator it = viewLayer.begin();
		 it != viewLayer.end(); ++it) {
		std::string viewname = it->first;
		if (viewname ==  "dynamind_table_definitions")
			continue;
		viewLayer[it->first] = poDS->GetLayerByName(viewname.c_str());
	}
}

std::string GDALSystem::getWorkingDirectory() const
{

	//Check if folder exits
	QDir working_dir;
	QString path = QString::fromStdString(this->workingDir) + "/";
	if (!working_dir.exists(path)){
		if (!working_dir.mkpath(path)) {
			DM::Logger(DM::Error) << "failed to create folder";
		}
	}
	return path.toStdString();
}

GDALSystem::GDALSystem(const GDALSystem &s)
{
	DM::Logger(DM::Warning) << "Split System " << s.getDBID();
	//Copy all that is needed
	poDrive = s.poDrive;
	viewLayer = s.viewLayer;
	state_ids = s.state_ids;
	keepDatabaseFile = s.keepDatabaseFile;
	workingDir = s.workingDir;
	sucessors = std::vector<DM::GDALSystem*>();
	DBID = QUuid::createUuid().toString();
	EPSG = s.EPSG;

	//Copy DB
	QString origin =  QString::fromStdString(s.getDBID());
	QString dest = QString::fromStdString(this->getDBID());
	QFile::copy(origin, dest);
	poDS = (GDALDataset*) GDALOpenEx( dest.toStdString().c_str(), GDAL_OF_VECTOR | GDAL_OF_UPDATE, NULL, NULL, NULL );
	// poDS = poDrive->Open(dest.toStdString().c_str(), true);

	//Create new state
	state_ids.push_back(QUuid::createUuid().toString().toStdString());

	//RebuildViewLayer
	for (std::map<std::string, OGRLayer *>::const_iterator it = viewLayer.begin();
		 it != viewLayer.end(); ++it) {
		std::string viewname = it->first;
		viewLayer[it->first] = poDS->GetLayerByName(viewname.c_str());
	}
}


void GDALSystem::updateAttributeDefinition(std::string view_name,
										   std::string attribute_name,
										   std::string data_type)
{
	OGRLayer * layer_dev = this->poDS->GetLayerByName("dynamind_table_definitions");
	OGRFeature * f_def = OGRFeature::CreateFeature(layer_dev->GetLayerDefn());
	f_def->SetField("view_name", view_name.c_str());
	f_def->SetField("attribute_name", attribute_name.c_str());
	f_def->SetField("data_type", data_type.c_str());

	layer_dev->CreateFeature(f_def);
	OGRFeature::DestroyFeature(f_def);
}

void GDALSystem::updateView(const View &v)
{
	std::vector<OGRLayer*> layers;
	//if view is not in map create a new ogr layer
	if (viewLayer.find(v.getName()) == viewLayer.end()) {
		if ( v.getName() == "dummy" ) {
			return;
		}

		OGRLayer * lyr_tmp = this->createLayer(v);

		if (lyr_tmp == NULL) {
			DM::Logger(DM::Error) << "couldn't create layer " << v.getName();
			return;
		} else {
			DM::Logger(DM::Debug) << "created layer " << v.getName();
		}
		this->viewLayer[v.getName()] = lyr_tmp;
		layers.push_back(lyr_tmp);


	}
	// std::cout << viewLayer.size() << std::endl;

	OGRLayer * lyr = viewLayer[v.getName()];
	//Update Features
	foreach(std::string attribute_name, v.getAllAttributes()) {
		//Feature already in layer
		if (lyr->GetLayerDefn()->GetFieldIndex(attribute_name.c_str()) >= 0)
			continue;
		if (v.getAttributeType(attribute_name) == DM::Attribute::INT){
			OGRFieldDefn oField ( attribute_name.c_str(), OFTInteger );
			lyr->CreateField(&oField);
			updateAttributeDefinition(v.getName(),attribute_name, "INTEGER" );
			continue;
		}
		if (v.getAttributeType(attribute_name) == DM::Attribute::STRING){
			OGRFieldDefn oField ( attribute_name.c_str(), OFTString );
			lyr->CreateField(&oField);
			updateAttributeDefinition(v.getName(),attribute_name, "STRING" );
			continue;
		}
		if (v.getAttributeType(attribute_name) == DM::Attribute::DOUBLE){
			OGRFieldDefn oField ( attribute_name.c_str(), OFTReal );
			updateAttributeDefinition(v.getName(),attribute_name, "DOUBLE" );
			lyr->CreateField(&oField);
			continue;
		}
		if (v.getAttributeType(attribute_name) == DM::Attribute::STRINGVECTOR){
			OGRFieldDefn oField ( attribute_name.c_str(), OFTStringList );
			lyr->CreateField(&oField);
			updateAttributeDefinition(v.getName(),attribute_name, "STRINGVECTOR" );
			DM::Logger(DM::Error) << "Attribute typer STRINGVECTOR is currently not supported";
			continue;
		}
		if (v.getAttributeType(attribute_name) == DM::Attribute::DOUBLEVECTOR){
			OGRFieldDefn oField ( attribute_name.c_str(), OFTBinary );
			updateAttributeDefinition(v.getName(),attribute_name, "DOUBLEVECTOR" );
			lyr->CreateField(&oField);
			continue;
		}
		if (v.getAttributeType(attribute_name) == DM::Attribute::DATE){
			OGRFieldDefn oField ( attribute_name.c_str(), OFTDate );
			updateAttributeDefinition(v.getName(),attribute_name, "DATE" );
			lyr->CreateField(&oField);
			continue;
		}
		if (v.getAttributeType(attribute_name) == DM::Attribute::LINK){
			OGRFieldDefn oField ( attribute_name.c_str(), OFTInteger );
			lyr->CreateField(&oField);
			updateAttributeDefinition(v.getName(),attribute_name, "LINK" );
			// Not using real reference because it causes a not reproducable
			// problems that the link attribute might not be written.
			// Going back to implement it as simeple integer.
			// Uncomment above line for another try later.
			//			std::stringstream query;
			//			v.getNameOfLinkedView(attribute_name.c_str());
			//			query << "ALTER TABLE " << v.getName() << " ADD COLUMN " << attribute_name.c_str() << " INTEGER REFERENCES " << v.getNameOfLinkedView(attribute_name.c_str()) << "(OGC_FID)";
			//			this->poDS->ExecuteSQL(query.str().c_str(), 0, "SQLITE");
			//			lyr->GetLayerDefn()->AddFieldDefn(&oField);
			continue;
		}
	}
	GDALFlushCache(poDS);
}

void GDALSystem::updateViewContainer(DM::ViewContainer v)
{
	this->updateView(v);
}

OGRFeature *GDALSystem::createFeature(const View &v)
{
	OGRLayer * lyr = viewLayer[v.getName()];
	OGRFeature * f = OGRFeature::CreateFeature(lyr->GetLayerDefn());
	return f;
}

OGRLayer *GDALSystem::getOGRLayer(const View &v)
{
	if (viewLayer.find(v.getName()) == viewLayer.end()) {
		Logger(Error) << "OGR Layer not found ";
		return 0;
	}
	return viewLayer[v.getName()];
}

GDALDataset *GDALSystem::getDataSource()
{
	return this->poDS;
}

bool GDALSystem::resetReading(const View &v)
{
	if (viewLayer.find(v.getName()) == viewLayer.end()) {
		Logger(Error) << "Layer not found for rest";
		return false;
	}
	OGRLayer * lyr = viewLayer[v.getName()];
	lyr->ResetReading();
	return true;
}

GDALSystem *GDALSystem::createSuccessor()
{
	Logger(Debug) << "Create Sucessor ";
	GDALSystem* result = new GDALSystem(*this);
	this->sucessors.push_back(result);
	result->setPredecessor(this);

	return result;
}

void GDALSystem::updateViews(const std::vector<View> &views)
{
	foreach (DM::View v, views) {
		this->updateView(v);
	}
}

GDALSystem *GDALSystem::getPredecessor() const
{
	return this->predecessor;
}

void GDALSystem::setPredecessor(GDALSystem * sys)
{
	this->predecessor = sys;
}

OGRFeature *GDALSystem::getNextFeature(const View &v)
{
	OGRLayer * lyr = viewLayer[v.getName()];
	return lyr->GetNextFeature();
}

void GDALSystem::setNextByIndex(const View &v, long index){
	OGRLayer * lyr = viewLayer[v.getName()];
	lyr->SetNextByIndex(index);
}

void GDALSystem::closeConnection()
{
	if (poDS) {
		// OGRDataSource::DestroyDataSource(poDS);
		DM::Logger(DM::Debug) << "close connection";
		GDALClose(poDS);


		poDS = NULL;
	}
	if (db) {
		sqlite3_close(db);
		db = NULL;
	}
}


void GDALSystem::reConnect() {
	// poDS = poDrive->Open(this->getDBID().c_str(), true);
	poDS = (GDALDataset*) GDALOpenEx( this->getDBID().c_str(), GDAL_OF_VECTOR | GDAL_OF_UPDATE, NULL, NULL, NULL );
	//RebuildViewLayer
	for (std::map<std::string, OGRLayer *>::const_iterator it = viewLayer.begin();
		 it != viewLayer.end(); ++it) {
		std::string viewname = it->first;
		viewLayer[it->first] = poDS->GetLayerByName(viewname.c_str());
	}
		int rc =  sqlite3_open( this->getDBID().c_str(), &db);
		if( rc ){
			std::cout <<  "Can't open database: " << sqlite3_errmsg(db) << std::endl; 
			DM::Logger(DM::Error) <<  "Can't open database: " << sqlite3_errmsg(db);
		} else{
			std::cout <<  "Open database"  << std::endl; 
		}

}

string GDALSystem::getCurrentStateID()
{
	return this->state_ids[state_ids.size()-1];
}

sqlite3 * GDALSystem::getSQLDatabase() const
{
	return this->db;
}

string GDALSystem::getDBID() const
{
	return this->getWorkingDirectory() + this->DBID.toStdString() + ".db";
}

GDALSystem::~GDALSystem()
{
	if (db) {
		sqlite3_close(db);
		db = NULL;
	}
	if (poDS) {
		GDALClose(poDS);
		poDS = NULL;


		//Delete Database
		QString dbname =  QString::fromStdString(this->getDBID());
		if (!this->keepDatabaseFile)
			QFile::remove(dbname);

		foreach (DM::GDALSystem * suc, this->sucessors) {
			delete suc;
		}
	}

}

OGRLayer *GDALSystem::createLayer(const View &v)
{

	char ** options = NULL;
	options = CSLSetNameValue( options, "FORMAT", "SPATIALITE" );
	//options = CSLSetNameValue( options, "OGR_SQLITE_CACHE", "1024" );
	// Add Layer to definition database

	OGRLayer * l = poDS->GetLayerByName(v.getName().c_str()); //Check if alread in db and return
	if (l != NULL) {
		return l;
	}

	addLayerToDef(v);


	OGRSpatialReference* oSourceSRS;
	oSourceSRS = new OGRSpatialReference();
	oSourceSRS->importFromEPSG(this->EPSG);

	switch ( v.getType() ) {
	case DM::COMPONENT:
#ifdef _WIN32 //Use in windows since driver seems to have a problem to create wkbNone tables
		return poDS->CreateLayer(v.getName().c_str(), oSourceSRS, wkbPoint, options );
#else
		return poDS->CreateLayer(v.getName().c_str(), oSourceSRS, wkbUnknown, NULL );
#endif
		break;
	case DM::NODE:
		return poDS->CreateLayer(v.getName().c_str(), oSourceSRS, wkbPoint, options );
		break;
	case DM::EDGE:
		return poDS->CreateLayer(v.getName().c_str(), oSourceSRS, wkbLineString, options );
		break;
	case DM::FACE:
		return poDS->CreateLayer(v.getName().c_str(), oSourceSRS, wkbPolygon, options );
		break;
	}



	return NULL;
}

void GDALSystem::addLayerToDef(const View &v)
{
	OGRLayer * layer_dev = this->poDS->GetLayerByName("dynamind_table_definitions");
	OGRFeature * f_def;

	f_def = OGRFeature::CreateFeature(layer_dev->GetLayerDefn());
	f_def->SetField("view_name", v.getName().c_str());
	f_def->SetField("attribute_name", "DEFINITION");
	switch ( v.getType() ) {
	case DM::COMPONENT:
		f_def->SetField("data_type", "COMPONENT");
		break;
	case DM::NODE:
		f_def->SetField("data_type", "NODE");
		break;
	case DM::EDGE:
		f_def->SetField("data_type", "EDGE");
		break;
	case DM::FACE:
		f_def->SetField("data_type", "FACE");
		break;
	}
	layer_dev->CreateFeature(f_def);
	OGRFeature::DestroyFeature(f_def);

}

void GDALSystem::syncNewFeatures(const DM::View & v, std::vector<OGRFeature *> & df, bool destroy)
{
	if (df.size() == 0)
		return;
	OGRLayer * lyr = viewLayer[v.getName()];
	//Sync all features
	int counter = 0;
	int global_counter = 0;
	lyr->StartTransaction();
	foreach (OGRFeature * f, df) {
		counter++;
		global_counter++;
		if (counter == 10000) {
			lyr->CommitTransaction();
			lyr->StartTransaction();
			counter=0;
		}
		if (!f)
			continue;
		lyr->CreateFeature(f);
		if (destroy)
			OGRFeature::DestroyFeature(f);
	}
	lyr->CommitTransaction();
	df.clear();
}

void GDALSystem::synsDeleteFeatures(const View &v, std::vector<long> &df)
{
	if (df.size() == 0)
		return;
	Logger(Debug) << "Start Delete";
	OGRLayer * lyr = viewLayer[v.getName()];
	lyr->StartTransaction();
	for (int i = 0; i < df.size(); i++) {
		lyr->DeleteFeature(df[i]);
		if (i % 1000000 == 0) {
			lyr->CommitTransaction();
			lyr->StartTransaction();
		}
	}
	lyr->CommitTransaction();
	df.clear();
}

void GDALSystem::syncAlteredFeatures(const DM::View & v, std::vector<OGRFeature *> & df, bool destroy)
{
	if (df.size() == 0)
		return;
	Logger(Debug) << "Sync Altered";
	if (viewLayer.find(v.getName()) == viewLayer.end()) {
		DM::Logger(DM::Warning) << "Can't sync features layer does not exists";
		return;
	}
	OGRLayer * lyr = viewLayer[v.getName()];
	//Sync all features
	int counter = 0;
	int global_counter = 0;
	lyr->StartTransaction();
	foreach (OGRFeature * f, df) {
		counter++;
		global_counter++;
		if (counter == 100000) {
			lyr->CommitTransaction();
			lyr->StartTransaction();
			counter=0;
		}
		if (!f)
			continue;
		lyr->SetFeature(f);
		if (destroy)
			OGRFeature::DestroyFeature(f);
	}
	lyr->CommitTransaction();
	df.clear();
}

}
