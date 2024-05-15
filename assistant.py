import requests
from openai import OpenAI

def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': 'bitcoin',
        'vs_currencies': 'usd'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data['bitcoin']['usd']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Bitcoin price: {e}")
        return None

# Add your api key here
API_KEY = "your-api-key"
client = OpenAI(api_key=API_KEY)

def run_conversation():
    messages = []
    tools = [
        {
            "type": "function",
            "function": {
                "name": "fetch_bitcoin_price",
                "description": "Get the current price of Bitcoin in USD",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        }
    ]

    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            available_functions = {
                "fetch_bitcoin_price": fetch_bitcoin_price,
            }
            messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_response = str(function_to_call())
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )
            second_response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
            )
            print(f"Assistant: {second_response.choices[0].message.content}")
        else:
            print(f"Assistant: {response_message.content}")

print(run_conversation())
