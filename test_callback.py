import os
import time

from crewai import Agent, Task, Crew, Process, LLM
from src.agent.tools import web_search  # mock import

os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-blabla"

def test_cb(task_output):
    print(f"[{time.strftime('%X')}] CALLBACK TRIGGERED!")

llm = LLM(model="openrouter/meta-llama/llama-3.3-70b-instruct", api_key="sk-or-v1-blabla")

a1 = Agent(role="A1", goal="Goal 1", backstory="b1", llm=llm, allow_delegation=False)
a2 = Agent(role="A2", goal="Goal 2", backstory="b2", llm=llm, allow_delegation=False)

t1 = Task(description="Wait 3 seconds. Say 'A1'", expected_output="A1", agent=a1, async_execution=True)
t2 = Task(description="Wait 1 second. Say 'A2'", expected_output="A2", agent=a2, async_execution=True)
t3 = Task(description="Say 'A3'", expected_output="A3", agent=a1)

crew = Crew(agents=[a1, a2], tasks=[t1, t2, t3], process=Process.sequential, task_callback=test_cb, verbose=True)

print(f"[{time.strftime('%X')}] KICKOFF")
crew.kickoff()
print(f"[{time.strftime('%X')}] KICKOFF DONE")
