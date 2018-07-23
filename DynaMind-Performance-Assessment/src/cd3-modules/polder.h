#ifndef POLDER_H
#define POLDER_H

#include <node.h>
#include <flow.h>

CD3_DECLARE_NODE(Polder)

public:
    Polder();

    bool init(ptime start, ptime end, int dt);
    int f(ptime time, int dt);

private:
    double storage_volume;
    Flow in;
//    int num_pumps;

    std::vector<double> Qp;
    std::vector<double> Vmin;

	std::vector<double> loadings;

    std::vector<Flow *> outputs;
    std::vector<std::string> output_names;

};

#endif // POLDER_H