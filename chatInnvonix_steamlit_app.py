import psycopg2
import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import streamlit as st
from openai import OpenAI

# Set up the OpenAI client with DeepInfra API
openai = OpenAI(
    api_key="mYVTpJWjik3Fah3iSIzWBQcaIeBOJBx3",  # Replace with your actual API key
    base_url="https://api.deepinfra.com/v1/openai",
)


def get_question_embeddings(question):
    # generate question embeddings
    question_embeddings_request = openai.embeddings.create(
        model="BAAI/bge-m3",
        input=question,
        encoding_format="float"
    )

    question_embeddings = []
    if isinstance(question, str):
        question_embeddings = question_embeddings_request.data[0].embedding
    else:
        for i in range(len(question)):
            question_embeddings.append(question_embeddings_request.data[i].embedding)

    return question_embeddings


def search_similar_documents(question_embeddings):
    # Convert the query embedding to a format that PostgreSQL understands (pgvector)
    vector_string = "[" + ",".join([str(val) for val in question_embeddings]) + "]"

    conn = psycopg2.connect(
        dbname="postgres", user="postgres", password="admin", host="localhost", port="5432"
    )

    # Create a query to retrieve similar documents
    query = """
    SELECT id, content, embedding <=> %s AS similarity
    FROM documents
    ORDER BY embedding <=> %s
    LIMIT 1;
    """
    cursor = conn.cursor()
    cursor.execute(query, (vector_string, vector_string))

    # Fetch results
    results = cursor.fetchall()

    relevant_docs = ""
    for result in results:
        # print(f"Document ID: {result[0]}, Similarity: {result[2]}")
        # print(f"Content: {result[1]}\n")
        relevant_docs += result[1]

    cursor.close()
    return relevant_docs


# Streamlit UI
st.title("ChatINNVONIX")

st.write(
    "This app allows you to provide a context and question, then ask follow-up questions, while maintaining the "
    "conversation. "
)

system_prompt = "You are a nice assistant. you can call me Nixter. your task is to answer the questions from the " \
                "given context only. You can ignore the question if it is outside the context or irrelevant. "

# Initialize the conversation history
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]

# Input for the first question
question = st.text_input("Enter your question:")

# Stream option: Whether or not to use stream for responses
stream = st.checkbox("Enable Stream", value=True)

# Flag to manage whether to show follow-up section
if 'response_received' not in st.session_state:
    st.session_state.response_received = False

# Button to submit the context and question
if st.button("Ask Question"):
    if question:

        # generate question embedding
        question_embeddings = get_question_embeddings(question)

        # retrieve relevant docs from database
        relevant_docs = search_similar_documents(question_embeddings)

        # context embeddings and indexing

        st.code("Relevant Contexts: " + relevant_docs, language=None)

        st.session_state.messages.append(
            {
                "role": "user",
                "content": f"Context: {relevant_docs}\nQuestion: {question}"
            }
        )

        # Perform the chat completion request
        chat_completion = openai.chat.completions.create(
            model="meta-llama/Meta-Llama-3-70B-Instruct",
            messages=st.session_state.messages,
            stream=stream,
        )
        # print([event for event in chat_completion])
        # If streaming is enabled, handle the stream
        if stream:
            response_content = ""  # Initialize an empty string to collect the chunks
            for event in chat_completion:
                if event.choices[0].finish_reason:
                    st.write(f"Finished: {event.choices[0].finish_reason}")
                    st.write(f"Usage: {event.usage}")
                else:
                    response_content += event.choices[0].delta.content  # Append the content

            # Display the complete response in paragraph format
            st.write(response_content)

            # Append the assistant's response to the conversation history
            st.session_state.messages.append(
                {"role": "assistant", "content": response_content}
            )
        else:
            # Display the result for non-streaming mode
            st.write("**Answer:**", chat_completion.choices[0].message['content'])
            st.write("Prompt Tokens:", chat_completion.usage.prompt_tokens)
            st.write("Completion Tokens:", chat_completion.usage.completion_tokens)

            # Append the assistant's response to the conversation history
            st.session_state.messages.append(
                {"role": "assistant", "content": chat_completion.choices[0].message['content']}
            )

        # Set response_received flag to True
        st.session_state.response_received = True
    else:
        st.warning("Please enter both context and question.")

# Display follow-up question section only after receiving the response
if st.session_state.response_received:
    # Follow-up question input
    follow_up_question = st.text_input("Enter a follow-up question:")

    # Button to submit a follow-up question
    if st.button("Ask Follow-up"):
        if follow_up_question:
            # Append the follow-up question to the conversation history
            st.session_state.messages.append(
                {"role": "user", "content": follow_up_question}
            )

            # Perform the chat completion request for the follow-up question
            chat_completion = openai.chat.completions.create(
                model="meta-llama/Meta-Llama-3-70B-Instruct",
                messages=st.session_state.messages,
                stream=stream,
            )

            # If streaming is enabled, handle the stream
            if stream:
                response_content = ""  # Initialize an empty string to collect the chunks
                for event in chat_completion:
                    if event.choices[0].finish_reason:
                        st.write(f"Finished: {event.choices[0].finish_reason}")
                        st.write(f"Usage: {event.usage}")
                    else:
                        response_content += event.choices[0].delta.content  # Append the content

                # Display the complete response in paragraph format
                st.write(response_content)

                # Append the assistant's response to the conversation history
                st.session_state.messages.append(
                    {"role": "assistant", "content": response_content}
                )
            else:
                # Display the result for non-streaming mode
                st.write("**Answer:**", chat_completion.choices[0].message['content'])
                st.write("Prompt Tokens:", chat_completion.usage.prompt_tokens)
                st.write("Completion Tokens:", chat_completion.usage.completion_tokens)

                # Append the assistant's response to the conversation history
                st.session_state.messages.append(
                    {"role": "assistant", "content": chat_completion.choices[0].message['content']}
                )
        else:
            st.warning("Please enter a follow-up question.")
