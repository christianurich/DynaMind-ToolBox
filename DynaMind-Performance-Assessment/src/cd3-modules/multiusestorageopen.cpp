#include "multiusestorageopen.h"

typedef  unsigned int uint;

CD3_DECLARE_NODE_NAME(MultiUseStorageOpen)

MultiUseStorageOpen::MultiUseStorageOpen() {
	addParameter(ADD_PARAMETERS(storage_volume))
			.setUnit("m^3");

	addState(ADD_PARAMETERS(spills));
	addState(ADD_PARAMETERS(dry));

	addInPort(ADD_PARAMETERS(in_sw));

	addOutPort(ADD_PARAMETERS(out_sw));


	for (int i = 0; i< 5; i++){
		Flow * q;
		q = new Flow();
		v_in_q.push_back(q);
		std::stringstream ss;
		ss << "q_in_" << i;
		addInPort(ss.str(), q);
	}

	for (int i = 0; i< 5; i++){
		Flow * q;
		q = new Flow();
		v_out_q.push_back(q);
		std::stringstream ss;
		ss << "q_out_" << i;
		addOutPort(ss.str(), q);
	}


	addState(ADD_PARAMETERS(spills));
	addState(ADD_PARAMETERS(dry));

	addState(ADD_PARAMETERS(storage_behaviour));
	addState(ADD_PARAMETERS(provided_volume));

}

MultiUseStorageOpen::~MultiUseStorageOpen() {
    for (uint i = 0; i < v_in_q.size(); i++){
			delete v_in_q[i];
			delete v_out_q[i];
	}
}



int MultiUseStorage::f(ptime time, int dt) {
	(void) time;

	//default returns
	out_sw[0] = 0;
	q_out_0[0] = 0;

	for (uint i = 0; i < v_out_q.size(); i++){
			(*v_out_q[i])[0] = 0;
	}

	// Total volume
	current_volume += in_sw[0];

	if (current_volume < 0.001)
		dry+=1;

	// reduce current volume
	double total_provided_v = 0;
	for (uint i = 0; i < v_in_q.size(); i++){
		// get demand on node
		double v = (*v_in_q[i])[0];

		// reduce demand from current volume
		current_volume -= v;

		double provided_v = v;

		// if current volume is negative, reduce demand and set current volume to 0
		if (current_volume < 0) {
			provided_v = current_volume + v;
			current_volume = 0;

		}
		total_provided_v+=provided_v;

		if (i < 3){
			(*v_out_q[i])[0] = v-provided_v;
		} else {
		// for infiltration and evoporation 
			(*v_out_q[i])[0] = provided_v;
		}
	}

	if (current_volume > storage_volume){
		out_sw[0] = current_volume - storage_volume;
		current_volume = storage_volume;
	}

	if (out_sw[0] > 0.001) {
		spills +=1;
	}
	storage_behaviour.push_back(current_volume);
	provided_volume.push_back(total_provided_v);

	return dt;
}


bool MultiUseStorage::init(ptime start, ptime end, int dt) {
	(void) start;
	(void) end;

	//Reset all values when init!
	total_in = 0;
	total_out = 0;
	current_volume = 0;
	spills = 0;
	dry = 0;

	current_volume = 0;
	//storage_volume = 0;

	storage_behaviour.clear();
	provided_volume.clear();
	return true;
}

