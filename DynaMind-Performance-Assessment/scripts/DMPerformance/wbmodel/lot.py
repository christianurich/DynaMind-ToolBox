import pycd3 as cd3
from enum import Enum
import numpy as np

from .unitparameters import SoilParameters, UnitFlows

class DemandProfile(Enum):
    potable_demand_per_person = 1
    non_potable_demand_per_person = 2
    black_water = 3
    grey_water = 4
    crop_factor = 5
    # crop_factor_tree = 6


class LotStream(Enum):
    potable_demand = 1
    non_potable_demand = 2
    outdoor_demand = 3
    black_water = 4
    grey_water = 5
    roof_runoff = 6
    impervious_runoff = 7
    pervious_runoff = 8
    evapotranspiration = 9
    infiltration = 10
    rainfall = 11


class Streams(Enum):
    potable_demand = 1
    non_potable_demand = 2
    outdoor_demand = 3
    sewerage = 4
    grey_water = 5
    stormwater_runoff = 6
    evapotranspiration = 7
    infiltration = 8
    rainfall = 9

    # "potable_demand": ["_potable_demand"],
    # "non_potable_demand": ["_non_potable_demand"],
    # "outdoor_demand": ["_outdoor_demand"],
    # "sewerage": ["_black_water"],
    # "grey_water": ["_grey_water"],
    # "storages": [{"inflow": "_roof_runoff", "demand": "_outdoor_demand", "volume": 5},
    #              {"inflow": "_grey_water", "demand": "_outdoor_demand", "volume": 0.5}]


