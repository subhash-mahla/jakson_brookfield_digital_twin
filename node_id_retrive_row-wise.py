import PySimpleGUI as sg
import json
import pyperclip
import pandas as pd
import math


def fetch_node_in_robo(in_json_data):
    # print(f'in features : {len(in_json_data)}')
    def get_prop_value(features, row, col, prop_name, phase = 1):
        # phase_features = [f for f in features if (str(f['properties']['phase']) == str(phase))]
        # print(f'p features : {len(phase_features)}')
        # col_features = [f for f in phase_features if (str(f['properties']['col']) == str(col))]
        # print(f'c features : {len(col_features)}')
        # row_features = [f for f in col_features if (str(f['properties']['row']) == str(row))]
        # print(f'r features : {len(row_features)}')
        matching_feature = [f for f in features if f['properties']['row'] == str(row) and f['properties']['col'] == str(col) and (str(f['properties']['phase']) == str(phase))]
        # print(matching_feature)
        if not matching_feature:
            return None
        else: 
            return matching_feature[0]['properties'][prop_name]
        
        # # Sort by column
        # matching_features.sort(key=lambda f: int(f['properties']['col']))
        
        # if col_index < len(matching_features) and col_index >= 0:
        #     return matching_features[col_index]['properties'][prop_name]
        
        # return None

    robo_layout = [[sg.Button('Load Robo Xl', key='LOAD_ROBO')],
                   [sg.Button('Start Process', key='START')]]
    robo_window = sg.Window('GeoJSON Node ID Finder', robo_layout)

    while True:
        event, values = robo_window.read()

        if event == sg.WIN_CLOSED:
            break

        if event == 'LOAD_ROBO':
            filepath = sg.popup_get_file('Select Robo XLSX File', file_types=(("XLSX Files", "*.xlsx"),), no_window=True)
            if filepath:
                robo_data = pd.read_excel(filepath)
                features = in_json_data.get('features', [])
                final_robo_data = pd.DataFrame(columns=robo_data.columns.to_list()+["total_table",'error_table','node_data'])
                # print(final_robo_data.columns)
                # print(f'in features : {len(features)}')
                for r in robo_data.iterrows():
                    if not math.isnan(r[1]['col']):
                        col = int(r[1]['col'])
                        start_row = r[1]['start_row']
                        end_row = r[1]['end_row']
                        node_data = ''
                        error_data = ''
                        table_count = 0
                        for row_index in range(int(start_row), int(end_row+1), 1):
                            m = get_prop_value(features, row=row_index, col=col, prop_name='tkr_master')
                            node = get_prop_value(features, row=row_index, col=col, prop_name='node_id')
                            if not m == None or not node == None: 
                                node_data += f'M{m}-{node},'
                                table_count += 1
                            else: 
                                print(f"error - R{row_index}-C{col}-ROBO{r[1]['robo_row']}")
                                error_data += f"error - R{row_index}-C{col}-ROBO{r[1]['robo_row']}, "
                        new_row = [r[1]['robo_row'], r[1]['B'], r[1]['robo_type'], col, start_row, end_row, table_count, error_data, node_data]
                    else: 
                        new_row = [r[1]['robo_row'], r[1]['B'], r[1]['robo_type'], '', '', '', '', '', '']
                    final_robo_data.loc[len(final_robo_data)] = new_row
                final_robo_data.to_excel(filepath.replace('.xlsx', '_out.xlsx'), index=False)
                print("out file genrated")
        if event == 'START':
            pass





