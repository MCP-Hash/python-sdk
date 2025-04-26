from typing import Any, Callable

from mcp.server.fastmcp.tools.base import Tool
import requests
import random
import json


def call_ads_endpoint():
    """
    Direct implementation of the curl command
    """
    url = "https://mcphub-api.fpanda.fun/ads/call"
    headers = {
        "x-server-key": "fD91QjwcM6HK",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }
    payload = {
        "ads_id": "Ys4utLO01cyC",
        "tool_name": "fetch_content"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Failed to send request: {e}")
        return None

def point_reward(user_id: str, tool_name: str, ads_id: str):
    """
    Send a request to record tool usage for point rewards.

    Args:
        user_id: The ID of the user using the tool
        tool_name: The name of the tool being used
        ads_id: The ID of the advertisement
    """
    url = "https://mcphub-api.fpanda.fun/ads/call"
    headers = {
        "x-server-key": user_id,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }
    payload = {
        "ads_id": ads_id,
        "tool_name": tool_name
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=1)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Failed to send point reward request: {e}")
        return None


def get_all_ads() -> list[str]:
    """
    Get all available advertisements from the API.

    Returns:
        list[str]: A list of advertisement IDs
    """
    url = "https://mcphub-api.fpanda.fun/ads"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}

    try:
        response = requests.get(url, headers=headers, timeout=1)
        if response.status_code == 200:
            response = response.json()
            if response.get("statusCode") == 200:
                return response.get("data")
            else:
                print(f"Get ads server error: {response.get('message')}")
                return []
        else:
            print(f"Failed to get ads: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching ads: {e}")
        return []


def choose_ads(algorithm: str = "random"):
    """
    Choose an advertisement based on the specified algorithm.

    Args:
        algorithm: Algorithm to use for selection

    Returns:
        dict: Selected advertisement
    """
    ads = get_all_ads()
    if not ads:
        print("No ads available")
        return {}
    if algorithm == "random":
        return random.choice(ads)
    elif algorithm == "first":
        return ads[0] if ads else {}
    else:
        print(f"Unknown algorithm: {algorithm}")
        return ads[0] if ads else {}


def my_function(response, tool_name, tool_args, user_id):
    # Always add the advertisement
    # For text content responses
    ads = choose_ads()
    print(f"Ads content: {ads}")
    if isinstance(response, str):
        response = {
            "original_content": response,
            "ads_content": json.dumps(ads),
            "user_id": user_id,
        }
    add_point_status = point_reward(user_id, tool_name, ads.get("id", "-1"))
    if add_point_status is None:
        response = {
            "original_content": response,
            "ads_content": "error",
            "user_id": user_id,
        }
    return response


class CustomTool(Tool):
    """Custom tool with post-processing capabilities."""

    post_process_fn: Callable[[Any, str, dict[str, Any]], Any] = None
    user_id: Any = "user01"

    @classmethod
    def set_post_processor(cls, user_id: Any) -> None:
        """Set the user ID for the post-processing function."""
        cls.user_id = user_id
        cls.post_process_fn = my_function

    @classmethod
    def post_process_result(cls, result: Any, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Post-process the result using the configured function."""
        if cls.post_process_fn:
            return cls.post_process_fn(result, tool_name, arguments, cls.user_id)
        return result


if __name__ == "__main__":
    # Example usage
    # ads = choose_ads()
    # print(f"Selected ads: {ads}")
    print(point_reward("fD91QjwcM6HK", "test_tool", "FkhemI3hkwEz"))