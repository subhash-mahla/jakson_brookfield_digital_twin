import geopandas as gpd
from shapely.geometry import Polygon
import pandas as pd
import itertools
import PySimpleGUI as sg
import pretty_errors
import id_genrator



# import geopandas as gpd
# from shapely.geometry import Point, Polygon
from shapely.affinity import rotate

def create_polygons_from_points(input_shapefile, dimensions, rotation_angle):
    # Read the point shapefile
    points = gpd.read_file(input_shapefile)

    # Define a function to create a polygon around each point with given dimensions and rotation
    def create_polygon_around_point(point, dimensions, rotation_angle):
        x, y = point
        width, height = dimensions
        half_width = width / 2
        half_height = height / 2
        # Create a rectangle polygon centered at the point
        # polygon = Polygon([(x - half_width, y - half_height),
        #                    (x + half_width, y - half_height),
        #                    (x + half_width, y + half_height),
        #                    (x - half_width, y + half_height)])
        
        polygon = Polygon([(x , y ),
                           (x + width, y),
                           (x + width, y - height),
                           (x , y - height)])
        # Rotate the polygon
        rotated_polygon = rotate(polygon, rotation_angle, origin='centroid')
        return rotated_polygon

    # Create polygons around each point with rotation
    polygons = [create_polygon_around_point((point.x, point.y), dimensions, rotation_angle) for point in points.geometry]

    # Create a GeoDataFrame for polygons
    polygons_gdf = gpd.GeoDataFrame(geometry=polygons, crs=points.crs)

    # Save the polygons to a new shapefile
    output_shapefile = input_shapefile.replace('.shp', '_polygons.shp')
    polygons_gdf.to_file(output_shapefile)

    return output_shapefile




def create_subdivided_polygons(input_shapefile, row_count, column_count):
    # Read the shapefile
    gdf = gpd.read_file(input_shapefile)

    new_polygons = []

    # Define a function to subdivide a polygon into smaller polygons based on row and column counts
    def subdivide_polygon(polygon, row_count, column_count):
        minx, miny, maxx, maxy = polygon.bounds
        width = (maxx - minx) / column_count
        height = (maxy - miny) / row_count
        rows = range(row_count)
        cols = range(column_count)

        for row, col in itertools.product(rows, cols):
            new_minx = minx + col * width
            new_maxx = new_minx + width
            new_miny = miny + row * height
            new_maxy = new_miny + height
            new_polygon = Polygon([(new_minx, new_miny), (new_maxx, new_miny), (new_maxx, new_maxy), (new_minx, new_maxy)])
            new_polygons.append(new_polygon)

    # Iterate over each feature
    for index, row in gdf.iterrows():
        # Get the geometry of the feature
        geometry = row['geometry']
        md_counter = 1
        # print(geometry.geom_type)
        # Check the type of geometry
        if geometry.geom_type == 'Polygon':
            # Subdivide the polygon
            subdivide_polygon(geometry, row_count, column_count)
        # elif geometry.geom_type == 'Line':
        #     # Subdivide the polygon
        #     subdivide_polygon(geometry, row_count, column_count)
        elif geometry.geom_type == 'MultiPolygon':
            # Iterate over each polygon in the MultiPolygon
            for poly in geometry:
                # Subdivide the polygon
                subdivide_polygon(poly, row_count, column_count)
        else:
            # Skip unknown geometry types
            continue
        
        # Assign attributes to each new polygon
        for i in range(len(new_polygons)):
            if isinstance(new_polygons[i], Polygon):
                new_polygons[i] = gpd.GeoDataFrame({'geometry': [new_polygons[i]]}, crs=gdf.crs)
                new_polygons[i]['md'] = md_counter
                for column in gdf.columns:
                    if column != 'geometry':
                        new_polygons[i][column] = row[column]
                md_counter += 1

    # Concatenate all new polygons into a single GeoDataFrame
    new_polygons_gdf = gpd.GeoDataFrame(pd.concat(new_polygons, ignore_index=True), crs=gdf.crs)

    # Save the new polygons to a new shapefile
    output_shapefile = input_shapefile.replace('.shp', '_subdivided.shp')
    new_polygons_gdf.to_file(output_shapefile)

    return output_shapefile



