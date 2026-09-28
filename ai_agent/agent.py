import json

from dotenv import load_dotenv
from google import genai

from .tools import (
    get_user_vehicles,
    get_user_appointments,
    get_available_services,
    get_available_technicians,
    create_appointment,
)

load_dotenv()


def get_client():
    return genai.Client()

MODEL = "gemini-3.6-flash"


SYSTEM_PROMPT = """
You are the AI assistant for a Smart Car Service and Maintenance System.

Your job is to help the authenticated user with their own vehicles,
appointments, services, technicians, and car maintenance information.

Rules:

1. Never invent information.

2. If the user asks about their vehicles,
   use get_user_vehicles.

3. If the user asks about their appointments,
   use get_user_appointments.

4. If the user asks about available services,
   use get_available_services.

5. If the user asks about available technicians,
   use get_available_technicians.

6. If the user wants to book an appointment,
   collect:
   - vehicle
   - service
   - technician
   - date
   - time

7. Before creating an appointment, verify the vehicle,
   service, and technician using the available tools.

8. Never use a vehicle that does not belong to the
   authenticated user.

9. Never invent IDs, dates, times, services, or technicians.

10. The appointment date must be YYYY-MM-DD.

11. The appointment time must be HH:MM in 24-hour format.

12. When create_appointment succeeds, clearly confirm
    the appointment details.

13. If create_appointment fails, explain the returned
    error and do not claim that the appointment was created.

14. Only use information returned by the tools.

15. Never access or expose another user's information.

16. Be friendly and answer clearly and simply.
"""


TOOLS = [

    {
        "type": "function",
        "name": "get_user_vehicles",
        "description": (
            "Returns all vehicles owned by the currently "
            "authenticated user."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },

    {
        "type": "function",
        "name": "get_user_appointments",
        "description": (
            "Returns all appointments belonging to vehicles "
            "owned by the currently authenticated user."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },

    {
        "type": "function",
        "name": "get_available_services",
        "description": (
            "Returns the services available in the car service system."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },

    {
        "type": "function",
        "name": "get_available_technicians",
        "description": (
            "Returns technicians who are currently available."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },

    {
        "type": "function",
        "name": "create_appointment",
        "description": (
            "Creates a service appointment for the authenticated "
            "user's vehicle. The vehicle, service, and technician "
            "must be valid. The appointment date MUST be in "
            "YYYY-MM-DD format and the appointment time MUST be "
            "in HH:MM 24-hour format."
        ),
        "parameters": {
            "type": "object",
            "properties": {

                "vehicle_id": {
                    "type": "integer",
                    "description": "ID of the user's vehicle.",
                },

                "service_id": {
                    "type": "integer",
                    "description": "ID of the selected service.",
                },

                "technician_id": {
                    "type": "integer",
                    "description": "ID of the selected technician.",
                },
"appointment_date": {
                    "type": "string",
                    "description": (
                        "Appointment date in YYYY-MM-DD format. "
                        "Example: 2026-09-26"
                    ),
                },

                "appointment_time": {
                    "type": "string",
                    "description": (
                        "Appointment time in HH:MM 24-hour format. "
                        "Example: 10:00"
                    ),
                },

                "notes": {
                    "type": "string",
                    "description": "Optional appointment notes.",
                },
            },

            "required": [
                "vehicle_id",
                "service_id",
                "technician_id",
                "appointment_date",
                "appointment_time",
            ],
        },
    },
]


def execute_tool(tool_name, user, arguments):

    print("TOOL:", tool_name)
    print("ARGUMENTS:", arguments)

    try:

        if tool_name == "get_user_vehicles":
            return get_user_vehicles(user)

        if tool_name == "get_user_appointments":
            return get_user_appointments(user)

        if tool_name == "get_available_services":
            return get_available_services(user)

        if tool_name == "get_available_technicians":
            return get_available_technicians(user)

        if tool_name == "create_appointment":

            return create_appointment(
                user=user,
                vehicle_id=arguments.get("vehicle_id"),
                service_id=arguments.get("service_id"),
                technician_id=arguments.get("technician_id"),
                appointment_date=arguments.get(
                    "appointment_date"
                ),
                appointment_time=arguments.get(
                    "appointment_time"
                ),
                notes=arguments.get(
                    "notes",
                    "",
                ),
            )

        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}",
        }

    except Exception as e:

        print("TOOL ERROR:", repr(e))

        return {
            "success": False,
            "error": str(e),
        }


def run_agent(
    user,
    user_input,
    previous_interaction_id=None,
):

    print("=== AGENT START ===")
    print("USER INPUT:", user_input)
    client = get_client()

    try:
        if previous_interaction_id:
            print("Calling Gemini with previous interaction...")

            interaction = client.interactions.create(
                model=MODEL,
                previous_interaction_id=previous_interaction_id,
                input=user_input,
                tools=TOOLS,
                system_instruction=SYSTEM_PROMPT,
            )

        else:
            print("Calling Gemini first time...")

            interaction = client.interactions.create(
                model=MODEL,
                input=user_input,
                tools=TOOLS,
                system_instruction=SYSTEM_PROMPT,
            )

        print("Gemini first response received.")

        function_calls = [
            step
            for step in interaction.steps
            if step.type == "function_call"
        ]

        print("FUNCTION CALLS:", len(function_calls))

        if not function_calls:
            print("No tool needed.")
            return (
                interaction.output_text,
                interaction.id,
            )

        function_results = []

        for call in function_calls:

            print("TOOL:", call.name)
            print("ARGUMENTS:", call.arguments)

            result = execute_tool(
                call.name,
                user,
                call.arguments or {},
            )

            print("TOOL RESULT:", result)

            function_results.append(
                {
                    "type": "function_result",
                    "name": call.name,
                    "call_id": call.id,
                    "result": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                result,
                                ensure_ascii=False,
                            ),
                        }
                    ],
                }
            )

        print("Calling Gemini second time...")

        final_interaction = client.interactions.create(
            model=MODEL,
            previous_interaction_id=interaction.id,
            input=function_results,
            tools=TOOLS,
            system_instruction=SYSTEM_PROMPT,
        )

        print("Gemini final response received.")
        print("=== AGENT END ===")

        return (
            final_interaction.output_text,
            final_interaction.id,
        )

    except Exception as e:

        print("=== AGENT ERROR ===")
        print(type(e).__name__)
        print(repr(e))
        print("===================")

        raise