#!/usr/bin/env python3
"""
ローカルFALアップロード機能 - MCP連携用
ローカルファイルをFAL.aiにアップロードし、URLを一時ファイルに保存
"""

import os
import sys
import json
import tempfile
import time
from pathlib import Path

# Add parent directory to path to import fal_upload_helper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fal_upload_helper import setup_fal_client, upload_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 local_fal_upload.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # FAL API クライアントセットアップ
    if not setup_fal_client():
        sys.exit(1)
    
    # ファイルの存在確認
    if not os.path.exists(file_path):
        print(f"❌ ファイルが見つかりません: {file_path}")
        sys.exit(1)
    
    # アップロード実行
    print(f"🚀 ローカルファイルをFAL.aiにアップロード中: {file_path}")
    uploaded_url = upload_file(file_path)
    
    if not uploaded_url:
        print("❌ アップロードに失敗しました")
        sys.exit(1)
    
    # 結果を一時ファイルに保存
    result_data = {
        "uploaded_url": uploaded_url,
        "original_file": file_path,
        "file_name": os.path.basename(file_path),
        "file_size_mb": os.path.getsize(file_path) / (1024 * 1024),
        "upload_time": time.time()
    }
    
    # 一時ファイルに結果を保存
    temp_file = tempfile.NamedTemporaryFile(mode='w', prefix='fal_upload_result_', suffix='.json', delete=False)
    json.dump(result_data, temp_file, indent=2)
    temp_file.close()
    
    print(f"✅ アップロード完了: {uploaded_url}")
    print(f"📄 結果ファイル: {temp_file.name}")
    
    # 結果ファイルパスを標準出力に出力（MCPサーバーが読み取る）
    print(f"RESULT_FILE:{temp_file.name}")
    
    return uploaded_url

if __name__ == "__main__":
    main()