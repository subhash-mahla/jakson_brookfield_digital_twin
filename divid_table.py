
import PySimpleGUI as sg

import geojson
from shapely.geometry import shape, Polygon, MultiPolygon, LineString, GeometryCollection
from shapely.ops import split
import numpy as np

def divide_polygon(polygon, num_rows, num_cols):
    bounds = polygon.bounds
    minx, miny, maxx, maxy = bounds
    row_height = (maxy - miny) / num_rows
    col_width = (maxx - minx) / num_cols

    lines = []
    for i in range(1, num_cols):
        vertical_line = LineString([(minx + i * col_width, miny), (minx + i * col_width, maxy)])
        lines.append(vertical_line)
    for j in range(1, num_rows):
        horizontal_line = LineString([(minx, miny + j * row_height), (maxx, miny + j * row_height)])
        lines.append(horizontal_line)

    result = [polygon]
    for line in lines:
        temp_result = []
        for geom in result:
            split_result = split(geom, line)
            if isinstance(split_result, Polygon):
                temp_result.append(split_result)
            elif isinstance(split_result, (MultiPolygon, GeometryCollection)):
                for g in split_result.geoms:
                    if isinstance(g, Polygon):
                        temp_result.append(g)
        result = temp_result

    return result

def divide_geojson(input_geojson, num_rows, num_cols):
    divided_features = []
    for feature in input_geojson['features']:
        geom = shape(feature['geometry'])
        if isinstance(geom, (Polygon, MultiPolygon)):
            divided_polygons = divide_polygon(geom, num_cols, num_rows)
            for polygon in divided_polygons:
                divided_features.append(geojson.Feature(geometry=polygon, properties=feature['properties']))
        else:
            divided_features.append(feature)

    return geojson.FeatureCollection(divided_features)

# Example usage:
# Load the input GeoJSON file
input_file = sg.popup_get_file(message="Select geojson",file_types=(("GeoJSON Files", "*.geojson"),))
output_file = input_file.replace(".geojson", "_output.geojson")
with open(input_file, 'r') as f:
    input_geojson = geojson.load(f)

# Divide the polygons into 4 parts each
num_cols = 5
num_rows = 1
divided_geojson = divide_geojson(input_geojson, num_cols, num_rows)

# Save the resulting divided polygons into a new GeoJSON file
with open(output_file, 'w') as f:
    geojson.dump(divided_geojson, f)
