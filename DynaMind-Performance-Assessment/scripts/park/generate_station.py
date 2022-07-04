# -*- coding: utf-8 -*- 


import pydynamind as dm


class GenerateStation(dm.Module):
    display_name = "Generate or Modifiy Station Data"
    group_name = "Performance Assessment"

    def getHelpUrl(self):
        return ""

    def __init__(self):
        dm.Module.__init__(self)
        self.setIsGDALModule(True) 

        self.createParameter("rainfall_values",dm.STRING,"Rainfall Data Time Series")
        self.rainfall_values = "0.0,0.6,2.0,0.0,0.0,0.0,0.0,3.0,0.4,0.0,1.0,5.0,3.0,4.0,0.0,0.0,2.0,0.2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.6,2.0,0.0,0.0,0.4,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,5.0,0.0,0.6,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.4,0.0,0.0,0.0,0.0,0.4,0.0,3.0,0.0,0.0,0.0,0.0,5.0,19.0,28.0,33.0,0.0,14.5,8.0,0.2,0.6,2.0,0.2,0.0,0.0,0.0,39.0,53.0,23.0,14.0,0.4,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,7.0,3.0,0.0,14.0,9.0,0.0,0.6,0.2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,10.0,0.0,0.0,0.2,0.0,0.0,0.0,0.0,0.0,2.0,5.0,0.4,0.0,0.0,0.0,5.0,1.0,0.2,1.0,12.0,9.0,1.0,0.0,0.0,0.6,0.2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,3.0,0.0,0.0,0.0,0.4,2.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.2,0.0,0.0,0.8,6.0,0.6,0.0,0.0,0.0,0.0,0.0,5.0,3.0,0.2,2.0,0.0,0.0,0.0,0.0,0.0,0.8,0.2,12.0,0.0,0.0,2.0,3.0,0.4,0.0,2.0,0.8,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.2,0.6,0.0,0.0,0.0,0.0,0.0,0.0,6.0,2.0,10.0,0.0,0.0,0.0,0.0,0.0,0.0,0.6,0.0,0.4,0.4,0.2,1.0,0.0,0.0,0.0,2.0,10.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.6,0.0,0.0,0.0,0.0,0.0,0.6,1.0,0.0,0.6,0.0,8.0,0.0,0.0,0.0,0.0,0.0,3.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,3.0,0.0,15.0,5.0,0.8,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,9.0,17.0,0.0,0.0,0.0,19.0,0.0,0.0,0.2,0.0,11.0,1.0,0.0,0.0,0.0,0.0,5.0,0.0,0.0,0.0,0.0,0.0,0.0,0.6,0.0,0.0,13.0,0.0,0.0,0.2,1.0,0.0,0.0,0.0,0.0,9.0,6.0,46.0,40.0,23.0,0.6,9.0,0.2,2.0,0.2,0.0,0.2,0.2,0.0,2.0,0.0,0.0,0.6,21.0,11.0,0.0,0.0,0.0,0.0,1.0,2.0,0.0,0.0,0.0,0.0,0.8,3.0,0.4,0.0,0.0,0.0,0.8,0.0,0.0,0.0,0.0,3.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0"

        self.createParameter("evapo_values",dm.STRING,"Evapotranspiration Data Time Series")
        self.evapo_values = "0.0,0.6,2.0,0.0,0.0,0.0,0.0,3.0,0.4,0.0,1.0,5.0,3.0,4.0,0.0,0.0,2.0,0.2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.6,2.0,0.0,0.0,0.4,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,5.0,0.0,0.6,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.4,0.0,0.0,0.0,0.0,0.4,0.0,3.0,0.0,0.0,0.0,0.0,5.0,19.0,28.0,33.0,0.0,14.5,8.0,0.2,0.6,2.0,0.2,0.0,0.0,0.0,39.0,53.0,23.0,14.0,0.4,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,7.0,3.0,0.0,14.0,9.0,0.0,0.6,0.2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,10.0,0.0,0.0,0.2,0.0,0.0,0.0,0.0,0.0,2.0,5.0,0.4,0.0,0.0,0.0,5.0,1.0,0.2,1.0,12.0,9.0,1.0,0.0,0.0,0.6,0.2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,3.0,0.0,0.0,0.0,0.4,2.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.2,0.0,0.0,0.8,6.0,0.6,0.0,0.0,0.0,0.0,0.0,5.0,3.0,0.2,2.0,0.0,0.0,0.0,0.0,0.0,0.8,0.2,12.0,0.0,0.0,2.0,3.0,0.4,0.0,2.0,0.8,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.2,0.6,0.0,0.0,0.0,0.0,0.0,0.0,6.0,2.0,10.0,0.0,0.0,0.0,0.0,0.0,0.0,0.6,0.0,0.4,0.4,0.2,1.0,0.0,0.0,0.0,2.0,10.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.6,0.0,0.0,0.0,0.0,0.0,0.6,1.0,0.0,0.6,0.0,8.0,0.0,0.0,0.0,0.0,0.0,3.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,3.0,0.0,15.0,5.0,0.8,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,9.0,17.0,0.0,0.0,0.0,19.0,0.0,0.0,0.2,0.0,11.0,1.0,0.0,0.0,0.0,0.0,5.0,0.0,0.0,0.0,0.0,0.0,0.0,0.6,0.0,0.0,13.0,0.0,0.0,0.2,1.0,0.0,0.0,0.0,0.0,9.0,6.0,46.0,40.0,23.0,0.6,9.0,0.2,2.0,0.2,0.0,0.2,0.2,0.0,2.0,0.0,0.0,0.6,21.0,11.0,0.0,0.0,0.0,0.0,1.0,2.0,0.0,0.0,0.0,0.0,0.8,3.0,0.4,0.0,0.0,0.0,0.8,0.0,0.0,0.0,0.0,3.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0"

        self.createParameter("irrigation_values",dm.STRING,"Irrigiation Data Time Series")
        self.irrigation_values = "0.0,0.6,2.0,0.0,0.0,0.0,0.0,3.0,0.4,0.0,1.0,5.0,3.0,4.0,0.0,0.0,2.0,0.2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.6,2.0,0.0,0.0,0.4,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,5.0,0.0,0.6,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.4,0.0,0.0,0.0,0.0,0.4,0.0,3.0,0.0,0.0,0.0,0.0,5.0,19.0,28.0,33.0,0.0,14.5,8.0,0.2,0.6,2.0,0.2,0.0,0.0,0.0,39.0,53.0,23.0,14.0,0.4,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,7.0,3.0,0.0,14.0,9.0,0.0,0.6,0.2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,10.0,0.0,0.0,0.2,0.0,0.0,0.0,0.0,0.0,2.0,5.0,0.4,0.0,0.0,0.0,5.0,1.0,0.2,1.0,12.0,9.0,1.0,0.0,0.0,0.6,0.2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,3.0,0.0,0.0,0.0,0.4,2.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.2,0.0,0.0,0.8,6.0,0.6,0.0,0.0,0.0,0.0,0.0,5.0,3.0,0.2,2.0,0.0,0.0,0.0,0.0,0.0,0.8,0.2,12.0,0.0,0.0,2.0,3.0,0.4,0.0,2.0,0.8,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.2,0.6,0.0,0.0,0.0,0.0,0.0,0.0,6.0,2.0,10.0,0.0,0.0,0.0,0.0,0.0,0.0,0.6,0.0,0.4,0.4,0.2,1.0,0.0,0.0,0.0,2.0,10.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.6,0.0,0.0,0.0,0.0,0.0,0.6,1.0,0.0,0.6,0.0,8.0,0.0,0.0,0.0,0.0,0.0,3.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,3.0,0.0,15.0,5.0,0.8,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,9.0,17.0,0.0,0.0,0.0,19.0,0.0,0.0,0.2,0.0,11.0,1.0,0.0,0.0,0.0,0.0,5.0,0.0,0.0,0.0,0.0,0.0,0.0,0.6,0.0,0.0,13.0,0.0,0.0,0.2,1.0,0.0,0.0,0.0,0.0,9.0,6.0,46.0,40.0,23.0,0.6,9.0,0.2,2.0,0.2,0.0,0.2,0.2,0.0,2.0,0.0,0.0,0.6,21.0,11.0,0.0,0.0,0.0,0.0,1.0,2.0,0.0,0.0,0.0,0.0,0.8,3.0,0.4,0.0,0.0,0.0,0.8,0.0,0.0,0.0,0.0,3.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0"

        self.createParameter("start_date", dm.STRING, "start date")
        self.start_date = "02.01.2000 00:00:00"

        self.createParameter("end_date", dm.STRING, "end date")
        self.end_date = "01.01.2001 00:00:00"

        self.createParameter("time_step", dm.INT, "data timestep")
        self.time_step = 86400

        self.createParameter("station_id", dm.INT, "station id")
        self.station_id = 1

        views = []

        self.stations = dm.ViewContainer("station", dm.COMPONENT, dm.READ)
        self.stations.addAttribute('station_id',dm.Attribute.INT, dm.WRITE) 

        self.timeseries = dm.ViewContainer('timeseries', dm.COMPONENT, dm.READ)
        self.timeseries.addAttribute('data', dm.Attribute.DOUBLEVECTOR, dm.WRITE)
        self.timeseries.addAttribute('type', dm.Attribute.STRING, dm.WRITE)
        self.timeseries.addAttribute('station_id', dm.Attribute.INT, dm.WRITE)
        self.timeseries.addAttribute('start', dm.Attribute.STRING, dm.WRITE)
        self.timeseries.addAttribute('end', dm.Attribute.STRING, dm.WRITE)
        self.timeseries.addAttribute('time_step', dm.Attribute.INT, dm.WRITE)


        views.append(self.stations)
        views.append( self.timeseries)

        self.registerViewContainers(views)


    def init(self):
        
        pass

    
    #Convert string to float list
    def convert_string_to_float_list(self, string):
        s_list = string.split(",")
        f_list = []
        for s in s_list:
            f_list.append(float(s))
        return f_list

    def run(self):

        # first create an element in the sation view 
        # check if it already exists to overwrite
        overwrite = False
        for s in self.stations:
            
            id = s.GetFID()
            if id == self.station_id:
                overwrite = True


        # if the overwrite is false, create a new station 
        # and populate the timeseries data
        if not overwrite:
            s = self.stations.create_feature()
            s.SetField("station_id",30)

            for i in ['rainfall intensity', 'potential pt data','irrigation']:
                t = self.timeseries.create_feature()
                t.SetField("station_id", self.station_id)
                t.SetField("type", i)
                t.SetField('start', self.start_date)
                t.SetField('end', self.end_date)
                t.SetField('time_step',self.time_step)

                if i == 'rainfall intensity':
                    dm.dm_set_double_list(t, "data", self.convert_string_to_float_list(self.rainfall_values))
                elif i == 'potential pt data':
                    dm.dm_set_double_list(t, "data", self.convert_string_to_float_list(self.evapo_values))
                elif i == 'irrigation':
                    dm.dm_set_double_list(t, "data", self.convert_string_to_float_list(self.irrigation_values))
                    

        # if overwrite is true, we dont need to create a new station,
        # but do need to update the timeseries values
        if overwrite:

            for t in self.timeseries:
                if t.GetFieldAsInteger("station_id") == self.station_id:

                    t.SetField('start', self.start_date)
                    t.SetField('end', self.end_date)
                    t.SetField('time_step',self.time_step)
                    
                    if t.GetFieldAsString('type') == 'rainfall intensity':
                        dm.dm_set_double_list(t, "data", self.convert_string_to_float_list(self.rainfall_values))
                    elif t.GetFieldAsString('type') == 'potential pt data':
                        dm.dm_set_double_list(t, "data", self.convert_string_to_float_list(self.evapo_values))
                    elif t.GetFieldAsString('type') == 'irrigation':
                        dm.dm_set_double_list(t, "data", self.convert_string_to_float_list(self.irrigation_values))

        self.stations.finalise()
        self.timeseries.finalise()
        
