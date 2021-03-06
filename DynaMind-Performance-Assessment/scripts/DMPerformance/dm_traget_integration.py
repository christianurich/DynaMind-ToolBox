__author__ = 'christianurich'

from pydynamind import *
import sqlite3
import sys
import os
import ogr

import numpy as np
import uuid
import datetime

class TargetInegration(Module):
    display_name = "Target"
    group_name = "Performance Assessment"

    def __init__(self):
        Module.__init__(self)
        self.setIsGDALModule(True)

        self.createParameter("from_temperature_station", DM.BOOL)
        self.from_temperature_station = False

        self.micro_climate_grid = ViewContainer("micro_climate_grid", DM.COMPONENT, DM.READ)
        self.micro_climate_grid.addAttribute("roof_fraction", DM.Attribute.DOUBLE, DM.READ)
        self.micro_climate_grid.addAttribute("road_fraction", DM.Attribute.DOUBLE, DM.READ)
        self.micro_climate_grid.addAttribute("water_fraction", DM.Attribute.DOUBLE, DM.READ)
        self.micro_climate_grid.addAttribute("concrete_fraction", DM.Attribute.DOUBLE, DM.READ)
        self.micro_climate_grid.addAttribute("tree_cover_fraction", DM.Attribute.DOUBLE, DM.READ)
        self.micro_climate_grid.addAttribute("grass_fraction", DM.Attribute.DOUBLE, DM.READ)
        self.micro_climate_grid.addAttribute("irrigated_grass_fraction", DM.Attribute.DOUBLE, DM.READ)
        self.micro_climate_grid.addAttribute("taf", DM.Attribute.DOUBLE, DM.WRITE)
        self.micro_climate_grid.addAttribute("taf_period", DM.Attribute.DOUBLEVECTOR, DM.WRITE)
        self.micro_climate_grid.addAttribute("ts", DM.Attribute.DOUBLE, DM.WRITE)
        self.micro_climate_grid.addAttribute("ucan", DM.Attribute.DOUBLE, DM.WRITE)

        self.createParameter("target_path", STRING)
        self.target_path = ""

        self.registerViewContainers([self.micro_climate_grid])

    def init(self):
        if self.from_temperature_station:

            self.temperature_station = ViewContainer("temperature_station", DM.COMPONENT, DM.READ)
            self.temperature_station.addAttribute("dance_station_id", DM.Attribute.INT, DM.READ)

            self.timeseries = ViewContainer("timeseries", DM.COMPONENT, DM.READ)
            self.timeseries.addAttribute("data", DM.Attribute.DOUBLEVECTOR, DM.READ)
            self.timeseries.addAttribute("temperature_station_id", DM.Attribute.INT, DM.READ)
            self.timeseries.addAttribute("start", DM.Attribute.STRING, DM.READ)
            self.registerViewContainers([self.micro_climate_grid, self.timeseries, self.temperature_station])


    def fixNulls(self, text):
        if (text == None):
            text = 0.0
        return round(text, 2)

    def load_temperature_data(self):
        t = [24.7	, 24.5	, 22.3	, 22.3	, 21.7	, 21.7	, 21.9	, 20.6	, 20.6	, 21.3	, 21.3	, 19.6	, 18.8	, 18.7	, 19.9	, 22.9	, 25.2	, 27.3	, 29.4	, 31	, 33	, 35	, 36.4	, 38	, 37.9	, 39.1	, 39	, 40.2	, 39.8	, 40.3	, 41.2	, 41.2	, 42.3	, 42.6	, 42.4	, 42.4	, 42.2	, 41.9	, 40.8	, 39.9	, 36.6	, 34.5	, 32.1	, 31.1	, 30.6	, 29.5	, 29.7	, 28.4	, 27.3	, 26.4	, 26.5	, 26.3	, 24.6	, 24.5	, 24.5	, 23.6	, 23.7	, 22.3	, 22.9	, 23	, 22	, 23	, 23.7	, 23.7	, 26	, 29.3	, 32.2	, 33.4	, 36.2	, 37.8	, 39.3	, 40.3	, 42.4	, 42.8	, 43.9	, 44	, 44.4	, 44.8	, 44.3	, 45.5	, 43.6	, 44.6	, 45.5	, 44.6	, 43.7	, 44.1	, 42.9	, 41.5	, 38.2	, 36.3	, 34.9	, 33.8	, 32.5	, 32.6	, 32.2	, 31.7	, 32.4	, 31.3	, 30.9	, 30.1	, 30.7	, 30.5	, 30.3	, 29.6	, 32.8	, 30.8	, 27.8	, 26.8	, 26.8	, 24.4	, 26.8	, 27.7	, 30.1	, 32.6	, 34.6	, 35.4	, 37.1	, 37.7	, 39.3	, 40.5	, 41.3	, 42.9	, 42.9	, 43	, 41.5	, 42.7	, 41.3	, 39.6	, 37	, 34.7	, 34.2	, 32.1	, 32.3	, 30.4	, 28.2	, 27	, 26.6	, 25.9	, 24.9	, 23.7	, 21.8	, 19.9	, 18.3	, 17.9]
        rh = [52	, 51	, 59	, 61	, 60	, 59	, 57	, 62	, 64	, 64	, 63	, 68	, 71	, 69	, 66	, 54	, 47	, 42	, 38	, 34	, 30	, 26	, 23	, 22	, 21	, 20	, 18	, 17	, 18	, 16	, 16	, 16	, 16	, 15	, 15	, 15	, 14	, 15	, 15	, 16	, 22	, 25	, 31	, 33	, 34	, 36	, 34	, 38	, 41	, 44	, 45	, 47	, 55	, 54	, 52	, 60	, 55	, 61	, 60	, 60	, 60	, 58	, 59	, 61	, 49	, 42	, 32	, 30	, 24	, 21	, 18	, 18	, 15	, 13	, 12	, 12	, 11	, 11	, 11	, 11	, 11	, 10	, 10	, 10	, 11	, 11	, 11	, 12	, 16	, 19	, 21	, 24	, 26	, 25	, 25	, 26	, 25	, 26	, 27	, 28	, 27	, 28	, 28	, 27	, 22	, 24	, 29	, 32	, 32	, 39	, 33	, 34	, 29	, 24	, 20	, 18	, 17	, 17	, 17	, 15	, 15	, 13	, 12	, 10	, 12	, 15	, 21	, 24	, 25	, 26	, 27	, 31	, 27	, 25	, 26	, 30	, 30	, 29	, 28	, 25	, 26	, 31	, 44	, 49]
        ws = [0	, 8	, 8	, 0	, 11	, 11	, 9	, 0	, 9	, 13	, 17	, 9	, 8	, 8	, 9	, 9	, 9	, 11	, 8	, 5	, 9	, 9	, 17	, 15	, 17	, 21	, 21	, 21	, 13	, 13	, 18	, 11	, 8	, 9	, 18	, 13	, 13	, 11	, 11	, 2	, 0	, 8	, 2	, 0	, 5	, 5	, 8	, 4	, 0	, 0	, 0	, 0	, 0	, 0	, 8	, 9	, 8	, 5	, 9	, 5	, 5	, 9	, 9	, 8	, 8	, 8	, 9	, 5	, 8	, 13	, 17	, 18	, 26	, 24	, 24	, 21	, 21	, 24	, 18	, 22	, 26	, 18	, 17	, 24	, 17	, 21	, 17	, 15	, 11	, 9	, 0	, 5	, 5	, 5	, 8	, 8	, 9	, 9	, 8	, 0	, 9	, 13	, 13	, 11	, 17	, 11	, 9	, 8	, 8	, 15	, 4	, 8	, 0	, 8	, 13	, 17	, 18	, 21	, 22	, 26	, 31	, 37	, 46	, 46	, 46	, 42	, 39	, 42	, 46	, 50	, 42	, 39	, 39	, 31	, 31	, 28	, 24	, 21	, 22	, 28	, 24	, 26	, 24	, 22]
        p = [1011.2	, 1010.9	, 1010.8	, 1010.6	, 1010.7	, 1010.6	, 1010.3	, 1010.2	, 1010.4	, 1010.6	, 1010.7	, 1011	, 1011.1	, 1011.3	, 1011.5	, 1011.8	, 1012.1	, 1012.4	, 1012.2	, 1012.4	, 1012.5	, 1012.6	, 1012.4	, 1012	, 1011.6	, 1011.1	, 1010.8	, 1010.4	, 1009.9	, 1009.5	, 1008.9	, 1008.4	, 1008	, 1007.6	, 1007.3	, 1007	, 1006.7	, 1006.5	, 1006.6	, 1006.6	, 1006.8	, 1007	, 1007.2	, 1007.5	, 1007.8	, 1007.9	, 1007.9	, 1007.9	, 1007.7	, 1007.6	, 1007.6	, 1007.3	, 1007.2	, 1007	, 1007	, 1006.8	, 1006.9	, 1007.1	, 1007.2	, 1007.4	, 1007.7	, 1008.1	, 1008.5	, 1008.6	, 1008.9	, 1009.3	, 1009.4	, 1009.1	, 1009.1	, 1008.8	, 1008.7	, 1008.4	, 1008	, 1007.6	, 1007.3	, 1006.7	, 1006.2	, 1005.8	, 1005.2	, 1004.7	, 1004.2	, 1003.9	, 1003.6	, 1003.6	, 1003.2	, 1003.2	, 1003.2	, 1003.3	, 1003.3	, 1003.4	, 1003.5	, 1003.6	, 1003.6	, 1003.5	, 1003.3	, 1003	, 1002.7	, 1002.5	, 1002.3	, 1001.9	, 1001.4	, 1001.1	, 1000.9	, 1000.9	, 1001	, 1000.8	, 1000.5	, 1000.5	, 1000.6	, 1000.8	, 1001	, 1001.2	, 1001.3	, 1001.4	, 1001.4	, 1001.2	, 1001	, 1000.9	, 1000.6	, 1000.3	, 1000	, 999.4	, 999	, 998.5	, 998.3	, 998.3	, 998.4	, 998.7	, 999.6	, 1000.6	, 1001.2	, 1001.8	, 1002.4	, 1003.4	, 1004.2	, 1004.6	, 1004.9	, 1005.3	, 1005.9	, 1006.7	, 1007.1	, 1007.5	, 1008.1	, 1008.2]
        kd = [0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 58.02	, 439.81	, 623.46	, 727.19	, 756.89	, 832.55	, 879.93	, 906.69	, 932.18	, 942.08	, 953.24	, 959.77	, 959.21	, 965.06	, 960.33	, 953.96	, 961.62	, 943.24	, 38.85	, 392.37	, 333.84	, 663.53	, 2.06	, 127.39	, 582.78	, 205.56	, 81.55	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 180.71	, 411.46	, 0.77	, 0.81	, 304.55	, 1.96	, 142.28	, 858.39	, 886.99	, 771.1	, 468.91	, 275.67	, 939.21	, 921.69	, 616.83	, 383	, 0.17	, 919.02	, 901.65	, 874.89	, 27.61	, 0	, 0.14	, 645.28	, 13.21	, 0.17	, 54.21	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0.8	, 306.92	, 605.16	, 642.92	, 777.19	, 835.82	, 878.07	, 894.85	, 280.47	, 727.82	, 0.59	, 50.37	, 0	, 0.22	, 1.09	, 0	, 0.69	, 1.27	, 0.93	, 0.52	, 0.38	, 0.21	, 0.31	, 0.32	, 14.66	, 440.46	, 74.87	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0	, 0]
        ld = [411.291	, 406.59	, 405.57	, 404.84	, 404.62	, 403.12	, 398.33	, 399.02	, 397.5	, 393.81	, 390.37	, 389.02	, 386.16	, 387.23	, 390.15	, 397.19	, 402.64	, 408.22	, 415.83	, 425.52	, 432	, 438.17	, 440.09	, 441.62	, 445.94	, 449.32	, 450.43	, 452.99	, 454.9	, 459.95	, 467.09	, 458.9	, 461.12	, 468.16	, 474.66	, 458.21	, 462.78	, 452.61	, 450.3	, 440.35	, 438.29	, 431.37	, 442.93	, 442.8	, 455.24	, 429.55	, 447.35	, 434.543	, 434.84	, 429.98	, 443.57	, 448.32	, 442.41	, 410.45	, 400.25	, 400.05	, 403.23	, 398.8	, 397.47	, 391.32	, 391.22	, 423.95	, 425.35	, 423.75	, 435.87	, 435.24	, 436.49	, 427.57	, 432.55	, 439.28	, 466.71	, 466.65	, 454.74	, 453.61	, 461.85	, 460.28	, 471.99	, 455.3	, 457.28	, 461.48	, 459.96	, 483.84	, 474.83	, 442.22	, 460.63	, 436.29	, 456.65	, 430.52	, 456.93	, 439.88	, 432.1	, 429.82	, 440.94	, 430.42	, 423.66	, 425.97	, 422.723	, 403.06	, 408.67	, 410.65	, 402.85	, 388.6	, 392.75	, 397.03	, 404.76	, 395.56	, 397.86	, 397.42	, 388.61	, 380.97	, 382.48	, 385.02	, 385.01	, 385.14	, 380.7	, 387.47	, 394.23	, 377.98	, 412.55	, 409.48	, 405.85	, 397.27	, 386.73	, 379.68	, 374.1	, 366.85	, 359.76	, 355.92	, 353.39	, 349.88	, 346.86	, 344.82	, 340.59	, 334.22	, 321.98	, 307.86	, 304.93	, 303.01	, 303.65	, 300.52	, 297.96	, 296.58	, 295.26	, 293.12]

        if not self.from_temperature_station:
            log("No temperature station defined loading default values", Warning)
            return t, rh, ws, p, kd, ld

        station_id = -1
        for s in self.temperature_station:
            # dance_station_id = s.Feature.GetFieldAsInteger("dance_station_id")
            station_id = s.GetFID()

        if station_id < 0:
            log("No temperature station defined loading default values", Warning)
            self.timeseries.finalise()
            self.temperature_station.finalise()
            return t, rh, ws, p, kd, ld

        log("Load data from station " + str(station_id), Standard)

        self.timeseries.setAttributeFilter("temperature_station_id = " + str(station_id))
        self.timeseries.reset_reading()

        for t in self.timeseries:
            # d = datetime.datetime.strptime(t.GetFieldAsString("start"), "%Y-%m-%d %H:%M:%S")

            temperatures = dm_get_double_list(t, "data")

        self.timeseries.finalise()
        self.temperature_station.finalise()

        return temperatures, rh, ws, p, kd, ld

    def write_climate_file(self, cimate_file):
        t, rh, ws, p, kd, ld = self.load_temperature_data()

        d = datetime.datetime.strptime("5/02/2009 00:00", "%d/%m/%Y %H:%M")

        with open(cimate_file, "w") as f:
            f.write("datetime,Ta,RH,WS,P,Kd,Ld\n")

            for idx, temperature in enumerate(t):
                f.write(d.strftime("%d/%m/%Y %H:%M"))
                f.write(",")
                f.write(str(temperature))
                f.write(",")
                f.write(str(rh[idx]))
                f.write(",")
                f.write(str(ws[idx]))
                f.write(",")
                f.write(str(p[idx]))
                f.write(",")
                f.write(str(kd[idx]))
                f.write(",")
                f.write(str(ld[idx]))
                f.write(str("\n"))
                d = d + datetime.timedelta(minutes=30)

    def run(self):
        sys.path.append(self.target_path + "/Toolkit2-Runs/bin/")
        import runToolkit as target
        landuse_file = "/tmp/" + str(uuid.uuid4()) + "lc.csv"
        result_file = "/tmp/" + str(uuid.uuid4()) + "output"
        cimate_file = "/tmp/" + str(uuid.uuid4()) + "climate.csv"

        self.write_input_file(landuse_file)
        self.write_climate_file(cimate_file)


        # Run target
        target.run_target(
            self.target_path + "/Sunbury1Extreme/controlfiles/Sunbury1Extreme/Sunbury1Extreme.txt", landuse_file,
            cimate_file, result_file)

        self.read_output(result_file)

        os.remove(result_file+ ".npy")
        os.remove(landuse_file )

    def read_output(self, result_file):
        img_array = np.load(result_file + ".npy")
        l1, l2, l3 = img_array.shape
        DTE_ITEM = 8
        QH_ITEM = 7
        QE_ITEM = 6
        QG_ITEM = 5
        RN_ITEM = 4
        TAF_ITEM = 3
        TS_ITEM = 2
        UCAN_ITEM = 1
        time = 29
        n = l2
        Z = np.zeros((n))
        UCAN = np.zeros((n))
        UCAN[:] = np.NAN
        TS = np.zeros((n))
        TS[:] = np.NAN
        TAF = np.zeros((n))
        TAF[:] = np.NAN
        RN = np.zeros((n))
        RN[:] = np.NAN
        QG = np.zeros((n))
        QG[:] = np.NAN
        QE = np.zeros((n))
        QE[:] = np.NAN
        QH = np.zeros((n))
        QH[:] = np.NAN
        # DTE=np.zeros((n))
        TAF[:] = np.NAN

        taf_vec = []
        for count in range(n):
            taf_vec.append(np.zeros(l1))
        for t in range(l1):
            for count in range(n):
                # if (count == n-1):
                #  count = n-2
                # print (i,j,count)
                Z[count] = img_array[time, count, 0][UCAN_ITEM]
                UCAN[count] = img_array[time, count, 0][UCAN_ITEM]
                TS[count] = img_array[time, count, 0][TS_ITEM]
                TAF[count] = img_array[time, count, 0][TAF_ITEM]
                RN[count] = img_array[time, count, 0][RN_ITEM]
                QG[count] = img_array[time, count, 0][QG_ITEM]
                QE[count] = img_array[time, count, 0][QE_ITEM]
                QH[count] = img_array[time, count, 0][QH_ITEM]

                taf_vec[count][t] = img_array[t, count, 0][TAF_ITEM]
                if TAF[count] > 50:
                    TAF[count] = np.nan

        self.micro_climate_grid.reset_reading()

        for (idx, m) in enumerate(self.micro_climate_grid):
            m.SetField("taf", taf_vec[idx].max())
            m.SetField("ts", TS[idx])
            m.SetField("ucan", UCAN[idx])
            dm_set_double_list(m, "taf_period", taf_vec[idx])
        self.micro_climate_grid.finalise()

    def write_input_file(self, landuse_file):
        text_file = open(landuse_file, "w")
        text_file.write("FID,roof,road,watr,conc,Veg,dry,irr,H,W" + '\n')
        for m in self.micro_climate_grid:

            # for high rise H/W is > 2
            # for compact high rise H/W = 0.75-2
            # compact low rise 0.75-1.5
            #
            # probably bush/scrub, so H/W = 0.25-1.0
            # and open low rise H/W 0.3-0.75

            ogc_fid = self.fixNulls(m.GetFID())
            roof_fraction = self.fixNulls(m.GetFieldAsDouble("roof_fraction"))
            road_fraction = self.fixNulls(m.GetFieldAsDouble("road_fraction"))
            water_fraction = self.fixNulls(m.GetFieldAsDouble("water_fraction"))
            concrete_fraction = self.fixNulls(m.GetFieldAsDouble("concrete_fraction"))
            tree_cover_fraction = self.fixNulls(m.GetFieldAsDouble("tree_cover_fraction"))
            grass_fraction = self.fixNulls(m.GetFieldAsDouble("grass_fraction"))
            irrigated_grass_fraction = self.fixNulls(m.GetFieldAsDouble("irrigated_grass_fraction"))

            H = '0.5'
            W = '1.0'

            if (roof_fraction > 0.3):
                H = '1'
                W = '1'
            else:
                if (grass_fraction + irrigated_grass_fraction > 0.5):
                    H = '0.3'
                    W = '1.0'

            # row_text =fixNulls(row[0]) + ',' + fixNulls(row[1]) + ',' + fixNulls(row[2])+ ',' + fixNulls(row[3])+ ',' + fixNulls(row[4])+ ',' + fixNulls(row[5])+ ',' + fixNulls(row[6])+ ',' + fixNulls(row[7]) +  ',' + H +  ',' + W + '\n'
            row_text = str(ogc_fid) + ',' + str(roof_fraction) + ',' + str(road_fraction) + ',' + str(
                water_fraction) + ',' + str(concrete_fraction) + ',' + str(tree_cover_fraction) + ',' + str(
                grass_fraction) + ',' + str(irrigated_grass_fraction) + ',' + H + ',' + W + '\n'
            text_file.write(row_text)
        text_file.close()
        self.micro_climate_grid.finalise()

