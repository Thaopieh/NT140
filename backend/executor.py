import subprocess
import re
from openai import OpenAI

class Executor:
    def __init__(self, api_key):
        self.current_task = None
        self.api_key = api_key
        self.client = OpenAI(base_url="https://api-inference.huggingface.co/v1/", api_key=self.api_key)



    def generate_command(self, task_description, target_ip):
        prompt = f"""
        You are responsible for generating commands given the task assigned by your boss. 
        Follow these guidelines:
        1. Give your command(s) in a format starting and ending with "$" for easy parsing.
        2. If the command is too long or complex, break it down into multiple commands.
        3. Only give a sequence of commands if they are logically connected and follow a sequence that makes sense.
        4. If you want to use Metasploit, please write in this format: "msfconsole: [command]".
        5. Assume that you are operating on a Kali Linux machine. All tools are pre-installed.
        6. The task is: {task_description}
        7. The target IP is: {target_ip}
        
        Generate the command(s).
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
            # print("Raw Response Text:", response_text)  # Debug: Check the raw response from the API

            # Split the response into lines and check for lines that contain a command wrapped in $ symbols
            command_line = None
            for line in response_text.splitlines():
                line = line.strip()  # Strip any extra spaces from each line
                if line.startswith("$") or line.endswith("$"):  # Ensure the command starts and ends with $
                    command_line = line
                    break

            if command_line:
                command_line = command_line.strip("$").strip()  # Remove the $ and extra spaces

            else:
                print("No valid command found.")
                command_line = None            

            return command_line

        except Exception as e:
            print(f"Error generating commands: {e}")
            return []



    def execute_command(self, command):
        """
        Executes a given shell command and captures its output and error messages.
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True
            )
            print(f"Command: {command}")
            
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
            if result.stderr:
                print(f"Error: {result.stderr.strip()}")
            
            return result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            print(f"Error executing command: {e}")
            return None, str(e)

    def run_task(self, task_description, target_ip):
        """
        Generates and executes commands for a given task description and target IP.
        If an error occurs or no command is found, appropriate actions are taken.
        """
        # Generate commands from task description and target IP
        commands = self.generate_command(task_description, target_ip)
        
        # Check if commands are generated
        if not commands:
            print("No commands generated to execute. Marking task as 'trouble'.")
            return "trouble", "No commands generated."

        # Execute the generated commands
        output, error = self.execute_command(commands)

        if error:
            # Handle the error (e.g., "no command found")
            print(f"Error encountered while executing task: {error}")
            return "failed", error

        # If successful, return the output
        print("Task executed successfully.")
        return "completed", output


    def fetch_task_from_planner(self, planner):
        # Debugging: Check the planner's tasks
        print("Fetching tasks from planner...")
        print("Total tasks:", len(planner.tasks))
        
        for task in planner.tasks:
            print(f"Checking Task: {task.id}, Status: {task.status}")
            if task.status == "to-do":
                self.current_task = task
                print(f"Found task: {task.id} with status 'to-do'")
                return True
            
            for subtask in task.subtasks:
                print(f"Checking Subtask: {subtask.id}, Status: {subtask.status}")
                if subtask.status == "to-do":
                    self.current_task = subtask
                    print(f"Found subtask: {subtask.id} with status 'to-do'")
                    return True
        print("No tasks with status 'to-do' found.")
        return False
