import random
import json
import os
from datetime import datetime
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from openai import OpenAI as OpenAIClient
import requests

# Question bank for dream analysis
QUESTION_BANK = [
    # Emotion-based questions
    "How did you feel during the dream?",
    "Can you describe the emotions you experienced?",
    
    # Sensory and visual questions
    "What was the most vivid image in your dream?",
    "Can you describe the colors or lighting in the dream?",
    
    # Symbolic and contextual questions
    "Were there any recurring symbols or unusual elements?", 
    "Did anything in the dream seem out of the ordinary?",
    
    # Personal connection questions
    "Does this dream remind you of anything in your current life?",
    "Are there any connections between the dream and your recent experiences?",
    
    # Spatial and movement questions
    "Where did the dream take place?",
    "Were you moving in the dream, or were you stationary?",
    
    # Character and interaction questions
    "Were there other people or beings in your dream?",
    "How did you interact with the characters or environment?",
    
    # Deeper exploration questions
    "What do you think this dream might be trying to tell you?",
    "If this dream were a message, what might it be saying?"
]

def generate_dream_image(prompt):
    """
    Generate an image using DALL-E 3 based on the dream conversation.
    
    Args:
        prompt (str): The image generation prompt
    """
    try:
        client = OpenAIClient()
        
        # Generate the image
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )

        # Get the image URL from the response
        image_url = response.data[0].url

        # Download the image
        image_response = requests.get(image_url)
        
        # Ensure the downloads directory exists
        os.makedirs("dream_images", exist_ok=True)

        # Save the image with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f"dream_images/dream_{timestamp}.png"
        
        with open(image_path, "wb") as f:
            f.write(image_response.content)

        print(f"\n✨ Dream image saved: {image_path}")
        return image_path

    except Exception as e:
        print(f"An error occurred generating the image: {e}")
        return None

def initialize_chain(instructions, memory=None):
    """
    Initialize the langchain for dream analysis.
    
    Args:
        instructions guidance for the dream analyst
        memory (ConversationBufferWindowMemory, optional): Conversation memory
    
    Returns:
        LLMChain: Initialized language model chain
    """
    if memory is None:
        memory = ConversationBufferWindowMemory()
        memory.ai_prefix = "Dream Analyst"

    template = f"""
    You are a professional dream analyst. Your goal is to help the dreamer understand their dream through careful, empathetic questioning.
    
    Guidelines:
    {instructions}
    
    Current Conversation History:
    {{{memory.memory_key}}}
    
    Human: {{{{"human_input"}}}}
    Dream Analyst:"""

    prompt = PromptTemplate(
        input_variables=["history", "human_input"], 
        template=template
    )

    chain = LLMChain(
        llm=OpenAI(temperature=0.7),
        prompt=prompt,
        verbose=True,
        memory=memory,
    )
    return chain

def generate_next_question(asked_questions):
    """
    Generate a unique question that hasn't been asked before.
    
    Args:
        asked_questions (set): Set of previously asked questions
    
    Returns:
        str: A unique question from the question bank
    """
    # Find available questions
    available_questions = [q for q in QUESTION_BANK if q not in asked_questions]
    
    # Reset if all questions have been asked
    if not available_questions:
        asked_questions.clear()
        available_questions = QUESTION_BANK
    
    # Select a random question
    question = random.choice(available_questions)
    asked_questions.add(question)
    
    return question

