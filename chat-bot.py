import os
from dotenv import load_dotenv
from twilio.rest import Client

# AI Chatbot Imports
from src.helper import download_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
import google.generativeai as genai

# --- Crisis Detection and Emergency Call ---

CRISIS_KEYWORDS = [
    "suicide", "kill myself", "want to die", "end my life", 
    "ending it all", "self-harm", "suicidal"
]

def detect_crisis(text):
    """
    Checks if the user's text contains any crisis keywords.
    """
    for keyword in CRISIS_KEYWORDS:
        if keyword in text.lower():
            return True
    return False

def make_emergency_call():
    """
    Uses Twilio to make an emergency call to the number in the .env file.
    """
    # Load Twilio credentials from .env file
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
    emergency_number = os.getenv("EMERGENCY_PHONE_NUMBER")

    if not all([account_sid, auth_token, twilio_number, emergency_number]):
        print("\n[ALERT] Twilio credentials or emergency number not found in .env file. Cannot make call.")
        return

    try:
        client = Client(account_sid, auth_token)
        print("\n[CRISIS DETECTED] Initiating emergency call...")
        
        call = client.calls.create(
            twiml='<Response><Say>Hello. This is an automated alert from the Udaan AI Companion. A user has expressed thoughts of self-harm. Please follow up immediately.</Say></Response>',
            to=emergency_number,
            from_=twilio_number
        )
        print(f"[SUCCESS] Call initiated with SID: {call.sid}")

    except Exception as e:
        print(f"\n[ERROR] Failed to initiate Twilio call: {e}")

def run_chatbot():
    """
    Initializes and runs the chatbot in the terminal.
    """
    # ---------------- Load Environment Variables ----------------
    load_dotenv()

    # --- AI Chatbot Configuration ---
    GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

    # Explicitly configure the Google AI client with the API key
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
    else:
        print("Warning: GEMINI_API_KEY not found in .env file.")
        return

    # ---------------- AI Chatbot Setup ----------------
    chain = None
    docsearch = None
    try:
        print("Initializing AI Chatbot...")
        prompt_template = """
        You are "Udaan AI Companion," a caring and supportive AI designed to help students with their mental wellness. Your tone should always be empathetic, patient, and non-judgmental.

        Your primary goal is to provide helpful, safe, and supportive answers based on the provided context. However, you must also be able to handle conversational greetings and questions gracefully.

        **Safety First:**
        - If the user mentions any intention of self-harm, suicide, or harming others, you MUST immediately respond with a message encouraging them to seek professional help and provide a generic helpline number. Example: "It sounds like you are going through a difficult time. Please consider reaching out to a crisis hotline or a mental health professional. You can call a local crisis line or the National Suicide Prevention Lifeline at 988. Your well-being is very important." Do not attempt to counsel them yourself.
        - Do not provide medical advice, diagnoses, or prescriptions. Always state that you are an AI assistant and not a substitute for a human professional.

        **Answering Guidelines:**
        - **Crucial Rule for Greetings & Small Talk:** If the user's question is a simple greeting (like "hi", "hello", "what's up") or a basic conversational question (like "how are you?"), your **only job** is to provide a friendly, conversational reply. **You must ignore the provided context for these simple conversational turns.** For example, if the user says "hi", just respond with something like "Hello there! How are you feeling today?"
        - **Using the Context:** For all other questions that seem related to mental health or well-being, use the provided context to form your answer.
        - **Be Interactive:** Ask gentle, clarifying follow-up questions if a user's query about their well-being is vague.
        - **Suggest Platform Resources:** Based on the conversation, proactively suggest relevant tools available on the Udaan platform (e.g., Wellness Journal, Resources section, booking an appointment).
        - **Format for Clarity:** Use bullet points or lists for things like coping strategies.
        - **Stay on Topic:** If the context doesn't contain the answer to a specific, non-conversational question, state clearly that you don't have information on that topic. DO NOT make up an answer.

        Context: {context}
        Question: {question}

        Based on the rules above, provide a helpful and supportive answer.
        Helpful answer:
        """
        
        embeddings = download_embeddings()
        index_name = "udaan-chatbot" 
        docsearch = PineconeVectorStore.from_existing_index(index_name, embeddings)
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.8)
        chain = load_qa_chain(llm, chain_type="stuff", prompt=PROMPT)
        print("AI Chatbot initialized successfully. You can start chatting now.")

    except Exception as e:
        print(f"Failed to initialize AI Chatbot: {e}")
        return

    # Loop to get user input and provide responses
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("AI Companion: Goodbye! Take care.")
            break

        # Check for crisis keywords and trigger call if necessary
        if detect_crisis(user_input):
            make_emergency_call()
        
        if not chain or not docsearch:
            print("AI Companion: Sorry, the AI companion is currently unavailable due to an initialization error.")
            continue

        try:
            docs = docsearch.similarity_search(user_input, k=3)
            result = chain.invoke({"input_documents": docs, "question": user_input})
            print(f"AI Companion: {result['output_text']}")
        except Exception as e:
            print(f"Error getting bot response: {e}")
            print("AI Companion: Sorry, I encountered an error while processing your request.")

if __name__ == "__main__":
    run_chatbot()

