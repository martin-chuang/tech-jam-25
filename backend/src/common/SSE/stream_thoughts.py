from flask import Blueprint, Response, stream_with_context
import time

chat_bp = Blueprint('chat', __name__)

def process_steps():
    steps = [
        "Validating files….",
        "Files validated!",
        "Anonymising prompt…",
        "Anonymised prompt is now {anon_prompt}",
        "LLM is thinking…",
        "Original LLM response is {raw_response}.",
        "Deanonymising…",
        "Success!"
    ]
    for step in steps:
        yield f"data: {step}\n\n"
        time.sleep(1)  # Simulate processing delay

@chat_bp.route('/stream-thoughts')
def stream_thoughts():
    return Response(stream_with_context(process_steps()), mimetype='text/event-stream')