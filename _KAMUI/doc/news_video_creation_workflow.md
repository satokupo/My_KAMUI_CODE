# リップシンク動画＋字幕＋素材統合 作業手順書

## 概要
音声ファイルとビデオファイルを使用してPixverseでリップシンク動画を作成し、日本語字幕と画像・動画素材を統合した最終動画を制作する手順。

## 使用したファイル
### 入力ファイル
- `inspirational_girl_part1.mp3` - 音声ファイル1
- `inspirational_girl_part2.mp3` - 音声ファイル2  
- `hailuo_02_20250723_235718.mp4` - ベース動画
- `githubactionsによるウェビナー・ブログ化ワークフロー.png` - ワークフロー画像
- `初学者向けブログ.png` - ブログ画像
- `AI自動外部リンク.mov` - AI外部リンク動画

### 最終出力ファイル
- `final_video_same_position.mp4` - 完成動画

## ベース動画撮影時の重要な注意点

### 撮影の基本ルール
**Pixverseリップシンクを成功させるために、以下を必ず守ること：**

1. **カメラを動かさない**
   - 三脚やスタンドを使用してカメラを完全に固定
   - ズームイン・ズームアウトは避ける
   - パン（左右の動き）・チルト（上下の動き）は禁止

2. **身体の動きを最小限に抑える**
   - 頭部の位置を一定に保つ
   - 大きな身振り手振りは避ける
   - 上半身の前後左右の動きを制限
   - 座った状態での撮影を推奨

3. **顔の向きを一定に保つ**
   - カメラに対して正面を向いたまま
   - 横を向いたり、うつむいたりしない
   - 口元が常にカメラから見えるように

4. **照明を安定させる**
   - 一定の明るさを保つ
   - 影の位置が変わらないように

### 推奨撮影環境
- **撮影距離**: 胸から上が画面に収まる程度
- **背景**: シンプルで変化のない背景
- **時間**: 短めのセグメント（10-20秒程度）
- **音声**: 別途収録（リップシンクで後から合成）

## 作業手順

### 1. 音声ファイルのFALアップロード
```bash
python upload_to_fal.py /Users/motokidaisuke/kamuicode/inspirational_girl_part1.mp3
python upload_to_fal.py /Users/motokidaisuke/kamuicode/inspirational_girl_part2.mp3
python upload_to_fal.py /Users/motokidaisuke/kamuicode/hailuo_02_20250723_235718.mp4
```

**取得したURL:**
- Part1音声: `https://v3.fal.media/files/monkey/Laaxh4ouPixWQ9QZJ7-Tr_inspirational_girl_part1.mp3`
- Part2音声: `https://v3.fal.media/files/penguin/Q6DZnJUrBLibwL1nxdNwS_inspirational_girl_part2.mp3`
- 動画: `https://v3.fal.media/files/koala/j1g4UfM_rf19MOsr9Gccl_hailuo_02_20250723_235718.mp4`

### 2. Pixverseリップシンク処理
**Part1:**
```bash
# Pixverseリップシンク実行
request_id: 99bd2ed0-e775-4b16-bb79-a841033885e2
# 完成後ダウンロード
curl -o "lipsync_part1_output.mp4" "https://v3.fal.media/files/tiger/zmBkmSMqAl8ZaFlmgNBr8_output.mp4"
```

**Part2:**
```bash
# Pixverseリップシンク実行
request_id: 871f1998-8edc-4d22-8667-40837d417af2
# 完成後ダウンロード
curl -o "lipsync_part2_output.mp4" "https://v3.fal.media/files/penguin/4xGzOJgSL9qhp3HZG8YVP_output.mp4"
```

### 3. 動画結合
```bash
ffmpeg -i lipsync_part1_output.mp4 -i lipsync_part2_output.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[outv][outa]" \
  -map "[outv]" -map "[outa]" combined_lipsync.mp4
```

### 4. 字幕ファイル作成
**detailed_subtitles.srt:**
```srt
1
00:00:00,500 --> 00:00:01,200
おはようございます。

2
00:00:01,500 --> 00:00:04,200
神威では、最新の生成AI技術を活用し、

3
00:00:04,200 --> 00:00:06,500
日々開催されるウェビナーの内容を

4
00:00:06,500 --> 00:00:08,200
初心者から上級者まで、

5
00:00:08,200 --> 00:00:11,800
それぞれのレベルに応じた質の高いブログ記事として

6
00:00:11,800 --> 00:00:14,500
自動生成するサービスの提供を開始いたします。

7
00:00:15,200 --> 00:00:18,800
AI開発の最前線からクリエイティブ分野、ビジネス活用まで

8
00:00:18,800 --> 00:00:20,500
幅広いトピックをカバーし、

9
00:00:20,500 --> 00:00:23,000
皆様の継続的な学習をサポートいたします。

10
00:00:23,500 --> 00:00:26,800
また、AIが厳選した関連リソースへのリンクも提供し、

11
00:00:26,800 --> 00:00:29,500
より深い学習体験を可能にします。

12
00:00:30,000 --> 00:00:32,000
この革新的なプラットフォームを通じて、

13
00:00:32,000 --> 00:00:34,000
皆様のスキルアップと知識の向上を

14
00:00:34,000 --> 00:00:35,500
全力でサポートしてまいります。
```

