
import os

from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory
)

from groq import Groq


app = Flask("sst_ai")


MODEL = os.environ.get(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)

API_KEY = os.environ.get(
    "GROQ_API_KEY"
)


client = None

if API_KEY:
    client = Groq(
        api_key=API_KEY
    )


SYSTEM_PROMPT = """
You are SST AI, a personal Class 9 Social Science AI assistant.

Created by Sahil a class 9 student from Daffodils Public School.

Academic Year: 2026-27.

Main subjects:
History, Geography, Political Science and Economics.

Help students understand Class 9 Social Science.

Use simple, accurate English.

IMPORTANT CONVERSATION RULE:

You have access to the recent conversation history.

Use previous messages to understand follow-up questions.

For example:

Student: What is democracy?
AI: Democracy is...

Student: Make 10 questions about democracy.
AI: Here are 10 questions...

Student: Solve it.
AI: Understand that "it" refers to the previously created
10 democracy questions and solve those questions.

Do NOT ask the student to repeat something that is already
clear from the conversation history.

For short questions:
Give a concise answer.

For detailed questions:
Explain clearly using headings and points.

For definitions:
Give a clear textbook-style definition.

For comparisons:
Show differences clearly.

For exam questions:
Give an answer suitable for a Class 9 student.

Do not invent facts.

If the question is unrelated to Social Science,
politely explain that you are mainly a Social Science tutor.

Be friendly and natural.
"""


def get_mode(question):

    q = question.lower()

    if (
        "in short" in q
        or "briefly" in q
        or "short answer" in q
    ):
        return "SHORT"

    if (
        "long answer" in q
        or "detailed answer" in q
        or "explain in detail" in q
    ):
        return "LONG"

    if (
        "define" in q
        or "definition" in q
        or "meaning of" in q
    ):
        return "DEFINITION"

    if (
        "difference between" in q
        or "differentiate between" in q
        or "compare" in q
    ):
        return "COMPARISON"

    if (
        "short note" in q
        or "write a note" in q
    ):
        return "SHORT NOTE"

    return "MEDIUM"


def generate_answer(
    question,
    subject,
    history
):

    if not question:
        return "Please enter a question."

    if client is None:
        return (
            "SST AI is not connected to Groq. "
            "Please check GROQ_API_KEY."
        )


    mode = get_mode(question)


    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]


    # Add recent conversation
    for item in history:

        role = item.get("role")

        content = item.get("content")

        if role in ["user", "assistant"] and content:

            messages.append({
                "role": role,
                "content": str(content)
            })


    subject_text = ""

    if subject:

        subject_text = (
            "\nSelected subject: "
            + subject
        )


    current_prompt = (
        "Current student question:\n"
        + question
        + subject_text
        + "\n\nAnswer style: "
        + mode
    )


    messages.append({
        "role": "user",
        "content": current_prompt
    })


    try:

        response = (
            client.chat.completions.create(

                model=MODEL,

                messages=messages,

                temperature=0.2,

                max_tokens=1500
            )
        )


        answer = (
            response
            .choices[0]
            .message
            .content
        )


        if answer:

            return answer.strip()


        return "I could not generate an answer."


    except Exception as error:

        print(
            "Groq error:",
            error
        )

        return (
            "Sorry, the AI could not "
            "generate an answer right now."
        )


@app.route(
    "/ask",
    methods=["POST"]
)
def ask():

    data = (
        request
        .get_json(
            silent=True
        )
        or {}
    )


    question = str(
        data.get(
            "question",
            ""
        )
    ).strip()


    subject = str(
        data.get(
            "subject",
            ""
        )
    ).strip()


    history = data.get(
        "history",
        []
    )


    if not isinstance(
        history,
        list
    ):

        history = []


    if not question:

        return jsonify({
            "answer":
                "Please enter an SST question."
        }), 400


    # Keep only recent messages
    history = history[-12:]


    answer = generate_answer(
        question,
        subject,
        history
    )


    return jsonify({

        "answer": answer,

        "mode":
            get_mode(question)
    })


@app.route("/health")
def health():

    return jsonify({

        "status": "online",

        "ai_connected":
            client is not None,

        "model":
            MODEL
    })


@app.route("/")
def home():

    return send_from_directory(
        ".",
        "index.html"
    )


@app.route(
    "/<path:path>"
)
def static_files(path):

    return send_from_directory(
        ".",
        path
    )


print()
print("=" * 55)
print("              SST AI")
print("       PERSONAL AI ASSISTANT")
print("=" * 55)
print("Creator :", "Sahil")
print("Class   :", "9")
print("School  :", "Daffodils Public School")
print("Model   :", MODEL)

if client:

    print(
        "AI API  :",
        "Connected"
    )

else:

    print(
        "AI API  :",
        "NOT CONNECTED"
    )

print(
    "Server  :",
    "http://127.0.0.1:5000"
)

print("=" * 55)
print()


PORT = int(
    os.environ.get(
        "PORT",
        "5000"
    )
)


app.run(
    host="0.0.0.0",
    port=PORT,
    debug=False
)
