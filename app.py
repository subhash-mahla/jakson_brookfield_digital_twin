from flask import Flask, request, jsonify
import geojson

app = Flask(__name__)

# Load GeoJSON data into memory
with open('https://subhash-mahla.github.io/jakson_brookfield_digital_twin/brookfield_final_layout_P1_V6.geojson') as f:
    data = geojson.load(f)

# Extract unique sorted values
def get_unique_sorted_values(data, key):
    values = {feature['properties'].get(key) for feature in data['features'] if feature['properties'].get(key)}
    return sorted(values)

unique_B = get_unique_sorted_values(data, 'B')

@app.route('/get_unique_values', methods=['GET'])
def get_unique_values():
    b_value = request.args.get('B', '')
    inv_value = request.args.get('INV', '')
    scb_value = request.args.get('SCB', '')

    if b_value:
        filtered_features = [feature for feature in data['features'] if feature['properties'].get('B') == b_value]
        unique_INV = get_unique_sorted_values({'features': filtered_features}, 'INV')
        return jsonify({'INV': unique_INV})

    if b_value and inv_value:
        filtered_features = [feature for feature in data['features'] if feature['properties'].get('B') == b_value and feature['properties'].get('INV') == inv_value]
        unique_SCB = get_unique_sorted_values({'features': filtered_features}, 'SCB')
        return jsonify({'SCB': unique_SCB})

    if b_value and inv_value and scb_value:
        filtered_features = [feature for feature in data['features'] if feature['properties'].get('B') == b_value and feature['properties'].get('INV') == inv_value and feature['properties'].get('SCB') == scb_value]
        unique_STR = get_unique_sorted_values({'features': filtered_features}, 'STR')
        return jsonify({'STR': unique_STR})

    return jsonify({'B': unique_B})

@app.route('/filter_geojson', methods=['GET'])
def filter_geojson():
    b_value = request.args.get('B', '')
    inv_value = request.args.get('INV', '')
    scb_value = request.args.get('SCB', '')
    str_value = request.args.get('STR', '')

    filtered_features = [feature for feature in data['features']]
    
    if b_value:
        filtered_features = [feature for feature in filtered_features if feature['properties'].get('B') == b_value]
    if inv_value:
        filtered_features = [feature for feature in filtered_features if feature['properties'].get('INV') == inv_value]
    if scb_value:
        filtered_features = [feature for feature in filtered_features if feature['properties'].get('SCB') == scb_value]
    if str_value:
        filtered_features = [feature for feature in filtered_features if feature['properties'].get('STR') == str_value]

    filtered_geojson = geojson.FeatureCollection(filtered_features)
    return jsonify(filtered_geojson)

if __name__ == '__main__':
    app.run(debug=True)
