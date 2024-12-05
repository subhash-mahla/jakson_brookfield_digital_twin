import PySimpleGUI as sg
import pandas as pd
import geopandas as gpd

def convert_geojson_to_xlsx(geojson_path, xlsx_path):
    gdf = gpd.read_file(geojson_path)
    gdf.drop(columns='geometry').to_excel(xlsx_path, index=False)

def update_geojson_with_xlsx(geojson_path, xlsx_path, output_geojson_path):
    gdf = gpd.read_file(geojson_path)
    df = pd.read_excel(xlsx_path)
    
    # Assuming `eq_id` is the matching key between GeoJSON and Excel
    key = 'eq_id'
    updated_gdf = gdf.set_index(key).combine_first(df.set_index(key)).reset_index()
    
    updated_gdf.to_file(output_geojson_path, driver='GeoJSON')

layout = [
    [sg.Text('Choose an option:')],
    [sg.Text('GeoJSON File'), sg.Input(), sg.FileBrowse(file_types=(("GeoJSON Files", "*.geojson"),))],
    [sg.Text('Excel File (for updating)'), sg.Input(), sg.FileBrowse(file_types=(("Excel Files", "*.xlsx"),))],
    [sg.Text('Output File'), sg.Input(), sg.SaveAs()],
    [sg.Button('1. Convert GeoJSON to XLSX'), sg.Button('2. Update GeoJSON with XLSX')],
    [sg.Button('Run'), sg.Button('Exit')]
]

window = sg.Window('GeoJSON and XLSX Operations', layout)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break

    if event == 'Run':
        geojson_file = values[2]
        excel_file = values[3]
        output_file = values[4]
        
        if 'Convert GeoJSON to XLSX' in values[0]:
            if geojson_file and output_file:
                convert_geojson_to_xlsx(geojson_file, output_file)
                sg.popup('Conversion Complete!', 'The data has been converted to Excel format.')
            else:
                sg.popup('Error', 'Please specify the GeoJSON and output files.')
        
        if 'Update GeoJSON with XLSX' in values[0]:
            if geojson_file and excel_file and output_file:
                update_geojson_with_xlsx(geojson_file, excel_file, output_file)
                sg.popup('Update Complete!', 'The GeoJSON file has been updated with Excel data.')
            else:
                sg.popup('Error', 'Please specify the GeoJSON, Excel, and output files.')
    if event == '1. Convert GeoJSON to XLSX':
        geojson_file = sg.popup_get_file(message="Select geojson",file_types=(("GeoJSON Files", "*.geojson"),))
        print(geojson_file)
        output_file = str(geojson_file).replace(".geojson", "_to_excel.xlsx")
        convert_geojson_to_xlsx(geojson_file, output_file)
window.close()
