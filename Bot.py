import threading
from time import time
from TaskQueue import TaskQueue


class Bot(threading.Thread):
    '''Producer/Consumer Bot utilising TaskQueue.'''

    def __init__(self, id, buffer=5):
        threading.Thread.__init__(self)
        self.id = id
        self.daemon = True
        self.buffer_time = buffer

        self.q = TaskQueue()
        self.last_action_time = 0
        self.new_task = threading.Event()
        self.task_done = threading.Event()

    def schedule(self, tasks):
        '''Schedule a new task by starting an independent thread.
        - tasks (list): tasks to be scheduled.'''
        t = threading.Thread(target=self._add_tasks, args=(tasks,), daemon=True)
        t.start()

    def _add_tasks(self, tasks):
        '''Adding tasks from a list to task queue and waiting if queue is full.'''
        for task in tasks:
            if self.q.full():
                print('Producer: Queue full - sleeping')
                self.task_done.wait()
                print('Producer: Queue not full now, adding task..')
                self.task_done.clear()
            self.q.put(task)
            print(f'Producer: Scheduled {task}')
            self.new_task.set()

    def run(self):
        '''Runs the thread which executes tasks.
        - stay idle until scheduled task time'''
        while True:
            if self.q.empty():
                self.new_task.wait()
                print('Bot: Woke up')
                self.new_task.clear()
            task = self._idle()
            print(f'Bot executing {task}')
            task.execute()
            self.last_action_time = time()
            self.q.task_done()
            self.task_done.set()

    def _idle(self):
        '''Wait for next scheduled task in queue.
        - If tasks are added to queue, check next task again'''
        next_task = self.q.peek()
        time_until = self._time_until(next_task)
        print(f'Bot: Time until next task {time_until}')
        flag = self.new_task.wait(timeout=time_until)
        if flag:
            print('Bot: New task added to queue - checking next task')
            self.new_task.clear()
            return self._idle()
        else:
            return self.q.get()

    def _time_until(self, task):
        '''Calculate time in seconds until scheduled task.
        - Convert task.time datetime to epoch time
        - Add buffer delay if scheduled task is too close to last action time'''
        now = time()
        time_since = now - self.last_action_time
        scheduled = int(task.time.strftime('%s'))
        time_until = scheduled - now
        if time_until < 0:
            if time_since < self.buffer_time:
                time_until = time_until + self.buffer_time
            else:
                time_until = 0
        return time_until
