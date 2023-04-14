import json
import os
from pathlib import Path
from github_client import GithubClient
from config import GH_ACCESS_TOKEN, OPENAI_KEY
import structlog

from pipeline import GithubEventPrompter, SummaryPrompter

logger = structlog.get_logger()

# set this to a selected date between today and a couple of days back (limited by GH API pagination limit)
DATE = os.getenv("DATE", "2023-04-13")
USERNAME = os.getenv("USERNAME", "arzelaascoii")

github_client = GithubClient(GH_ACCESS_TOKEN)
prompter_events = GithubEventPrompter(OPENAI_KEY, Path("./prompts/events.txt"))
prompter_summaries = SummaryPrompter(OPENAI_KEY, Path("./prompts/summary.txt"))


def generate_events():
    results = {}
    events = github_client.get_events(USERNAME, DATE)
    for event, payload in events.items():
        result = prompter_events.query(event=event, input=json.dumps(payload))
        results[event] = {
            "input": payload,
            "output": result[0],
        }
        logger.info("Updating result example  with event ", event=event)
        # write strigified results to file 'DATE.json' in /examples
        with open(f"./examples/{DATE}.json", "w") as f:
            f.write(json.dumps(results, indent=4))
    logger.info("Done generating event summaries", date=DATE)


def create_summary():
    # load events from file 'DATE.json' in /examples
    with open(f"./examples/{DATE}.json", "rb") as f:
        event_dict = json.loads(f.read())
    events = ""
    for key, value in event_dict.items():
        entry = f"# {key} \n {value['output']}"
        events += f"\n\n{entry}"

    return prompter_summaries.query(
        events=events,
    )


# fetch events from github and summarize them
generate_events()

# create summary (EOD message)
eod_message = create_summary()
print(eod_message[0])
