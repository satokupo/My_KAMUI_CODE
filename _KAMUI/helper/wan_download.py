#!/usr/bin/env python3
"""
WAN v2.2-a14b T2V動画ダウンロードヘルパー

Purpose: WAN v2.2-a14bで生成された動画を直接ダウンロードする
Dependencies: requests, os
Usage: python wan_download.py <request_id> <output_path>
"""

import sys
import os
import requests
import json

def download_wan_video(request_id, output_path):
    """WAN v2.2-a14bの動画をダウンロード"""

    # ステータスURL（公開エンドポイント）
    status_url = f'https://queue.fal.run/fal-ai/wan/v2.2-a14b/text-to-video/requests/{request_id}'

    try:
        # ステータスを取得（GETメソッド）
        response = requests.get(status_url)

        if response.status_code != 200:
            print(f'Error: HTTP {response.status_code}')
            print(f'Response: {response.text}')
            return False

        result = response.json()

        # 動画URLを抽出
        if 'video' in result and 'url' in result['video']:
            video_url = result['video']['url']
            print(f'Video URL found: {video_url}')

            # 動画をダウンロード
            print(f'Downloading to: {output_path}')
            video_response = requests.get(video_url, stream=True)

            with open(output_path, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            size = os.path.getsize(output_path)
            print(f'Download completed: {size:,} bytes')
            return True
        else:
            print(f'Error: No video URL in response')
            print(f'Response: {json.dumps(result, indent=2)}')
            return False

    except Exception as e:
        print(f'Exception: {e}')
        return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python wan_download.py <request_id> <output_path>')
        sys.exit(1)

    request_id = sys.argv[1]
    output_path = sys.argv[2]

    success = download_wan_video(request_id, output_path)
    sys.exit(0 if success else 1)
