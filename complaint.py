class Complaint():
    def __init__(self, location, author, problem, description, date, time):
        self.author = author
        self.problem = problem
        self.description = description
        self.date = date
        self.time = time
        self.location = location
    
    def __str__(self):
        return f"Complaint by {self.author} on {self.date} at {self.time}: {self.problem} - {self.description} (Location: {self.location})"
    def __repr__(self):
        return self.__str__()