# Github EOD BOT 
ALLM powered github end-of-day bot.

Powered by [haystack](https://haystack.deepset.ai/) and [OpenAI](https://openai.com/)

<img src="img/haystack.png" width="200">
<img src="img/openai.jpeg" width="200">

This github bot crawls your github activity of a selected day, groups the events by action (Push, Pull Request, Issue, etc.) and sends you a summary of your activity in natural language. This message can be used as EOD(End of Day) report in your slack channel. 

> This bot should help me to close my laptop and be happy about the work I've done on that day. Hopefully it will help you too.

A summary can look like this:
<img src="img/summary.png" width="800">

This example of a haystack promptnode uses two templates to generate a summary of actions. The [first template](/prompts/events.txt) is used to generate a summary per event type from github. The [second template](/prompts/summary.txt) is used to generate the final summary of all events.

## How to use it
### Installation 
1. Clone this repository
2. Install the dependencies with `pip3 install -r requirements.txt`. This installs haystack and some other required packages to fetch the data from github.
3. Create a new github access token.
4. Create a OpenAI API key.

### Run 
Run the bot with 
```sh 
GH_ACCESS_TOKEN=<your-token> OPENAI_KEY=<openai-key> python3 main.py
```




