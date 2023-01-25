from pyyoutube import Api
import requests
import re
import sys

CSV_NAME = "channels.csv"

if len(sys.argv) > 1:
    CSV_NAME = sys.argv[1]

DELIMER = ";"

def get_channel_names():
    """
    This function gets channel names from channels.csv file.
    The channel names are at the first column of the csv file.
    """
    with open(CSV_NAME, 'r') as f:
        lines = f.readlines()[1:]
        channel_names = [line.split(DELIMER)[0].strip() for line in lines]
    return channel_names

def get_channelid(channel_name):
    """
    This function gets the page and uses regex to get the channelId
    itemprop="channelId" content="channelIdgoeshere"
    """
    url = "https://www.youtube.com/c/" + channel_name
    r = requests.get(url).text
    channel_id = re.findall(r'itemprop="channelId" content="(.+?)"', r)[0]
    return channel_id

def get_video_id(video):
    """
    This function gets the video id from a video object
    """
    try:
        id_ = video.to_dict()["contentDetails"]["upload"]["videoId"]
    except:
        id_ = video.to_dict()["playlistItem"]["resourceId"]["kind"]["videoId"]
    return id_

def get_view_count(ids, n=1):
    """
    This function gets the channel object and uses the api to get the average view count of the latest n videos
    """
    vid_ids = [[get_video_id(item) for item in api.get_activities_by_channel(channel_id=id_, count=n).items] for id_ in ids]
    view_counts = [int(sum([get_view(vid_id) for vid_id in vid_id])/n) for vid_id in vid_ids]
    return view_counts

def get_view(video_id):
    """
    This function gets the view count of a video
    """
    return int(api.get_video_by_id(video_id=video_id).items[0].statistics.viewCount)

def update_csv(channel_names, view_counts, sub_counts):
    """
    This function updates the csv file with the new view counts and subscriber counts
    """
    lines = ["Name;View Count;Subscriber Count"]
    for cn, vc, sc in zip(channel_names, view_counts, sub_counts):
        lines.append(DELIMER.join([cn, str(vc), str(sc)]))
    
    with open(CSV_NAME, 'w') as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    api = Api(api_key="YOURAPIKEY")
    channel_names = get_channel_names()
    ids = [get_channelid(channel_name) for channel_name in channel_names]
    channels = api.get_channel_info(channel_id=",".join(ids))
    sub_counts = [channel.statistics.subscriberCount for channel in channels.items]
    view_counts = get_view_count(ids)
    update_csv(channel_names, view_counts, sub_counts)