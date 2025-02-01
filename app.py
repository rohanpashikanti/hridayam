import time
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# -------------------------------------------------
#           Hugging Face Chat Setup
# -------------------------------------------------
API_URL = "https://api-inference.huggingface.co/models/rdwdaww/Hridayam"
HEADERS = {"Authorization": "Bearer Enter_Your_Api_Key"}

def query_huggingface_api(payload, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.post(API_URL, headers=HEADERS, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                print(f"[HuggingFace] Server busy, retrying in {delay}s...")
                time.sleep(delay)
            else:
                return {"error": str(e)}

# -------------------------------------------------
#            CBT Quiz Data & Logic
# -------------------------------------------------
questions = {
    "How often have you felt down, depressed, or hopeless in the last two weeks?":
        ['Rarely or none of the time', 'Some of the time', 'Often', 'Nearly every day'],
    "Over the last two weeks, how often have you felt nervous, anxious, or on edge?":
        ['Not at all', 'Several days', 'More than half the days', 'Nearly every day'],
    "How comfortable do you feel in social situations?":
        ['Very comfortable', 'Somewhat comfortable', 'Uncomfortable', 'Very uncomfortable'],
    "How would you describe your recent sleep patterns?":
        ['Regular and restful', 'Occasionally restless', 'Frequently interrupted', 'Poor and unsatisfying'],
    "Have you experienced any physical symptoms of stress or anxiety, such as headaches, stomach upset, or rapid heartbeat?":
        ['No symptoms', 'Mild symptoms', 'Moderate symptoms', 'Severe symptoms'],
    "When you feel overwhelmed, which of the following coping strategies are you most likely to use?":
        ['Physical activity', 'Talking to friends/family', 'Avoiding the situation', 'Substance use'],
    "How do you generally perceive yourself?":
        ['Mostly positive', 'Mixed feelings', 'Mostly negative', 'I struggle with self-perception'],
    "Overall, how satisfied are you with your life?":
        ['Very satisfied', 'Somewhat satisfied', 'Not very satisfied', 'Not satisfied at all'],
    "Have you noticed a change in your interest or pleasure in doing things?":
        ['No change', 'Slight change', 'Noticeable change', 'Significant change'],
    "How would you rate your relationships with family, friends, and coworkers?":
        ['Very healthy', 'Generally healthy', 'Strained', 'Very strained'],
    "How do you usually handle stress in your life?":
        ['I excel at managing stress', 'I generally manage well', 'I manage it with some difficulty', 'I find it overwhelming and hard to manage'],
    "How often do you feel confident about your abilities?":
        ['Almost always', 'Often', 'Sometimes', 'Almost never'],
    "Do you feel you have enough emotional support from others?":
        ['I always have the support I need', 'I usually have enough support', 'I have some support, but I need more', 'I don’t have enough support'],
    "How difficult is it for you to make decisions?":
        ['Not difficult at all', 'Not very difficult', 'Somewhat difficult', 'Very difficult'],
    "Do you feel fulfilled in your personal life and career?":
        ['Completely fulfilled', 'Mostly fulfilled', 'Somewhat fulfilled', 'Not fulfilled'],
    "Have you ever received any form of psychological therapy?":
        ['No, never', 'Yes, but it was a long time ago', 'Yes, recently', 'Yes, I am currently in therapy'],
    "How would you describe your usual energy levels?":
        ['High', 'Normal', 'Somewhat low', 'Very low'],
    "How often do you struggle with focus or concentration?":
        ['Never', 'Rarely', 'Occasionally', 'Frequently'],
    "When faced with a challenge, how do you usually react?":
        ['I thrive on challenges', 'I take it as a learning opportunity', 'I feel anxious but manage to cope', 'I feel overwhelmed'],
    "How much control do you feel you have over your life direction?":
        ['Full control', 'Some control', 'Little control', 'No control']
}

category_questions = {
    "Mood": [0, 1, 6, 9, 17],
    "Relationships": [2, 9, 12, 13],
    "Habits": [3, 4, 5, 16],
    "Focus": [10, 11, 13, 18, 19]
}

response_weights = {
    'Rarely or none of the time': 0, 'Some of the time': 1, 'Often': 2, 'Nearly every day': 3,
    'Not at all': 0, 'Several days': 1, 'More than half the days': 2, 'Nearly every day': 3,
    'Very comfortable': 0, 'Somewhat comfortable': 1, 'Uncomfortable': 2, 'Very uncomfortable': 3,
    'Regular and restful': 0, 'Occasionally restless': 1, 'Frequently interrupted': 2, 'Poor and unsatisfying': 3,
    'No symptoms': 0, 'Mild symptoms': 1, 'Moderate symptoms': 2, 'Severe symptoms': 3,
    'Physical activity': 0, 'Talking to friends/family': 0, 'Avoiding the situation': 1, 'Substance use': 3,
    'Mostly positive': 0, 'Mixed feelings': 1, 'Mostly negative': 2, 'I struggle with self-perception': 3,
    'Very satisfied': 0, 'Somewhat satisfied': 1, 'Not very satisfied': 2, 'Not satisfied at all': 3,
    'No change': 0, 'Slight change': 1, 'Noticeable change': 2, 'Significant change': 3,
    'Very healthy': 0, 'Generally healthy': 1, 'Strained': 2, 'Very strained': 3,
    'I excel at managing stress': 0, 'I generally manage well': 1, 'I manage it with some difficulty': 2, 'I find it overwhelming and hard to manage': 3,
    'Almost always': 0, 'Often': 1, 'Sometimes': 2, 'Almost never': 3,
    'I always have the support I need': 0, 'I usually have enough support': 1, 'I have some support, but I need more': 2, 'I don’t have enough support': 3,
    'Not difficult at all': 0, 'Not very difficult': 1, 'Somewhat difficult': 2, 'Very difficult': 3,
    'Completely fulfilled': 0, 'Mostly fulfilled': 1, 'Somewhat fulfilled': 2, 'Not fulfilled': 3,
    'No, never': 0, 'Yes, but it was a long time ago': 1, 'Yes, recently': 2, 'Yes, I am currently in therapy': 3,
    'High': 0, 'Normal': 1, 'Somewhat low': 2, 'Very low': 3,
    'Never': 0, 'Rarely': 1, 'Occasionally': 2, 'Frequently': 3,
    'I thrive on challenges': 0, 'I take it as a learning opportunity': 1, 'I feel anxious but manage to cope': 2, 'I feel overwhelmed': 3,
    'Full control': 0, 'Some control': 1, 'Little control': 2, 'No control': 3
}

def calculate_category_scores(responses):
    category_scores = {}
    max_scores = {}
    for category, question_indices in category_questions.items():
        category_score = sum(
            response_weights.get(responses[i], 0)
            for i in question_indices
            if i < len(responses)
        )
        max_score = len(question_indices) * 3
        category_scores[category] = category_score
        max_scores[category] = max_score

    category_percentages = {
        category: round((max_scores[category] - score) / max_scores[category] * 100, 2)
        for category, score in category_scores.items()
    }
    return category_scores, category_percentages

# -------------------------------------------------
#              Flask Routes
# -------------------------------------------------

@app.route("/")
def landing():
    """ 
    Simple landing page or redirect. 
    For example, we just link to /login 
    or do: return redirect(url_for('login')) 
    """
    return "<h1>Welcome to CBT App</h1><p><a href='/login'>Go to Login / Register</a></p>"

@app.route("/login")
def login():
    """
    Single page that has BOTH login form and registration form (log.html).
    """
    return render_template("log.html")

@app.route("/logout")
def logout():
    """
    Route to handle user logout.
    Clears session data and redirects to login page.
    """
    return redirect(url_for('login'))
    
@app.route("/quiz")
def quiz_page():
    """
    Serves your quiz page (quiz.html).
    """
    return render_template("quiz.html")

@app.route("/home")
def home_page():
    """
    Serves your final multi-page phone interface (home.html).
    """
    return render_template("home.html")

# -------------- QUIZ API Routes --------------
@app.route("/get-question", methods=["GET"])
def get_question():
    index = int(request.args.get('index', 0))
    question_keys = list(questions.keys())
    if index >= len(question_keys):
        return jsonify({"error": "No more questions"}), 400

    question_text = question_keys[index]
    options = questions[question_text]
    return jsonify({
        "question": question_text,
        "options": options
    })

@app.route("/submit-responses", methods=["POST"])
def submit_responses():
    try:
        data = request.json
        responses = data.get('responses', [])
        if not responses or len(responses) != len(questions):
            return jsonify({"error": "Incomplete or invalid responses"}), 400

        _, category_percentages = calculate_category_scores(responses)
        return jsonify({
            "mood": category_percentages.get("Mood", 0),
            "relationships": category_percentages.get("Relationships", 0),
            "habits": category_percentages.get("Habits", 0),
            "focus": category_percentages.get("Focus", 0)
        })
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# -------------- Chat Endpoint with Hugging Face --------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    instruction = (
        "You are a professional CBT therapist. Your role is to help users process their feelings, "
        "validate their emotions, and guide them using cognitive behavioral therapy techniques. "
        "Respond empathetically, encourage positive thinking, and offer small actionable steps "
        "to help users feel better.\n"
    )
    inputs = instruction + user_message

    response = query_huggingface_api({"inputs": inputs})
    if "error" in response:
        return jsonify({"error": response["error"]}), 500

    ai_response = "I'm here to listen. (fallback)"
    if isinstance(response, dict) and "generated_text" in response:
        ai_response = response["generated_text"]
    elif isinstance(response, list) and len(response) > 0:
        ai_response = response[0].get("generated_text", ai_response)

    return jsonify({"response": ai_response})

if __name__ == "__main__":
    app.run()
