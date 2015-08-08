/**
 * CityDrain3 is an open source software for modelling and simulating integrated 
 * urban drainage systems.
 * 
 * Copyright (C) 2012 Gregor Burger
 * 
 * This program is free software; you can redistribute it and/or modify it under 
 * the terms of the GNU General Public License as published by the Free Software 
 * Foundation; version 2 of the License.
 * 
 * This program is distributed in the hope that it will be useful, but WITHOUT ANY 
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
 * PARTICULAR PURPOSE. See the GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License along with 
 * this program; if not, write to the Free Software Foundation, Inc., 51 Franklin 
 * Street, Fifth Floor, Boston, MA 02110-1301, USA.
 **/

#ifndef FLOWBUFFER_H
#define FLOWBUFFER_H

struct FBPrivate;
class Flow;

#include <queue>
#include <cd3globals.h>
#include <flow.h>

typedef std::pair<Flow, int> buf_item;

class CD3_PUBLIC FlowBuffer
{
public:
	FlowBuffer();
	virtual ~FlowBuffer();
	void put(const Flow &f, int dt);
	Flow take(int dt);
	int buffered() const;
private:
	std::queue<buf_item> buffer;
	int	buffereddt;
};

#endif // FLOWBUFFER_H