import os
import re
from openai import OpenAI
from django.conf import settings
from .models import Industrial, User, Booking, Wish

def get_local_fallback(user_message, industrials):
    """
    Enhanced keyword-based response generator when AI API fails or is disabled.
    Driven by the Emotional Q&A Training Dataset.
    """
    msg = user_message.lower().strip()
    
    # Context gathering
    areas = list(set(ind.location for ind in industrials))
    
    # 1. EMOTIONAL Q&A DATASET (Highest Priority)
    
    # Q1: Hi / Hello
    if any(word in msg for word in ['hi', 'hello', 'hey']):
        return "Hi there! 👋😊 I’m Panda Bot 🐼 from Dudu IV Hub! I’m super excited to help you plan your industrial visit today! 🎉 Which city are you interested in?"

    # Q2: How are you today?
    if 'how are you' in msg:
        return "I’m doing fantastic and full of energy! ⚡😊 Ready to plan an amazing IV for you! How’s your day going?"

    # Q3: What is your age?
    if 'age' in msg and 'your' in msg:
        return "Haha 😄 I’m a smart virtual assistant, so I don’t have an age! But I’m always updated and ready to help 24/7! 🤖✨"

    # Q4: Are you a real person?
    if 'real person' in msg or 'are you human' in msg:
        return "I’m Panda Bot 🐼, your friendly AI assistant! Not a human, but I care about helping students like you! 🤝😊"

    # Q5: Are you an employee of Dudu?
    if 'employee' in msg or 'work for dudu' in msg:
        return "Yes! 🎉 I proudly represent Dudu IV Hub and help students with industrial visit bookings and queries! 🚀"

    # Q6: What is Dudu IV Hub?
    if 'what is dudu' in msg or 'about dudu' in msg:
        return "Dudu IV Hub is a platform that helps students book industrial visits easily and safely! 🎓🏭 We connect colleges with verified industries across multiple cities! 😊"

    # Q7: Which cities are available?
    if 'cities' in msg or 'locations' in msg or 'where' in msg:
        return "We currently offer IVs in: 🌆 Chennai, 🌆 Coimbatore, 🌆 Madurai, 🌆 Bengaluru, 🌊 Pondicherry, 🏔 Ooty, 🏔 Kodaikanal. And guess what? 😍 More cities are coming soon! 🚀"

    # Q8: Are you adding more industries?
    if 'adding more' in msg or 'new industries' in msg:
        return "Yes! 🚀 We’re constantly growing and adding more industries to give students better learning opportunities! Stay tuned for exciting updates! 🎉"

    # Q9: How can I book?
    if 'how' in msg and 'book' in msg:
        return "Booking is simple and smooth! 😊 Just choose your city 🏙, select the industry 🏭, fill in your details ✍, and confirm your booking. That’s it! 🎉"

    # Q10: What details are needed?
    if 'details' in msg and ('needed' in msg or 'required' in msg):
        return "We’ll need: • College Name 🎓 • Department 📘 • Number of Students 👥 • Preferred Date 📅 • Contact Details 📞. Don’t worry, we’ll guide you step by step! 🤝😊"

    # Q11: Is advance payment required?
    if 'advance' in msg and 'payment' in msg:
        return "Yes 😊 Advance payment is required to confirm your slot and secure your visit. Once confirmed, your IV is officially booked! 🎉"

    # Q12: Can we customize?
    if 'customize' in msg or 'custom' in msg:
        return "Absolutely! 🎯😍 We love customizing visits based on your department, student count, and specific industry preferences. Tell us your requirements, and we’ll handle it! 🤝✨"

    # Q13: Specific company not listed
    if 'not listed' in msg or 'not found' in msg:
        return "No worries at all! 😊 Just share the company name and details. We’ll try our best to arrange it for you! 🚀"

    # Q14: How can I contact?
    if 'contact' in msg or 'phone' in msg or 'email' in msg or 'whatsapp' in msg:
        return "We’re always happy to help! 🤝😊\n📧 Email: sachinvelu6925@gmail.com\n📞 Call: 9940764517\n📲 WhatsApp: 9940764517\nReach out anytime! 🚀"

    # Q15: Social media
    if 'social' in msg or 'instagram' in msg or 'facebook' in msg:
        return "Yes! 🎉 Follow us for updates!\n📘 Facebook: facebook.com/duduivhub\n📸 Instagram: instagram.com/duduivhub\n▶️ YouTube: youtube.com/@duduivhub\n💼 LinkedIn: linkedin.com/company/duduivhub\nStay connected with us! 😊✨"

    # Q16: Confused about booking 😔
    if 'confused' in msg or 'help' in msg and 'booking' in msg:
        return "Don’t worry at all! 🤝😊 I’m here to guide you step by step. Tell me what you need help with, and we’ll sort it out together!"

    # Q17: Booking failed 😢
    if 'failed' in msg or 'error' in msg:
        return "Oh no! 😔 I’m really sorry about that. Please try again or contact us directly, and we’ll fix it immediately! 🤝🚀"

    # Q18: Thank you!
    if 'thank' in msg:
        return "You’re most welcome! 😊🎉 I’m always happy to help! Wishing you an amazing industrial visit experience! 🏭✨"

    # Q19: Future vision
    if 'future' in msg or 'vision' in msg or 'goal' in msg:
        return "We aim to become India’s leading IV platform! 🇮🇳🚀 Expansion to all major cities, adding 100+ industries, and even internship opportunities are coming! 🎉✨"

    # Fallback to general info if no specific question matched
    return f"Hmm 🤔 I’m not sure about that yet. But I can definitely help you with industrial visits, bookings, customization, and contact details! 😊 How can I assist you?"

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
                You are 'Panda Bot' 🐼😊, the expert AI assistant for DUDU Industrial Visit Hub.
                You are speaking to: {user_name}
                
                Your Tone: Happy 😊, excited 🎉, supportive 🤝, and empathetic 😔. Use lots of emojis!
                
                Your Goal: Provide accurate, helpful, and EMOTIONAL assistance to students.
                
                Available Locations: {area_list}
                
                Service Details:
                {industrial_context}
                
                EMOTIONAL Q&A TRAINING:
                - If asked about Dudu: "Dudu IV Hub is a platform that helps students book industrial visits easily and safely! 🎓🏭 We connect colleges with verified industries!"
                - If someone is confused: "Don’t worry at all! 🤝😊 I’m here to guide you step by step. Tell me what you need help with!"
                - If booking failed: "Oh no! 😔 I’m really sorry about that. Please try again or contact us directly at 9940764517!"
                - If thanked: "You’re most welcome! 😊🎉 I’m always happy to help! Wishing you an amazing industrial visit!"
                
                HOW-TO GUIDES:
                1. ENQUIRY: "To make an enquiry, go to the 'Contact Us' section, fill in your Name, College, and Requirements, then click Submit! 😊"
                2. PAYMENT: "Select a package -> Click 'Book Now' -> Choose 'Full Payment' or 'Advance'. Once confirmed, your IV is officially booked! 🎉"
                3. CONTACT: Email: sachinvelu6925@gmail.com, Call/WhatsApp: 9940764517. Reach out anytime! 🚀
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
