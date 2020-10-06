from abc import ABC, abstractmethod
import json


class Model(ABC):

    def to_json(self):
        """Converts the object to json string

        Properties are sorted and indented using 4 spaces.
        """

        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
