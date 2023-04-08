import fnmatch
import httpx
from typing import Any, Dict, List
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)
FORCE_REMOVE = ["_links"]

TO_REMOVE = [
    "id",
    "gravatar_id",
    "gravatar_url",
    "avatar_url",
    "node_id",
    "html_url",
    "followers_url",
    "following_url",
    "repos_url",
    "events_url",
    "received_events_url",
    "site_admin",
    "display_login",
    "push_id",
    "repository_id",
    "head",
    "before",
    "sha",
    "subscriptions_url",
    "organizations_url",
    "starred_url",
    "gists_url",
    "languages_url",
    "ssh_url",
    "_links",
    "notifications_url",
    "has_wiki",
    "has_downloads",
    "has_pages",
    "has_projects",
    "has_issues",
    "forks_url",
    "forks_count",
    "forks",
    "fork",
    "private",
    "language",
    "maintainer_can_modify",
    "rebaseable",
    "mergeable_state",
    "homepage",
    "web_commit_signoff_required",
    "public",
    "disabled",
    "watchers_count",
    "is_template",
    "watchers",
    "archived",
    "license",
    "visibility",
    "has_discussions",
    "allow_forking",
    "stargazers_count",
    "active_lock_reason",
    "avatar_user_actor",
    "locked",
    "url",  # might be important
    "href",  # might be important
]

TO_REMOVE_WILDCARD = ["*url*", "*sha*", "*id*"]


def remove_fields_from_dict(
    input_dict: Dict[str, Any], fields_to_remove: List[str]
) -> Dict[str, Any]:
    output_dict = {}
    for key, value in input_dict.items():
        if key in FORCE_REMOVE:
            continue

        if isinstance(value, dict):
            new_dict = remove_fields_from_dict(value, fields_to_remove)
            if new_dict:
                output_dict[key] = new_dict
        elif isinstance(value, list):
            output_dict[key] = [
                remove_fields_from_dict(item, fields_to_remove)
                for item in value
                if isinstance(item, dict)
            ]
        elif key not in fields_to_remove and not any(
            fnmatch.fnmatch(key, pattern) for pattern in TO_REMOVE_WILDCARD
        ):
            output_dict[key] = value
    return output_dict


class GithubClient:
    def __init__(self, token: str) -> None:
        self.token = token
        self.headers = {"Authorization": f"token {token}"}

    @staticmethod
    def _group_by_event_type(
        events: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        result = {}
        for event in events:
            event_type = event["type"]
            if event_type not in result:
                result[event_type] = []
            result[event_type].append(event)
        return result

    def get_events(self, username: str, date: str) -> List[Dict[str, Any]]:

        page = 1
        done = False

        results = []
        while not done:
            if page > 10:
                raise Exception("Please select a date closer to today.")
            logger.info("Fetching page", page=page, username=username, date=date)
            url = f"https://api.github.com/users/{username}/events?per_page=100&page={page}"
            response = httpx.get(url, headers=self.headers)
            response.raise_for_status()
            events = response.json()

            # check if last event is older than date
            done = datetime.strptime(
                events[-1]["created_at"], "%Y-%m-%dT%H:%M:%SZ"
            ) < datetime.fromisoformat(date)

            results += [remove_fields_from_dict(p, TO_REMOVE) for p in events]
            page += 1

        return self._group_by_event_type(
            [
                r
                for r in results
                if datetime.strptime(r["created_at"], "%Y-%m-%dT%H:%M:%SZ").date()
                == datetime.fromisoformat(date).date()
            ]
        )

    def get_created_issues(self, username: str, date: str) -> List[str]:
        url = f"https://api.github.com/search/issues?q=author:{username}+created:{date}+type:issue"
        response = httpx.get(url, headers=self.headers)
        response.raise_for_status()
        issues = response.json()["items"]
        return issues

    def get_comments(self, username: str, date: str) -> List[Dict[str, Any]]:
        url = f"https://api.github.com/search/issues?q=commenter:{username}+updated:{date}+type:issue"
        response = httpx.get(url, headers=self.headers)
        response.raise_for_status()
        issues = response.json()["items"]

        result = []
        for issue in issues:
            issue_comment = {"issue": issue, "comments": []}
            issue_comment["comments"] = self._get_issue_comments(issue["url"], date)
            result.append(issue_comment)
        return result

    def _get_issue_comments(self, issue_url: str, date: str) -> List[str]:
        url = f"{issue_url}/comments"
        response = httpx.get(url, headers=self.headers)
        response.raise_for_status()
        comments = response.json()
        filtered_comments = [
            comment for comment in comments if comment["created_at"].startswith(date)
        ]

        return [
            self._get_comment_content(filtered_comment["url"])
            for filtered_comment in filtered_comments
        ]

    def _get_comment_content(self, comment_url: str) -> str:
        response = httpx.get(comment_url, headers=self.headers)
        response.raise_for_status()
        comment = response.json()
        return comment["body"]
