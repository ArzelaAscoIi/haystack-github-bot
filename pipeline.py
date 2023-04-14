from pathlib import Path
from haystack.nodes import PromptNode, PromptTemplate


def get_prompt(input: str, prompt_template: Path) -> str:
    prompt = prompt_template.read_text()
    return prompt.format(input=input)


class GithubEventPrompter:
    """
    This class is responsible for querying the OpenAI API for a prompt
    based on a Github event.
    """

    def __init__(self, openai_key: str, prompt_template: Path):
        self._prompt_node = PromptNode(
            model_name_or_path="text-davinci-003", api_key=openai_key, max_length=1000
        )
        self._github_template = PromptTemplate(
            name="github-events", prompt_text=prompt_template.read_text()
        )

    def query(self, event: str, input: str, username: str) -> str:
        result = self._prompt_node.prompt(
            prompt_template=self._github_template,
            input=input,
            event=event,
            username=username,
        )
        return result


class SummaryPrompter:
    """
    This class is responsible for querying the OpenAI API for a prompt
    based on a Github event.
    """

    def __init__(self, openai_key: str, prompt_template: Path):
        self._prompt_node = PromptNode(
            model_name_or_path="text-davinci-003", api_key=openai_key, max_length=1000
        )
        self._summary_template = PromptTemplate(
            name="github-summary", prompt_text=prompt_template.read_text()
        )

    def query(self, events: str, username: str) -> str:
        result = self._prompt_node.prompt(
            prompt_template=self._summary_template, events=events, username=username
        )
        return result
