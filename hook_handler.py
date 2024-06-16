from abc import ABC
from typing import Callable
import time
from datetime import datetime, timedelta


class AbstractHookHandler(ABC):
    """
    This class is an abstract class that shows the basic performances of any hook handler.
    the basic hook handler has:
        1) the event name that it should handle
        2) a dict of cases in the form of {"the cause for logging" : function(data :dict)->bool should log}
        3) an alert function that performs the basic alerts.
        4) optional - further logger provided by outside object that will further save the data somewhere
    """

    def __init__(self, event_name: str,outside_logger=None):
        self.event_name = event_name
        self.cases: {str: Callable[[dict], bool]} = dict()
        self.logger=outside_logger

        # this section checks if the logger actually can log. otherwise it will throw an error.
        # the developer must make sure the log function is log(*args, **kwargs)
        if self.logger is not None:
            if not hasattr(self.logger, 'log') or not callable(getattr(self.logger, 'log')):
                raise ValueError("Logger must have a callable 'log' method.")

    def alert(self, causes: []):
        """
        The alert function will show in the terminal the anomaly and all its causes in the form of
        'time of anomaly' causes : 1).. 2)... 3)...
        will also call the logger to further log these causes if the logger is not None
        :param causes: a list of all the causes for the anomaly
        """
        timestr = time.strftime("%Y%m%d-%H%M%S")
        result = f"at {timestr} got anomaly due to : "
        for i in range(len(causes)):
            result += f"{i + 1}) {causes[i]} "
        print(result)

        if self.logger is not None:
            self.logger.log(self.event_name, causes)

    def check_post(self, event, data):
        """
        goes through the data provided by the post and check if they should be logged as anomalies.
        if there is any cause for logging it save it and in the end send the alert function all the causes.
        :param event: name of the event, just in case
        :param data: the data from the push
        """
        if event != self.event_name:
            return
        causes = []
        for cause, case in self.cases.items():
            if case(data):
                causes.append(cause)
        if causes:
            self.alert(causes)


class PushHandler(AbstractHookHandler):
    def __init__(self, outside_logger=None):
        super().__init__("push", outside_logger)
        self.cases["pushing code between 14:00-16:00"] = self.is_push_between_14_and_16

    def is_push_between_14_and_16(self, data: dict) -> bool:
        """
        uses the repository json provided along with the pushed_at epoch timestamp to calculate when was the commit pushed.
        :param data: json data from the web hook
        :return: True if there is an anomaly, False otherwise
        """
        repo = data.get('repository',dict())
        push_timestamp = repo.get('pushed_at',0)
        if push_timestamp ==0:
            return False # there was an error

        # Convert epoch timestamp to datetime
        dt = datetime.fromtimestamp(push_timestamp)

        # Extract the date part and set the time to 14:00 and 16:00
        start_time = dt.replace(hour=14, minute=0, second=0, microsecond=0)
        end_time = dt.replace(hour=16, minute=0, second=0, microsecond=0)

        # Check if the datetime falls between 14:00 and 16:00
        return start_time <= dt < end_time
