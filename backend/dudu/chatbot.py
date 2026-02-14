import os
import re
import json
import uuid
from openai import OpenAI
from django.conf import settings
from .models import Industrial, User, Booking, Wish, ChatbotKnowledge

def get_local_fallback(user_message, industrials):
    """
    Smarter keyword-based matching using scoring and database knowledge.
    """
    msg = user_message.lower().strip()
    words = re.findall(r'\w+', msg)
    
    # 1. Expanded Stopword filtering
    stopwords = {
        'the', 'a', 'is', 'am', 'are', 'was', 'were', 'to', 'for', 'in', 'on', 'with', 'and', 'or', 'of', 'at', 'by', 'from', 
        'it', 'tell', 'me', 'about', 'how', 'what', 'where', 'who', 'i', 'can', 'you', 'do', 'does', 'please', 'help', 'want', 'need'
    }
    query_keywords = [w for w in words if w not in stopwords and len(w) > 1]
    
    if not query_keywords:
        query_keywords = words

    # Load knowledge from database
    knowledge_base = ChatbotKnowledge.objects.all()

    best_score = 0
    best_answer = None

    for item in knowledge_base:
        q_text = item.question.lower()
        q_words = re.findall(r'\w+', q_text)
        q_keywords = [w for w in q_words if w not in stopwords]
        
        score = 0
        # Matching precision improvements
        for kw in query_keywords:
            if kw in q_words:
                score += 3 # Direct word match (Weight increased)
            elif any(kw in qw or qw in kw for qw in q_keywords):
                score += 1 # Partial/Substring match
        
        # Substring sequence match (Strong signal)
        if q_text in msg or msg in q_text:
            score += 10 # Massive bonus for phrasing overlap

        if score > best_score:
            best_score = score
            best_answer = item.answer

    # Threshold reduced to 1 to allow more matches if any keyword hits
    if best_score >= 2: 
        return best_answer
    
    # 2. DYNAMIC LOGIC (Cities, Booking, etc.)
    if any(k in msg for k in ['cities', 'locations', 'where', 'city']):
        areas = list(set(ind.location for ind in industrials))
        area_str = ", ".join(areas) if areas else "multiple cities"
        return f"We currently offer IVs in: {area_str}! And guess what? 😍 More cities are coming soon! 🚀"

    if 'how' in msg and ('book' in msg or 'enquire' in msg or 'payment' in msg):
        return "Booking is simple! 😊 Choose your city 🏙, select the industry 🏭, fill in your details ✍, and confirm. For payments, we accept UPI, Cards, and Net Banking! 💳🎉"

    # Default fallback (Friendly and helpful)
    return "Hmm 🤔 I’m not sure about that yet. But I can definitely help you with industrial visits, bookings, customization, and contact details! 😊 How can I assist you?"

def get_panda_response(user_message, user=None, session_id=None):
    """
    Main chatbot function with database context retrieval and optional GPT fallback.
    """
    try:
        industrials = Industrial.objects.filter(status='active')
    except Exception as e:
        print(f"DEBUG: Database error in chatbot: {e}")
        return "I'm having trouble accessing our database right now. Please try again in a moment! 🐼"
    
    if getattr(settings, 'CHATBOT_FALLBACK_MODE', True):
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
        
        # Pull dynamic context from database
        knowledge_base = ChatbotKnowledge.objects.all()
        msg_words = set(re.findall(r'\w+', user_message.lower()))
        scored_items = []
        for item in knowledge_base:
            q_words = set(re.findall(r'\w+', item.question.lower()))
            score = len(msg_words.intersection(q_words))
            scored_items.append((score, item))
        
        scored_items.sort(key=lambda x: x[0], reverse=True)
        qa_context = ""
        for score, item in scored_items[:15]:
            qa_context += f"Q: {item.question} | A: {item.answer}\n"

        user_name = "Guest"
        if user and not user.is_anonymous:
            user_name = getattr(user, 'name', 'Friend')

        system_instruction = f"""
        You are 'Panda Bot' 🐼😊, the expert AI assistant for DUDU Industrial Visit Hub.
        Speak to: {user_name}
        Tone: Happy, high-energy, supportive, and empathetic. Use emojis!
        
        Facts:
        {qa_context}
        
        Locations: {area_list}
        Industrials: {industrial_context}
        
        Instructions:
        - Use emojis! Be warm!
        - Prioritize the 'Facts' provided. 
        - If not sure, guide them to contact support: 📧 sachinvelu6925@gmail.com | 📞 9940764517
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
