from youtubesearchpython import Hashtag, Comments
from tqdm import tqdm
import time
import pandas as pd
import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import utils

def gather_from_youtube(query, n):
    hashtag = Hashtag(query, limit = n)
    data = []
    df = pd.DataFrame()
    for res in tqdm(hashtag.result()['result']):
        vid_id = res.get('id')
        data_dict = {}
        data_dict['id'] = vid_id
        data_dict['channel_id'] = res.get('channel').get('id')
        data_dict['text'] = res.get('title')
        data_dict['published_time'] = res.get('publishedTime')
        data_dict['duration'] = res.get('duration')
        data_dict['viewCount'] = res.get('viewCount').get('text')
        data.append(data_dict)
        try:
            com = Comments(vid_id)
            while com.hasMoreComments:
                com.getNextComments()
            for comment in com.comments['result']:
                data_dict = {}
                data_dict['id'] = comment.get('id')
                data_dict['video_id'] = vid_id
                data_dict['channel_id'] = comment.get('author').get('id')
                data_dict['text'] = comment.get('content')
                data_dict['published_time'] = comment.get('publishedTime')
                data_dict['likes'] = comment.get('votes').get('simpleText')
                data_dict['replies'] = comment.get('replyCount')
                data.append(data_dict)
        except Exception as e:
            print(f'No comments: {e}')
        time.sleep(10)
        df = pd.concat((df, pd.DataFrame(data)), axis=0, ignore_index=True)
        df.to_csv(f'{os.path.dirname(__file__)}/output/{query}_{n}.csv', index = False)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Youtube video and comment extractor')
    parser.add_argument('-q', '--query', type=str, help='Hashtag to search for within YouTube')
    parser.add_argument('-n', '--num', type=int, help='limiting the number of responses')
    args = parser.parse_args()

    gather_from_youtube(args.query, args.num)
    s3 = utils.S3_Manager()
    s3.upload_to_bucket(filename=f'{os.path.dirname(__file__)}/output/{args.query}_{args.num}.csv', dirname='DataCollection')