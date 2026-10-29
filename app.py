from functools import lru_cache

from mtaa import tanzania
from flask import Flask, jsonify, render_template, request


app = Flask(__name__)


@app.get('/')
def index():
    return render_template('index.html', tanzania=tanzania, list=list)


@app.get('/<region>')
def districts(region):
    region = tanzania.get(region)
    _districts = list(region.districts) if region else []
    return jsonify(_districts)


@app.get('/<region>/<district>')
def wards(region, district):
    district = tanzania.get(region).districts.get(district)
    wards = []
    if district:
        wards = list(district.wards)
        wards.remove('ward_post_code')
    return jsonify(wards)


@app.get('/<region>/<district>/<ward>')
def streets(region, district, ward):
    ward = tanzania.get(region).districts.get(district).wards.get(ward)
    streets = list(ward.streets) if ward else []
    return jsonify(streets)


@app.get('/<region>/<district>/<ward>/<street>')
def neighborhood(region, district, ward, street):
    neighborhoods = tanzania.get(region).districts.get(
        district).wards.get(ward).streets.get(street)
    return jsonify((neighborhoods))


@lru_cache(maxsize=1)
def location_search_index():
    locations = []

    def add_location(name, level, region, district='', ward='', street=''):
        locations.append({
            'name': name,
            'level': level,
            'region': region,
            'district': district,
            'ward': ward,
            'street': street,
        })

    for region in tanzania:
        add_location(region, 'Region', region)
        region_data = tanzania.get(region)
        for district in region_data.districts:
            add_location(district, 'District', region, district)
            district_data = region_data.districts.get(district)
            for ward in district_data.wards:
                if ward == 'ward_post_code':
                    continue
                add_location(ward, 'Ward', region, district, ward)
                ward_data = district_data.wards.get(ward)
                for street in ward_data.streets:
                    add_location(street, 'Street', region, district, ward, street)
                    for place in ward_data.streets.get(street):
                        add_location(place, 'Place', region, district, ward, street)

    return locations


@app.get('/api/search')
def search_locations():
    query = request.args.get('q', '').strip().casefold()
    if len(query) < 2:
        return jsonify([])

    matches = [
        location for location in location_search_index()
        if query in location['name'].casefold()
    ]
    matches.sort(key=lambda location: (
        not location['name'].casefold().startswith(query),
        len(location['name']),
        location['name'].casefold(),
    ))
    return jsonify(matches[:8])


if __name__ == '__main__':
    app.run(debug=True)
