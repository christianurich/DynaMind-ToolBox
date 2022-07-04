# -*- coding: utf-8 -*- 


import pydynamind as dm


class GenerateClimateTimeseries(dm.Module):
    display_name = "Generate Cimate Time series"
    group_name = "Performance Assessment"

    def getHelpUrl(self):
        return ""

    def __init__(self):
        dm.Module.__init__(self)
        self.setIsGDALModule(True)

        self.createParameter("values", dm.STRING, "Climate Data Time Series")
        self.values = "0.0,0.6,2.0,0.0,0.0,0.0,0.0,3.0,0.4,0.0,1.0,5.0,3.0,4.0,0.0,0.0,2.0,0.2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.6,2.0,0.0,0.0,0.4,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,5.0,0.0,0.6,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.4,0.0,0.0,0.0,0.0,0.4,0.0,3.0,0.0,0.0,0.0,0.0,5.0,19.0,28.0,33.0,0.0,14.5,8.0,0.2,0.6,2.0,0.2,0.0,0.0,0.0,39.0,53.0,23.0,14.0,0.4,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,7.0,3.0,0.0,14.0,9.0,0.0,0.6,0.2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,10.0,0.0,0.0,0.2,0.0,0.0,0.0,0.0,0.0,2.0,5.0,0.4,0.0,0.0,0.0,5.0,1.0,0.2,1.0,12.0,9.0,1.0,0.0,0.0,0.6,0.2,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,3.0,0.0,0.0,0.0,0.4,2.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.2,0.0,0.0,0.8,6.0,0.6,0.0,0.0,0.0,0.0,0.0,5.0,3.0,0.2,2.0,0.0,0.0,0.0,0.0,0.0,0.8,0.2,12.0,0.0,0.0,2.0,3.0,0.4,0.0,2.0,0.8,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.2,0.6,0.0,0.0,0.0,0.0,0.0,0.0,6.0,2.0,10.0,0.0,0.0,0.0,0.0,0.0,0.0,0.6,0.0,0.4,0.4,0.2,1.0,0.0,0.0,0.0,2.0,10.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.6,0.0,0.0,0.0,0.0,0.0,0.6,1.0,0.0,0.6,0.0,8.0,0.0,0.0,0.0,0.0,0.0,3.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,3.0,0.0,15.0,5.0,0.8,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,9.0,17.0,0.0,0.0,0.0,19.0,0.0,0.0,0.2,0.0,11.0,1.0,0.0,0.0,0.0,0.0,5.0,0.0,0.0,0.0,0.0,0.0,0.0,0.6,0.0,0.0,13.0,0.0,0.0,0.2,1.0,0.0,0.0,0.0,0.0,9.0,6.0,46.0,40.0,23.0,0.6,9.0,0.2,2.0,0.2,0.0,0.2,0.2,0.0,2.0,0.0,0.0,0.6,21.0,11.0,0.0,0.0,0.0,0.0,1.0,2.0,0.0,0.0,0.0,0.0,0.8,3.0,0.4,0.0,0.0,0.0,0.8,0.0,0.0,0.0,0.0,3.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,"

        self.createParameter("type", dm.STRING, "rainfall")
        self.type = "rainfall"

        self.createParameter("start_date", dm.STRING, "start date")
        self.start_date = "02.01.2000 00:00:00"

        self.createParameter("end_date", dm.STRING, "end date")
        self.end_date = "01.01.2001 00:00:00"

        self.createParameter("time_step", dm.INT, "data timestep")
        self.time_step = 86400

        views = []

        self.stations = dm.ViewContainer("station", dm.COMPONENT, dm.READ)


        
        self.timeseries = dm.ViewContainer('timeseries', dm.COMPONENT, dm.WRITE)
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
        
        # Read json file
        for s in self.stations:
            print(s.GetFID())
            print()
            station_id = s.GetFID()


            t = self.timeseries.create_feature()
            t.SetField("station_id", station_id)
            t.SetField("type", self.type)
            t.SetField('start', self.start_date)
            t.SetField('end', self.end_date)
            t.SetField('time_step',self.time_step)

            
            dm.dm_set_double_list(t, "data", self.convert_string_to_float_list(self.values))

        self.stations.finalise()
        self.timeseries.finalise()
        



