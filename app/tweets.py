import http.client
import urllib.parse
import json
import re # to remove escape sequences we get from json file
# Threshold: 500 Requests / MO
def twt__1(company_name: str):
    """
    Fetches the latest tweets from Twitter API based on the query.
    """
    # Define the connection to the Twitter API
    conn = http.client.HTTPSConnection("twitter241.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "7ee1c65373msh181b4a01f21d239p1e5ff7jsnc2f07e071e6d",
        'x-rapidapi-host': "twitter241.p.rapidapi.com"
    }
    query_params = {
        'type': 'Top',
        'count': 5,
        'query': f"{company_name} ceo"
    }
    url_safe_query = urllib.parse.urlencode(query_params)
    # make a request to the Twitter API with the query parameters and headers
    conn.request("GET", f"/search-v2?{url_safe_query}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    ouput_dict = json.loads(data.decode("utf-8"))
    
    def extract_tweets(output_dict):
        tweets = []
        # navigate through the timeline instructions
        instructions = output_dict.get('result', {}).get('timeline', {}).get('instructions', [])
        for instruction in instructions:
            entries = instruction.get('entries', [])
            for entry in entries:
                content = entry.get('content', {})
                if content.get('entryType') == 'TimelineTimelineItem':
                    item_content = content.get('itemContent', {})
                    if item_content.get('itemType') == 'TimelineTweet':
                        tweet_result = item_content.get('tweet_results', {}).get('result', {})
                        tweet_legacy = tweet_result.get('legacy', {})
                        user_result = tweet_result.get('core', {}).get('user_results', {}).get('result', {})
                        user_legacy = user_result.get('legacy', {})
                        # get the text from dictionary - get partally decoded json
                        text = tweet_legacy.get('full_text', '')
                        def makeSense(text):
                            # step_1 : remove other escape sequences like '\n','\r',\v','\t' from cleaned_text
                            cleaned_text = re.sub(r'[\n\r\t\v]+', ' ', text)
                            # step_2: remove any remaining spaces
                            cleaned_text = cleaned_text.strip()
                            return cleaned_text
                        text = makeSense(text)
                        # Extract tweet information
                        tweet_info = {
                            "tweet_id": tweet_legacy.get('id_str', ''),
                            "text": text,
                            "created_at": tweet_legacy.get('created_at', ''),
                            "hashtags": [hashtag.get('text') for hashtag in tweet_legacy.get('entities', {}).get('hashtags', [])],
                            "mentions": [mention.get('screen_name') for mention in tweet_legacy.get('entities', {}).get('user_mentions', [])],
                            "urls": [url.get('expanded_url') for url in tweet_legacy.get('entities', {}).get('urls', [])],
                            "media": [media.get('media_url_https') for media in tweet_legacy.get('entities', {}).get('media', [])],
                            "retweet_count": tweet_legacy.get('retweet_count', 0),
                            "favorite_count": tweet_legacy.get('favorite_count', 0),
                            "lang": tweet_legacy.get('lang', ''),
                            "source": tweet_legacy.get('source', ''),
                            "is_quote_status": tweet_legacy.get('is_quote_status', False),
                            "quote_count": tweet_legacy.get('quote_count', 0),
                            "reply_count": tweet_legacy.get('reply_count', 0),
                            "user_id": user_legacy.get('id_str', ''),
                            "user_screen_name": user_legacy.get('screen_name', ''),
                            "user_name": user_legacy.get('name', ''),
                            "user_verified": user_legacy.get('verified', False),
                            "user_followers_count": user_legacy.get('followers_count', 0),
                            "user_profile_image": user_legacy.get('profile_image_url_https', ''),
                        }
                        tweets.append(tweet_info)
        return tweets
    return extract_tweets(ouput_dict)

# Threshold: 1000 Requests / MO
def twt__2(company_name: str):
    conn = http.client.HTTPSConnection("twitter-api45.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "7ee1c65373msh181b4a01f21d239p1e5ff7jsnc2f07e071e6d",
        'x-rapidapi-host': "twitter-api45.p.rapidapi.com"
    }
    query_params = {
        "query": f"{company_name} ceo",
        "search_type": "Top"
    }
    # get url safe query
    url_safe_query = urllib.parse.urlencode(query_params)
    # request to the Twitter API with the query parameters and headers
    conn.request("GET", f"/search.php?{url_safe_query}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    output_dict = json.loads(data)

    def extract_tweets(output_dict):
        tweets = []
        # traverse  through the timeline to extract tweets
        for tweet in output_dict.get("timeline", []):
            if tweet.get("type") == "tweet":
                # extract tweet information
                tweet_info = {
                    "tweet_id": tweet.get("tweet_id", ""),
                    "text": tweet.get("text", ""),
                    "created_at": tweet.get("created_at", ""),
                    "screen_name": tweet.get("screen_name", ""),
                    "source": tweet.get("source", ""),
                    "lang": tweet.get("lang", ""),
                    "conversation_id": tweet.get("conversation_id", ""),
                    "retweets": tweet.get("retweets", 0),
                    "replies": tweet.get("replies", 0),
                    "quotes": tweet.get("quotes", 0),
                    "favorites": tweet.get("favorites", 0),
                    "bookmarks": tweet.get("bookmarks", 0),
                    "views": tweet.get("views", "0"),
                    "hashtags": [hashtag.get("text") for hashtag in tweet.get("entities", {}).get("hashtags", [])],
                    "mentions": [
                        {
                            "id": mention.get("id_str", ""),
                            "name": mention.get("name", ""),
                            "screen_name": mention.get("screen_name", ""),
                        }
                        for mention in tweet.get("entities", {}).get("user_mentions", [])
                    ],
                    "urls": [
                        {
                            "url": url.get("url", ""),
                            "expanded_url": url.get("expanded_url", ""),
                            "display_url": url.get("display_url", ""),
                        }
                        for url in tweet.get("entities", {}).get("urls", [])
                    ],
                    "media": [
                        {
                            "type": media.get("type", ""),
                            "url": media.get("media_url_https", ""),
                            "video_info": media.get("video_info", {}),
                            "sizes": media.get("sizes", {}),
                        }
                        for media in tweet.get("entities", {}).get("media", [])
                    ],
                    "user_info": {
                        "screen_name": tweet.get("user_info", {}).get("screen_name", ""),
                        "name": tweet.get("user_info", {}).get("name", ""),
                        "description": tweet.get("user_info", {}).get("description", ""),
                        "followers_count": tweet.get("user_info", {}).get("followers_count", 0),
                        "friends_count": tweet.get("user_info", {}).get("friends_count", 0),
                        "verified": tweet.get("user_info", {}).get("verified", False),
                        "avatar": tweet.get("user_info", {}).get("avatar", ""),
                    },
                }
                tweets.append(tweet_info)
        return tweets
    return extract_tweets(output_dict)

