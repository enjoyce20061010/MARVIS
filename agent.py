import os
from typing import Any, Dict, List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from rich.console import Console
from openai import OpenAI

# Load environment variables
load_dotenv()

console = Console()

# Define a simple tool schema using Pydantic
class WeatherRequest(BaseModel):
	city: str = Field(..., description="City name, e.g., Taipei")
	unit: str = Field("celsius", description="Temperature unit: celsius or fahrenheit")


class ToolCallResult(BaseModel):
	name: str
	args: Dict[str, Any]
	result: Any


def fake_weather_api(city: str, unit: str = "celsius") -> Dict[str, Any]:
	"""A fake tool that simulates weather lookup."""
	temp_c = 28.0
	if unit.lower() == "fahrenheit":
		return {"city": city, "unit": "fahrenheit", "temperature": temp_c * 9 / 5 + 32}
	return {"city": city, "unit": "celsius", "temperature": temp_c}


def run_agent(user_query: str) -> str:
	"""Run a minimal function-calling agent with tool support."""
	api_key = os.getenv("OPENAI_API_KEY")
	if not api_key:
		raise RuntimeError("Missing OPENAI_API_KEY. Set it in your environment or .env file.")

	client = OpenAI(api_key=api_key)

	# Define the tool schema compatible with the OpenAI Responses API
	tools = [
		{
			"type": "function",
			"function": {
				"name": "fake_weather_api",
				"description": "Get current weather for a city.",
				"parameters": WeatherRequest.model_json_schema(),
			},
		},
	]

	messages: List[Dict[str, Any]] = [
		{"role": "system", "content": "You are a helpful assistant. Use tools when relevant."},
		{"role": "user", "content": user_query},
	]

	# First turn: ask model; it may request a tool call
	resp = client.chat.completions.create(
		model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
		messages=messages,
		tools=tools,
		tool_choice="auto",
	)

	message = resp.choices[0].message

	# If the model asked to call a tool, execute it and return final answer
	if message.tool_calls:
		tool_results: List[ToolCallResult] = []
		for tc in message.tool_calls:
			fn_name = tc.function.name
			args = WeatherRequest.model_validate_json(tc.function.arguments).model_dump()
			if fn_name == "fake_weather_api":
				result = fake_weather_api(**args)
				tool_results.append(ToolCallResult(name=fn_name, args=args, result=result))

		# Append tool result messages and ask for final answer
		messages.append(message.model_dump(exclude_none=True))
		for tr in tool_results:
			messages.append({
				"role": "tool",
				"tool_call_id": message.tool_calls[0].id,
				"name": tr.name,
				"content": str(tr.result),
			})

		final = client.chat.completions.create(
			model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
			messages=messages,
		)
		return final.choices[0].message.content or ""

	# No tool call; just return the answer
	return message.content or ""


if __name__ == "__main__":
	console.print("[bold green]Minimal Agent[/bold green]")
	question = os.getenv("QUESTION", "台北現在的天氣？")
	answer = run_agent(question)
	console.print("[bold]Q:[/bold]", question)
	console.print("[bold]A:[/bold]", answer)

