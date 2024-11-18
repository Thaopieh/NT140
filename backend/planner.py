from openai import OpenAI
from task import Task

class Planner:
    def __init__(self, target_ip, api_key):
        self.tasks = []
        self.target_ip = target_ip
        self.api_key = api_key
        self.client = OpenAI(base_url="https://api-inference.huggingface.co/v1/", api_key=self.api_key)
    
    def create_task(self, id, description, status="to-do"):
        # Ensure the id is treated as a string
        id = str(id)
        return self.tasks.append(Task(id, description, status))
        
    def get_task_by_id(self, task_id):
        # Ensure the task_id is treated as a string
        task_id = str(task_id)
        return next((task for task in self.tasks if task.id == task_id), None)
    
    def update_task(self, task_id, status, result=None):
        task = self.get_task_by_id(task_id)
        if task:
            task.update_status(status, result)
    
    def assign_subtask(self, task_id, subtasks):
        task = self.get_task_by_id(task_id)
        if task:
            for subtask in subtasks:
                task.add_subtask(subtask)
    
    def display_task_plan(self):
        for task in self.tasks:
            print(task)
            for subtask in task.subtasks:
                print(f"  - {subtask}")
    
    def create_attack_plan(self):
        prompt = f"""
        As a penetration testing assistant, you are responsible for generating an attack plan. 
        Please follow these guidelines:
        1. Organize tasks in a hierarchical sequence (e.g., Task 1, Task 1.1, Task 1.1.1).
        2. Ensure tasks cover all essential phases of penetration testing:
        - Reconnaissance
        - Scanning
        - Vulnerability Assessment
        - Exploitation
        3. Include a description for each task and ensure it is actionable.
        4. Assign a status to each task: "to-do" by default.
        5. If needed, create subtasks under main tasks to provide detailed steps.
        6. For each task and subtask, include the target system's IP address: {self.target_ip} in the task description.

        Output the attack plan as a JSON array, where each task is represented as:
        {{
            "id": "<task_id>",
            "description": "<task_description> - Target IP: {self.target_ip}",
            "status": "to-do",
            "subtasks": [
                {{
                    "id": "<subtask_id>",
                    "description": "<subtask_description> - Target IP: {self.target_ip}",
                    "status": "to-do"
                }}
            ]
        }}

        Now, generate the attack plan for the target IP: {self.target_ip}.
        """
        message = [{"role": "user", "content": prompt}]
        try:
            stream = self.client.chat.completions.create(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                messages=message,
                max_tokens=1024,
                stream=True,
            )
            response_text = "".join(chunk.choices[0].delta.content for chunk in stream)

            # Print out the raw response for debugging
            # print("Raw response text:", response_text)

            # Try to parse the response as JSON
            import json
            attack_plan = json.loads(response_text)

            # Create tasks in the Planner from the API response
            for task in attack_plan:
                # Ensure task id is treated as a string
                main_task = Task(str(task["id"]), task["description"], task["status"])
                for subtask in task.get("subtasks", []):
                    # Ensure subtask id is treated as a string
                    sub_task = Task(str(subtask["id"]), subtask["description"], subtask["status"])
                    main_task.add_subtask(sub_task)
                self.tasks.append(main_task)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Invalid JSON response: {response_text}")
            return []
        except Exception as e:
            print(f"Error generating attack plan: {e}")
            return []
