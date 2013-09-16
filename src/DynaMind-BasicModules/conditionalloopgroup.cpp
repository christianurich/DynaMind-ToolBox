/**
* @file
* @author  Chrisitan Urich <christian.urich@gmail.com>
* @version 1.0
* @section LICENSE
*
* This file is part of DynaMind
*
* Copyright (C) 2011  Christian Urich

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

#include "conditionalloopgroup.h"
#include "guiloopgroup.h"
#include <dmlogger.h>
#include <QInputDialog>
#include <dmsystem.h>

using namespace DM;

#include <guiloopgroup.h>

DM_DECLARE_NODE_NAME(ConditionalLoopGroup, Groups)

ConditionalLoopGroup::ConditionalLoopGroup() 
{
	conditionString = "<enter condition>";
	this->addParameter("conditionString", DM::STRING, &conditionString);
}

bool ConditionalLoopGroup::condition()
{
	if(evalConditionString())
	{
		loopStreams();
		return true;
	}
	return false;
}

bool checkAttribute(Attribute* a, char* op, double value)
{
	if(a->getType() != Attribute::DOUBLE)
		return false;

	double actualvalue = a->getDouble();
	
	if(strcmp(op, "<") == 0)
		return actualvalue < value;
	else if(strcmp(op, ">") == 0)
		return actualvalue > value;
	else if(strcmp(op, "=") == 0)
		return actualvalue == value;
	else if(strcmp(op, ">=") == 0)
		return actualvalue >= value;
	else if(strcmp(op, "<=") == 0)
		return actualvalue <= value;

	return false;
}

bool ConditionalLoopGroup::evalConditionString()
{
	char viewName[512];
	char attributeName[512];
	char op[512];
	double value = 0.0;

	if(sscanf(conditionString.c_str(), "%[^. ].%s %s %g", viewName, attributeName, op, &value) != 4)
	{
		Logger(Error) << "invalid condition string in module '" << getName() << "'";
		return false;
	}

	Attribute* a;
	foreach(std::string writePort, writeStreams)
	{
		if(System* sys = getInPortData(writePort))
		{
			mforeach(Component* c, sys->getAllComponentsInView(View(viewName)))
			{
				std::map<std::string, Attribute*> attributes = c->getAllAttributes();
				if(map_contains(&attributes, std::string(attributeName), a))
					if(!checkAttribute(a, op, value))
						return false;
			}
		}
	}

	return true;
}

bool ConditionalLoopGroup::createInputDialog() 
{
	LoopGroup::createInputDialog();
	
	conditionString = QInputDialog::getText(NULL, "set condition string", "usage: \"view.attribute operator compare-value\ne.g. CITY.area > 500", 
		QLineEdit::Normal, QString::fromStdString(conditionString)).toStdString();

	return true;
}
