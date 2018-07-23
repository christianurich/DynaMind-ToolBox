#include "simpletreatment.h"

CD3_DECLARE_NODE_NAME(SimpleTreatment)

SimpleTreatment::SimpleTreatment()
{
	removal_fraction = 0;
	addParameter(ADD_PARAMETERS(removal_fraction))
			.setUnit("m^3");

	addInPort(ADD_PARAMETERS(in));
	addOutPort(ADD_PARAMETERS(out));

}

int SimpleTreatment::f(ptime time, int dt) {
	(void) time;

	out[0] = in[0];

	for (size_t i = 1; i < out.size(); i++)
		out[i] = in[i] * (1.-removal_fraction);
	return dt;
}




bool SimpleTreatment::init(ptime start, ptime end, int dt) {
	(void) start;
	(void) end;

	return true;
}