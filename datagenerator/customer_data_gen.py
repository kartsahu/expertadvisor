from faker import Faker
import random
import json


def generate_customer_profile():
    fake = Faker()
    loyalty_program_membership =fake.boolean()
    customer = {
        "name": fake.name(),
        "age": random.randint(18, 80),
        "gender": fake.random_element(["Male", "Female", "Other"]),
        "address": fake.address(),
        "phone_number": fake.phone_number(),
        "email": fake.email(),
        "preferred_room_type": fake.random_element(["Single", "Double", "Suite"]),
        "preferred_room_view": fake.random_element(["City", "Mountain", "Ocean"]),
        "preferred_room_floor": fake.random_element(["Low", "Mid", "High"]),
        "average_length_of_stay": random.randint(1, 14),
        "booking_frequency": random.randint(1, 12),
        "booking_channels": fake.random_element(["Online", "Phone", "In-Person"]),
        "average_spending_per_stay": round(random.uniform(100, 1000), 2),
        "frequent_purchases": fake.random_element(["Mini-bar", "Room Service", "Spa", "All"]),
        "loyalty_program_membership": loyalty_program_membership,
        "Loyalty_membership_status":fake.random_element(["Gold", "Silver", "Platinum","Titanium","Ambassador"]) if loyalty_program_membership else 'NA',
        "points_balance": random.randint(0, 10000) if loyalty_program_membership else 0,
        "Total No of reservations": random.randint(1, 50),
        "peak_travel_season": fake.random_element(["Summer", "Winter", "Spring", "Fall"]),
        "destination_preferences": fake.random_element(
            ["Domestic", "International", "Sea Side", "Mountains", "Warm", "Cold"]),
        "special_requests": fake.random_element(["Early Check-in", "Late Check-out", "Allergy-Friendly Room", "None"])
    }

    return customer


# Generate a list of 1000 customer profiles
customer_profiles =[]
for _ in range(100):
    customer_profile = generate_customer_profile()
    customer_profiles.append(customer_profile)



# # Print the first 5 profiles
# for profile in customer_profiles[:5]:
#     print(profile)

# Save to JSON
with open('C:\\Users\\61078782\\Documents\\Hackathon\\inputdata\\customer_profiles_updated.json','w') as f:
    json.dump(customer_profiles,f,indent=4)
#json.dumps(customer_profiles,'C:\\Hackathon\\testdata\\customer_profiles_updated.json')