# Load the GeoJSON data from file
def load_geojson(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

# Retrieve the node_id for the feature with the given row and column index
def get_node_id(features, row, col_index, prop_name):
    matching_features = [f for f in features if f['properties']['row'] == str(row)]
    if not matching_features:
        return None
    
    # Sort by column
    matching_features.sort(key=lambda f: int(f['properties']['col']))
    
    if col_index < len(matching_features) and col_index >= 0:
        return matching_features[col_index]['properties'][prop_name]
    
    return None

# Main GUI function
def main():
    sg.theme('LightBlue')

    layout = [
        [sg.Button('Load GeoJSON', key='-LOAD-'), sg.Button('Node-Robo data Marge', key= 'ROBO', disabled=True)],
        [sg.Text('Enter Row:'), sg.InputText(key='-ROW-', s=10), sg.Text('Enter Phase:'), sg.InputText(key='-PHASE-', s=10), sg.Button('Submit Row', key='-SUBMIT-')],
        [sg.Text('Total Tkr:', size=(10, 1)), sg.Text('', key='-T_COL-'), sg.Text('Current Tkr:', size=(10, 1)), sg.Text('', key='-C_COL-'), sg.Text('Remaining Tkr:', size=(10, 1)), sg.Text('', key='-R_COL-')],
        [sg.Text('Node ID:', size=(10, 1)), sg.Text('', key='-NODE_ID-')],
        [sg.Button('Previous', key='-PREV-', disabled=True, expand_x=True, size=(10, 3)), sg.Button('Next', key='-NEXT-', disabled=True, expand_x=True, size=(10, 3))],
        [sg.Output(size=(60, 10))]
    ]

    window = sg.Window('GeoJSON Node ID Finder', layout)

    features = []
    col_index = 0

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        if event == '-LOAD-':
            # filepath = sg.popup_get_file('Select GeoJSON File', file_types=(("GeoJSON Files", "*.geojson"),), no_window=True)
            filepath = 'C:\\Users\\solar\\Documents\\GitHub\\jakson_brookfield_digital_twin\\brookfield_final_layout_P1_V13.geojson'
            if filepath:
                geojson_data = load_geojson(filepath)
                features = geojson_data.get('features', [])
                col_index = 0
                window['-NEXT-'].update(disabled=True)
                window['ROBO'].update(disabled=False)
                # sg.popup('GeoJSON file loaded successfully!')

        if event == '-SUBMIT-':
            if not features:
                sg.popup('Please load a GeoJSON file first.')
                continue

            row = values['-ROW-']
            phase = values['-PHASE-']
            if not row or not phase:
                sg.popup('Please enter a row number or phase.')
                continue

            # Check if row is available in the data
            matching_features = [f for f in features if (str(f['properties']['row']) == str(row)) and (str(f['properties']['phase']) == str(phase))]
            if not matching_features:
                sg.popup(f'Row {row} not found in the data.')
            else:
                total_tkr = round(len(matching_features)/2)
                window['-T_COL-'].update(total_tkr)
                col_index = 0
                node_id = get_node_id(matching_features, row, col_index, prop_name='node_id')
                master = get_node_id(matching_features, row, col_index, prop_name='tkr_master')
                col = get_node_id(matching_features, row, col_index, prop_name='col')
                show_text = f"{round((col_index+2)/2)}. R{row}-C{col}-M{master}-{node_id}"
                if node_id:
                    window['-NODE_ID-'].update(show_text)
                    window['-C_COL-'].update(round((col_index+2)/2))
                    window['-R_COL-'].update(total_tkr - round((col_index+2)/2))
                    window['-NEXT-'].update(disabled=False)
                    print(show_text)
                    pyperclip.copy(node_id)
                else:
                    sg.popup('No features found with the given row.')

        if event == '-NEXT-':
            row = values['-ROW-']
            if not row:
                sg.popup('Please enter a row number.')
                continue

            col_index += 2  # Increment by 2 for each "Next" click
            node_id = get_node_id(matching_features, row, col_index, prop_name='node_id')
            if node_id:
                master = get_node_id(matching_features, row, col_index, prop_name='tkr_master')
                col = get_node_id(matching_features, row, col_index, prop_name='col')
                show_text = f"{round((col_index+2)/2)}. R{row}-C{col}-M{master}-{node_id}"
                window['-NODE_ID-'].update(show_text)
                window['-C_COL-'].update(round((col_index+2)/2))
                window['-R_COL-'].update(total_tkr - round((col_index+2)/2))
                print(show_text)
                pyperclip.copy(node_id)
                window['-PREV-'].update(disabled=False)
            else:
                sg.popup('Reached the end of columns for the given row.')
                window['-NEXT-'].update(disabled=True)
                col_index -= 2
        if event == '-PREV-':
            row = values['-ROW-']
            if not row:
                sg.popup('Please enter a row number.')
                continue

            col_index -= 2  # Decrement by 2 for each "Next" click
            node_id = get_node_id(matching_features, row, col_index, prop_name='node_id')
            if node_id:
                master = get_node_id(matching_features, row, col_index, prop_name='tkr_master')
                col = get_node_id(matching_features, row, col_index, prop_name='col')
                show_text = f"{round((col_index+2)/2)}. R{row}-C{col}-M{master}-{node_id}"
                window['-NODE_ID-'].update(show_text)
                window['-C_COL-'].update(round((col_index+2)/2))
                window['-R_COL-'].update(total_tkr - round((col_index+2)/2))
                print(show_text)
                pyperclip.copy(node_id)
                window['-NEXT-'].update(disabled=False)
            else:
                col_index += 2
                sg.popup('Reached the start of columns for the given row.')
                window['-PREV-'].update(disabled=True)
        if event == 'ROBO':
            fetch_node_in_robo(geojson_data)
    window.close()

if __name__ == "__main__":
    main()