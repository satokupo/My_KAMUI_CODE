#!/usr/bin/env python3
"""
FAL.ai ファイルアップロードヘルパー
任意のファイルをfal.aiにアップロードし、各種AIモデルで使用可能なURLを取得
"""

import os
import sys
import fal_client
from dotenv import load_dotenv
from pathlib import Path
import argparse

def setup_fal_client():
    """FAL API クライアントをセットアップ"""
    load_dotenv()
    
    fal_api_key = os.getenv('FAL_API_KEY') or os.getenv('FAL_KEY')
    if not fal_api_key:
        print("❌ エラー: FAL_API_KEY または FAL_KEY が設定されていません")
        print("💡 .env ファイルに以下を追加してください:")
        print("FAL_KEY=your_api_key_here")
        return False
    
    os.environ['FAL_KEY'] = fal_api_key
    print(f"✅ FAL API キーが設定されました")
    return True

def upload_file(file_path, output_file=None):
    """ファイルをアップロードしてURLを取得"""
    if not os.path.exists(file_path):
        print(f"❌ ファイルが見つかりません: {file_path}")
        return None
    
    # ファイル情報を表示
    file_size = os.path.getsize(file_path)
    file_size_mb = file_size / (1024 * 1024)
    file_name = os.path.basename(file_path)
    
    print(f"📁 ファイル: {file_name}")
    print(f"📂 パス: {file_path}")
    print(f"📊 サイズ: {file_size_mb:.2f} MB")
    
    try:
        print("🚀 アップロード中...")
        uploaded_url = fal_client.upload_file(file_path)
        
        print("🎉 アップロード成功!")
        print("=" * 60)
        print(f"📎 URL: {uploaded_url}")
        print("=" * 60)
        
        # URLをファイルに保存
        if output_file:
            with open(output_file, 'w') as f:
                f.write(uploaded_url)
            print(f"💾 URLを {output_file} に保存しました")
        
        # 各種モデル用の使用例を表示
        file_ext = Path(file_path).suffix.lower()
        print(f"\n🔗 使用例:")
        
        if file_ext in ['.jpg', '.jpeg', '.png', '.webp']:
            print(f'📸 画像生成モデル用:')
            print(f'"image_url": "{uploaded_url}"')
            print(f'📸 Flux Kontext用:')
            print(f'"image_url": "{uploaded_url}"')
            
        elif file_ext in ['.mp4', '.mov', '.avi', '.webm']:
            print(f'🎬 動画処理モデル用:')
            print(f'"video_url": "{uploaded_url}"')
            
        elif file_ext in ['.wav', '.mp3', '.m4a', '.flac']:
            print(f'🎵 音声処理モデル用:')
            print(f'"audio_url": "{uploaded_url}"')
            
        elif file_ext == '.zip':
            print(f'📦 LoRAトレーニング用:')
            print(f'"image_data_url": "{uploaded_url}"')
            print(f'📦 Flux Kontext Trainer用:')
            print(f'"image_data_url": "{uploaded_url}"')
            
        else:
            print(f'📄 一般的な使用:')
            print(f'"file_url": "{uploaded_url}"')
        
        return uploaded_url
        
    except Exception as e:
        print(f"❌ アップロードエラー: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='FAL.ai ファイルアップロードヘルパー')
    parser.add_argument('file_path', help='アップロードするファイルのパス')
    parser.add_argument('-o', '--output', help='URLを保存するファイル名')
    parser.add_argument('--open', action='store_true', help='アップロード後にURLをブラウザで開く')
    
    args = parser.parse_args()
    
    if not setup_fal_client():
        sys.exit(1)
    
    result = upload_file(args.file_path, args.output)
    
    if result:
        if args.open:
            import webbrowser
            webbrowser.open(result)
            print("🌐 ブラウザでURLを開きました")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()