import logging
from pyexpat import model
import pycd3 as cd3

from enum import Enum

# for intergration only
import pandas as pd


class SoilParameters(Enum):
    impervious_threshold = 1
    initial_soil_storage = 2
    infiltration_capacity = 3
    infiltration_exponent = 4
    initial_groundwater_store = 5
    daily_recharge_rate = 6
    daily_drainage_rate = 7
    daily_deep_seepage_rate = 8
    soil_store_capacity = 9
    field_capacity = 10
    transpiration_capacity = 11

class SoilParameters_Irrigation(Enum):
    horton_inital_infiltration = 1
    horton_final_infiltration = 2
    horton_decay_constant = 3
    wilting_point = 4
    field_capactiy = 5
    saturation = 6
    soil_depth = 7
    intial_soil_depth = 8
    ground_water_recharge_rate = 9
    transpiration_capacity = 10
    initial_loss = 11


class UnitFlows(Enum):
    roof_runoff = 1
    impervious_runoff = 2
    outdoor_demand = 3
    possible_infiltration = 4
    actual_infiltration = 5
    groundwater_infiltration = 6
    pervious_storage = 7
    effective_evapotranspiration = 8
    pervious_runoff = 9
    rainfall = 10
    evapotranspiration = 11
    pervious_evapotranspiration = 12
    pervious_evapotranspiration_irrigated = 13
    impervious_evapotranspiration = 14
    roof_evapotranspiration = 15
    soil_moisture = 16


