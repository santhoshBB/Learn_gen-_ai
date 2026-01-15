
from rq import Queue
from redis import Redis

conn = Redis(host="localhost", port=6379, db=0)
queue = Queue(connection=conn)

