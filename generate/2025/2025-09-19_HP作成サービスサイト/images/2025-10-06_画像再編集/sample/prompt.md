# 画像編集プロンプト - セクション入れ替え

## 使用モデル
- qwen-image-edit-plus-lora（複数画像対応）
- gemini-25-flash-image-edit（複数画像対応）

## 入力画像
1. **元画像**: オリジナルのホームページデザインカンプ
2. **注釈画像**: セクションを四角で囲んでマーキングした画像

## プロンプト（英語版）

```
Use the first image as the base design. The second image shows sections marked with colored rectangles for reference.

Task:
1. Identify the section marked with rectangle A (3-column section)
2. Identify the section marked with rectangle B (text section)
3. Swap the positions of these two sections - move section B to appear before section A
4. Keep all other sections (navigation menu, hero header, CTA section, footer) in their original positions
5. Remove all rectangle markers from the final output
6. Maintain the original design style, colors, and layout quality

Output: A clean homepage design with swapped sections and no visible rectangles.
```

## プロンプト（日本語版 - 参考）

```
1枚目の画像をベースデザインとして使用してください。2枚目の画像は、参照用に色付き四角でセクションをマーキングしたものです。

タスク:
1. 四角Aでマークされたセクション（3カラムセクション）を特定
2. 四角Bでマークされたセクション（テキストセクション）を特定
3. これら2つのセクションの位置を入れ替える - セクションBがセクションAの前に来るように移動
4. その他のセクション（ナビメニュー、ヒーローヘッダー、CTAセクション、フッター）は元の位置を維持
5. 最終出力からすべての四角マーカーを削除
6. オリジナルのデザインスタイル、色、レイアウト品質を維持

出力: セクションが入れ替わり、四角が表示されていないクリーンなホームページデザイン
```

## 実装コード例

### qwen-image-edit-plus-lora
```python
mcp__i2i-kamui-qwen-image-edit-plus-lora__qwen_image_edit_plus_lora_submit(
    image_urls=["元画像URL", "注釈画像URL"],
    prompt="Use the first image as the base design. The second image shows sections marked with colored rectangles for reference. Task: 1. Identify the section marked with rectangle A (3-column section) 2. Identify the section marked with rectangle B (text section) 3. Swap the positions of these two sections - move section B to appear before section A 4. Keep all other sections (navigation menu, hero header, CTA section, footer) in their original positions 5. Remove all rectangle markers from the final output 6. Maintain the original design style, colors, and layout quality. Output: A clean homepage design with swapped sections and no visible rectangles.",
    image_size="landscape_4_3"
)
```

### gemini-25-flash-image-edit
```python
mcp__i2i-kamui-gemini-25-flash-image-edit__gemini_25_flash_image_edit_submit(
    image_urls=["元画像URL", "注釈画像URL"],
    prompt="Use the first image as the base design. The second image shows sections marked with colored rectangles for reference. Task: 1. Identify the section marked with rectangle A (3-column section) 2. Identify the section marked with rectangle B (text section) 3. Swap the positions of these two sections - move section B to appear before section A 4. Keep all other sections (navigation menu, hero header, CTA section, footer) in their original positions 5. Remove all rectangle markers from the final output 6. Maintain the original design style, colors, and layout quality. Output: A clean homepage design with swapped sections and no visible rectangles."
)
```

## 注意事項
- 注釈画像では、入れ替えたいセクションを明確に識別できるように色分けした四角でマーキングする
- プロンプト内で「rectangle A」「rectangle B」のように具体的な識別子を使用
- 最終出力では四角マーカーが完全に削除されることを明示