### 5. 字幕付き動画作成
```bash
ffmpeg -i combined_lipsync.mp4 \
  -vf "subtitles=detailed_subtitles.srt:force_style='Fontsize=20,PrimaryColour=&Hffffff&,OutlineColour=&H000000&,Outline=2,Alignment=2'" \
  final_lipsync_detailed_timing.mp4
```

### 6. 素材準備
```bash
# デスクトップからファイルをコピー
cp "/Users/motokidaisuke/Desktop/githubactionsによるウェビナー・ブログ化ワークフロー.png" ./workflow_image.png
cp "/Users/motokidaisuke/Desktop/AI自動外部リンク.mov" ./ai_link_video.mov
cp "/Users/motokidaisuke/Desktop/初学者向けブログ.png" ./beginner_blog_image.png
```

### 7. 最終動画統合
**素材配置タイミング:**
- GitHubActionsワークフロー画像: 1.5-14.5秒（サービス紹介中）
- 初学者向けブログ画像: 6.5-11.8秒（レベル別説明中）
- AI自動外部リンク動画: 23.5-29.5秒（リソース提供説明中）

```bash
ffmpeg -i final_lipsync_detailed_timing.mp4 \
  -i workflow_image.png \
  -i beginner_blog_image.png \
  -stream_loop -1 -i ai_link_video.mov \
  -filter_complex "[0:v]scale=1080:1080[main]; [1]scale=800:400[workflow]; [2]scale=800:500[blog]; [3:v]scale=800:500[ai_video]; [main][workflow]overlay=140:500:enable='between(t,1.5,14.5)'[tmp1]; [tmp1][blog]overlay=140:400:enable='between(t,6.5,11.8)'[tmp2]; [tmp2][ai_video]overlay=140:400:enable='between(t,23.5,29.5)'[out]" \
  -map "[out]" -map 0:a -c:a copy -t 36.13 \
  final_video_same_position.mp4
```

## 重要なパラメータ

### 素材サイズ・位置
- **ワークフロー画像**: 800x400px、座標(140,500)
- **ブログ画像**: 800x500px、座標(140,400) 
- **AI動画**: 800x500px、座標(140,400)

### 字幕設定
- **フォントサイズ**: 20
- **色**: 白文字（&Hffffff&）
- **縁取り**: 黒、太さ2（&H000000&, Outline=2）
- **位置**: 下部中央（Alignment=2）

### 動画設定
- **解像度**: 1080x1080
- **フレームレート**: 24fps
- **総時間**: 36.13秒
- **音声**: AACコーデック、モノラル、44.1kHz

## トラブルシューティング

### 字幕が表示されない場合
- 字幕を動画に直接焼き込む方式を使用
- `subtitles` フィルターで `force_style` パラメータを指定

### AI動画がループしない場合
- `stream_loop -1` オプションでループ設定
- 表示時間内で動画が繰り返し再生される

### 素材の位置・サイズ調整
- `scale` フィルターでサイズ調整
- `overlay` フィルターで位置と表示タイミング指定
- `enable='between(t,開始秒,終了秒)'` で表示期間制御

## 成果物
- **リップシンク動画**: 2つの音声と1つの動画を統合
- **日本語字幕**: 14セグメントに細分化した詳細タイミング
- **素材統合**: 3つの画像・動画素材を適切なタイミングで配置
- **最終品質**: 高品質なH.264エンコード、字幕焼き込み済み

## 使用ツール
- **Pixverse**: AIリップシンク生成
- **FFmpeg**: 動画編集・結合・字幕追加
- **Python**: ファイルアップロード（upload_to_fal.py）
- **MCP Tools**: Pixverseリップシンク操作

## 作成日時
2025年7月24日

## 備考
- 全ての動画は1080x1080の正方形フォーマット
- 字幕はヒラギノ角ゴシックフォントで表示
- AI動画は表示期間中にループ再生される設定