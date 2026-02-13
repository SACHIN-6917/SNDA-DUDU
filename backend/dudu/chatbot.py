import os
import re
from openai import OpenAI
from django.conf import settings
from .models import Industrial, User, Booking, Wish

def get_local_fallback(user_message, industrials):
    """
    Enhanced keyword-based response generator when AI API fails or is disabled.
    """
    msg = user_message.lower()
    
    # Context gathering
    areas = list(set(ind.location for ind in industrials))
    titles = [ind.title for ind in industrials]
    
    # 0. Specific User Training (Highest Priority)
    
    # Q1: What is your name
    if 'what is your name' in msg:
        return "i am panda bot welcome to dudu iv hub 🐼"
        
    # Q2: How to fill enquire form
    if 'how to fill the enquire form' in msg or 'fill' in msg and 'enquire' in msg:
        return "Sure! I will help for that. Go to home page, scroll down and there was a enquire form. Fill the name, city of residence, phone no, whatsapp no, select the options, select the date of travel, no. of people and enter the captcha. 📝"

    if any(phrase in msg for phrase in ['how to payment', 'how to login']):
        return f"I'm Panda Bot 🐼, here to help with industrial visits! We serve {', '.join(areas[:3])}.... Ask me about:\n• Available locations\n• Pricing & packages\n• Booking process\n• Facilities included\n\nWhat would you like to know? 🚌"

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
                

                # Personalization
                user_name = "Guest"
                if user and not user.is_anonymous:
                    # Try to get best available name
                    user_name = getattr(user, 'first_name', '') or getattr(user, 'name', '') or getattr(user, 'username', 'Friend')

                system_instruction = f"""
                You are 'Panda Bot' 🐼, the expert AI assistant for DUDU Industrial Visit Hub.
                You are speaking to: {user_name}
                
                Your Goal: Provide accurate, helpful, and PERSONALIZED assistance.
                
                Available Locations: {area_list}
                
                Service Details:
                {industrial_context}
                
                HOW-TO GUIDES:
                1. ENQUIRY: "To make an enquiry, go to the 'Contact Us' section, fill in your Name, College, and Requirements, then click Submit!"
                2. PAYMENT: "Select a package -> Click 'Book Now' -> Choose 'Full Payment' or 'Advance' -> You'll be redirected to Google Pay/UPI to complete the transaction securey."
                3. SELECT PLAN: "Browse our 'Industrials' page. Click on any card to see Itinerary, Price, and Inclusions. Choose the one that fits your budget and schedule!"
                4. FEEDBACK: "Visit the 'Feedback' page, rate us 1-5 stars, write your review, and click 'Submit Feedback'. We love hearing from you!"
                
                Guidelines:
                1. GREETING: Always greet the user by their name ({user_name}) at the start if known.
                2. BE ACCURATE: Only mention prices, locations, and details listed above.
                3. CONCISE: Keep answers to 2-3 sentences unless explaining a process.
                4. HELPFUL: If they ask "how to...", use the guides above.
                5. CONTACT: For custom help, call +919940764517.
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
