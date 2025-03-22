import pandas as pd
import os
from osgeo import ogr, osr
from osgeo import gdal
from tqdm import tqdm
import json
import PySimpleGUI as sg


Shapefile_have_row = False
def Points_SortRowWise(pointsfiles, block, first_row:int, dis_bw_rows:float):
    global Shapefile_have_row
    Layout_Block = block
    for f in pointsfiles:
    # GIVE COLUMN ID
        if Shapefile_have_row : df_cols = ['lon', 'lat', 'id','row']
        else :df_cols = ['lon', 'lat', 'id']
        df = pd.DataFrame(columns=df_cols)
        file = ogr.Open(f)
        shape = file.GetLayer(0)
        print('Point File Reading :')

        #read points new method
        def read_points (shape_obj, i):
            feature = shape_obj.GetFeature(i)
            first = feature.ExportToJson()
            data = json.loads(first)
            # rack = data['properties']['rack']
            # lon = data['geometry']['coordinates'][1]
            # lat = data['geometry']['coordinates'][0]
            lon = data['geometry']['coordinates'][0]
            lat = data['geometry']['coordinates'][1]
            # itype = str(data['properties']['panel'])
            # try:eq_name = str(data['properties']['equip_name'])
            # except: eq_name = ""
            try:eq_id = str(data['properties']['equip_id'])
            except: eq_id = ""
            # plot = data['properties']['plot']
            # inv = data['properties']['inv']
            # scb = data['properties']['scb']
            # panel = data['properties']['panel']
            if Shapefile_have_row : 
                row = int(data['properties']['row'])
                rowList = [lon, lat, eq_id, row]
            else : rowList = [lon, lat, eq_id]
            return rowList
        
        new_dict = {index : read_points(shape, index) for index in tqdm(range(len(shape)))}
        df = pd.DataFrame(new_dict).transpose()
        df.columns = df_cols

        #read points old method
        # for i in tqdm(range(len(shape))):
        #     feature = shape.GetFeature(i)
        #     first = feature.ExportToJson()
        #     data = json.loads(first)
        #     rack = data['properties']['rack']
        #     # lon = data['geometry']['coordinates'][1]
        #     # lat = data['geometry']['coordinates'][0]
        #     lon = data['geometry']['coordinates'][0]
        #     lat = data['geometry']['coordinates'][1]
        #     itype = str(data['properties']['panel'])
        #     try:eq_name = str(data['properties']['equip_name'])
        #     except: eq_name = ""
        #     try:eq_id = str(data['properties']['equip_id'])
        #     except: eq_id = ""
        #     # plot = data['properties']['plot']
        #     # inv = data['properties']['inv']
        #     # scb = data['properties']['scb']
        #     # panel = data['properties']['panel']
        #     if Shapefile_have_row : 
        #         row = int(data['properties']['row'])
        #         rowList = [rack, lon, lat, itype, eq_name, eq_id, row]
        #     else : rowList = [rack, lon, lat, itype, eq_name, eq_id]
            
        #     df.loc[len(df)] = rowList

        ### Row Column Sorting ###
        # Sort by latitude
        if Shapefile_have_row : df = df.sort_values(by=['row'], ascending=True)
        else: df = df.sort_values(by=['lat'], ascending=False)
        # df = df.sort_values(by=['lat'], ascending=False)
        temprows = {}
        pre_row = 0
        rowscount = first_row
        dcount = 0
        df_cols = ['lon', 'lat', 'id']


        print('Row Counting :')
        if Shapefile_have_row: 
            for i in tqdm(range(df.shape[0])):
                rowscount = df.iloc[i, 6]
                try:
                    temprows[rowscount].loc[len(temprows[rowscount])] = [df.iloc[i, 0],
                                                    df.iloc[i, 1], df.iloc[i, 2]]
                except:
                    temprows[rowscount] = pd.DataFrame(
                        columns=df_cols)
                    temprows[rowscount].loc[0] = [df.iloc[i, 0],
                                                    df.iloc[i, 1], df.iloc[i, 2]]
                # dcount += 1
                # if i > 0 and df.iloc[i, 6] != df.iloc[i-1, 6]:
                if pre_row != rowscount:
                    print(" "+str(rowscount))
                    pre_row = rowscount
                #     dcount = 0
        else : 
            # def count_rows_RND (tempdict, i):
            #     global dcount
            #     global rowscount
            #     try:
            #         tempdict[rowscount].loc[dcount] = [df.iloc[i, 0],
            #                                         df.iloc[i, 1], df.iloc[i, 2], df.iloc[i, 3], df.iloc[i, 4], df.iloc[i, 5]]
            #     except:
            #         tempdict[rowscount] = pd.DataFrame(
            #             columns=df_cols)
            #         tempdict[rowscount].loc[dcount] = [df.iloc[i, 0],
            #                                         df.iloc[i, 1], df.iloc[i, 2], df.iloc[i, 3], df.iloc[i, 4], df.iloc[i, 5]]
            #     dcount += 1
            #     if i >= 0 and i < int(df.shape[0])-1:
            #         # 0.00003:  # vertical distance
            #         #0.00002
            #         # 0.000018
            #         #0.0000005
            #         # 0.000001
                    
            #         ver_dis = -1 * (df.iloc[i+1, 2] - df.iloc[i, 2])
            #         if ver_dis > dis_bw_rows:
            #             rowscount += 1
            #             dcount = 0

            # temprows = {}


            for i in tqdm(range(df.shape[0])):
                # if i >= 0 and i < int(df.shape[0])-1: ver_dis = -1 * (df.iloc[i+1, 2] - df.iloc[i, 2])
                try:
                    temprows[rowscount].loc[dcount] = [df.iloc[i, 0],
                                                    df.iloc[i, 1], df.iloc[i, 2]]
                except:
                    temprows[rowscount] = pd.DataFrame(
                        columns=df_cols)
                    temprows[rowscount].loc[dcount] = [df.iloc[i, 0],
                                                    df.iloc[i, 1], df.iloc[i, 2]]
                dcount += 1
                if i >= 0 and i < int(df.shape[0])-1:
                    # 0.00003:  # vertical distance
                    #0.00002
                    # 0.000018
                    #0.0000005
                    # 0.000001
                    
                    ver_dis = -1 * (df.iloc[i+1, 2] - df.iloc[i, 2])
                    if ver_dis > dis_bw_rows:
                        rowscount += 1
                        dcount = 0

        print("Rows :", rowscount)
        # print(temprows[1])

        # Sorting dictionary
        sorted_dict = sorted(temprows.keys())

        strings_count = first_row
        # rowname = f"{strings_count}U"
        str_count = 1
        resultDf = pd.DataFrame(
            columns=['lon', 'lat', 'id','row', 'col'])
            # columns=['equip_id', 'equip_name', 'rack_panel', 'block_bs', 'row', 'col', "col_id", 'key'])
        
        # current_table = None
        # table_count = 0
        key_list = list((sorted_dict))
        pervious_rack_panel = ""
        print('CSV Genrating :')
        total_rp_dupli = 0
