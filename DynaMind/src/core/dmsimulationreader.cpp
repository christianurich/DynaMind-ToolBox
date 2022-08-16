/**
 * @file
 * @author  Chrisitan Urich <christian.urich@gmail.com>
 * @version 1.0
 * @section LICENSE
 *
 * This file is part of DynaMind
 *
 * Copyright (C) 2011-2015  Christian Urich

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

#include "dmsimulationreader.h"
#include "dmlogger.h"

using namespace std;

SimulationReader::SimulationReader(QIODevice* source,  const DM::SimulationConfig & config) 
{
	source->open(QIODevice::ReadOnly);
	settingsConfig = config;
	id = 0;
	QXmlSimpleReader r;
	r.setContentHandler(this);
	r.setErrorHandler(this);
	r.parse(QXmlInputSource(source));
	tmpNode.DebugMode = false;
	source->close();
}

bool SimulationReader::fatalError(const QXmlParseException & exception) 
{
	DM::Logger(DM::Error) << "fatal error while parsing xml " << exception.message().toStdString();

	return true;
}

bool SimulationReader::characters(const QString & ch) 
{
	tmpValue = tmpValue + ch;
	return true;
}

bool SimulationReader::startElement(const QString & namespaceURI,
									const QString & localName,
									const QString & qName,
									const QXmlAttributes & atts)
{
	Q_UNUSED(namespaceURI)
	Q_UNUSED(localName)
	if (qName == "DynaMind")
		return true;
	if (qName == "DynaMindCore")
		return true;

	if (qName == "Settings") {
		// settingsConfig = DM::SimulationConfig();
		return true;
	}
	if (qName == "EPSG") {
		this->settingsConfig.setCoordinateSystem(atts.value("value").toInt());
		return true;
	}
	if (qName == "WorkingDir") {
		this->settingsConfig.setWorkingDir(atts.value("value").toStdString());
		return true;
	}
	if (qName == "KeepSystems") {
		this->settingsConfig.setKeepSystems((bool)atts.value("value").toInt());
		return true;
	}
	if (qName == "Nodes") {
		ParentName = "Nodes";
		return true;
	}
	if (qName == "RootNode") {
		tmpNode = ModuleEntry();
		ParentName = "RootNode";
		return true;
	}
	if (qName == "Node") {
		tmpNode = ModuleEntry();
		ParentName = "Node";
		return true;
	}
	if (qName == "Links") {
		ParentName = "Links";
		return true;
	}
	if (qName == "InPort") {
		ParentName = "InPort";
		return true;
	}
	if (qName == "OutPort") {
		ParentName = "OutPort";
		return true;
	}

	if (qName == "Link") {
		tmpLink = LinkEntry();
		return true;
	}
	if (qName == "ClassName") {
		tmpNode.ClassName = atts.value("value");
		return true;
	}
	if (qName == "UUID") {
		if (ParentName == "Node")
			tmpNode.UUID = atts.value("value");
		if (ParentName == "InPort")
			tmpLink.InPort.UUID = atts.value("value");
		if (ParentName == "OutPort")
			tmpLink.OutPort.UUID = atts.value("value");
		if (ParentName == "RootNode")
			RootUUID = atts.value("value");
		return true;
	}
	if (qName == "DebugMode") {
		if (ParentName == "Node")
			tmpNode.DebugMode = (bool) atts.value("value").toInt();
		return true;
	}
	if (qName == "PortName") {
		if (ParentName == "InPort")
			tmpLink.InPort.PortName = atts.value("value");
		//tmpLink.InPort.isTuplePort = -1;
		if (ParentName == "OutPort")
			tmpLink.OutPort.PortName = atts.value("value");
		//tmpLink.OutPort.isTuplePort = -1;
		return true;
	}
	if (qName == "PortType") {
		if (ParentName == "InPort")
			tmpLink.InPort.isTuplePort = atts.value("value").toInt();
		if (ParentName == "OutPort")
			tmpLink.OutPort.isTuplePort = atts.value("value").toInt();
		return true;
	}
	if (qName == "BackLink") {
		tmpLink.backlink =  atts.value("value").toInt();
		return true;
	}
	if (qName == "GroupUUID") {
		tmpNode.GroupUUID = atts.value("value");
		return true;
	}
	if (qName == "Name") {
		tmpNode.Name = atts.value("value");
		return true;
	}
	if (qName == "parameter") {
		tmpParameterName = atts.value("name");
		tmpValue.clear();
		return true;
	}
	if (qName == "Filter") {
		tmpFilter = FilterEntry();
		return true;
	}
	if (qName == "attribtue_filter") {
		tmpValue.clear();
		return true;
	}
	if (qName == "spatial_filter") {
		tmpValue.clear();
		return true;
	}
	if (qName == "view_name") {
		tmpValue.clear();
		return true;
	}
	return true;
}

bool SimulationReader::endElement(const QString & namespaceURI,
								  const QString & localName,
								  const QString & qName)
{
	if (qName == "Node") {
		this->moduleEntries.append(tmpNode);
	}
	if (qName == "parameter") {
		tmpValue = tmpValue.trimmed();
		this->tmpNode.parameters[tmpParameterName] = tmpValue;
		tmpValue.clear();
	}
	if (qName == "spatial_filter") {
		tmpValue = tmpValue.trimmed();
		tmpFilter.spatial_filter = tmpValue;
		tmpValue.clear();
	}
	if (qName == "attribtue_filter") {
		tmpValue = tmpValue.trimmed();
		tmpFilter.attribtue_filter = tmpValue;
		tmpValue.clear();
	}
	if (qName == "view_name") {
		tmpValue = tmpValue.trimmed();
		tmpFilter.view_name = tmpValue;
		tmpValue.clear();
	}
	if (qName == "Link") {
		this->linkEntries.append(tmpLink);
	}
	if (qName == "Filter") {
		this->tmpNode.filterEntries.push_back(tmpFilter);
	}
	return true;
}
