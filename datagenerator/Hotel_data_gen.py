## This is test data for Hotels ####
import pandas as pd
import random
import json
#from random_address import generate_random_address_in_state, State

hotel_type_list={
    "Luxury": [
        "The Ritz-Carlton",
        "St. Regis",
        "JW Marriott",
        "Ritz-Carlton Reserve",
        "The Luxury Collection",
        "W Hotels",
        "EDITION"
    ],
    "Premium": [
        "Marriott Hotels",
        "Sheraton",
        "Marriott Vacation Club",
        "Delta Hotels by Marriott",
        "Westin",
        "Le M\u00e9ridien",
        "Renaissance Hotels",
        "Gaylord Hotels"
    ],
    "Select": [
        "Courtyard by Marriott",
        "Four Points by Sheraton",
        "SpringHill Suites",
        "Fairfield Inn & Suites",
        "AC Hotels",
        "Aloft Hotels",
        "Moxy Hotels",
        "Protea Hotels",
        "City Express"
    ],
    "Longer Stays": [
        "Residence Inn",
        "TownePlace Suites",
        "Element Hotels",
        "Homes & Villas by Marriott Bonvoy",
        "Apartments by Marriott Bonvoy",
        "Marriott Executive Apartments"
    ],
    "Collections": [
        "Autograph Collection",
        "Design Hotels",
        "Tribute Portfolio",
        "MGM Collection with Marriott Bonvoy"
    ]
}
hotel_attributes={"Luxury":{'capacity':800, 'base_price': 500, 'amenities': ['Wi-Fi', 'TV', 'AC', 'SPA','RESORT','RESTRAUNTS','VEGAN RESTRAUNTS','CHILD CARE','BABY FOOD', 'SUITES']},
           "Premium":{'capacity': 600, 'base_price': 250, 'amenities': ['Wi-Fi', 'TV', 'AC', 'Kitchenette', 'Balcony','SPA','RESTRAUNTS','VEGAN RESTRAUNTS','CHILD CARE','BABY FOOD']},
           "Select":{'capacity': 250, 'base_price': 150, 'amenities': ['Wi-Fi', 'TV', 'AC']},
           'Longer Stays':{'capacity': 150, 'base_price': 200, 'amenities': ['Wi-Fi', 'TV', 'AC','Two Bedrooms','Laundry']},
           "Collections":{'capacity': 100, 'base_price': 300, 'amenities': ['Wi-Fi', 'TV', 'AC','Picaso Paintings','Laundry']}}

brand_attributes={'AC Hotels':{'pet_friendly':True, 'pet_fee': 100, 'pet_weight limit in pounds': 40 },
           'Aloft Hotels':{'pet_friendly':True, 'pet_fee': 20, 'pet_weight limit in pounds': 40 },
           'Autograph Collection':{'pet_friendly':True, 'pet_fee': 150, 'pet_weight limit in pounds': 40 },
           'Courtyard by Marriott':{'pet_friendly':True, 'pet_fee': 100, 'pet_weight limit in pounds': 40 },
           'Delta Hotels':{'pet_friendly':True, 'pet_fee': 75, 'pet_weight limit in pounds': 75 },
           'Element Hotels': {'pet_friendly': True, 'pet_fee': 50, 'pet_weight limit in pounds': 40},
           'JW Marriott': {'pet_friendly': True, 'pet_fee': 150, 'pet_weight limit in pounds': 40},
           'Residence Inn': {'pet_friendly': True, 'pet_fee': 100, 'pet_weight limit in pounds': 50},
           'The Ritz-Carlton': {'pet_friendly': True, 'pet_fee': 150, 'pet_weight limit in pounds': 30},
           'W Hotels': {'pet_friendly': True, 'pet_fee': 100, 'pet_weight limit in pounds': 50} }

def pet_friendly_data(brand_name):
    print("pet friendly data", brand_name)
  #  hoteldets = random.choice(hotel_type_list[brand_name])
    if brand_name in brand_attributes.keys():
        return brand_attributes[brand_name]
    else:
        return 'not pet friendly'

def generate_hotel_brand(hotel_type):
    brand_name=random.choice(hotel_type_list[hotel_type])
    print(hotel_type,brand_name)
    return brand_name

def generate_hotel_attribute(hotel_type):
    hotel_attribute=hotel_attributes[hotel_type]
    print(hotel_type,hotel_attribute)
    return hotel_attribute

def generate_hotel_data(num_hotels):
    data = []
    values = ["Cancel Anytime",
              "Free cancellation till 24hrs before check-in",
              "Free cancellation till 48hrs before check-in",
              "Free cancellation till 72hrs before check in"]

    for _ in range(num_hotels):
        hotel_id = f"HOTEL_{str(_).zfill(3)}"
        hotel_type = random.choice(list(hotel_type_list.keys()))
        brand_name = generate_hotel_brand(hotel_type)
        city_list = ["New York", "London", "Paris", "Tokyo", "Dubai", "Sydney", "Bangkok", "Rome"]
        city = random.choice(["New York", "London", "Paris", "Tokyo", "Dubai", "Sydney", "Bangkok", "Rome"])
        hotel_name = f"{brand_name} {city}"
        address = f"{random.randint(1, 100)} {random.choice(['Main St', 'Oxford St', 'Champs-Élysées', 'Ginza'])}"
        star_rating = random.randint(1,5)
        cancellation_policy = random.choices(values,k=1)
        hotel_attribute = generate_hotel_attribute(hotel_type)
        pet_frendly =pet_friendly_data(brand_name)
        data.append({
            'Hotel ID': hotel_id,
            'Hotel Name': hotel_name,
            'Hotel Type': hotel_type,
            'brand name': brand_name,
            'City': city,
            'Address': address,
            'Star Rating': star_rating,
            'Attributes of Hotel':hotel_attribute,
            'Cancellation_policy':cancellation_policy,
            'pet frendly':pet_frendly
           })
    print(type(data),'data')
    return data #pd.DataFrame(data)

# Generate 100 hotels
hotel_data = generate_hotel_data(100)

# Print the first 5 rows
#print(hotel_data.head())

# Save to CSV
##hotel_data.to_csv('C:\\Hackathon\\testdata\\hotel_data_updated.csv', index=False)
with open('C:\\Users\\61078782\\Documents\\Hackathon\\inputdata\\hotel_data.json','w') as f:
    json.dump(hotel_data,f,indent=4)
