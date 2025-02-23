from dotenv import load_dotenv
from openai import OpenAI
import requests
from colorama import init, Fore, Style
import time, json, os

load_dotenv()

init(autoreset = True)


class Assistant():
	"""
	Assistant class to manage OpenAI Assistant
	
	Attributes:
		name (str): The name of the assistant.
		ASSISTANT_ID (str): The unique identifier for the assistant.
		TOOLS_API_URL (str): API endpoint that generates responses from external tools
	"""
	
	def __init__(self, name, ASSISTANT_ID, TOOLS_API_URL):
		self.client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))
		self.name = name
		self.ASSISTANT_ID = ASSISTANT_ID
		self.TOOLS_API_URL = TOOLS_API_URL
		self.error_msg = "Ha ocurrido un error, por favor realice la consulta más tarde."
	
	
	def create_thread(self):
		return self.client.beta.threads.create().id


	def wait_on_run(self, run, thread_id):
		while run.status == "queued" or run.status == "in_progress":
			run = self.client.beta.threads.runs.retrieve(thread_id = thread_id, run_id = run.id)
			time.sleep(0.5)
		  
		return run


	def get_response(self, message_object, thread_id):
		
		response = self.client.beta.threads.messages.list(thread_id = thread_id, order="asc", after = message_object.id)
		ans = ""
		for r in response:
			ans += f"{r.content[0].text.value}\n"

		return ans


	def submit_message(self, message:str, user_id = False, thread_id = None):
		"""Send a message to the model and get its response
		
		Keyword arguments:
		message -- user message (input)
		user_id -- phone number or telegram id (exclusive uses of tools)
		thread_id -- unique identifier of the conversation
	
		Return: (model_response:str, status_code:str | False)
		"""
	
		try:
			if not thread_id:
				thread_id = self.create_thread()
   
			message_object = self.client.beta.threads.messages.create (
				thread_id = thread_id, 
				role = "user", 
				content = message
			)
			
			run = self.client.beta.threads.runs.create (
				thread_id = thread_id,
				assistant_id = self.ASSISTANT_ID,
			)

			tools_called = []
   
			while True:
				run = self.wait_on_run(run, thread_id)
	
				if run.status == 'completed':
					return self.get_response(message_object, thread_id), tools_called

				tools = run.required_action.submit_tool_outputs.tool_calls
				print(Fore.BLUE + "="*50, f" {len(tools)} tools need to be called! ", Fore.BLUE + "="*50)
				tool_outputs = []

				for tool in tools:
					print("Function Name:", tool.function.name)
					print("Function Arguments:", tool.function.arguments, sep='\n')

					if user_id:
						try:
							response = requests.post (
								url = f"{self.TOOLS_API_URL}/{tool.function.name}/{user_id}", 
								headers = {'Content-Type': 'application/json'}, 
								data = tool.function.arguments,
							)
							print(Fore.GREEN + f"Código de respuesta de la API: {response.status_code}")
							response.raise_for_status()
							tool_ans = str(response.json())
							print("Respuesta de la herramienta:", Fore.BLUE + tool_ans)
	
						except requests.exceptions.RequestException as exc:
							print(Fore.RED + f"Error consumiendo de la API: {exc}")
							tools_called.append("API_ERROR")
							tool_ans = self.error_msg

					else:
						print(Fore.RED + "No se envió user_id")
						tools_called.append("NO_USER_ID")
						tool_ans = self.error_msg

					tool_outputs.append({
						"tool_call_id": tool.id,
						"output": tool_ans,
					})

					if tool_ans != self.error_msg:
						tools_called.append(tool.function.name)

					# end of for loop
				
				try:
					run = self.client.beta.threads.runs.submit_tool_outputs_and_poll (
						thread_id = thread_id,
						run_id = run.id,
						tool_outputs = tool_outputs,
					)
					print("Respuestas de las herramientas enviadas al modelo")
				
				except Exception as exc:
					print(Fore.RED + f"Falló la interacción del modelo con la herramienta: {exc}")
					return self.error_msg, False
				
				# end of while loop

		except Exception as exc:
			print(Fore.RED + f"Falló la respuesta del modelo: {exc}")
			return self.error_msg, False


if __name__ == "__main__":
	args = {'product_name': 'producto'}
	TOOLS_API_URL = os.getenv('TOOLS_API_URL')
	
	response = requests.post (
		url = "http://127.0.0.1:8000/get_products/34936069261", 
		headers = {'Content-Type': 'application/json'}, 
		data = json.dumps(args)
	)
	
	print(response.status_code)
	ans = response.json()
	print(type(ans), ans, sep='\n')
	