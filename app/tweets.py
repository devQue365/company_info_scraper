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
        'query': f"{company_name} company CEO's latest tweets"
    }
    url_safe_query = urllib.parse.urlencode(query_params)
    # make a request to the Twitter API with the query parameters and headers
    conn.request("GET", f"/search-v2?{url_safe_query}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    ouput_dict = json.loads(data.decode("utf-8"))
    
    def extract_tweets(data):
        tweets = []
        # navigate through the timeline instructions
        instructions = data.get('result', {}).get('timeline', {}).get('instructions', [])
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