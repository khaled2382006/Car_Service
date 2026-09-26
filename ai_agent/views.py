import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .agent import run_agent


@login_required
def chat_page(request):
    return render(
        request,
        "ai_agent/chat.html"
    )


@login_required
@require_POST
def chat_api(request):

    try:
        data = json.loads(request.body)

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON."},
            status=400
        )

    user_input = data.get("message", "").strip()

    if not user_input:
        return JsonResponse(
            {"error": "Message is required."},
            status=400
        )

    previous_interaction_id = request.session.get(
        "gemini_interaction_id"
    )

    try:

        response_text, interaction_id = run_agent(
            user=request.user,
            user_input=user_input,
            previous_interaction_id=previous_interaction_id,
        )

    except Exception as e:

        return JsonResponse(
            {
                "error": "AI service error.",
                "details": str(e),
            },
            status=500
        )

    request.session["gemini_interaction_id"] = interaction_id

    return JsonResponse({
        "response": response_text
    })