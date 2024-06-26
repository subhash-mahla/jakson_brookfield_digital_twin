import uuid
import geopandas as gpd

def generate_unique_id():
    return str(uuid.uuid4())

    # Read the shapefile
def assign_unique_id_to_polygons(shp_file_path):
    # Read the shapefile
    gdf = gpd.read_file(shp_file_path)
    
    # Assign a unique ID to each polygon
    gdf['eq_id'] = gdf.apply(lambda _: generate_unique_id(), axis=1)
    
    # Save the modified shapefile
    output_file_path = shp_file_path.replace('.shp', '_with_ids.shp')
    gdf.to_file(output_file_path)
    
    return output_file_path