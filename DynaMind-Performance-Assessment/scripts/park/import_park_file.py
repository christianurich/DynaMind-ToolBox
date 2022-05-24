# -*- coding: utf-8 -*- 

import sys

import pydynamind as dm
import gdal, osr
import json

class ImportParkFile(dm.Module):
    display_name = "Import Park File"
    group_name = "Performance Assessment"

    def getHelpUrl(self):
        return ""

    def __init__(self):
        dm.Module.__init__(self)
        self.setIsGDALModule(True)

        self.createParameter("filename", dm.FILENAME, "Name of json file")
        self.filename = ""

        views = []

        # set up the zones view (same as the parcel view)
        self.zones = dm.ViewContainer("zone", dm.COMPONENT, dm.WRITE)
        self.zones.addAttribute("name", dm.Attribute.STRING, dm.WRITE)
        self.zones.addAttribute("wb_soil_id", dm.Attribute.STRING, dm.WRITE)

        
        # set up the lot view. Nothing gets written to the lot here, but just setting the structure
        self.lot = dm.ViewContainer('wb_lot', dm.COMPONENT, dm.WRITE)
        self.lot.addAttribute("persons", dm.Attribute.DOUBLE, dm.WRITE)
        self.lot.addAttribute("area", dm.Attribute.DOUBLE, dm.WRITE)
        self.lot.addAttribute("roof_area", dm.Attribute.DOUBLE, dm.WRITE)
        self.lot.addAttribute("outdoor_imp", dm.Attribute.DOUBLE, dm.WRITE)
        self.lot.addAttribute("garden_area", dm.Attribute.DOUBLE, dm.WRITE)
        self.lot.addAttribute("wb_grouping_id", dm.Attribute.INT, dm.WRITE)
        self.lot.addAttribute("units", dm.Attribute.INT, dm.WRITE)
        self.lot.addAttribute("station_id", dm.Attribute.INT, dm.WRITE)

        for i in range(1, 10):
            self.lot.addAttribute(f"wb_sub_catchment_id_{i}", dm.Attribute.INT, dm.WRITE)

        self.lot.addAttribute("demand", dm.Attribute.DOUBLE, dm.WRITE)
        self.lot.addAttribute("wb_lot_template_id", dm.Attribute.INT, dm.WRITE)
        self.lot.addAttribute("provided_volume", dm.Attribute.DOUBLE, dm.WRITE)
        self.lot.addAttribute("wb_soil_id", dm.Attribute.INT, dm.WRITE)
        self.lot.addAttribute("green_roof_id", dm.Attribute.INT, dm.WRITE)
        self.lot.addAttribute("wb_demand_profile_id", dm.Attribute.INT, dm.WRITE)


        #setup the soil moisture view. This is where all the soil properties are added from the parkfile
        self.soil = dm.ViewContainer('wb_soil_irrigated', dm.COMPONENT, dm.WRITE)
        self.soil.addAttribute('horton_inital_infiltration',dm.Attribute.DOUBLE,dm.WRITE)
        self.soil.addAttribute('horton_final_infiltration',dm.Attribute.DOUBLE,dm.WRITE)
        self.soil.addAttribute('horton_decay_constant',dm.Attribute.DOUBLE,dm.WRITE)
        self.soil.addAttribute('wilting_point',dm.Attribute.DOUBLE,dm.WRITE)
        self.soil.addAttribute('field_capactiy',dm.Attribute.DOUBLE,dm.WRITE)
        self.soil.addAttribute('soil_depth',dm.Attribute.DOUBLE,dm.WRITE)
        self.soil.addAttribute('saturation',dm.Attribute.DOUBLE,dm.WRITE)
        self.soil.addAttribute('intial_soil_depth',dm.Attribute.DOUBLE,dm.WRITE)
        self.soil.addAttribute('ground_water_recharge_rate',dm.Attribute.DOUBLE,dm.WRITE)
        self.soil.addAttribute('transpiration_capacity',dm.Attribute.DOUBLE,dm.WRITE)
        self.soil.addAttribute('initial_loss',dm.Attribute.DOUBLE,dm.WRITE)
        

        #TODO set up the station view here. linking each zone to a weater station







        views.append(self.lot)
        views.append(self.zones)
        views.append(self.soil)

        self.registerViewContainers(views)

    def init(self):
        
        pass


    def run(self):
        
        
        # Read json file
        with open(self.filename) as json_file:
            zones_data = json.load(json_file)
        
        # Set the zonedata from the parkfile
        for idx,z in enumerate(zones_data):
            zone = self.zones.create_feature()
            zone.SetField("name", z["name"])
            zone.SetField("wb_soil_id",idx+1)


            soil = self.soil.create_feature()
            soil.SetField('horton_inital_infiltration',z["soil_parameters"]["horton_inital_infiltration"])
            soil.SetField('horton_final_infiltration',z["soil_parameters"]["horton_final_infiltration"])
            soil.SetField('horton_decay_constant',z["soil_parameters"]["horton_decay_constant"])
            soil.SetField('wilting_point',z["soil_parameters"]["wilting_point"])
            soil.SetField('field_capactiy',z["soil_parameters"]["field_capactiy"])
            soil.SetField('soil_depth',z["soil_parameters"]["soil_depth"])
            soil.SetField('saturation',z["soil_parameters"]["saturation"])
            soil.SetField('intial_soil_depth',z["soil_parameters"]["intial_soil_depth"])
            soil.SetField('ground_water_recharge_rate',z["soil_parameters"]["ground_water_recharge_rate"])
            soil.SetField('transpiration_capacity',z["soil_parameters"]["transpiration_capacity"])
            soil.SetField('initial_loss',z["soil_parameters"]["initial_loss"])
        

        self.soil.finalise()
        self.zones.finalise()


