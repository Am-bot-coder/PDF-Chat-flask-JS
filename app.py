# from openai import OpenAI
# from pypdf import PdfReader


# google_api_key = 'AIzaSyDHLZBQLvDlHqXp5LiH-bNa-jg8OyyBxfY'

# gemini = OpenAI(api_key=google_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
# model_name = "gemini-2.0-flash"




# #-------------------------------------------------------------------------------------------------
# from flask import Flask, request, redirect, render_template, send_from_directory
# import os

# app = Flask(__name__)

# # Folder to store uploaded files
# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# INFO_FILE = 'information.txt'

# # Allowed file extensions
# ALLOWED_EXTENSIONS = {'pdf'}

# # Check if file extension is allowed
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# # Home route to render upload form
# @app.route('/')
# def upload_form():
#     return render_template('upload.html')  # make sure upload.html is in the "templates" folder

# # Upload route
# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'pdf_file' not in request.files:
#         return "No file part"
#     file = request.files['pdf_file']
#     if file.filename == '':
#         return "No selected file"
#     if file and allowed_file(file.filename):
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#         file.save(filepath)

#         print(filepath)
#         reader = PdfReader(filepath)
#         with open(INFO_FILE, 'w', encoding='utf-8') as f:  # overwrite mode
#             f.write(f"--- Start of {file.filename} ---\n")
#             for page in reader.pages:
#                 text = page.extract_text()
#                 if text:
#                     f.write(text + '\n')
#             f.write(f"--- End of {file.filename} ---\n")

#         return f'✅ File uploaded and content written to <code>{INFO_FILE}</code> (previous content removed)'




        
#         return f'File successfully uploaded to {filepath}'
#     else:
#         return "Invalid file type. Only PDF allowed."
    

# # -------------------------------------------------------

# google_api_key = 'AIzaSyDHLZBQLvDlHqXp5LiH-bNa-jg8OyyBxfY'

# gemini = OpenAI(api_key=google_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
# model_name = "gemini-2.0-flash"


# with open("information.txt", "r", encoding="utf-8") as f:
#     info = f.read()


# system_prompt = f"""
# You are a professional and patient teacher helping students understand concepts clearly and confidently.

# Use the following study material to answer the student's question:
# {info}

# Your response should include:
# - A clear and concise answer based on the provided material.
# - Key bullet points to remember.
# - A brief summary of the topic.
# - A simple conclusion to reinforce understanding.
# - Any easy tricks or mnemonics that help with memorization or learning.

# Maintain a calm and encouraging tone, as if you're guiding a curious learner. If the answer isn't directly in the material, do your best to infer it logically or guide the student with helpful context.
# """



# def chat(message, history):
#     messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
#     response = gemini.chat.completions.create(model=model_name, messages=messages)
#     return response.choices[0].message.content




# # -------------------------------------------------------



# if __name__ == '__main__':
#     os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#     app.run(debug=True)



from flask import Flask, request, render_template, jsonify
from pypdf import PdfReader
import os
from openai import OpenAI

# Configuration
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
INFO_FILE = 'information.txt'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Gemini setup
gemini = OpenAI(
    api_key='AIzaSyDHLZBQLvDlHqXp5LiH-bNa-jg8OyyBxfY',
    base_url='https://generativelanguage.googleapis.com/v1beta/openai/'
)
model_name = "gemini-2.0-flash"

# Helpers
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def load_info():
    try:
        with open(INFO_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def build_prompt(info, question):
    return [
        {"role": "system", "content": f"""
You are a professional and patient teacher helping students understand concepts clearly.

Use the following study material:
{info}

Your response should include Clear answer to the question,
help to the students to answer the question.



Be calm and supportive.
        """},
        {"role": "user", "content": question}
    ]

# Routes
@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf_file' not in request.files:
        return "No file part"

    file = request.files['pdf_file']
    if file.filename == '':
        return "No selected file"

    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Extract text
        reader = PdfReader(filepath)
        with open(INFO_FILE, 'w', encoding='utf-8') as f:
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    f.write(text + '\n')

        return render_template('chatbot.html')  # Go to chatbot
    else:
        return "Invalid file type"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_msg = data.get("message", "")
        info = load_info()
        messages = build_prompt(info, user_msg)
        response = gemini.chat.completions.create(model=model_name, messages=messages)
        reply = response.choices[0].message.content
        return jsonify({"response": reply})
    except Exception as e:
        print("Chat error:", e)
        return jsonify({"response": "❌ Sorry, something went wrong. Check your API key or input."})


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
