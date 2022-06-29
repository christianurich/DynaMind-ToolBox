# -*- coding: utf-8 -*- 


import pydynamind as dm


class AssignStation(dm.Module):
    display_name = "Assign a station to a lot"
    group_name = "Performance Assessment"

    def getHelpUrl(self):
        return ""

    def __init__(self):
        dm.Module.__init__(self)
        self.setIsGDALModule(True)

        self.createParameter('guid', dm.STRING, 'The zone identification number')
        self.guid = ""

        self.createParameter('Station_id', dm.INT, 'The station being assigned')
        self.Station_id = 1

        views = []

        self.lot = dm.ViewContainer("wb_lot", dm.COMPONENT, dm.WRITE)
        self.lot.addAttribute("guid",dm.Attribute.STRING, dm.READ)
        self.lot.addAttribute("station_id",dm.Attribute.INT, dm.WRITE)

        views.append(self.lot)
        self.registerViewContainers(views)

    def init(self):
    
        pass

    def run(self):

        for zone in self.lot:

            guid = zone.GetFieldAsString('guid')

            if guid == self.guid:
                zone.SetField("station_id",self.Station_id)

        self.lot.finalise()