class Lot:
    def __init__(self,
                 id,
                 cd3_instance: cd3.CityDrain3,
                 lot_detail: {},
                 standard_values: {},
                 demand_profile: {},
                 lot_storage_reporting: {},):

        self._id = id
        self._cd3 = cd3_instance

        self._standard_values = standard_values[(lot_detail["soil_id"],lot_detail["station_id"], lot_detail["wb_demand_profile_id"])]

        self._green_roofs = None
        if lot_detail["green_roof"]:
            self._green_roofs = standard_values[(lot_detail["green_roof"]["soil_id"],lot_detail["station_id"],lot_detail["wb_demand_profile_id"])]

        self._internal_streams = {}
        self._external_streams = {}
        self._internal_report_streams = {}

        self._demand_profile = demand_profile

        self._lot_storage_reporting = lot_storage_reporting

        self._reporting_internal_stream = {}

        for e in LotStream:
            self._internal_streams[e] = None

        for e in Streams:
            self._external_streams[e] = None

        # Reporting stream
        self._lot_storage_reporting[id] = {}

        # Assume I'll be able to get all parameters for database
        self._create_lot(lot_detail)

    def get_stream(self, stream):
        return self._external_streams[stream]

    def get_internal_stream_report(self, stream: LotStream):
        return self._internal_streams[stream][0]

    def _create_lot(self, lot: {}):
        """
        What happens in the lot stays in the lot
        Following nodes are produced

        # Include potential for recycled water

        # Gather data for lot scale interventions
        # Lots can be part of supply zones

        # Exclude routing for now

        :return:
        """

        self._create_demand_node(lot["persons"])

        pervious_area = lot["area"] - lot["roof_area"] - lot["impervious_area"]

        print("Lot area: ", lot["area"])
        print("Roof area: ", lot["roof_area"])
        print("Impervious area: ", lot["impervious_area"])
        print("Pervious area: ", pervious_area)
        print("Garden area:",lot['irrigated_garden_area'])


        # Green roofs
        if (self._green_roofs):
            roof_evapotranspiration = np.array(self._green_roofs[UnitFlows.pervious_evapotranspiration]) * (
                lot["roof_area"])
            roof_runoff = (np.array(self._green_roofs[UnitFlows.pervious_runoff]) * lot["roof_area"] + \
                          np.array(self._green_roofs[UnitFlows.groundwater_infiltration]) * lot["roof_area"]).tolist()
            self._internal_streams[LotStream.roof_runoff] = self._create_stream(
                roof_runoff, 1)
        else:
            roof_evapotranspiration = np.array(self._standard_values[UnitFlows.roof_evapotranspiration]) * (
                lot["roof_area"])
            self._internal_streams[LotStream.roof_runoff] = self._create_stream(
                self._standard_values[UnitFlows.roof_runoff], lot["roof_area"])

        evapo = (np.array(self._standard_values[UnitFlows.impervious_evapotranspiration]) * (lot["impervious_area"]) + \
                 roof_evapotranspiration + \
                 np.array(self._standard_values[UnitFlows.pervious_evapotranspiration_irrigated]) * lot[
                     "irrigated_garden_area"] + \
                 np.array(self._standard_values[UnitFlows.pervious_evapotranspiration]) * (
                             pervious_area - lot["irrigated_garden_area"])).tolist()

        self._internal_streams[LotStream.rainfall] = self._create_stream(self._standard_values[UnitFlows.rainfall],
                                                                         lot["area"])
        self._internal_streams[LotStream.pervious_runoff] = self._create_stream(
            self._standard_values[UnitFlows.pervious_runoff], pervious_area)
        self._internal_streams[LotStream.impervious_runoff] = self._create_stream(
            self._standard_values[UnitFlows.impervious_runoff], lot["impervious_area"])

        self._internal_streams[LotStream.outdoor_demand] = self._create_stream(
            self._standard_values[UnitFlows.outdoor_demand], lot["irrigated_garden_area"])

        self._internal_streams[LotStream.evapotranspiration] = self._create_stream(evapo, 1)
        self._internal_streams[LotStream.infiltration] = self._create_stream(
            self._standard_values[UnitFlows.groundwater_infiltration], pervious_area)

        # This and reconnected
        if "storages" in lot:
            units = lot["units"]
            for idx, s in enumerate(lot["storages"]):
                self._add_storage(units, s)

        # Setup Streams
        for stream_id in self._external_streams:
            if stream_id in lot["streams"]:
                self._external_streams[stream_id] = self._sum_streams(
                    [self._internal_streams[s] for s in lot["streams"][stream_id]])

    def _create_const_flow(self, value: float) -> cd3.Flow:
        f = cd3.Flow()
        f[0] = value
        return f

    def _create_const_source(self, value: float) -> cd3.Flow:
        cs = self._cd3.add_node("ConstSource")
        cs.setParameter("const_flow", self._create_const_flow(value))
        return list((cs, "out"))

    def _add_storage(self, units: int, storage: dict) -> None:

        s = self._cd3.add_node("MultiUseStorageOpen")
        s.setDoubleParameter("storage_volume", storage["volume"] * units)

        self._lot_storage_reporting[self._id][storage["id"]] = s

        demand_stream = self._internal_streams[storage["demand"]]
        inflow_stream = self._internal_streams[storage["inflow"]]

        self._cd3.add_connection(demand_stream[0], demand_stream[1], s, "q_in_0")
        self._cd3.add_connection(inflow_stream[0], inflow_stream[1], s, "in_sw")
        f_inflow_stream = self._add_flow_probe(s, "out_sw")
        f_demand_stream = self._add_flow_probe(s, "q_out_0")
        inflow_stream[0] = f_inflow_stream[0]
        inflow_stream[1] = f_inflow_stream[1]
        demand_stream[0] = f_demand_stream[0]
        demand_stream[1] = f_demand_stream[1]

        if "demand_1" in storage:
            demand_stream = self._internal_streams[storage["demand_1"]]
            self._cd3.add_connection(demand_stream[0], demand_stream[1], s, "q_in_1")
            f_demand_stream = self._add_flow_probe(s, "q_out_1")
            demand_stream[0] = f_demand_stream[0]
            demand_stream[1] = f_demand_stream[1]

        if "demand_2" in storage:
            demand_stream = self._internal_streams[storage["demand_2"]]
            self._cd3.add_connection(demand_stream[0], demand_stream[1], s, "q_in_2")
            f_demand_stream = self._add_flow_probe(s, "q_out_2")
            demand_stream[0] = f_demand_stream[0]
            demand_stream[1] = f_demand_stream[1]

        if "loss_1" in storage:
            loss_stream = self._create_const_source(storage["loss_1_value"])
            self._cd3.add_connection(loss_stream[0], loss_stream[1], s, "q_in_3")

            f_loss_stream = self._add_flow_probe(s, "q_out_3")

            current_loss_stream = self._internal_streams[storage["loss_1"]]

            # combined_loss = self._sum_streams([current_loss_stream, f_loss_stream])

            # current_loss_stream[0] = combined_loss[0]
            # current_loss_stream[1] = combined_loss[1]

        if "loss_2" in storage:
            loss_stream = self._create_const_source(storage["loss_2_value"])
            self._cd3.add_connection(loss_stream[0], loss_stream[1], s, "q_in_4")

            f_loss_stream = self._add_flow_probe(s, "q_out_4")

            current_loss_stream = self._internal_streams[storage["loss_2"]]

            combined_loss = self._sum_streams([current_loss_stream, f_loss_stream])

            current_loss_stream[0] = combined_loss[0]
            current_loss_stream[1] = combined_loss[1]


    def _create_demand_node(self, residents: float):
        # Produces non-potable (out_np) and potable demands (out_p)
        consumer = self._cd3.add_node("Consumption")
        l_d_to_m_s = 1. / (1000. * 60. * 60. * 24.)

        consumer.setParameter("const_flow_potable", self._create_const_flow(
            self._demand_profile[DemandProfile.potable_demand_per_person] * l_d_to_m_s * residents))
        consumer.setParameter("const_flow_nonpotable", self._create_const_flow(
            self._demand_profile[DemandProfile.non_potable_demand_per_person] * l_d_to_m_s * residents))

        consumer.setParameter("const_flow_greywater",
                              self._create_const_flow(
                                  self._demand_profile[DemandProfile.grey_water] * l_d_to_m_s * residents))
        consumer.setParameter("const_flow_sewer",
                              self._create_const_flow(
                                  self._demand_profile[DemandProfile.black_water] * l_d_to_m_s * residents))

        self._internal_streams[LotStream.potable_demand] = self._add_flow_probe(consumer, "out_p")
        self._internal_streams[LotStream.non_potable_demand] = self._add_flow_probe(consumer, "out_np")

        self._internal_streams[LotStream.grey_water] = self._add_flow_probe(consumer, "out_g")
        self._internal_streams[LotStream.black_water] = self._add_flow_probe(consumer, "out_s")

    def _add_flow_probe(self, out_port, port_name):
        flow_probe = self._cd3.add_node("FlowProbe")
        self._cd3.add_connection(out_port, port_name, flow_probe, "in")
        return list((flow_probe, "out"))

    def _create_stream(self, stream, area):
        source_vector = self._cd3.add_node("SourceVector")
        source_vector.setDoubleVectorParameter("source", stream)
        source_vector.setDoubleParameter("factor", area)
        flow_probe = self._add_flow_probe(source_vector, "out")
        return flow_probe

    def _sum_streams(self, streams: []) -> list:
        mixer = self._cd3.add_node("Mixer")
        mixer.setIntParameter("num_inputs", len(streams))
        self._cd3.init_nodes()
        for idx, s in enumerate(streams):
            s: list
            self._cd3.add_connection(s[0], s[1], mixer, f"in_{idx}")
        return list((mixer, "out"))
