from datetime import datetime
from time import time
from queue import Queue, Full


class Task():
    '''Data structure representing scheduled tasks with underlying functions,'''

    def __init__(self, function, scheduled_time, args=[], kwargs={}, id=None):
        self.id = id
        self.func = function
        self.args = args
        self.kwargs = kwargs
        self.time = scheduled_time
        self.created = datetime.now()

    def __repr__(self):
        return f"[{self.time.strftime('%Y-%m-%d %H:%M:%S')}] {self.id}:{self.func.__name__}"

    def __str__(self):
        return f"[{self.time.strftime('%Y-%m-%d %H:%M:%S')}] {self.func.__name__}"

    def execute(self):
        self.func(*self.args, **self.kwargs)


class TaskQueue(Queue):
    '''Queue which sorts items of type(Task) by scheduled date.'''

    def __init__(self, maxsize=0):
        super().__init__(maxsize)

    def put(self, task, block=True, timeout=None, highest_priority=False):
        with self.not_full:
            if self.maxsize > 0:
                if not block:
                    if self._qsize() >= self.maxsize:
                        raise Full
                elif timeout is None:
                    while self._qsize() >= self.maxsize:
                        self.not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = time() + timeout
                    while self._qsize() >= self.maxsize:
                        remaining = endtime - time()
                        if remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)
            self._put(task, highest_priority=highest_priority)
            self.unfinished_tasks += 1
            self.not_empty.notify()

    def remove(self, id):
        '''Remove and return task with id. Raises ValueError if not found.'''
        with self.not_empty:
            for i, task in enumerate(self.queue):
                if task.id == id:
                    return self.queue.pop(i)
            raise LookupError(f"Task with id {id} not found in queue")

    def pop(self, i):
        '''Delete task at index i.'''
        with self.not_empty:
            self.queue.pop(i)

    def peek(self, i=0):
        '''Returns task at index i in queue without modifying.'''
        with self.not_empty:
            return self.queue[i]

    def _init(self, maxsize):
        self.queue = []

    def _put(self, task, highest_priority=False):
        '''Put task at appropiate queue position determined by scheduled date'''
        try:
            if highest_priority:
                self.queue.insert(0, task)
            elif task.time > self.queue[-1].time:
                self.queue.append(task)
            else:
                for i, queued in enumerate(self.queue):
                    if task.time <= queued.time:
                        self.queue.insert(i, task)
                        break
        except IndexError:
            self.queue.append(task)

    def _get(self):
        return self.queue.pop(0)
