import time

class LocalHeartbeat:
    heartbeat = None

    @classmethod
    def set_heartbeat(cls, value):
        cls.heartbeat = value

    @classmethod
    def get_heartbeat(cls):
        return cls.heartbeat
    
    @classmethod
    def set_heartbeat_now(cls):
        cls.heartbeat = time.time()
    
    @classmethod
    def check_heartbeat_outdate(cls):
        if cls.heartbeat is None:
            return False
        # 20min is outdate
        if time.time() - cls.heartbeat > 1200:
            return True

LocalHeartbeat.set_heartbeat_now()