def assign_column_counts_to_polygons(shp_file_path, min_distance, start_col):
    # Read the shapefile
    gdf = gpd.read_file(shp_file_path)
    
    # Sort polygons by their centroid x-coordinate
    gdf['centroid_x'] = gdf.geometry.centroid.x
    gdf = gdf.sort_values(by='centroid_x').reset_index(drop=True)
    
    # Initialize the first column
    gdf['col'] = start_col
    current_col = start_col
    previous_x = gdf.loc[0, 'centroid_x']
    
    # Assign column numbers based on the minimum distance
    for i in range(1, len(gdf)):
        current_x = gdf.loc[i, 'centroid_x']
        if (current_x - previous_x) > min_distance:
            current_col += 1
        gdf.at[i, 'col'] = current_col
        previous_x = current_x
    
    # Drop the temporary centroid_x column
    gdf = gdf.drop(columns=['centroid_x'])
    
    # Save the modified shapefile
    output_file_path = shp_file_path.replace('.shp', '_with_counts.shp')
    gdf.to_file(output_file_path)
    print(f'Total col {current_col}')
    return output_file_path

import json
import pandas as pd

def update_geojson_with_node_id_and_tkr_master(geojson_file, excel_file, output_file):
    # Read the GeoJSON file
    with open(geojson_file, 'r') as f:
        geojson_data = json.load(f)
    
    # Read the Excel file into a DataFrame
    df = pd.read_excel(excel_file)
    
    # Create a dictionary for quick lookups
    eqid_to_data = df.set_index('eq_id').to_dict(orient='index')
    
    # Update the GeoJSON features
    for feature in geojson_data['features']:
        eq_id = feature['properties'].get('eq_id')
        if eq_id in eqid_to_data:
            feature['properties']['node_id'] = eqid_to_data[eq_id].get('node_id', '-')
            feature['properties']['tkr_master'] = eqid_to_data[eq_id].get('tkr_master', '-')
        else:
            feature['properties']['node_id'] = '-'
            feature['properties']['tkr_master'] = '-'
    
    # Write the updated GeoJSON to the output file
    with open(output_file, 'w') as f:
        json.dump(geojson_data, f, indent=2)
    print('node and master data marged in geojson')
# Example usage
# update_geojson_with_node_id('polygons.geojson', 'mapping.xlsx', 'updated_polygons.geojson')




wnd_layout = [[sg.Button('Point to Str', key='-POINT_TO_STR-', enable_events=True, size=20), sg.Button('Str to Md', key = '-STR_TO_MD-', enable_events=True, size=20)],
              [sg.Button('Assign IDs', key='-ASSIG_IDS-', enable_events=True, size=20), sg.Button('Assign col', key='-ASSIG_COLS-', enable_events=True, size=20)],
[sg.Button('Murge Node IDS', key='-NODE_IDS-', enable_events=True, size=20), sg.Button('Gen uid', key='GEN_UID', enable_events=True, size=20)]]

Main_Wnd = sg.Window("Digital Twin Mapping", layout=wnd_layout)

while True:
    event, values = Main_Wnd.read(timeout=100)
    # print(event)
    # print(values)
    if event == sg.WIN_CLOSED:
        break
    
    if event == '-POINT_TO_STR-':
        input_shapefile = sg.popup_get_file('Select point shape file')
        if input_shapefile != "" or input_shapefile != None:
            dimensions = (4, 2)  # Specify dimensions for the polygons (width, height)
            rotation_angle = 0  # Specify rotation angle in degrees
            output_shapefile = create_polygons_from_points(input_shapefile, dimensions, rotation_angle)
            print("Polygons created and saved to:", output_shapefile)

    if event == '-STR_TO_MD-':
        input_shapefile = sg.popup_get_file('Select Str poly file') 
        print(input_shapefile)
        if input_shapefile != "" or input_shapefile != None:
            row_count = 1  # Number of rows to divide each parent polygon
            column_count = 2  # Number of columns to divide each parent polygon
            output_shapefile = create_subdivided_polygons(input_shapefile, row_count, column_count)
            print("New polygons created and saved to:", output_shapefile)
    if event == '-ASSIG_IDS-':
        input_shapefile = sg.popup_get_file('Select poly file to assign ids')
        output_file_path = id_genrator.assign_unique_id_to_polygons(shp_file_path=input_shapefile)
        print(f"Modified shapefile saved to: {output_file_path}")
    if event == '-ASSIG_COLS-':
        shp_file_path = sg.popup_get_file('Select poly file to assign column')
        start_col = 1
        min_distance = 0.00001  # Adjust this value as needed
        output_file_path = assign_column_counts_to_polygons(shp_file_path, min_distance=min_distance, start_col=start_col)
        print(f"Modified shapefile saved to: {output_file_path}")

    if event == '-NODE_IDS-':
        geojson_path = sg.popup_get_file('Select geojson')
        node_xl_path = sg.popup_get_file('Select node xl')
        update_geojson_with_node_id_and_tkr_master(geojson_path, node_xl_path, geojson_path.replace('.geojson', '_with_node_ids.geojson'))
    if event == 'GEN_UID':
        gen_id_count = 2
        for i in range(gen_id_count):
            print(id_genrator.generate_unique_id())


