import os
import json
import requests
import openai
import streamlit as st
from dotenv import load_dotenv
from langchain_core.pydantic_v1 import BaseModel, Field
# from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage


# from opensearchpy import OpenSearch
# from langchain.chains import LLMChain
# from langchain.prompts import PromptTemplate
# from langchain.output_parsers import PydanticOutputParser
# from langchain_core.pydantic_v1 import BaseModel, Field
# from langchain_openai import ChatOpenAI
# from langchain_core.output_parsers import JsonOutputParser
# from langchain_core.prompts import PromptTemplate
# from typing import List, Dict, Optional



# Load environment variables from .env file
load_dotenv()

# Get the API token from environment variable
api_token = os.getenv("OPENAI_API_KEY")
opensearch_url = "http://localhost:9200/geeta_vector_index/_search"

# Initialize OpenAI with the API key
openai.api_key = api_token

# App config
st.set_page_config(page_title="Bhagavad Gita Chatbot", page_icon="📚")
st.title("Bhagavad Gita Chatbot 🕉️")

# Define the Pydantic model for the expected response
class GitaResponse(BaseModel):
    response: str = Field(description="The response based on the Bhagavad Gita context and user query")

# Define the OpenSearch query function
def search_opensearch(user_input):
    query = {
        "_source": {
            "excludes": ["vector_embedding"]
        },
        "query": {
            "bool": {
                "should": [
                    {
                        "script_score": {
                            "query": {
                                "neural": {
                                    "vector_embedding": {
                                        "query_text": user_input,
                                        "model_id": "tYXPbZABrU5_ZSuI34pb",
                                        "k": 10
                                    }
                                }
                            },
                            "script": {
                                "source": "_score * 1.5"
                            }
                        }
                    }
                ]
            }
        },
        "ext": {
            "generative_qa_parameters": {
                "llm_model": "gpt-3.5-turbo",
                "llm_question": user_input,
                "memory_id": "7JEUc5AB8DGxj7qnyRWd",
                "context_size": 10,
                "message_size": 2500,
                "timeout": 15
            }
        }
    }
    
    # Send the query to OpenSearch
    response = requests.get(opensearch_url, headers={"Content-Type": "application/json"}, data=json.dumps(query))
    response_data = response.json()
    
    # Extract the relevant context from the response
    context = " ".join(hit["_source"]["text"] for hit in response_data["hits"]["hits"])
    
    return context

# Set up the JSON output parser
parser = JsonOutputParser(pydantic_object=GitaResponse)

# Define the prompt template
template = """
You are a chatbot that provides responses to user questions based on chat history and the context from the OpenSearch database given below based on the Bhagavad Gita. 

Here is the context from the Bhagavad Gita fetched from our database:
{context}

User question:
{user_question}

{format_instructions}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["context", "user_question"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# Initialize the OpenAI model using LangChain
model = ChatOpenAI(api_key=api_token, temperature=0)

# Create the chain
chain = prompt | model | parser

# Function to get a response from the model
def get_response(user_query, context):
    response = chain.invoke({
        "context": context,
        "user_question": user_query,
    })
    
    return response

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello, I am your Bhagavad Gita chatbot. How can I assist you today?"),
    ]

# Display chat history
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

# User input
user_query = st.chat_input("Type your message here...")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    # Get context from OpenSearch
    context = search_opensearch(user_query)

    # Get response from GPT-4
    response = get_response(user_query, context)

    with st.chat_message("AI"):
        st.write(response.response)

    st.session_state.chat_history.append(AIMessage(content=response.response))
