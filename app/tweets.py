import http.client
import urllib.parse
import json
from datetime import datetime, date, timedelta
import re # to remove escape sequences we get from json file

# we conider a global clock
current_year = datetime.now().year
current_date = date.today() # date time object
limiting_epoch = datetime.now().date().replace(day = 1, month = 1) # first day of the current year

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

# Threshold: 300 Requests / MO
def twt__3(company_name: str):
    conn = http.client.HTTPSConnection("twitter-aio.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "7ee1c65373msh181b4a01f21d239p1e5ff7jsnc2f07e071e6d",
        'x-rapidapi-host': "twitter-aio.p.rapidapi.com"
    }

    filters =  {
        "lang": "en",
        "since": (date.today() - timedelta(days=30)).isoformat(),
        "until": date.today().isoformat()   
    }
    query_params = {
        'count': 5,
        'category': 'Top',
        'filters': json.dumps(filters),
        'includeTimestamp': 'true',
    }
    url_safe_query = urllib.parse.urlencode(query_params)
    conn.request("GET", f"/search/{company_name}+ceo?{url_safe_query}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    output_dict = json.loads(data)
    def extract_tweets(data):
        tweet_data = []
        # get current year
        current_year = datetime.now().year
        # traverse through the timeline entries
        outer_entries = data.get("entries", [])
        for entry in outer_entries:
            # traverse inner entries
            entries = entry.get('entries', [])
            for entry in entries:
                content = entry.get("content", {})
                if content.get("entryType") == "TimelineTimelineItem":
                    item_content = content.get("itemContent", {})
                    if item_content.get("itemType") == "TimelineTweet":
                        tweet_result = item_content.get("tweet_results", {}).get("result", {})
                        tweet_legacy = tweet_result.get("legacy", {})
                        user_result = tweet_result.get("core", {}).get("user_results", {}).get("result", {})
                        user_legacy = user_result.get("legacy", {})
                        # --- filter tweets based on creation date ---
                        created_at = tweet_legacy.get("created_at", "")
                        try:
                            tweet_date = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
                            if(tweet_date.year != current_year):
                                continue
                        except:
                            continue
                        # extract tweet information
                        tweet_info = {
                            "tweet_id": tweet_legacy.get("id_str", ""),
                            "text": tweet_legacy.get("full_text", ""),
                            "created_at": created_at,
                            "conversation_id": tweet_legacy.get("conversation_id_str", ""),
                            "retweets": tweet_legacy.get("retweet_count", 0),
                            "replies": tweet_legacy.get("reply_count", 0),
                            "quotes": tweet_legacy.get("quote_count", 0),
                            "favorites": tweet_legacy.get("favorite_count", 0),
                            "lang": tweet_legacy.get("lang", ""),
                            "source": tweet_legacy.get("source", ""),
                            "hashtags": [hashtag.get("text") for hashtag in tweet_legacy.get("entities", {}).get("hashtags", [])],
                            "mentions": [
                                {
                                    "id": mention.get("id_str", ""),
                                    "name": mention.get("name", ""),
                                    "screen_name": mention.get("screen_name", ""),
                                }
                                for mention in tweet_legacy.get("entities", {}).get("user_mentions", [])
                            ],
                            "urls": [
                                {
                                    "url": url.get("url", ""),
                                    "expanded_url": url.get("expanded_url", ""),
                                    "display_url": url.get("display_url", ""),
                                }
                                for url in tweet_legacy.get("entities", {}).get("urls", [])
                            ],
                            "media": [
                                {
                                    "type": media.get("type", ""),
                                    "url": media.get("media_url_https", ""),
                                    "sizes": media.get("sizes", {}),
                                }
                                for media in tweet_legacy.get("extended_entities", {}).get("media", [])
                            ],
                        }

                        # extract user information
                        user_info = {
                            "user_id": user_legacy.get("id_str", ""),
                            "name": user_legacy.get("name", ""),
                            "screen_name": user_legacy.get("screen_name", ""),
                            "description": user_legacy.get("description", ""),
                            "followers_count": user_legacy.get("followers_count", 0),
                            "friends_count": user_legacy.get("friends_count", 0),
                            "statuses_count": user_legacy.get("statuses_count", 0),
                            "verified": user_legacy.get("verified", False),
                            "profile_image_url": user_legacy.get("profile_image_url_https", ""),
                            "profile_banner_url": user_legacy.get("profile_banner_url", ""),
                        }

                        # combine tweet and user information
                        tweet_info["user_info"] = user_info
                        tweet_data.append(tweet_info)
        return tweet_data
    return extract_tweets(output_dict)

# Threshold: 500 Requests / MO
def twt__4(company_name: str):
    global current_date, limiting_epoch
    conn = http.client.HTTPSConnection("twitter154.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "7ee1c65373msh181b4a01f21d239p1e5ff7jsnc2f07e071e6d",
        'x-rapidapi-host': "twitter154.p.rapidapi.com"
    }
    # Define the query parameters
    query_params = {
        'query': f'{company_name} ceo',
        'section': 'top',
        'min_retweets': 1,
        'min_likes': 1,
        'limit': 5,
        'start_date': limiting_epoch.isoformat(),
        'language': 'en',
        'end_date': current_date.isoformat()
    }
    url_safe_query = urllib.parse.urlencode(query_params)
    conn.request("GET", f"/search/search?{url_safe_query}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    output_dict = json.loads(data)
    def extract_tweets():
        nonlocal output_dict
        tweets = []
        # Iterate through the results
        for tweet in output_dict.get("results", []):
            # Extract tweet information
            tweet_info = {
                "tweet_id": tweet.get("tweet_id", ""),
                "creation_date": tweet.get("creation_date", ""),
                "text": tweet.get("text", ""),
                "language": tweet.get("language", ""),
                "favorite_count": tweet.get("favorite_count", 0),
                "retweet_count": tweet.get("retweet_count", 0),
                "reply_count": tweet.get("reply_count", 0),
                "quote_count": tweet.get("quote_count", 0),
                "views": tweet.get("views", 0),
                "video_view_count": tweet.get("video_view_count", None),
                "source": tweet.get("source", ""),
                "conversation_id": tweet.get("conversation_id", ""),
                "in_reply_to_status_id": tweet.get("in_reply_to_status_id", None),
                "quoted_status_id": tweet.get("quoted_status_id", None),
                "expanded_url": tweet.get("expanded_url", ""),
                "media": [],
                "videos": [],
            }

            # Extract media information
            extended_entities = tweet.get("extended_entities", {}).get("media", [])
            for media in extended_entities:
                media_info = {
                    "type": media.get("type", ""),
                    "url": media.get("media_url_https", ""),
                    "display_url": media.get("display_url", ""),
                    "expanded_url": media.get("expanded_url", ""),
                    "sizes": media.get("sizes", {}),
                    "video_info": media.get("video_info", {}),
                }
                if media_info["type"] == "video":
                    tweet_info["videos"].append(media_info)
                else:
                    tweet_info["media"].append(media_info)

            # Extract user information
            user = tweet.get("user", {})
            user_info = {
                "user_id": user.get("user_id", ""),
                "username": user.get("username", ""),
                "name": user.get("name", ""),
                "creation_date": user.get("creation_date", ""),
                "follower_count": user.get("follower_count", 0),
                "following_count": user.get("following_count", 0),
                "favourites_count": user.get("favourites_count", 0),
                "listed_count": user.get("listed_count", 0),
                "is_verified": user.get("is_verified", False),
                "is_blue_verified": user.get("is_blue_verified", False),
                "profile_pic_url": user.get("profile_pic_url", ""),
                "profile_banner_url": user.get("profile_banner_url", ""),
                "description": user.get("description", ""),
                "external_url": user.get("external_url", ""),
                "number_of_tweets": user.get("number_of_tweets", 0),
                "location": user.get("location", ""),
            }

            # Combine tweet and user information
            tweet_info["user_info"] = user_info
            tweets.append(tweet_info)
        return tweets
    return extract_tweets()


# ---- more to be added soon ----