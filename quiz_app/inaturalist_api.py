import requests
import random
from datetime import datetime, timedelta

def get_inaturalist_images(species, max_results=10, max_retries=3):
    url = f"https://api.inaturalist.org/v1/observations"
    params = {
        "taxon_name": species,
        "quality_grade": "research",
        "order": "random",
        "per_page": 200,
        "photos": "true",
        "license": "cc-by,cc-by-sa,cc0"
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            images = []
            if data['total_results'] > 0:
                results = data['results']
                random.shuffle(results)

                for result in results:
                    if len(images) >= max_results:
                        break

                    for photo in result['observation_photos']:
                        image_url = photo['photo']['url'].replace('square', 'medium')
                        observation_url = f"https://www.inaturalist.org/observations/{result['id']}"
                        license_code = result.get('license_code') or photo['photo'].get('license_code', 'unknown')
                        attribution = result.get('attribution') or photo['photo'].get('attribution', 'unknown')

                        images.append({
                            "url": image_url,
                            "species": species,
                            "observed_on": result['observed_on'],
                            "observation_url": observation_url,
                            "license_code": license_code,
                            "attribution": attribution,
                            "inaturalist_id": result['id']  # Aggiungi questa riga
                        })

                        if len(images) >= max_results:
                            break

            return images

        except requests.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Failed to get images for {species} after {max_retries} attempts: {e}")
                return []

    return []