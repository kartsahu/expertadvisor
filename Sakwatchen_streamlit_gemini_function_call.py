import base64
import glob
import streamlit as st
import json
import vertexai
# from numpy import error_message
from vertexai.generative_models import (GenerativeModel,
                                        SafetySetting,
                                        Content,
                                        FunctionDeclaration,
                                        GenerationConfig,
                                        GenerativeModel,
                                        Part,
                                        Tool,
                                        )
import os
import logging as log
import PyPDF2
import difflib

## Set the Gemini Model Api key
gemini_api_key = "470155914573"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.path.join(os.getcwd(),".\\access\\gemini_key.json")


print(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
print("completed the credential setup")

## Set the Streamlit Chatbot app information

st.header("Expert Advisor")
st.image("Chatbot_image.png")

## Set the Google App credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.path.join(os.getcwd(),"access\\gemini_key.json")

## Read the Customer Profiles based on which actions will be taken for existing customers

customer_data_path =os.path.join(os.getcwd(),".\\customer_dir\\customer_profiles.json")
hotel_data_path = os.path.join(os.getcwd(), ".\\data\\hotel_data_updated.json")

with open(hotel_data_path) as r_json:
     hotel_json_data=json.load(r_json)



log.basicConfig(filename=os.path.join(os.getcwd(),"newfile.log"),format='%(asctime)s %(message)s',filemode='w')
logger = log.getLogger(__name__)

# Setting the threshold of logger to DEBUG
logger.setLevel(log.INFO)

logger.info("Chatbot started")


def extract_hotel_details_location(city_name):
    hotels_in_city = [hotel for hotel in hotel_json_data if hotel['City'].lower() == city_name.lower()]
    return hotels_in_city

def extract_hotel_details_pet(pet_friendly):
    for i in hotel_json_data:
        print(i)
        break
    hotels_based_pet_preference = [hotel for hotel in hotel_json_data if hotel.get('pet friendly', {}).get('pet_friendly') == pet_friendly]
    return hotels_based_pet_preference

get_hotels_detail_based_on_location_func=FunctionDeclaration(
    name='get_hotels_detail_based_on_location',
    description='get all the hotel details based on city location',
    parameters={
        'type':'object',
        'properties':{
            'location':{
                'type':'string',
                'description':'Location'
            }
        }
    }
)

get_hotel_details_based_on_pet_preference_func=FunctionDeclaration(
    name='get_hotel_details_based_on_pet_preference',
    description='get all the hotel details based on pet preference i.e., either True or false',
    parameters={
        'type':'object',
        'properties':{
            'pet_friendly':{
                'type':'boolean',
                'description':' get pet_friendly as boolen value'
            }
        }
    }
)





hotel_detail_tool = Tool(
    function_declarations=[get_hotels_detail_based_on_location_func,
                           get_hotel_details_based_on_pet_preference_func]
)

vertexai.init(project="sakwatchen-expertadvisor", location="us-central1")

model = GenerativeModel(
    "gemini-1.5-pro-002",
    tools=[hotel_detail_tool],
)



def reading_single_file(pdf_file_path):
    file_data=[]
    with open(pdf_file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)


        num_pages = len(reader.pages)
        print(f'Total pages: {num_pages}')

    # Read each page
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            file_data.append(text)
            print(f'Page {page_num + 1}:\n{text}\n')
    return " ".join(file_data)

## This method extracts the hotel, customer and any Json data into text for gemini to be able read as text message




def load_chat_history(cust_name):
    try:
        with open(f'{cust_name}_chat_history.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
# ## This is for loading the chat session history so that we can provide contextual responses

def save_chat_history(cust_name):
    with open(f'{cust_name}_chat_history.json', 'w') as file:
        json.dump(st.session_state['messages'], file)

# ## This is for closing chat session history so tha agent can use it for next customer

def close_session(cust_name):
    save_chat_history(cust_name)
    st.session_state['messages'] = []
    st.rerun()



def find_customer_by_name(file_path, customer_name):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        customer_names=[]
        for customer_data in data:
            customer_names.append(customer_data['name'].lower())
            if customer_name.lower() in customer_names:
                return customer_data

        return False

    except FileNotFoundError:
        return "File not found."
    except json.JSONDecodeError:
        return "Error decoding JSON."




if __name__ == '__main__':

    cust_name = st.text_input('Please provide your customer Name')
    if cust_name:
        cls_cust_name = find_customer_by_name(customer_data_path,cust_name)
        if not cls_cust_name:
            use_details_fromUI = st.text_input("Customer doesn't seems to exist in database \nProvide trip purpose and other perference detials")
        else:

            use_details_fromUI="already provide"
        logger.info(f"closest customer name :{cls_cust_name} based on cust_name :{cust_name}")
        if st.sidebar.button("Close Session"):
            close_session(cust_name)
        if 'messages' not in st.session_state:
            st.session_state['messages'] = load_chat_history(cust_name)
        chat = model.start_chat()
        for message in st.session_state['messages']:
            with st.chat_message(message['role']):
                st.markdown(message['content'])
        user_query = st.chat_input("Ask a question:")
        if user_query:
            with st.chat_message("user"):
                st.markdown(user_query)
            st.session_state['messages'].append({"role": "user", "content": user_query})
            if cls_cust_name:
                ## when user details are available in db
                prompt=(f"""\n\nGenerate response for the query based on above data\n\n
                User details and preferences : {json.dumps(cls_cust_name)} 
                to create a response for query {user_query} """)
            else:
                ## When user details are not available
                prompt=(f"""\n\nGenerate response for the query based on above data\n\n
                Query: {user_query}
                for customer names : {cust_name} 
                consider the special preference as follows \n{use_details_fromUI} """ )
            response = chat.send_message(prompt)
            response = response.candidates[0].content.parts[0]
            print(response)
            api_requests_and_responses = []
            backend_details = ""

            function_calling_in_process = True
            while function_calling_in_process:
                try:
                    params={}
                    for key,value in response.function_call.args.items():
                        params[key]=value
                    print('function calling right now')
                    print(response.function_call.name)
                    print(params)

                    if response.function_call.name=='get_hotels_detail_based_on_location':
                        api_response=extract_hotel_details_location(params['location'])
                        api_requests_and_responses.append(
                            [response.function_call.name,params,api_response]
                        )
                    if response.function_call.name=='get_hotel_details_based_on_pet_preference':
                        api_response = extract_hotel_details_pet(params['pet_friendly'])
                        api_requests_and_responses.append(
                            [response.function_call.name, params, api_response]
                                                        )
                    print(api_response)
                    response = chat.send_message(
                        Part.from_function_response(
                            name=response.function_call.name,
                            response={
                                'content': api_response
                            }
                        )
                    )

                    response = response.candidates[0].content.parts[0]

                    backend_details += "- Function call: \n"
                    backend_details += (
                            " - Function name:"
                            + str(api_requests_and_responses[-1][0])
                    )
                    backend_details += (
                            "\n\n Parameters \n"
                            + str(api_requests_and_responses[-1][1])
                    )
                    backend_details += (
                            "\n\n API response \n"
                            + str(api_requests_and_responses[-1][2])
                    )


                except AttributeError:
                    function_calling_in_process = False
                    # st.error(error_message)
                    # api_response = error_message
                    # api_requests_and_responses.append(
                    #     [response.function_call.name, params, api_response]
                    # )





            full_response = response.text

            with st.chat_message("assistant"):
                st.markdown(full_response)
            st.session_state['messages'].append({"role": "assistant", "content": full_response})