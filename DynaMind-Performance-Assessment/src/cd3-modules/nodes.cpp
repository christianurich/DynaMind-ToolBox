#include "tank.h"
#include "defaultblock.h"
#include "consumption.h"
#include "storage.h"
#include "imperviousrunoff.h"
#include "rwht.h"
#include "flowprobe.h"
#include "multiplyer.h"
#include "sourcevector.h"
#include "polder.h"
#include "simpletreatment.h"
#include "monthlyevo.h"
#include "redistributer.h"
#include "multiusestorage.h"
#include "multiusestorageopen.h"

#include <noderegistry.h>
#include <nodefactory.h>
#include <simulationregistry.h>
#include <simulationfactory.h>

#include <typefactory.h>
#include <cd3globals.h>

static const char *SOURCE = "Watersupply";

extern "C" {
	void CD3_PUBLIC registerNodes(NodeRegistry *registry) {
                registry->addNodeFactory(new NodeFactory<Tank>(SOURCE));
                registry->addNodeFactory(new NodeFactory<Default>(SOURCE));
                registry->addNodeFactory(new NodeFactory<Consumption>(SOURCE));
                registry->addNodeFactory(new NodeFactory<Storage>(SOURCE));
                registry->addNodeFactory(new NodeFactory<ImperviousRunoff>(SOURCE));
                registry->addNodeFactory(new NodeFactory<RWHT>(SOURCE));
				registry->addNodeFactory(new NodeFactory<FlowProbe>(SOURCE));
				registry->addNodeFactory(new NodeFactory<Multiplyer>(SOURCE));
				registry->addNodeFactory(new NodeFactory<SourceVector>(SOURCE));
                registry->addNodeFactory(new NodeFactory<Polder>(SOURCE));
				registry->addNodeFactory(new NodeFactory<SimpleTreatment>(SOURCE));
				registry->addNodeFactory(new NodeFactory<MonthlyEvo>(SOURCE));
				registry->addNodeFactory(new NodeFactory<Redistributer>(SOURCE));
				registry->addNodeFactory(new NodeFactory<MultiUseStorage>(SOURCE));
                registry->addNodeFactory(new NodeFactory<MultiUseStorageOpen>(SOURCE));

	}

    void CD3_PUBLIC registerSimulations(SimulationRegistry *registry) {
    }
}
