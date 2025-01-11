import requests

def get_car_detail (license_number):
    try:
        base_url = "https://data.gov.il/api/3/action/datastore_search"
        params = {
            'resource_id': '053cea08-09bc-40ec-8f7a-156f0677aff3', 
            'q': license_number
        }

        response = requests.get(base_url, params=params)
        response.raise_for_status()

        api_results = response.json()
        records = api_results.get('result', []).get('records', [])
        if records:
            vehicle_type = records[0]['tozeret_nm'][::-1]
            production_year = records[0]['shnat_yitzur']
            vehicle_color = records[0]['tzeva_rechev'][::-1]
            vehicle_name = records[0]['kinuy_mishari']

            return {"type": vehicle_type, "year": production_year, "color": vehicle_color, "model": vehicle_name}
        
        else:
            return None
    
    except Exception as e:
        print(f"Error: Can't fetch car's details from the API: {e}")
        return None