import os
import re
from openai import OpenAI
from django.conf import settings
from .models import Industrial, User, Booking, ChatbotLog

def get_local_fallback(user_message, industrials):
    """
    Enhanced keyword-based response generator when AI API fails or is disabled.
    """
    msg = user_message.lower()
    
    # Context gathering
    areas = list(set(ind.location for ind in industrials))
    titles = [ind.title for ind in industrials]
    
    # 1. Greeting
    if any(word in msg for word in ['hello', 'hi', 'hey', 'greetings']):
        return f"Hello! 🐼 I'm Panda Bot, your DUDU Industrial Visit assistant! We offer amazing industrial visits across {', '.join(areas)}. How can I help you today?"
    
    # 2. Check for specific areas
    for area in areas:
        if area.lower() in msg:
            local_inds = [ind for ind in industrials if ind.location == area]
            response = f"Great choice! 🐼 We have {len(local_inds)} industrial visits in {area}:\n"
            for ind in local_inds[:3]:  # Show top 3
                response += f"• {ind.title} (₹{ind.price}, {ind.duration})\n"
            response += "\nVisit our Industrial's page for full details! 🚌"
            return response
    
    # 3. List all packages
    if any(word in msg for word in ['list', 'show', 'packages', 'available', 'where', 'all']):
        return f"We operate in {len(areas)} locations: {', '.join(areas)} 🏢\nWe have {len(titles)} amazing industrial visit packages! Check out the Industrial's page to explore them all! 🐼"
    
    # 4. Pricing inquiries
    if any(word in msg for word in ['price', 'cost', 'cheap', 'expensive', 'budget']):
        prices = [ind.price for ind in industrials]
        min_price = min(prices) if prices else 0
        return f"Our industrial visit packages start from just ₹{min_price}! 💰 Each package includes transportation, accommodation, meals, and guided tours. Check the Industrial's page for specific pricing."
    
    # 5. Booking
    if any(word in msg for word in ['book', 'reserve', 'register', 'enroll']):
        return "Ready to book? 🎟️ Simply:\n1. Browse our Industrial's page\n2. Select your preferred visit\n3. Click 'Book Now'\n4. Complete payment\n\nNeed help? Contact us at +919940764517! 📞"
    
    # 6. Duration/timing
    if any(word in msg for word in ['duration', 'days', 'long', 'time']):
        return "Our industrial visits range from 1-day trips to multi-day experiences! 🕐 Each package lists the exact duration. Most include factory tours, interactive sessions, and fun activities!"
    
    # 7. Facilities
    if any(word in msg for word in ['food', 'meal', 'accommodation', 'hotel', 'transport']):
        return "Every DUDU Industrial Visit includes:\n✅ Safe transportation (Bus/Train)\n✅ Quality accommodation\n✅ Hygienic meals\n✅ Professional guides\n✅ Fun activities\n\nYour comfort and safety are our priority! 🐼"
    
    # 8. Thank you
    if any(word in msg for word in ['thank', 'thanks', 'appreciate']):
        return "You're welcome! 🐼 Happy to help! If you have more questions, just ask. Ready to explore? Check out our Industrial's page! 🚌"
    
    # Default friendly response
    return f"I'm Panda Bot 🐼, here to help with industrial visits! We serve {', '.join(areas[:3])}{'...' if len(areas) > 3 else ''}. Ask me about:\n• Available locations\n• Pricing & packages\n• Booking process\n• Facilities included\n\nWhat would you like to know? 🚌"

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
                    industrial_context += f"- {ind.title} in {ind.location}: ₹{ind.price}, {ind.duration}\n  {ind.description[:80]}...\n"
                
                area_list = ", ".join(areas)
                
                system_instruction = f"""
                You are 'Panda Bot' 🐼, the friendly AI assistant for DUDU Industrial Visit Hub.
                
                Personality: Energetic, helpful, professional yet warm. Use emojis sparingly but effectively.
                
                Available Locations: {area_list}
                {industrial_context}
                
                Guidelines:
                1. Provide specific information about our industrial visits
                2. Mention exact locations, prices, and durations when asked
                3. Direct users to the 'Industrial's' page for booking
                4. Keep responses concise (2-4 sentences max)
                5. Be encouraging and enthusiastic about industrial learning!
                6. If you don't know something, admit it and suggest contacting +919940764517
                """
                
                api_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=250,
                    temperature=0.8
                )
                
                response = api_response.choices[0].message.content.strip()
                
        except Exception as e:
            error_msg = str(e).lower()
            print(f"DEBUG: OpenAI API Error: {e}")
            
            # Intelligent fallback based on error type
            if any(keyword in error_msg for keyword in ['quota', '429', 'rate_limit', 'insufficient']):
                print("DEBUG: API quota exceeded, using fallback")
            elif any(keyword in error_msg for keyword in ['api_key', 'authentication', 'invalid']):
                print("DEBUG: API authentication failed, using fallback")
            
            response = get_local_fallback(user_message, industrials)
    
    # 4. Log conversation
    try:
        log_entry = ChatbotLog.objects.create(
            user=user if user and not user.is_anonymous else None,
            session_id=session_id or 'anonymous',
            query=user_message,
            response=response
        )
        print(f"DEBUG: Logged chatbot conversation (ID: {log_entry.id})")
    except Exception as e:
        print(f"DEBUG: Failed to log chatbot conversation: {e}")
    
    return response
