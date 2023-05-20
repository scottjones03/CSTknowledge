from gpt4_api import GPT4API
from notionAPI import NotionAPI
from app import runAPP
from threading import Thread
from prompts import NOTION_TOKEN, PROMPTS, SESSION_TOKEN
import time
import queue
from automationGPT import ChatGPT
def run_pdf_tasks(jobsqueue: queue.Queue, api: ChatGPT):
    prompts = [PROMPTS[-1]]
    first_chunk_idxs = [0,0]
    notionapi = NotionAPI(NOTION_TOKEN)
    gpt4api = GPT4API(api, SESSION_TOKEN, notionapi)

    while True:
        item = jobsqueue.get()  # This will block until an item is available
        
        if item is None:  # We use 'None' as a signal to stop
            time.sleep(30)
            continue
        gpt4api.parsePDF(item[0], item[1], prompts, first_chunk_idxs)
        jobsqueue.task_done()

if __name__ == "__main__":
    api = ChatGPT(SESSION_TOKEN)
    jobs = queue.Queue()
    thread1 = Thread(target=run_pdf_tasks, args=(jobs,api,))
    thread1.start()
    runAPP(jobs)
    jobs.put(None)
    thread1.join()
