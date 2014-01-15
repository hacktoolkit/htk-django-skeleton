import random

class MasterSlaveRouter(object):
    """A router that sets up a simple master/slave configuration
    """

    def __init__(self):
        self.db_master = 'master'
        self.db_list = ['master', 'slave1', 'slave2']
        self.db_slaves = ['slave1', 'slave2']

    def db_for_read(self, model, **hints):
        """Point all read operations to master
        """
        # If desired, can point all read operations to a random slave
        #db = random.choice(self.db_slaves)
        db = self.db_master
        return db

    def db_for_write(self, model, **hints):
        """Point all write operations to the master
        """
        db = self.db_master
        return db

    def allow_relation(self, obj1, obj2, **hints):
        """Allow any relation between two objects in the db pool
        """
        if obj1._state.db in self.db_list and obj2._state.db in self.db_list:
            return True
        return None

    def allow_syncdb(self, db, model):
        """Explicitly put all models on all databases.
        """
        return True
