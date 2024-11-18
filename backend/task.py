class Task:
    def __init__(self, id : str, description, status ="to-do", subtasks= None):
        self.id = id
        self.description = description
        self.status = status
        self.subtasks = subtasks if subtasks else []
                                            
    def update_status(self, new_status, result=None):
        self.status = new_status
        self.result = result
        
    def add_subtask(self, subtask):
        self.subtasks.append(subtask)
        
    def __str__(self) -> str:
        return f"Task {self.id}: {self.description}, Status: {self.status}"