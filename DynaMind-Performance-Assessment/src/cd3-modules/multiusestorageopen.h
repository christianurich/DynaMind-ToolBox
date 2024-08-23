#ifndef MULTIUSESTORAGEOPEN_H
#define MULTIUSESTORAGEOPEN_H



#include <node.h>
#include <flow.h>

CD3_DECLARE_NODE(MultiUseStorageOpen)

public:
	MultiUseStorageOpen();
	~MultiUseStorageOpen();

	bool init(ptime start, ptime end, int dt);
	int f(ptime time, int dt);

private:
	double current_volume;
	double storage_volume;
	double storage_area;


	Flow in_sw;
	Flow out_sw;


	Flow q_in_0;
	Flow q_in_1;
	Flow q_in_2;

	Flow q_out_0;
	Flow q_out_1;
	Flow q_out_2;

	std::vector<Flow*> v_in_q;
	std::vector<Flow*> v_out_q;

	

	double total_in;
	double total_out;
	double total_provided;

	int spills;
	int dry;

	std::vector<double> storage_behaviour;
	std::vector<double> provided_volume;

};


#endif // MULTIUSESTORAGEOPEN_H
