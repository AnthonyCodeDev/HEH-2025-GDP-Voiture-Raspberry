from abc import ABC,abstractmethod
class Imotor(ABC):
    
    @abstractmethod
    def read_data():
        pass

    @abstractmethod
    def display_data():
        pass