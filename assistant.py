from dotenv import load_dotenv
from openai import OpenAI
import requests
import time, json, os

load_dotenv()


def pretty_print(messages):
	print("# Messages")
	for m in messages:
		print(f"{m.role}: {m.content[0].text.value}")
	print()
	  
		  
class Assistant():
	"""
    Assistant class to manage OpenAI Assistant
    
    Attributes:
        name (str): The name of the assistant.
        assistant_id (str): The unique identifier for the assistant.
        end_point_tools (str): API endpoint that generates responses from external tools
    """
    
	def __init__(self, name, assistant_id, end_point_tools):
		self.client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))
		self.name = name
		self.assistant_id = assistant_id
		self.end_point_tools = end_point_tools
	
	
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
	
		Return: model response
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
				assistant_id = self.assistant_id,
			)

			status = "NO_TOOL_CALLS"
   
			while True:
				run = self.wait_on_run(run, thread_id)
    
				if run.status == 'completed':
					return self.get_response(message_object, thread_id), status

				else:
					if not user_id:
						print("No se envió user_id")
						return "Ha ocurrido un error, por favor realice la consulta más tarde.", False
      
					print("Tool calls!")
					try:
						tool = run.required_action.submit_tool_outputs.tool_calls[0]
						print("Function Name:", tool.function.name)
						print(f"Function Arguments: {tool.function.arguments}")

						try:
							response = requests.get(f"{self.end_point_tools}/{tool.function.name}/{tool.function.arguments}")
							response.raise_for_status()
							tool_ans = response.json()
       
						except requests.exceptions.RequestException as exc:
							print(f"Error consumiendo de la API: {exc}")
			
						run = self.client.beta.threads.runs.submit_tool_outputs_and_poll(
							thread_id = thread_id,
							run_id = run.id,
							tool_outputs = [{
								"tool_call_id": tool.id,
								"output": tool_ans,
							}],
						)
						print(f"Respuesta de la herramienta enviada al modelo: {tool_ans}")
						status = tool.function.name
			
					except Exception as exc:
						print(f"Falló la respuesta de la herramienta: {exc}")
						return "Ha ocurrido un error, por favor realice la consulta más tarde.", False
   
		except Exception as exc:
			print(f"Falló la respuesta del modelo: {exc}")
			return "Ha ocurrido un error, por favor realice la consulta más tarde.", False


if __name__ == "__main__":
    args = {}
    response = requests.get(f"http://127.0.0.1:8000/get_product_details/producto")
    print(response.json())
    