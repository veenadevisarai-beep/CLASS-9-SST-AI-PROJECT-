
const chat = document.getElementById("chat");
const welcome = document.getElementById("welcome");

const question = document.getElementById("question");
const chatForm = document.getElementById("chatForm");
const sendButton = document.getElementById("sendButton");

const newChat = document.getElementById("newChat");
const menuBtn = document.getElementById("menuBtn");
const sidebar = document.getElementById("sidebar");


let selectedSubject = "";


/*
    CONVERSATION MEMORY

    This array stores the current conversation.
*/

let conversation = [];


/* SUBJECT BUTTONS */

document.querySelectorAll("[data-subject]").forEach(
    function(button) {

        button.addEventListener(
            "click",
            function() {

                selectedSubject =
                    button.getAttribute(
                        "data-subject"
                    );

                question.placeholder =
                    "Ask a " +
                    selectedSubject +
                    " question...";

                question.focus();

                if (sidebar) {

                    sidebar.classList.remove(
                        "open"
                    );
                }
            }
        );
    }
);


/* NEW CHAT */

newChat.addEventListener(
    "click",
    function() {

        selectedSubject = "";

        conversation = [];

        question.value = "";

        question.placeholder =
            "Ask your question...";

        chat.innerHTML = "";

        chat.appendChild(welcome);

        question.focus();
    }
);


/* ADD MESSAGE */

function addMessage(
    text,
    type
) {

    const message =
        document.createElement(
            "div"
        );

    message.className =
        "message " + type;

    message.textContent =
        text;

    chat.appendChild(
        message
    );

    chat.scrollTop =
        chat.scrollHeight;
}


/* ASK AI */

async function askQuestion() {

    const text =
        question.value.trim();


    if (!text) {

        return;
    }


    /* Show student message */

    addMessage(
        text,
        "user-message"
    );


    question.value = "";


    /* Thinking message */

    const thinking =
        document.createElement(
            "div"
        );

    thinking.className =
        "message ai-message";

    thinking.textContent =
        "Thinking...";


    chat.appendChild(
        thinking
    );


    chat.scrollTop =
        chat.scrollHeight;


    sendButton.disabled =
        true;


    try {

        /*
            Send the previous conversation
            together with the new question.
        */

        const response =
            await fetch(
                "/ask",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        question: text,

                        subject:
                            selectedSubject,

                        history:
                            conversation
                    })
                }
            );


        if (!response.ok) {

            throw new Error(
                "HTTP " +
                response.status
            );
        }


        const data =
            await response.json();


        const answer =
            data.answer ||
            "No answer received.";


        thinking.textContent =
            answer;


        /*
            Save the conversation
            for future questions.
        */

        conversation.push({

            role: "user",

            content: text
        });


        conversation.push({

            role: "assistant",

            content: answer
        });


        /*
            Keep browser memory small.
            The server also limits history.
        */

        if (
            conversation.length >
            12
        ) {

            conversation =
                conversation.slice(
                    -12
                );
        }

    }


    catch (error) {

        console.error(
            "SST AI ERROR:",
            error
        );


        thinking.textContent =
            "Sorry, I could not connect to the AI.";
    }


    finally {

        sendButton.disabled =
            false;

        question.focus();
    }
}


/*
    ENTER + SEND BUTTON

    Because this is a form,
    Enter automatically triggers
    this submit event.
*/

chatForm.addEventListener(
    "submit",
    function(event) {

        event.preventDefault();

        askQuestion();
    }
);


/* MOBILE MENU */

menuBtn.addEventListener(
    "click",
    function() {

        sidebar.classList.toggle(
            "open"
        );
    }
);

