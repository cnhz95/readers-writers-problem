from threading import Thread
from threading import Lock
from datetime import datetime
import time

readers = 0
writers = 0
threads = 100
shared_resource = ""

resource_lock = Lock()
reader_lock = Lock()
writer_lock = Lock()
lock = Lock()

def wait():
    time.sleep(1)

class reader(Thread):
    def run(self):
        global readers, shared_resource

        for i in range(threads):
            lock.acquire() # Tvingar varje reader att individuellt fråga om åtkomst
            reader_lock.acquire() # Undviker race-tillstånd med andra readers

            readers += 1 # Skriver upp sig som reader
            if readers == 1: # Om det är första reader, lås resursen
                resource_lock.acquire()
            
            reader_lock.release() # Låt en annan reader modifiera den globala variabeln readers
            lock.release() # Möjliga writers som väntade kan nu få åtkomst

            print("Läser: ", shared_resource)

            reader_lock.acquire()

            readers -= 1 # Anger att den lämnar
            if readers == 0: # Om det är sista reader, lås upp resursen
                resource_lock.release()
            
            reader_lock.release()
            wait() # Tvingar tråden att släppa sin tidslucka

class forward_writer(Thread):
    def run(self):
        global writers, shared_resource

        for i in range(threads):
            writer_lock.acquire() # Undviker race-tillstånd med andra writers

            writers += 1 # Skriver upp sig som writer
            if writers == 1: # Om det är första writer, lås ut readers
                lock.acquire()
            
            writer_lock.release() # Låt en annan writer modifiera den globala variabeln writers
            resource_lock.acquire() # Går in i den kritiska sektionen

            print("Skriver framlänges...")
            shared_resource = datetime.now() # Tidsstämpel

            resource_lock.release()
            writer_lock.acquire()

            writers -= 1 # Anger att den lämnar
            if writers == 0: # Om det är sista writer, låt möjliga readers komma in
                lock.release()
            
            writer_lock.release()
            wait()

class bakward_writer(Thread):
    def run(self):
        global writers, shared_resource

        for i in range(threads):
            writer_lock.acquire()

            writers += 1
            if writers == 1:
                lock.acquire()
            
            writer_lock.release()
            resource_lock.acquire()

            print("Skriver baklänges...")
            shared_resource = str(datetime.now()) [::-1]
            
            resource_lock.release()
            writer_lock.acquire()

            writers -= 1
            if writers == 0:
                lock.release()
            
            writer_lock.release()
            wait()

def main():
    forward_writer().start()
    bakward_writer().start()
    reader().start()
    reader().start()
    reader().start()
    reader().start()

if __name__ == "__main__":
    main()