#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
背景透過処理スクリプト
rembgライブラリを使用して画像の背景を透明にします

使用方法:
python background_remover.py input_image.jpg [output_image.png]

依存関係:
pip install rembg[new] pillow
"""

import sys
import os
from pathlib import Path
from rembg import remove
from PIL import Image
import argparse


def remove_background(input_path, output_path=None, model_name='u2net'):
    """
    画像の背景を透過させる
    
    Args:
        input_path (str): 入力画像のパス
        output_path (str, optional): 出力画像のパス
        model_name (str): 使用するモデル名 (u2net, u2netp, silueta, isnet-general-use)
    
    Returns:
        str: 出力ファイルのパス
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {input_path}")
    
    # 出力パスが指定されていない場合は自動生成
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_transparent.png"
    else:
        output_path = Path(output_path)
    
    print(f"入力ファイル: {input_path}")
    print(f"出力ファイル: {output_path}")
    print(f"使用モデル: {model_name}")
    
    try:
        # 画像を読み込み
        with open(input_path, 'rb') as input_file:
            input_data = input_file.read()
        
        # 背景除去処理
        print("背景除去処理中...")
        output_data = remove(input_data, model_name=model_name)
        
        # 結果を保存
        with open(output_path, 'wb') as output_file:
            output_file.write(output_data)
        
        # ファイルサイズ確認
        if output_path.exists() and output_path.stat().st_size > 0:
            # 画像として読み込み可能か確認
            try:
                with Image.open(output_path) as img:
                    print(f"✓ 背景透過完了: {output_path}")
                    print(f"  - サイズ: {img.size}")
                    print(f"  - モード: {img.mode}")
                    print(f"  - ファイルサイズ: {output_path.stat().st_size:,} bytes")
                return str(output_path)
            except Exception as e:
                print(f"✗ 出力ファイルが破損しています: {e}")
                return None
        else:
            print("✗ 出力ファイルが正常に作成されませんでした")
            return None
            
    except Exception as e:
        print(f"✗ エラーが発生しました: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='画像の背景を透過させます')
    parser.add_argument('input', help='入力画像ファイルのパス')
    parser.add_argument('output', nargs='?', help='出力画像ファイルのパス (省略可能)')
    parser.add_argument('--model', default='u2net', 
                       choices=['u2net', 'u2netp', 'silueta', 'isnet-general-use'],
                       help='使用するモデル (デフォルト: u2net)')
    
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n例:")
        print("  python background_remover.py image.jpg")
        print("  python background_remover.py image.jpg output.png")
        print("  python background_remover.py image.jpg --model u2netp")
        return
    
    args = parser.parse_args()
    
    # 背景除去実行
    result = remove_background(args.input, args.output, args.model)
    
    if result:
        print(f"\n✅ 処理完了: {result}")
    else:
        print("\n❌ 処理に失敗しました")
        sys.exit(1)


if __name__ == "__main__":
    main()