class UnitParameters:
    def __init__(self,
                 start_date,
                 end_date,
                 soil_parameters: {},
                 climate_data: {},
                 crop_factor: float,
                 library_path):
        """
        Calculate standard values for per m2
        This includes
         - roof_runoff per m2 roof
         - surface_runoff per m2 surface runoff
         - outdoor_demand per m2 garden space
         - possible_infiltration per m2 non perv area
         - actual_infiltration per m2 non perv area
         - groundwater_infiltration per m2 non perv area
         - effective_evapotranspiration
         - rainfall
         - evapotranspiration
        """

        """
        Impervious threshold      1 mm
        Initial soil storage      30%
        Infiltration capacity     200 mm
        Infiltration exponent     1
        Initial groundwater store 10 mm
        Daily recharge rate       25%
        Daily drainage rate       5%
        Daily deep seepage rate   0%
        """

        print("Unit parameters")
        self._library_path = library_path
        self._standard_values = {}
        self.start_date = start_date
        self._climate_data = climate_data
        self.end_date = end_date
        self.soil = soil_parameters

        lot_area = 500
        perv_area_fra = 0.2
        roof_imp_fra = 0.5


        # get the keys of the soil parameters of the model. These will be different depending on what model is being used and thus can be
        # used to identify each model
        soil_param = list(self.soil.keys())

        # setup the inputs and reporting dicts for the model

        # old model
        if soil_param[0] == SoilParameters.impervious_threshold:

            horton_initial_cap = 0.09
            horton_final_cap = 0.001
            horton_decay_constant = 0.06
            # perv_soil_storage_capacity = 0.03
            # daily_recharge_rate = 0.25
            # transpiration_capacity = 7

            parameters = {}
            parameters["Catchment_Area_[m^2]"] = lot_area
            parameters["Fraktion_of_Pervious_Area_pA_[-]"] = perv_area_fra
            parameters["Fraktion_of_Impervious_Area_to_Stormwater_Drain_iASD_[-]"] = 1.0 - perv_area_fra - roof_imp_fra
            parameters["Fraktion_of_Impervious_Area_to_Reservoir_iAR_[-]"] = roof_imp_fra
            parameters["Outdoor_Demand_Weighing_Factor_[-]"] = 1.0

            parameters["Initial_Infiltration_Capacity_[m/h]"] = horton_initial_cap
            parameters["Final_Infiltration_Capacity_[m/h]"] = horton_final_cap
            parameters["Decay_Constant_[1/min]"] = horton_decay_constant
            parameters["Soil Storage Capacity in m"] = self.soil[SoilParameters.soil_store_capacity]
            parameters["Daily Recharge Rate"] = self.soil[SoilParameters.daily_recharge_rate]
            parameters["Transpire Capacity"] = self.soil[SoilParameters.transpiration_capacity]

            reporting = {}
            reporting[UnitFlows.roof_runoff] = {"port": "Collected_Water", "factor": (lot_area * roof_imp_fra)}
            reporting[UnitFlows.impervious_runoff] = {"port": "impervious_runoff",
                                                    "factor": (lot_area * (1 - perv_area_fra - roof_imp_fra))}
            reporting[UnitFlows.outdoor_demand] = {"port": "Outdoor_Demand", "factor": (lot_area / crop_factor * (
                perv_area_fra))}  # {"port": "Outdoor_Demand", "factor" : (lot_area * ( perv_area_fra ))}

            reporting[UnitFlows.possible_infiltration] = {"port": "Possible_Infiltration",
                                                        "factor": (lot_area * (perv_area_fra))}
            reporting[UnitFlows.actual_infiltration] = {"port": "Actual_Infiltration",
                                                        "factor": (lot_area * (perv_area_fra))}
            reporting[UnitFlows.groundwater_infiltration] = {"port": "groundwater_infiltration",
                                                            "factor": (lot_area * (perv_area_fra))}
            reporting[UnitFlows.pervious_storage] = {"port": "previous_storage", "factor": (lot_area * (perv_area_fra))}
            reporting[UnitFlows.effective_evapotranspiration] = {"port": "effective_evapotranspiration",
                                                                "factor": (lot_area * (perv_area_fra))}
            reporting[UnitFlows.pervious_runoff] = {"port": "pervious_runoff", "factor": (lot_area * (perv_area_fra))}

        # new model
        elif soil_param[0] == SoilParameters_Irrigation.horton_inital_infiltration:

            parameters = {}

            parameters["Catchment_Area_[m^2]"] = lot_area
            parameters["Fraktion_of_Pervious_Area_pA_[-]"] = perv_area_fra
            parameters["Fraktion_of_Impervious_Area_to_Stormwater_Drain_iASD_[-]"] = 1.0 - perv_area_fra - roof_imp_fra
            parameters["Fraktion_of_Impervious_Area_to_Reservoir_iAR_[-]"] = roof_imp_fra

            parameters["Initial_Infiltration_Capacity_[m/h]"] = self.soil[SoilParameters_Irrigation.horton_inital_infiltration]
            parameters["Final_Infiltration_Capacity_[m/h]"] = self.soil[SoilParameters_Irrigation.horton_final_infiltration]
            parameters["Decay_Constant_[1/min]"] = self.soil[SoilParameters_Irrigation.horton_decay_constant]

            parameters["Wilting_Point_[%]"] = self.soil[SoilParameters_Irrigation.wilting_point]
            parameters["Field_Capacity_[%]"] = self.soil[SoilParameters_Irrigation.field_capactiy]
            parameters["Saturation_[%]"] = self.soil[SoilParameters_Irrigation.saturation]
            
            parameters["Soil Storage Capacity [m]"] = self.soil[SoilParameters_Irrigation.soil_depth]
            parameters["Initial_Pervious_Storage_Level_[m]"] = self.soil[SoilParameters_Irrigation.intial_soil_depth]
            parameters["Wetting_Loss_[m]"] = self.soil[SoilParameters_Irrigation.initial_loss]

            parameters["Daily Recharge Rate"] = self.soil[SoilParameters_Irrigation.ground_water_recharge_rate]
            parameters["Transpire Capacity"] = self.soil[SoilParameters_Irrigation.transpiration_capacity]


            reporting = {}

            reporting[UnitFlows.roof_runoff] = {"port": "roof_runoff", "factor": (lot_area * roof_imp_fra)}
            reporting[UnitFlows.impervious_runoff] = {"port": "impervious_runoff","factor": (lot_area * (1 - perv_area_fra - roof_imp_fra))}
            reporting[UnitFlows.pervious_runoff] = {"port": "pervious_runoff", "factor": (lot_area * (perv_area_fra))}
            reporting[UnitFlows.outdoor_demand] = {"port": "outdoor_demand", "factor": (lot_area * perv_area_fra)} 
            reporting[UnitFlows.possible_infiltration] = {"port": "possible_infiltration", "factor": (lot_area * (perv_area_fra))}
            reporting[UnitFlows.actual_infiltration] = {"port": "actual_infiltration","factor": (lot_area * (perv_area_fra))}
            reporting[UnitFlows.groundwater_infiltration] = {"port": "groundwater_infiltration","factor": (lot_area * (perv_area_fra))}
            reporting[UnitFlows.pervious_storage] = {"port": "pervious_storage", "factor": (lot_area * (perv_area_fra))}
            reporting[UnitFlows.pervious_evapotranspiration] = {"port": "pervious_evapotranspiration", "factor": (lot_area * (perv_area_fra))}
            reporting[UnitFlows.pervious_evapotranspiration_irrigated] = {"port": "pervious_evapotranspiration", "factor": (lot_area * (perv_area_fra))}
            reporting[UnitFlows.impervious_evapotranspiration] = {"port": "impervious_evapotranspiration", "factor": (lot_area * (1 - perv_area_fra - roof_imp_fra))}
            reporting['Perv_Rainstorage'] = {"port": "Perv_Rainstorage", "factor": (lot_area * (perv_area_fra))}
            reporting[UnitFlows.soil_moisture] = {"port": "soil_moisture", "factor": 1}

        #set up the city model and register the python plugins

        flow = {'Q': cd3.Flow.flow, 'N': cd3.Flow.concentration}


        print("Init CD3")
        catchment_model = cd3.CityDrain3(
            self.start_date,
            self.end_date,
            "86400",
            flow
        )

        # Init CD3
        # Register Modules
        catchment_model.register_native_plugin(
            self.get_default_folder() + "/libcd3core")

        cd3_module_root_folder = self.get_default_folder()

        if "/usr/local/bin/"  in cd3_module_root_folder:
            cd3_module_root_folder = "/usr/local/share/DynaMind"
        elif "/usr/bin/"  in cd3_module_root_folder:
            cd3_module_root_folder = "/usr/share/DynaMind"

        catchment_model.register_native_plugin(
            cd3_module_root_folder + "/CD3Modules/libdance4water-nodes")
        catchment_model.register_python_path(
            cd3_module_root_folder + "/CD3Modules/CD3Waterbalance/Module")
        catchment_model.register_python_path(
            cd3_module_root_folder + "/CD3Modules/CD3Waterbalance/WaterDemandModel")
        catchment_model.register_python_plugin(
            cd3_module_root_folder + "/CD3Modules/CD3Waterbalance/Module/cd3waterbalancemodules.py")


        # select the model based on the soil parameter types and carry this foward

        if soil_param[0] == SoilParameters.impervious_threshold:

            catchment_w_routing = catchment_model.add_node("Catchment_w_Routing")
            model = catchment_w_routing


        elif soil_param[0] == SoilParameters_Irrigation.horton_inital_infiltration: 
        
            catchment_w_irrigation = catchment_model.add_node('Catchment_w_Irrigation')
            model = catchment_w_irrigation

            # add the correct ET data and rainfall to the model
            # climate = pd.read_csv("/workspaces/DynaMind-ToolBox/tests/resources/climate_data.csv")
            # climate['Date'] = pd.to_datetime(climate['Date'],format='%d/%m/%Y')
            # climate.set_index('Date',inplace=True)
            #self._climate_data["evapotranspiration"] = [v/1000 for v in climate.loc['2021']['ET'].to_list()]
            #self._climate_data["rainfall intensity"] = [v/1000 for v in climate.loc['2021']['Rainfall'].to_list()]

        
        for p in parameters.items():
            model.setDoubleParameter(p[0], p[1])

        rain = catchment_model.add_node("SourceVector")
        rain.setDoubleVectorParameter("source", self._climate_data["rainfall intensity"])
        evapo = catchment_model.add_node("SourceVector")

        if soil_param[0] == SoilParameters.impervious_threshold:
            evapo.setDoubleVectorParameter("source", self._climate_data["evapotranspiration"])
        elif soil_param[0] == SoilParameters_Irrigation.horton_inital_infiltration:
            evapo.setDoubleVectorParameter("source", self._climate_data["potential pt data"])
        
        
        catchment_model.add_connection(rain, "out", model, "Rain")
        catchment_model.add_connection(evapo, "out", model, "Evapotranspiration")

        # if its the irrigation module, we also need an irrigation stream to the catchment
        if soil_param[0] == SoilParameters_Irrigation.horton_inital_infiltration:
            irrigation = catchment_model.add_node("SourceVector")

            irrigation.setDoubleVectorParameter("source", self._climate_data["irrigation"])
            catchment_model.add_connection(irrigation, "out", model, "irrigation")

        flow_probe = {}
        for key, r in reporting.items():
            rep = catchment_model.add_node("FlowProbe")
            catchment_model.add_connection(model, r["port"], rep, "in")
            flow_probe[key] = rep
        
        catchment_model.init_nodes()
        catchment_model.start(self.start_date)
        
        
        for key, probe in flow_probe.items():
            
            try:
                scaling = 1. / reporting[key]["factor"]
            except ZeroDivisionError:
                scaling = 0

            self._standard_values[key] = [v * scaling for v in probe.get_state_value_as_double_vector('Flow')]
            #for testing to get the full unscaled values
            #self._standard_values[key] = [v for v in probe.get_state_value_as_double_vector('Flow')]

        self._standard_values[UnitFlows.rainfall] = [v for v in self._climate_data["rainfall intensity"]]
        

        if soil_param[0] == SoilParameters.impervious_threshold:
            self._standard_values[UnitFlows.evapotranspiration] = [v for v in self._climate_data["evapotranspiration"]]
        elif soil_param[0] == SoilParameters_Irrigation.horton_inital_infiltration:
            self._standard_values[UnitFlows.evapotranspiration] = [v for v in self._climate_data["potential pt data"]]

        pervious_evapotranspiration_irrigated = []
        impervious_evapotranspiration = []
        roof_evapotranspiration = []
        pervious_evapotranspiration = []

        # the old and new models go about calculating the evapotranspiration differently. 
        # old model: the storage losses are caluclated below
        # new model: the storage losses are calculated interanlly and added to the right 'standard value' in the previos step

        for idx, v in enumerate(self._standard_values[UnitFlows.groundwater_infiltration]):

            if soil_param[0] == SoilParameters.impervious_threshold:

                pervious_evapotranspiration.append(self._standard_values[UnitFlows.rainfall][idx]
                                                - self._standard_values[UnitFlows.pervious_runoff][idx]
                                                - self._standard_values[UnitFlows.actual_infiltration][idx]
                                                + self._standard_values[UnitFlows.effective_evapotranspiration][idx])
                pervious_evapotranspiration_irrigated.append(
                    self._standard_values[UnitFlows.rainfall][idx] -
                    self._standard_values[UnitFlows.pervious_runoff][idx] -
                    self._standard_values[UnitFlows.actual_infiltration][idx] +
                    self._standard_values[UnitFlows.effective_evapotranspiration][idx] +
                    self._standard_values[UnitFlows.outdoor_demand][idx]
                )

            impervious_evapotranspiration.append(
                self._standard_values[UnitFlows.rainfall][idx] - self._standard_values[UnitFlows.impervious_runoff][
                    idx])
            roof_evapotranspiration.append(
                self._standard_values[UnitFlows.rainfall][idx] - self._standard_values[UnitFlows.roof_runoff][
                    idx])
        
        
        if soil_param[0] == SoilParameters.impervious_threshold:

            self._standard_values[UnitFlows.pervious_evapotranspiration] = pervious_evapotranspiration
            self._standard_values[UnitFlows.pervious_evapotranspiration_irrigated] = pervious_evapotranspiration_irrigated
            self._standard_values[UnitFlows.impervious_evapotranspiration] = impervious_evapotranspiration

        self._standard_values[UnitFlows.roof_evapotranspiration] = roof_evapotranspiration

        #print('Soil Mositure: ', [i/self.soil[SoilParameters_Irrigation.soil_depth] * 100 for i in self._standard_values[UnitFlows.pervious_storage]])

        for key, values in self._standard_values.items():
            logging.info(
                f"{key} {format(sum(values), '.4f')}")
        #print('impervious_check:', sum(impervious_evapotranspiration) )
            # logging.warning(
            #     f"{key} {[format(v, '.2f') for v in values]}")

        #del catchment_model

        # write the soil moisture, date, rainfall field capacity, wilting point, saturation to a csv file for plotting
        
        #df['Soil Moisture'] = [i/self.soil[SoilParameters_Irrigation.soil_depth] * 100 for i in self._standard_values[UnitFlows.pervious_storage]]
        #df[['wilding_point', 'field_capacity', 'saturation']] = [self.soil[SoilParameters_Irrigation.wilting_point], self.soil[SoilParameters_Irrigation.field_capactiy], self.soil[SoilParameters_Irrigation.saturation]]
        # df['Date'] = climate.loc['2021'].index

        # df = pd.DataFrame(self._standard_values)
        # df.to_csv('/workspaces/DynaMind-ToolBox/tests/resources/soil_moisture5.csv', index=False)

    @property
    def unit_values(self) -> {}:
        return self._standard_values

    def get_default_folder(self):
        return self._library_path
