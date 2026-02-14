import os
import re
import json
import uuid
from openai import OpenAI
from django.conf import settings
from .models import Industrial, User, Booking, Wish

def get_local_fallback(user_message, industrials):
    """
    Smarter keyword-based matching using scoring.
    """
    msg = user_message.lower().strip()
    words = re.findall(r'\w+', msg)
    
    # 1. Stopword filtering for better matching
    stopwords = {'the', 'a', 'is', 'am', 'are', 'was', 'were', 'to', 'for', 'in', 'on', 'with', 'and', 'or', 'of', 'at', 'by', 'from', 'it', 'tell', 'me', 'about', 'how', 'what', 'where', 'who', 'i'}
    query_keywords = [w for w in words if w not in stopwords and len(w) > 1]
    
    # Fallback to full words if keywords list is empty (for short queries)
    if not query_keywords:
        query_keywords = words

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

    # 1. SCORING MATCHES
    best_score = 0
    best_answer = None

    for item in dataset:
        q_words = re.findall(r'\w+', item['q'].lower())
        q_keywords = [w for w in q_words if w not in stopwords]
        
        # Calculate score (number of matching keywords)
        score = 0
        for kw in query_keywords:
            if kw in q_words:
                score += 2 # Direct word match
            elif any(kw in qw or qw in kw for qw in q_keywords):
                score += 1 # Partial match
        
        # Exact substring match bonus
        if item['q'].lower() in msg or msg in item['q'].lower():
            score += 5

        if score > best_score:
            best_score = score
            best_answer = item['a']

    if best_score > 2: # Minimum threshold for a "good" match
        return best_answer
    
    # 2. ADDITIONAL LOGIC (Cities, etc.)
    if any(k in msg for k in ['cities', 'locations', 'where', 'city']):
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
    Main chatbot function with fallback support and dynamic context retrieval.
    """
    try:
        industrials = Industrial.objects.filter(status='active')
    except Exception as e:
        print(f"DEBUG: Database error in chatbot: {e}")
        return "I'm having trouble accessing our database right now. Please try again in a moment! 🐼"
    
    if settings.CHATBOT_FALLBACK_MODE:
        return get_local_fallback(user_message, industrials)

    # try OpenAI API
    try:
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if not api_key:
            return get_local_fallback(user_message, industrials)
            
        client = OpenAI(api_key=api_key)
        
        # Build Industrial context
        industrial_context = "Available Industrial Visits:\n"
        areas = set()
        for ind in industrials:
            areas.add(ind.location)
            industrial_context += f"- {ind.title} in {ind.location}: ₹{ind.price}, {ind.duration}\n"
        
        area_list = ", ".join(areas)
        
        # Smarter Dynamic context selection from knowledge base
        data_path = os.path.join(os.path.dirname(__file__), 'chatbot_data.json')
        qa_context = ""
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                dataset = data.get('dataset', [])
                
                # Simple relevance ranking for context
                msg_words = set(re.findall(r'\w+', user_message.lower()))
                scored_items = []
                for item in dataset:
                    q_words = set(re.findall(r'\w+', item['q'].lower()))
                    score = len(msg_words.intersection(q_words))
                    scored_items.append((score, item))
                
                # Sort by relevance and take top 15
                scored_items.sort(key=lambda x: x[0], reverse=True)
                for score, item in scored_items[:15]:
                    qa_context += f"Q: {item['q']} | A: {item['a']}\n"

        user_name = "Guest"
        if user and not user.is_anonymous:
            user_name = getattr(user, 'first_name', '') or getattr(user, 'name', '') or getattr(user, 'username', 'Friend')

        system_instruction = f"""
        You are 'Panda Bot' 🐼😊, the expert AI assistant for DUDU Industrial Visit Hub.
        Speak to: {user_name}
        
        Tone: Happy, high-energy, supportive, and empathetic. Use emojis!
        
        Knowledge Base (Fact source):
        {qa_context}
        
        Available Locations: {area_list}
        
        Service Context:
        {industrial_context}
        
        Instructions:
        - Prioritize facts from the Knowledge Base above. 
        - If the exact answer isn't in the context, use your Dudu Hub expertise to provide a helpful, relevant answer in same Panda tone.
        - Be concise but warm.
        """
        
        api_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ],
            max_tokens=300,
            temperature=0.6
        )
        
        response = api_response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"DEBUG: OpenAI API Error: {e}")
        response = get_local_fallback(user_message, industrials)
    
    # Log conversation
    try:
        Wish.objects.create(
            user=user if user and not user.is_anonymous else None,
            session_id=session_id or 'anonymous',
            query=user_message,
            response=response
        )
    except Exception: pass
    
    return response
