import pandas as pd
from datetime import datetime
import os.path


class BasicLogger:
    """
    A very basic logger, logs the event name, the causes for anomaly as presented and basic data like:
    time, repository_name pusher_name team_name
    if any data point is not available, it will be filled with "None"
    """

    def __init__(self, file_name):
        abs_path = os.path.abspath(file_name)
        self.file_name = abs_path
        self.columns = ["event", "time", "causes", "repository_name", "pusher_name", "team_name"]
        self.df = pd.read_csv(abs_path) if os.path.exists(abs_path) else pd.DataFrame(columns=self.columns)

    def log(self, event_name: str, causes: [str], data):
        team = data.get('team', dict())
        team_name = "None" if "name" not in team else team["name"]
        repo = data.get("repository", dict())
        repo_name = repo.get("full_name", "None")
        pusher = data.get("pusher", dict())
        pusher_name = pusher.get("name", "None")
        time = datetime.now().timestamp()
        self.df.loc[len(self.df)] = [event_name, time, causes, repo_name, pusher_name, team_name]
        self.df.to_csv(self.file_name)
