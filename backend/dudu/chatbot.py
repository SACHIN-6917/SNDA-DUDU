import os
import re
import json
import uuid
from openai import OpenAI
from django.conf import settings
from .models import Industrial, User, Booking, Wish

def get_local_fallback(user_message, industrials):
    """
    Enhanced keyword-based response generator driven by chatbot_data.json.
    """
    msg = user_message.lower().strip()
    
    # Try to load dataset
    data_path = os.path.join(os.path.dirname(__file__), 'chatbot_data.json')
    dataset = []
    if os.path.exists(data_path):
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                dataset = data.get('dataset', [])
        except Exception as e:
            print(f"DEBUG: Error loading chatbot_data.json: {e}")

    # 1. DATASET MATCHING (High Priority)
    for item in dataset:
        q = item['q'].lower()
        # Simple keyword matching or partial phrase match
        if q in msg or msg in q:
            return item['a']
    
    # 2. ADDITIONAL LOGIC (Cities, etc.)
    if 'cities' in msg or 'locations' in msg or 'where' in msg:
        areas = list(set(ind.location for ind in industrials))
        area_str = ", ".join(areas) if areas else "multiple cities"
        return f"We currently offer IVs in: {area_str}! And guess what? 😍 More cities are coming soon! 🚀"

    # 3. DYNAMIC REASONING FALLBACK
    if 'how' in msg and 'book' in msg:
        return "Booking is simple and smooth! 😊 Just choose your city 🏙, select the industry 🏭, fill in your details ✍, and confirm your booking. That’s it! 🎉"

    # Default fallback
    return "Hmm 🤔 I’m not sure about that yet. But I can definitely help you with industrial visits, bookings, customization, and contact details! 😊 How can I assist you?"

def get_panda_response(user_message, user=None, session_id=None):
    """
    Main chatbot function with fallback support and conversation logging.
    Returns response string.
    """
    # 1. Fetch Context from Database
    try:
        industrials = Industrial.objects.filter(status='active')
    except Exception as e:
        print(f"DEBUG: Database error in chatbot: {e}")
        return "I'm having trouble accessing our database right now. Please try again in a moment! 🐼"
    
    # 2. Check if fallback mode is enabled
    if settings.CHATBOT_FALLBACK_MODE:
        print("DEBUG: Chatbot running in FALLBACK MODE (local responses)")
        response = get_local_fallback(user_message, industrials)
    else:
        # 3. Try OpenAI API
        try:
            api_key = getattr(settings, "OPENAI_API_KEY", None)
            
            if not api_key:
                print("DEBUG: No OpenAI API key, falling back to local")
                response = get_local_fallback(user_message, industrials)
            else:
                client = OpenAI(api_key=api_key)
                
                # Build context
                industrial_context = "Available Industrial Visits:\n"
                areas = set()
                for ind in industrials:
                    areas.add(ind.location)
                    industrial_context += f"- {ind.title} in {ind.location}: ₹{ind.price}, {ind.duration}\n"
                
                area_list = ", ".join(areas)
                
                # Load additional Q&A context for AI
                data_path = os.path.join(os.path.dirname(__file__), 'chatbot_data.json')
                qa_context = ""
                if os.path.exists(data_path):
                    with open(data_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for item in data.get('dataset', [])[:20]: # Include top 20 for context
                            qa_context += f"Q: {item['q']} | A: {item['a']}\n"

                # Personalization
                user_name = "Guest"
                if user and not user.is_anonymous:
                    user_name = getattr(user, 'first_name', '') or getattr(user, 'name', '') or getattr(user, 'username', 'Friend')

                system_instruction = f"""
                You are 'Panda Bot' 🐼😊, the expert AI assistant for DUDU Industrial Visit Hub.
                You are speaking to: {user_name}
                
                Tone: Happy, excited, supportive, and empathetic. Use emojis!
                
                Knowledge Base (Use this for facts):
                {qa_context}
                
                Available Locations: {area_list}
                
                Service Context:
                {industrial_context}
                
                Instructions:
                - Be warm and friendly.
                - If asked about Dudu: explain it's a platform for safe and easy IV booking.
                - If someone is confused: guide them step-by-step with empathy.
                - Always prioritize the knowledge base answers provided above.
                """
                
                api_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=250,
                    temperature=0.5  # Lower temperature for more accuracy
                )
                
                response = api_response.choices[0].message.content.strip()
                
        except Exception as e:
            print(f"DEBUG: OpenAI API Error: {e}")
            # Fallback to local logic on ANY error
            response = get_local_fallback(user_message, industrials)
            


    
    # 4. Log conversation
    try:
        log_entry = Wish.objects.create(
            user=user if user and not user.is_anonymous else None,
            session_id=session_id or 'anonymous',
            query=user_message,
            response=response
        )
        print(f"DEBUG: Logged chatbot conversation (ID: {log_entry.id})")
    except Exception as e:
        print(f"DEBUG: Failed to log chatbot conversation: {e}")
    
    return response
