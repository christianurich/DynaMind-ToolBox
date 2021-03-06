#include "dm_strahler.h"
#include <dm.h>
#include <ogr_api.h>
#include <ogrsf_frmts.h>

DM_DECLARE_CUSTOM_NODE_NAME(DM_Strahler,Strahler Ordering, Network Generation)

DM_Strahler::DM_Strahler()
{
	GDALModule = true;

	this->view_name = "network";
	this->addParameter("view_name", DM::STRING, &view_name);
}

void DM_Strahler::init()
{
	network = DM::ViewContainer(view_name, DM::EDGE, DM::READ);
	network.addAttribute("strahler_order",  DM::Attribute::INT, DM::WRITE);
	network.addAttribute("start_id",  DM::Attribute::INT, DM::READ);
	network.addAttribute("end_id",  DM::Attribute::INT, DM::MODIFY);

	std::vector<DM::ViewContainer*> data_stream;
	data_stream.push_back(&network);

	this->registerViewContainers(data_stream);
}

void DM_Strahler::getNext(long node_id, long current_strahler, std::set<long> & visted)
{
	// [end_id] -----> [start_id]
	if (start_nodes.count(node_id) == 0) {
		return;
	}

	std::vector<long> start_edges = start_nodes[node_id];
	bool change_next = false;

	// Start Node
	std::vector<long> edges_at_start = end_nodes[node_id];

	int s_counter = 0;
	int g_counter = 0;
	foreach(long e, edges_at_start) {
		if (current_strahler <= strahler_id[e]) {
			s_counter++;
		} else if (strahler_id[e] != 0) {
			g_counter++;
		}
	}
	if (s_counter > 1)
		change_next = true;

	foreach (long edge, start_edges) {
		// Get next edge
		std::pair<long, long> e = edge_list[edge];
		long next = e.first;
		if (change_next) {
			if (strahler_id[edge] == current_strahler) {
				DM::Logger(DM::Debug) << "increase strahler " << current_strahler << " " << strahler_id[edge] << " " << edge << " " << node_id;
				current_strahler++;
			} else if(strahler_id[edge] > current_strahler){
				DM::Logger(DM::Debug) << "use strahler " << current_strahler << " " << strahler_id[edge] << " " << edge << " " << node_id;
				current_strahler = strahler_id[edge];
			}
		}

//		if (strahler_id[edge] > current_strahler){
//			current_strahler = strahler_id[edge];
//			change_next = true;
//		}

		strahler_id[edge] = current_strahler;
		if (g_counter > 1 && !change_next) {
			//continue;
		}
		if (visted.find(edge) != visted.end()) {
			DM::Logger(DM::Debug) << "Break Loop";
			continue;
		}
		visted.insert(edge);
		getNext(next, current_strahler, visted);
		break;
	}
}

void DM_Strahler::run()
{
	// reset all data
	edge_list.clear();
	strahler_id.clear();
	visitor_id.clear();
	start_nodes.clear();
	end_nodes.clear();
	node_con_counter.clear();

	network.resetReading();
	// [end_id] -----> [start_id]
	OGRFeature * f;
	DM::Logger(DM::Standard) << "Build search structure";
	int counter = 0;
	while (f = network.getNextFeature()) {
		counter++;
		if (counter % 10000 == 0) {
			DM::Logger(DM::Debug) << counter;
		}
		long start_id = f->GetFieldAsInteger("start_id"); // downstream
		long end_id = f->GetFieldAsInteger("end_id"); //upstream

		if (start_id == end_id)
			continue;

		strahler_id[f->GetFID()] = 0;
		visitor_id[f->GetFID()] = -1;
		edge_list[f->GetFID()] = std::pair<long, long>(start_id, end_id);

		if (start_nodes.count(end_id) == 0)
			start_nodes[end_id] = std::vector<long>();

		if (end_nodes.count(start_id) == 0)
			end_nodes[start_id] = std::vector<long>();

		if (node_con_counter.find(start_id) == node_con_counter.end())
			node_con_counter[start_id] = 0;

		if (node_con_counter.find(end_id) == node_con_counter.end())
			node_con_counter[end_id] = 0;

		node_con_counter[start_id] = node_con_counter[start_id] + 1;
		node_con_counter[end_id] = node_con_counter[end_id] + 1;

		std::vector<long> & vec_end = start_nodes[end_id];
		vec_end.push_back(f->GetFID());

		std::vector<long> & vec_start = end_nodes[start_id];
		vec_start.push_back(f->GetFID());
	}
	DM::Logger(DM::Debug) << "Start search";
	int start_nodes = 0;
	for (std::map<long, long >::const_iterator it = node_con_counter.begin();
		 it != node_con_counter.end();
		 it++) {
		if (it->second != 1)
			continue;
		start_nodes++;
	}
	counter = 0;
	for (std::map<long, long >::const_iterator it = node_con_counter.begin();
		 it != node_con_counter.end();
		 it++) {
		if (it->second != 1)
			continue;
		counter++;
		if (counter % 1000 == 0) {
			DM::Logger(DM::Debug) << counter << "/" << start_nodes;
		}
		// Get starting edge with inital strahler number 1
		std::set<long> visted;
		getNext(it->first, 1, visted);
	}
	DM::Logger(DM::Debug) << counter << "/" << start_nodes;
	// Write Strahler
	DM::Logger(DM::Debug) << "Write number";
	network.resetReading();
	// [end_id] -----> [start_id]
	while (f = network.getNextFeature()) {
		f->SetField("strahler_order", strahler_id[f->GetFID()]);
	}
}

