class Complaint:
    def __init__(
        self,
        author=None,
        problem=None,
        description=None,
        date=None,
        time=None,
        location=None
    ):
        self.author = author
        self.problem = problem
        self.description = description
        self.date = date
        self.time = time
        self.location = location
        self.status = "Pending"  # Default status for new complaints

    def set_status(self, status):
        valid_statuses = ["Pending", "In Progress", "Resolved", "Closed"]
        if status in valid_statuses:
            self.status = status
        else:
            raise ValueError(
                f"Invalid status: {status}. Valid statuses are: {valid_statuses}"
            )

    def is_valid(self):
        return all(
            [
                self.author,
                self.problem,
                self.description,
                self.date,
                self.time,
                self.location,
                self.status
            ]
        )

    def __str__(self):
        return f"Complaint by {self.author} on {self.date} at {self.time}: {self.problem} - {self.description} (Location: {self.location}), Current Status: {self.status}"

    def __repr__(self):
        return self.__str__()
