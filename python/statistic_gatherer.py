from dataclasses import dataclass
from typing import List, Dict, Any
from api import Api
from os import path
import json
from datetime import datetime
from threading import Event, Thread
import matplotlib.pyplot as plt

@dataclass
class Statistic:
    timestamp: float
    users_inside_facility: int
    
    """
    Create a suitable dictionary that represents this class.
    Made because JSON couldn't parse this class by itself.
    """
    def to_json(self) -> Dict[str, Any]:
        return {"timestamp": self.timestamp, "users_inside_facility": self.users_inside_facility}
    
    
class Gatherer:
    
    """
    Initialize this class with an API, a list of statistics, the filepath for the statistics file and a stop event to close the loop.
    """
    def __init__(self, api: Api, statistics: List[Statistic], filepath: str, table_name: str) -> None:
        self.api = api
        self.statistics = statistics
        self.filepath = filepath
        self.stop_event = Event()
        self.table_name = table_name
    
    """
    Find the file "statistics". If it doesn't exist, create an instance of the "Gatherer" class with an empty data field.
    If found, read in the file contents as JSON and create an instance of the "Gatherer" class with the file's contents as its data field.
    """
    @staticmethod
    def from_file(api: Api, filepath: str, table_name: str) -> "Gatherer":
        if not path.exists(filepath):
            return Gatherer(api, [], filepath, table_name)
        with open(filepath, "r") as fp:
            data = [Statistic(x["timestamp"], x["users_inside_facility"]) for x in json.load(fp)]
            return Gatherer(api, data, filepath, table_name)
    
    """
    Open the file found previously and dump our current list of statistics into it, overwriting the file in the process.
    """
    def save_statistics(self) -> None:
        with open(self.filepath, "w") as fp:
            json.dump([x.to_json() for x in self.statistics], fp)
    
    """
    Get the list of users from the online database. If none are present, return.
    If there are users present, check whether they are inside the facility or not. If they are, increment a counter.
    Once we counted all the users who are present,
    create an instance of the "Statistics" class where we set the current time and the number of users who are present at this time.
    """
    def create_statistic(self) -> None:
        users = self.api.get_users(self.table_name)
        if len(users) == 0:
            return
        
        active_users = 0
        for user in users:
            if user["inside_facility"]:
                active_users += 1
        
        self.statistics.append(Statistic(datetime.now().timestamp(), active_users))
                  
    """
    Every 30 minutes or on the hour, get the statistics from the facility and save them to a file.
    Assign this loop to its own thread so it allows the rest of the program to keep running.
    """   
    def __loop(self) -> None:
        while not self.stop_event.is_set():
            now = datetime.now()
            # Run the loop on every 30 minute or every hour.
            # Set "next_minute" to 30 if the time currently is less than 30, else set it to 0.
            next_minute = 30 if now.minute < 30 else 0
            # Set "next_hour" to the current hour + 1 if the next_minute is 0, i.e. we haven't gone to the next hour, else stay within the hour.
            next_hour = now.hour + 1 if next_minute == 0 else now.hour
            # Subtract the current time from the next 30 minute interval.
            td = datetime.now().replace(hour=next_hour, minute=next_minute, second=0, microsecond=0) - now
            # Wait the previously found time in seconds.
            self.stop_event.wait(td.total_seconds())
            
            # If the program stopped due to us quitting, quit the function to prevent statistic gathering.
            if self.stop_event.is_set():
                return
            
            self.create_statistic()
            self.save_statistics()
            
    """
    Start the loop by clearing the "stop_event" Event. The statistic gathering thread gathers statistics on its own, individual CPU thread.
    """
    def start(self) -> None:
        self.stop_event.clear()
        #Create a new thread for the __loop method.
        #This allows the program to keep running while the __loop method keeps running.
        self.thread = Thread(target=self.__loop)
        #Name the thread so that it can be followed.
        self.thread.name = "Statistic Gathering Thread"
        self.thread.start()

    """
    Stop the loop by setting the "stop_event" Event.
    """
    def stop(self) -> None:
        self.stop_event.set()
        # Do another save just in case the program didn't save the first time around.
        self.save_statistics()
                
    """
    Generate the plot from the statistics we found.
    """
    def generate_plot(self) -> None:
        # x axis values
        x = [datetime.fromtimestamp(x.timestamp) for x in self.statistics]
        # corresponding y axis values
        y = [y.users_inside_facility for y in self.statistics]

        # plotting the points 
        plt.plot(x, y)

        # naming the x axis
        plt.xlabel('Time')
        # naming the y axis
        plt.ylabel('Customers Present in Facility')

        # giving a title to my graph
        plt.title('Customer Presence in Facility Over Time')

        # function to show the plot
        plt.show()

if __name__ == "__main__":
    def main() -> None:
        datastore = path.join(path.dirname(path.dirname(__file__)), "data")
        gatherer = Gatherer.from_file(None, path.join(datastore, "statistics"), None)
        gatherer.generate_plot()
        
    main()
