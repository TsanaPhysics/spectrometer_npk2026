#!/usr/bin/env python3
"""
Enhance Thailand Rivers GeoJSON with all major river basins & tributaries:
- Chao Phraya Basin (Chao Phraya, Ping, Wang, Yom, Nan, Pa Sak, Tha Chin)
- Mae Klong Basin (Mae Klong, Khwae Yai, Khwae Noi)
- Bang Pakong & Eastern Basin (Bang Pakong, Nakhon Nayok, Prachin Buri, Chanthaburi River)
- Chi-Mun & Northeast Mekong Basin (Mun, Chi, Songkhram, Mekong)
- Southern River Basins (Tapi, Phum Duang, Pattani, Sai Buri, Trang, Songkhla Lake)
"""

import json

def enrich_thailand_rivers():
    with open('data/thailand_rivers.geojson', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    additional_rivers = [
        {
            "type": "Feature",
            "properties": {"name": "Nan", "name_th": "แม่น้ำน่าน", "basin": "Chao Phraya Basin"},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [100.85, 19.10], [100.78, 18.77], [100.60, 18.25],
                    [100.45, 17.80], [100.12, 17.62], [100.15, 17.15],
                    [100.26, 16.82], [100.35, 16.44], [100.25, 16.05],
                    [100.13, 15.70] # Confluence at Pak Nam Pho, Nakhon Sawan
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Wang", "name_th": "แม่น้ำวัง", "basin": "Chao Phraya Basin"},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [99.65, 19.10], [99.52, 18.55], [99.48, 18.28],
                    [99.30, 17.90], [99.20, 17.50], [99.12, 17.15] # Confluence with Ping
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Pa Sak", "name_th": "แม่น้ำป่าสัก", "basin": "Chao Phraya Basin"},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [101.35, 17.30], [101.25, 16.85], [101.18, 16.40],
                    [101.12, 15.80], [101.05, 15.25], [100.95, 14.85],
                    [100.80, 14.55], [100.58, 14.35] # Confluence with Chao Phraya at Ayutthaya
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Tha Chin", "name_th": "แม่น้ำท่าจีน", "basin": "Chao Phraya Basin"},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [100.05, 15.18], [100.08, 14.85], [100.12, 14.47],
                    [100.15, 14.15], [100.20, 13.82], [100.27, 13.53] # Gulf of Thailand
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Bang Pakong", "name_th": "แม่น้ำบางปะกง", "basin": "Eastern Basin"},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [101.38, 14.05], [101.25, 13.90], [101.18, 13.82],
                    [101.08, 13.68], [100.98, 13.48] # Gulf of Thailand
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Chanthaburi River", "name_th": "แม่น้ำจันทบุรี", "basin": "Eastern Basin"},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [102.25, 12.95], [102.18, 12.75], [102.12, 12.60], [102.05, 12.45]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Tapi", "name_th": "แม่น้ำตาปี", "basin": "Southern Basin"},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [99.70, 8.45], [99.55, 8.70], [99.35, 8.95],
                    [99.28, 9.15], [99.35, 9.20] # Bandon Bay
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Pattani", "name_th": "แม่น้ำปัตตานี", "basin": "Southern Basin"},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [101.08, 5.85], [101.20, 6.15], [101.28, 6.55],
                    [101.28, 6.88] # Gulf of Thailand
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {"name": "Songkhla Lake", "name_th": "ทะเลสาบสงขลา", "basin": "Southern Basin"},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [100.15, 7.82], [100.25, 7.60], [100.40, 7.40],
                    [100.55, 7.20], [100.58, 7.18]
                ]
            }
        }
    ]
    
    # Check existing names so we don't duplicate
    existing_names = set(f.get('properties', {}).get('name') for f in data['features'])
    for r in additional_rivers:
        if r['properties']['name'] not in existing_names:
            data['features'].append(r)
            
    with open('data/thailand_rivers.geojson', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Enriched Thailand rivers GeoJSON: total {len(data['features'])} features.")

if __name__ == '__main__':
    enrich_thailand_rivers()
