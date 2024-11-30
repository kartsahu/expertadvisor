import base64
import glob
import streamlit as st
import json
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting, Part
import os
import logging as log
import PyPDF2
import difflib

gemini_api_key = "470155914573"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.path.join(os.getcwd(),".\\access\\gemini_key.json")


print(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
print("compelted the credential setup")
st.header("Chat bot")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.path.join(os.getcwd(),"access\\gemini_key.json")

customer_data_path =os.path.join(os.getcwd(),".\\customer_dir\\customer_profiles.json")
log.basicConfig(filename=os.path.join(os.getcwd(),"newfile.log"),format='%(asctime)s %(message)s',filemode='w')
logger = log.getLogger(__name__)

# Setting the threshold of logger to DEBUG
logger.setLevel(log.INFO)

logger.info("Chatbot started")

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

def extract_text_from_json(json_data):
    """
    Recursively extracts all text (strings) from a nested JSON object or array.
    Returns a concatenated string of all extracted text.
    """
    texts = []

    def extract_from_item(item):
        if isinstance(item, dict):
            for keys in item.keys():
                extract_from_item(f"{keys} {item[keys]}")
        elif isinstance(item, list):
            for element in item:
                extract_from_item(element)
        elif isinstance(item, str):
            texts.append(item)

    extract_from_item(json_data)
    return " ".join(texts)



def read_and_extract_from_multiple_files(json_file_path):
    """
    Reads multiple JSON files and combines their extracted text content.
    """
    all_text = []
    json_pattern = os.listdir(json_file_path)
    logger.info(json_pattern)
    for file in json_pattern:

        file_w_path = os.path.join(json_file_path, file)
        if file_w_path.endswith('.json'):

            try:
                with open(file_w_path, 'r') as file_data:
                    json_data = json.load(file_data)
                    extracted_text = extract_text_from_json(json_data)
                    all_text.append(extracted_text)
            except Exception as e:
                print(f"Error reading {file_data}: {e}")

        elif file_w_path.endswith('.pdf'):
            try:
                all_text.append(reading_single_file(file_w_path))
            except Exception as e:
                raise Exception(e)
        else:
            raise Exception(f"Invalid file format : {file_w_path}")
    logger.info("all data type")
    logger.info(type(all_text))
    return "\n\n".join(all_text)

def multiturn_generate_content(user_input):
    #Read JSON file
    json_file_path = ".\\data"
    combined_text = read_and_extract_from_multiple_files(json_file_path)
    data_txt = extract_text_from_json(combined_text)
    vertexai.init(project="sakwatchen-expertadvisor", location="us-central1")

    model = GenerativeModel(
        "gemini-1.5-pro-002",
        system_instruction=[data_txt]
    )

    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.1,
        "top_p": 0.7,
    }

    safety_settings = [
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=SafetySetting.HarmBlockThreshold.OFF
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=SafetySetting.HarmBlockThreshold.OFF
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=SafetySetting.HarmBlockThreshold.OFF
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=SafetySetting.HarmBlockThreshold.OFF
        ),
    ]

    chat = model.start_chat()


    logger.info("\nChatbot Interaction:")

    if isinstance(user_input, list):
        user_input = " ".join(user_input)
    elif not isinstance(user_input, str):
        user_input = str(user_input)

    message = f"{data_txt}\n\n{user_input}"
    logger.info(message)

    print(f"prompt sent to model beginning:\n {message}  \n end of prompt")
    # Send message to the model
    response = chat.send_message(
        message,  # Pass the message as a string
        generation_config={
            "max_output_tokens": 1024,
            "temperature": 0.1,
            "top_p": 0.6,
        },
        safety_settings=[],
    )
    logger.info("\nChatbot Response:")
    print(response.text)
    print("-" * 50)
    return response

def load_chat_history(cust_name):
    try:
        with open(f'{cust_name}_chat_history.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
def save_chat_history(cust_name):
    with open(f'{cust_name}_chat_history.json', 'w') as file:
        json.dump(st.session_state['messages'], file)
def close_session(cust_name):
    save_chat_history(cust_name)
    st.session_state['messages'] = []
    st.experimental_rerun()



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

        for message in st.session_state['messages']:
            with st.chat_message(message['role']):
                st.markdown(message['content'])

        user_query = st.chat_input("Ask a question:")
        if user_query:

            with st.chat_message("user"):
                st.markdown(user_query)

            st.session_state['messages'].append({"role": "user", "content": user_query})

            if cls_cust_name:

                prompt=(f"""\n\nGenerate response for the query based on abobe data
                User details and preferences : {json.dumps(cls_cust_name)} 
                to create a response for query {user_query} 
following are the order of best cancellation policy in decreasing order : 
1. Cancel Anytime
2. Free cancellation till 24hrs before check-in
3. Free cancellation till 48hrs before check-in
4. Free cancellation till 72hrs before check in""")
            else:

                prompt=(f"""\n\nGenerate response for the query based on above data
                Query: {user_query}
                for customer names : {cust_name} 
                consider the special preference as follows \n{use_details_fromUI}
following are the order of best cancellation policy in decreasing order : 
1. Cancel Anytime
2. Free cancellation till 24hrs before check-in
3. Free cancellation till 48hrs before check-in
4. Free cancellation till 72hrs before check in""" )

            logger.info("closest name ",type(cls_cust_name))
            logger.info("query ",type(user_query))
            logger.info("use_details_fromUI ", type(use_details_fromUI))
            print(prompt)
            gemini_response = multiturn_generate_content(prompt)
            with st.chat_message("assistant"):
                st.markdown(gemini_response.text)
            st.session_state['messages'].append({"role": "assistant", "content": gemini_response.text})