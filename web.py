import streamlit as st
import requests
import json

# Set up Streamlit
st.title("Bhagavad Gita Chatbot")
st.write("Ask a question to get motivational responses from the Bhagavad Gita:")

# User input
user_input = st.text_input("Enter your question:")

# If the user has entered a question
if user_input:
    # Construct the query with the user's input
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
                                        "k": 5
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
                "context_size": 5,
                "message_size": 3000,
                "timeout": 15
            }
        }
    }

    # OpenSearch endpoint
    opensearch_url = "http://localhost:9200/geeta_vector_index/_search"

    # Send the query to OpenSearch
    response = requests.get(opensearch_url, headers={"Content-Type": "application/json"}, data=json.dumps(query))
    
    if response.status_code == 200:
        # Extract the answer from the response
        result = response.json()
        answer = result.get("ext", {}).get("retrieval_augmented_generation", {}).get("answer", "No answer found.")
        st.write("Response from the Bhagavad Gita:")
        st.write(answer)
        st.json(result)
    else:
        st.write("Error: Unable to fetch response from OpenSearch.")
        st.write(f"Status code: {response.status_code}")
        st.write(response.text)