#New method
        # def format_report_row(data, i, key_list):
        #     key = key_list[j]
        #     col_id = 0
        #     col_dicri = 0
        #     reqdDf = temprows[key]
        #     reqdDf = reqdDf.sort_values(by=['lon'], ascending=[True])
        #     # reqdDf = pd.DataFrame.sort_values()
        #     # privious_point_data = None
        #     first_md_position = None
        #     for i in range(reqdDf.shape[0]):
        #         rack_panel = f"{reqdDf.iloc[i, 0]}-{reqdDf.iloc[i, 3]}"
        #         if pervious_rack_panel != rack_panel:
        #             string = "ROW-" + str(strings_count) + \
        #                 "-COL-" + str(reqdDf.shape[0] - col_id)
        #             # panel = reqdDf.iloc[i, 3]
        #             # if (col_id+1) % 2 != 0:
        #             #     col = f"U{str(col_id+1-col_dicri)}"
        #             #     col_dicri += 1
        #             # else : col = f"L{str(col_id+1-col_dicri)}"

        #             try : upper_module = (reqdDf.iloc[i, 2] > reqdDf.iloc[i+1, 2])
        #             except : upper_module = (reqdDf.iloc[i, 2] > reqdDf.iloc[i-1, 2])
        #             if i == 0:
        #                 if upper_module: first_md_position = "U"
        #                 else : first_md_position = 'L'
        #             if upper_module:
        #                 col = f"U{str(col_id+1-col_dicri)}"
        #                 if first_md_position == 'U' :col_dicri += 1
        #             else : 
        #                 col = f"L{str(col_id+1-col_dicri)}"
        #                 if first_md_position == 'L' :col_dicri += 1

        #             resultDf.loc[len(resultDf)] = [reqdDf.iloc[i, 0], reqdDf.iloc[i, 1], reqdDf.iloc[i, 2], reqdDf.iloc[i, 3], 
        #                                            reqdDf.iloc[i, 5], reqdDf.iloc[i, 4], Layout_Block, strings_count, col, col_id+1, string, str(str_count), rack_panel, f"{Layout_Block}-{strings_count}{col}"]
        #             # resultDf.loc[len(resultDf)] = [df.iloc[i, 5], reqdDf.iloc[i, 4], rack_panel, block, strings_count, col, col_id+1, f"{block}-{strings_count}{col}"]
        #             # if int(reqdDf.iloc[i, 3]) == 32:
        #             #     strings_count += 1
        #             # else:
        #             #     strings_count += 2
        #             # print(key)
        #             str_count += 1
                    
        #             col_id += 1

        #             pervious_rack_panel = rack_panel
        #         else: 
        #             total_rp_dupli += 1
        #             # print(f"Duplicate : {rack_panel}")
        #     # if "U" in rowname: rowname = f"{strings_count}L"
        #     # else:
        #     #     strings_count += 1
        #     #     rowname = f"{strings_count}U"
        #     strings_count += 1
        #     # col_dicri = 0

        # new_dict = {index : format_report_row(shape, index, key_list=key_list) for index in tqdm(range(len(key_list)))}
        # resultDf = pd.DataFrame(new_dict).transpose()

        for j in tqdm(range(len(key_list))):
            key = key_list[j]
            col_id = 0
            col_dicri = 0
            reqdDf = temprows[key]
            reqdDf = reqdDf.sort_values(by=['lon'], ascending=[True])
            # reqdDf = pd.DataFrame.sort_values()
            # privious_point_data = None
            first_md_position = None
            for i in range(reqdDf.shape[0]):
                rack_panel = f"{reqdDf.iloc[i, 0]}-{reqdDf.iloc[i, 3]}"
                if pervious_rack_panel != rack_panel:
                    string = "ROW-" + str(strings_count) + \
                        "-COL-" + str(reqdDf.shape[0] - col_id)
                    # panel = reqdDf.iloc[i, 3]
                    # if (col_id+1) % 2 != 0:
                    #     col = f"U{str(col_id+1-col_dicri)}"
                    #     col_dicri += 1
                    # else : col = f"L{str(col_id+1-col_dicri)}"

                    try : upper_module = (reqdDf.iloc[i, 2] > reqdDf.iloc[i+1, 2])
                    except : upper_module = (reqdDf.iloc[i, 2] > reqdDf.iloc[i-1, 2])
                    if i == 0:
                        if upper_module: first_md_position = "U"
                        else : first_md_position = 'L'
                    if upper_module:
                        col = f"U{str(col_id+1-col_dicri)}"
                        if first_md_position == 'U' :col_dicri += 1
                    else : 
                        col = f"L{str(col_id+1-col_dicri)}"
                        if first_md_position == 'L' :col_dicri += 1

                    resultDf.loc[len(resultDf)] = [reqdDf.iloc[i, 0], reqdDf.iloc[i, 1], reqdDf.iloc[i, 2], reqdDf.iloc[i, 3], 
                                                   reqdDf.iloc[i, 5], reqdDf.iloc[i, 4], Layout_Block, strings_count, col, col_id+1, string, str(str_count), rack_panel, f"{Layout_Block}-{strings_count}{col}"]
                    # resultDf.loc[len(resultDf)] = [df.iloc[i, 5], reqdDf.iloc[i, 4], rack_panel, block, strings_count, col, col_id+1, f"{block}-{strings_count}{col}"]
                    # if int(reqdDf.iloc[i, 3]) == 32:
                    #     strings_count += 1
                    # else:
                    #     strings_count += 2
                    # print(key)
                    str_count += 1
                    
                    col_id += 1

                    pervious_rack_panel = rack_panel
                else: 
                    total_rp_dupli += 1
                    # print(f"Duplicate : {rack_panel}")
            # if "U" in rowname: rowname = f"{strings_count}L"
            # else:
            #     strings_count += 1
            #     rowname = f"{strings_count}U"
            strings_count += 1
            # col_dicri = 0
        # # print(resultDf.head(20))
        output_csv = f.replace('.shp', '') + "_ref_file.csv"
        resultDf.to_csv(output_csv, index=False, chunksize=None)
        print("CSV Genrated")
        print(f"Total RP Dupli : {total_rp_dupli}")
        return output_csv
        # os.system("mpg123 " + "yay_sound.mp3")

file = sg.popup_get_file('select shp file')
Points_SortRowWise(pointsfiles=file, block=0, first_row=6, dis_bw_rows=0.000018)