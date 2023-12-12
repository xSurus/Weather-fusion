def ch_to_wgs_lng(x, y):
    lv03_95 = lv03_95_to_ch(x, y)
    i = (lv03_95['x'] - 600000) / 1e6
    r = (lv03_95['y'] - 200000) / 1e6
    o = 2.6779094 + 4.728982 * i + 0.791484 * i * r + 0.1306 * i * r ** 2 - 0.0436 * i ** 3
    return 100 * o / 36


def ch_to_wgs_lat(x, y):
    lv03_95 = lv03_95_to_ch(x, y)
    i = (lv03_95['x'] - 600000) / 1e6
    r = (lv03_95['y'] - 200000) / 1e6
    o = 16.9023892 + 3.238272 * r - 0.270978 * i ** 2 - 0.002528 * r ** 2 - 0.0447 * i ** 2 * r - 0.014 * r ** 3
    return 100 * o / 36


def ch_to_wgs(x, y):
    return [ch_to_wgs_lng(x, y), ch_to_wgs_lat(x, y)]


def lv03_95_to_ch(x, y):
    return {
        'x': x - 2000000 if x >= 2000000 else x,
        'y': y - 1000000 if y >= 1000000 else y
    }


def calculate_orientation(coords):
    # Use the shoelace formula to determine the orientation (clockwise or counter-clockwise)
    area = sum((x1 * y2 - x2 * y1) for (x1, y1), (x2, y2) in zip(coords, coords[1:]))
    return "clockwise" if area < 0 else "counter-clockwise"


def decode_shape_coordinates(encoded_shape, coordinates):
    x_index = encoded_shape['i']
    y_index = encoded_shape['j']

    decoded_coordinates = []
    char_index = 0

    while char_index < len(encoded_shape['o']):
        x = 0
        y = 0

        offset = int(encoded_shape['o'][char_index]) / 10 + 0.05

        if x_index % 2 == 0:
            x = coordinates['x_min'] + (coordinates['x_max'] - coordinates['x_min']) * (x_index / 2) / coordinates[
                'x_count']
            y = coordinates['y_min'] + (coordinates['y_max'] - coordinates['y_min']) * ((y_index - 1) / 2 + offset) / \
                coordinates['y_count']
        else:
            x = coordinates['x_min'] + (coordinates['x_max'] - coordinates['x_min']) * ((x_index - 1) / 2 + offset) / \
                coordinates['x_count']
            y = coordinates['y_min'] + (coordinates['y_max'] - coordinates['y_min']) * (y_index / 2) / coordinates[
                'y_count']

        latitude, longitude = ch_to_wgs(1e3 * x, 1e3 * y)  # You need to implement the ch_to_wgs function
        decoded_coordinates.append([latitude, longitude])

        if 2 * char_index < len(encoded_shape['d']):
            x_index += ord(encoded_shape['d'][2 * char_index]) - 77
            y_index += ord(encoded_shape['d'][2 * char_index + 1]) - 77

        char_index += 1

    # Ensure that the first and last coordinates are the same for each LinearRing
    if len(decoded_coordinates) > 1 and decoded_coordinates[0] != decoded_coordinates[-1]:
        decoded_coordinates.append(decoded_coordinates[0])

    # Ensure that the orientation is counter-clockwise
    if calculate_orientation(decoded_coordinates) == "clockwise":
        decoded_coordinates.reverse()

    # Ensure that four or more coordinates are used for each Polygon
    if len(decoded_coordinates) < 4:
        decoded_coordinates = []

    return decoded_coordinates


def decode_geojson(input_file: dict):
    t = 0
    features = []
    i = False

    if len(input_file['areas']) > 0 and any(len(shape) > 1 for shape in input_file['areas'][0]['shapes']):
        while True:
            i = -1
            r = [
                {
                    'type': "Feature",
                    'properties': {'color': "#" + area['color']},
                    'geometry': {
                        'type': "MultiPolygon",
                        'coordinates': [decode_shape_coordinates(shape, input_file['coords']) for shape in area['shapes'] if
                                        shape[0]['l'] == t]
                    }
                }
                for area in input_file['areas'] if (r := [
                    decode_shape_coordinates(shape, input_file['coords'])
                    for shape in area['shapes']
                    if shape[0]['l'] == t
                ]) and len(r) > 0
            ]

            if len(r) == 0:
                break

            features.extend(r)

            if i == -1:
                break

            t = i
    else:
        while True:
            i = -1
            r = "ffffff"
            o = []

            for area in input_file['areas']:
                for a in area['shapes']:
                    for c, a_item in enumerate(a):
                        if a_item['l'] == t:
                            t_result = decode_shape_coordinates(a_item, input_file['coords'])
                            if t_result is not None and len(t_result) > 0:
                                o.append({
                                    'type': "Feature",
                                    'properties': {'color': "#" + area['color'] if c == 0 else r},
                                    'geometry': {
                                        'type': "Polygon",
                                        'coordinates': [t_result]
                                    }
                                })
                        elif a_item['l'] > t and (i == -1 or a_item['l'] < i):
                            i = a_item['l']

            features.extend(o)

            if i == -1:
                break

            t = i

    return {
        'type': "FeatureCollection",
        'features': features
    }

if __name__ == "__main__":
    import json
    decoded = None
    with open('../example_data/meteo.json', "r") as f:
        decoded = decode_geojson(json.load(f))

    if decoded is not None:
        with open('../example_data/meteo.geojson', "w") as f:
            json.dump(decoded, f)