def save_dream_log(conversation_log):
    """
    Save dream analysis conversation to a JSON file.
    
    Args:
        conversation_log (list): Log of questions and answers
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists('dream_logs'):
        os.makedirs('dream_logs')
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'dream_logs/dream_log_{timestamp}.json'
    
    # Save conversation log
    with open(filename, 'w') as f:
        json.dump(conversation_log, f, indent=4)
    
    print(f"\n✨ Dream log saved: {filename}")

def generate_dream_image_prompt(meta_chain, chat_history):
    """
    Generate a creative image generation prompt based on the dream conversation.
    
    Args:
        meta_chain (LLMChain): Meta-analysis chain
        chat_history (str): Conversation history
    
    Returns:
        str: Detailed image generation prompt
    """
    meta_template = """
    Analyze the following dream conversation and extract key visual and symbolic elements:

    Conversation History:
    {chat_history}

    Based on this conversation, create a very concise and short, creative prompt for an image generation tool:
    1. Identify the core visual symbols
    2. Capture the emotional atmosphere
    3. Suggest an artistic style that reflects the dream's essence
    4. Include metaphorical representations

    Concise and short Image Generation Prompt:"""

    prompt = PromptTemplate(
        input_variables=["chat_history"],
        template=meta_template
    )

    meta_chain = LLMChain(
        llm=OpenAI(temperature=0.8),
        prompt=prompt,
        verbose=True
    )

    try:
        prompt_output = meta_chain.predict(chat_history=chat_history)
        return prompt_output
    except Exception as e:
        print(f"Error image prompt: {e}")
        return "A surreal, dreamlike landscape representing subconscious imagery and emotional depth"

def initialize_meta_chain():
    """
    Initialize the meta-analysis chain for deeper dream insights.
    
    Returns:
        LLMChain: Meta-analysis chain
    """
    meta_template = """
    You are a dream analysis supervisor. Review the conversation between the Dream Analyst and the dreamer.
    Your job is to provide deeper insights and potential interpretations.

    Conversation History:
    {chat_history}

    Provide:
    1. Key psychological themes
    2. Potential symbolic meanings
    3. Connections to personal life
    4. Suggested areas for further reflection

    Insights and Interpretation:"""

    meta_prompt = PromptTemplate(
        input_variables=["chat_history"], 
        template=meta_template
    )

    meta_chain = LLMChain(
        llm=OpenAI(temperature=0.7),
        prompt=meta_prompt,
        verbose=True,
    )
    return meta_chain

def main(max_questions=7):
    """
    Main dream analysis session.
    
    Args:
        max_questions (int, optional): Maximum number of questions. Defaults to 7.
    """
    initial_instructions = """
    Dream Analysis Guidelines:
    1. Ask open-ended, empathetic questions
    2. Explore emotional and symbolic aspects of the dream
    3. Help the dreamer uncover potential meanings
    4. Maintain a supportive, non-judgmental approach
    5. Guide the dreamer towards self-understanding
    """
    
    # Initialize chains
    chain = initialize_chain(initial_instructions)
    meta_chain = initialize_meta_chain()
    
    # Conversation tracking
    asked_questions = set()
    conversation_log = []
    
    print("🌙 Dream Analysis Exploration 🌙")
    print("I'll help you explore your dream through thoughtful questions.")
    
    # Ask the user to describe their dream
    print("To begin, please describe your dream in as much detail as you can:")
    dream_description = input("You: ").strip()
    
    # Log the dream description
    conversation_log.append({
        "question": "Please describe your dream:",
        "human_input": dream_description,
        "ai_response": None,
        "timestamp": datetime.now().isoformat()
    })
    
    # Analyze the dream description
    response = chain.predict(human_input=dream_description)
    print(f"Dream Analyst: {response}")
    
    # Log the initial analysis
    conversation_log.append({
        "question": None,
        "human_input": None,
        "ai_response": response,
        "timestamp": datetime.now().isoformat()
    })
    
    print("Now, I'll ask some questions to explore your dream further.")
    print("Answer as detailed as you can, or type 'done' to finish.")
    
    for _ in range(max_questions):
        # Generate next unique question
        question = generate_next_question(asked_questions)
        print(f"\nDream Analyst: {question}")
        
        # Get user response
        human_input = input("You: ").strip()
        
        if human_input.lower() in ['quit', 'exit', 'done']:
            break
        
        # Get AI response and analyze
        response = chain.predict(human_input=human_input)
        print(f"Dream Analyst: {response}")
        
        # Log conversation
        conversation_log.append({
            "question": question,
            "human_input": human_input,
            "ai_response": response,
            "timestamp": datetime.now().isoformat()
        })
    
    # Final analysis and insights
    if conversation_log:
        save_dream_log(conversation_log)
        
        # Get chat history for meta-analysis
        chat_history = "\n".join([
            f"Q: {entry['question']}\nA: {entry['human_input']}\nAnalysis: {entry['ai_response']}" 
            for entry in conversation_log
        ])
        
        # Generate meta-insights
        print("\n--- Dream Insights ---")
        meta_insights = meta_chain.predict(chat_history=chat_history)
        print(meta_insights)
        
        # Generate image prompt
        print("\nWould you like an image representation of your dream? (yes/no)")
        generate_prompt = input("You: ").lower()
        
        if generate_prompt == 'yes':
            image_prompt = generate_dream_image_prompt(meta_chain, chat_history)
            print("\n--- Dream Image Generation Prompt ---")
            print(image_prompt)
            
            # Generate and save the dream image
            image_path = generate_dream_image(image_prompt)
            if image_path:
                print(f"Image saved at: {image_path}")

if __name__ == "__main__":
    print("Dream Analysis and Image Generation Agent")
    main()
