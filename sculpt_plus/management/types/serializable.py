import pickle
import shelve


class Serializable(object):
    @classmethod
    def from_pickle(cls, filepath: str):
        with open(filepath, 'rb') as f:
            object: cls = pickle.load(f)
        return object
    
    def write_to_pickle(self, filepath: str) -> None:
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    def write_to_shelve(self, db: shelve.DbfilenameShelf) -> None:
        db[self.id] = self
