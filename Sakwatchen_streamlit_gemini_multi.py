import base64
import glob
import streamlit as st
import json
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting, Part
import os
import logging as log
# from google.colab import files
gemini_api_key = "470155914573"

st.header("Chat bot")

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=C:\Users\61087069\sakwatchen-expertadvisor-912e382bba88.json

# Create and configure logger
log.basicConfig(filename="C:\\Users\\61087069\\OneDrive - LTIMindtree\\Desktop\\hackathon\\pythonProject1\\newfile.log",
                    format='%(asctime)s %(message)s',filemode='w')

# Creating an object

logger = log.getLogger()
# Setting the threshold of logger to DEBUG
logger.setLevel(log.DEBUG)
logger.info("Chatbot started")

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
        try:
            with open(file_w_path, 'r') as file_data:
                json_data = json.load(file_data)
                extracted_text = extract_text_from_json(json_data)
                all_text.append(extracted_text)
        except Exception as e:
            print(f"Error reading {file_data}: {e}")
    return "\n\n".join(all_text)

def multiturn_generate_content(user_input):
    #Read JSON file
    json_file_path = "C:\\Users\\61087069\\OneDrive - LTIMindtree\\Desktop\\hackathon\\pythonProject1\\JSON"
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
        "gemini-1.5-flash-002",
        system_instruction=[data_txt]
    )

    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 1,
        "top_p": 0.95,
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
    # Send message to the model
    response = chat.send_message(
        message,  # Pass the message as a string
        generation_config={
            "max_output_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.95,
        },
        safety_settings=[],
    )
    logger.info("\nChatbot Response:")
    print(response.text)
    print("-" * 50)
    return response
# Example usage
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
if __name__ == '__main__':

    cust_name = st.text_input('Please provide your customer Name')
    if cust_name:
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

            prompt = "Use preference from the customer i.e., "+ cust_name +" to create a response based on the available data " + user_query
            gemini_response = multiturn_generate_content(prompt)
            with st.chat_message("assistant"):
                st.markdown(gemini_response.text)
            st.session_state['messages'].append({"role": "assistant", "content": gemini_response.text})




