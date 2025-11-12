import requests as rq 
import json
import os
from datetime import date
from dotenv import load_dotenv
load_dotenv()

def _get_api_key() -> str:
    return os.getenv("YOUTUBE_API_KEY")     

def get_playlist_id() -> str:
    CHANNEL_HANDLE:str="MrBeast"
    API_KEY:str=_get_api_key()

    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"
        response = rq.get(url)
        response.raise_for_status()
        data = response.json()
        channel_items = data["items"][0]
        channel_playlistId = channel_items["contentDetails"]["relatedPlaylists"][
            "uploads"
        ]
        return channel_playlistId

    except rq.exceptions.RequestException as e:
        raise e

def get_video_ids() -> list:
    #play_list_id:str="UUX6OQ3DkcsbYNE6H8uQQuVA"
    play_list_id = get_playlist_id()
    API_KEY:str=_get_api_key()
    max_result:int=50
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={max_result}&playlistId={play_list_id}&key={API_KEY}"
    videos_ids:list = []    
    page_token:str = None # funciona como un puntero para la paginación

    try:
        while True:
           url = base_url
           if page_token:
              url += f"&pageToken={page_token}"
           response = rq.get(url)
           response.raise_for_status()
           data = response.json()

           for item in data.get('items', []):
               video_id = item['contentDetails']['videoId']
               videos_ids.append(video_id) 
               page_token = data.get('nextPageToken')   
               
               if not page_token:
                  break           
           return videos_ids
        
    except rq.exceptions.RequestException as e:
       raise e

def extract_video_metadata(video_ids) -> list:
    API_KEY = _get_api_key()
    max_results:int= 50
    extracted_data = []

    def batch_list(video_id_list:list, batch_size:int):
        for video_id in range(0, len(video_id_list), batch_size):
            yield video_id_list[video_id: video_id + batch_size]
    try:
        for batch in batch_list(video_ids, max_results):
            video_ids_str = ','.join(batch)
            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}"
            response = rq.get(url)
            response.raise_for_status()
            data = response.json()
            
            for video_item in data.get('items',[]):
                video_data = {
                    "video_id": video_item['id'],
                    "title": video_item['snippet']['title'],
                    "description": video_item['snippet']['description'],
                    "published_at": video_item['snippet']['publishedAt'],
                    "duration": video_item['contentDetails']['duration'],
                    "view_count": video_item['statistics'].get('viewCount', 0),
                    "like_count": video_item['statistics'].get('likeCount', 0),
                    "comment_count": video_item['statistics'].get('commentCount', 0)
                }
                extracted_data.append(video_data)
        return extracted_data
    except rq.exceptions.RequestException as e:
        raise e
    
def load_data_to_file(extracted_data:list) -> bool:
    json_data_file = f"{os.getcwd()}/videos_data_{date.today()}.json"
    try:
        with open(json_data_file, 'w', encoding='utf-8') as json_file:
            json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)
        return True
    except IOError as e:
        raise e

def _run() -> None:    
    video_ids = get_video_ids()
    video_extracted_data = extract_video_metadata(video_ids)
    load_data_to_file(video_extracted_data)

if __name__ == "__main__":
    _run()