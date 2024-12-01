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
log.basicConfig(filename=os.path.join(os.getcwd(),"newfile.log"),format='%(asctime)s %(message)s',filemode='w')
logger = log.getLogger(__name__)

# Setting the threshold of logger to DEBUG
logger.setLevel(log.INFO)

logger.info("Chatbot started")

## This method was created to read cancellations policy documents in PDF

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


## This method is essential as it combines all the data from Hotel data, customer data, Loyalty data into one big string for gemini to tokenize
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


## This is Main function that is extracting data , generating the prompt and send the response from Gemini model to Streamlit code

def multiturn_generate_content(user_input):
    #Read JSON file
    json_file_path = ".\\data"
    contents = []
    #contents.append(os.read(file_w_path))
    combined_text = read_and_extract_from_multiple_files(json_file_path)


    #with open(combined_text, 'r') as file:
    #data = json.load(file)

        # Extract complaint text from JSON
    data_txt = extract_text_from_json(combined_text)
    # text1_1 = data.get('complaint_text', '')
    # textsi_1 = complaint_data.get('system_instruction',
    #    """You are a chatbot assistant in customer service. When a customer email or chat is given to you, you will extract the main issues from it. You must flag any references to illegal activity, violence, or discrimination. Write up to 3 main issues per paragraph. After, suggest to the customer service representative how this could be handled in the moment and give examples. Then, suggest changes to protocols and systems that can be made to prevent future similar complaints. Include a greeting and sign-off. Your tone should be friendly and upbeat.""")
    vertexai.init(project="sakwatchen-expertadvisor", location="us-central1")

    model = GenerativeModel(
        "gemini-1.5-pro-002",
        system_instruction=[data_txt]
    )

    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.1,
        "top_p": 0.6,
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

    # Display extracted JSON content and allow user input
    # print("\nExtracted Text from JSON:")
    # for idx, text in enumerate(data_txt, 1):
    #   print(f"{idx}. {text}")

    logger.info("\nChatbot Interaction:")
    # while True:
    # user_input = input("Enter your message (type 'exit' to quit): ")
    # if user_input.lower() == 'exit':
    # print("Goodbye!")
    # break

    # Validate and format the input if needed
    if isinstance(user_input, list):
        user_input = " ".join(user_input)
    elif not isinstance(user_input, str):
        user_input = str(user_input)

    # Combine user input with extracted text if needed
    message = f"{data_txt}\n\n{user_input}"
    logger.info(message)

    print(f"prompt sent to model beginning:\n {message}  \n end of prompt")
    # Send message to the model
    response = chat.send_message(
        message,  # Pass the message as a string
        generation_config=generation_config,
        safety_settings=[],
    )
    logger.info("\nChatbot Response:")
    print(response.text)
    print("-" * 50)
    return response

# ## This is for loading the chat session history so that we can provide contextual responses
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


# ## Find the customer based on the customer name that is provided

def find_customer_by_name(file_path, customer_name):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        customer_names=[]
        for customer_data in data:
            customer_names.append(customer_data['name'].lower())
            if customer_name.lower() in customer_names:
                return customer_data
        # st.text(customer_names)
        # customer_names = [customer['name'] for customer in data]
        # closest_match = difflib.get_close_matches(customer_name, customer_names, n=1, cutoff=0.8)

        # if closest_match:
        #     for customer in data:
        #         if customer['name'] == closest_match[0]:
        #             st.text(customer)
        #             return customer

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
    #user_query = st.text_input('input your request')
        if user_query:
            # if user_query.lower() == 'exit':
            #     print("Goodbye!")
    # Display user message
            with st.chat_message("user"):
                st.markdown(user_query)
    # Add user message to chat history
            st.session_state['messages'].append({"role": "user", "content": user_query})
        # if user_query:
        #     # Use the document search or Gemini API to generate a response
        #     # First, get relevant text from FAISS (optional but preferred for RAG)
        #     # response_text = docsearch.similarity_search(user_query, k=1)[0].page_content
        #     # Now query the Gemini API with the retrieved text or the user's query
        #     # full_query = f"{response_text}\n\nQuestion: {user_query}\nAnswer:"
        #     # gemini_response = query_gemini_api(full_query, gemini_api_key)
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

            logger.info("closest name ",type(cls_cust_name))
            logger.info("query ",type(user_query))
            logger.info("use_details_fromUI ", type(use_details_fromUI))
            # prompt = ("Use preference from the customer i.e., "+ json.dumps(cls_cust_name) +
            #           " to create a response based on the available data " + user_query+
            #           " if customer details are not available then use the following details"+
            #           use_details_fromUI)
            print(prompt)
            gemini_response = multiturn_generate_content(prompt)
            with st.chat_message("assistant"):
                st.markdown(gemini_response.text)
            st.session_state['messages'].append({"role": "assistant", "content": gemini_response.text})