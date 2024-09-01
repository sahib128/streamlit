from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

# Function to load and return the model based on the model_name
def load_model(model_name: str):
    return Ollama(model=model_name)  # Instantiate the Ollama model with the chosen model_name

# Function to handle the prompt and get a response from the model
def handle_prompt(query_text: str, context_text: str, model):
    # Create prompt for the model
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    
    # Get the response from the model
    response_text = model.invoke(prompt)
    
    return response_text

def query_rag(query_text: str, context_text: str, model_name: str):
    # Load the model
    model = load_model(model_name)
    
    # Handle the prompt with the loaded model
    response = handle_prompt(query_text, context_text, model)
    
    return response

def query_general_model(query_text: str, model_name: str):
    # General model context is empty
    context_text = ""
    
    # Load the model
    model = load_model(model_name)
    
    # Handle the prompt with the loaded model
    response = handle_prompt(query_text, context_text, model)
    
    return response