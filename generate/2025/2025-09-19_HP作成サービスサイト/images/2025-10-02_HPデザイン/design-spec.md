# デザインカンプ仕様書
生成日: 2025-10-02

## プロジェクト情報
- プロジェクト名: HP制作サービス
- ページ種別: トップページ
- スタイルモード: mixed（各モデルで有機的/無機的/ハイブリッドを混在）
- トンマナ: 親しみ・信頼

## 構造（絶対不変）
### セクション順序
1. ヘッダー/ナビゲーション
2. ヒーローセクション（フルハイト固定）
3. 説明テキストセクション
4. 特徴カードセクション（3カラム）
5. CTAセクション（2カラム）
6. フッター（背景色使用）

### 要素数
- ヘッダーメニュー: 6項目
- ヒーロー要素: メインコピー、サブコピー、CTA×2（配置・サイズは自由）
- 説明テキスト: 4段落
- 特徴カード: 3個（アイコン使用は任意）
- CTAカード: 2個（アイコン使用は任意）

## デザインパラメータ（YAML）

```yaml
project: HP制作サービス
page: top
style_mode: mixed
layout_constraint: soft
tone: [親しみ, 信頼]

palette:
  primary: "#3B82F6"
  secondary: "#10B981"
  neutrals: ["#FFFFFF", "#F8FAFC", "#1F2937"]

imagery: mixed
icon_style: mixed

typography:
  heading: geo-sans
  body: readability-first

motifs: [web, digital, connection]

vector_separators:
  allowed: true
  notes: "スタイルモードに応じて使用"

accessibility:
  contrast: ">=4.5:1"

creative_intensity: high

notes: |
  - ヒーローセクションはフルハイト固定、内部要素の配置・サイズは自由
  - 特徴カード・CTAセクションのアイコン使用は任意
  - フッターは背景色を使用
  - 構造・要素数は厳守、表現は大胆に
```

## 生成用プロンプト補足

参照ワイヤーフレームで検出・合意したセクション順序と要素数を厳守。矩形は位置の目安で形状指定ではない。非矩形マスクや軽い重なり、±12〜24pxのオフセットで動きを付けてよい。creative_intensity=High の初回案は挑戦的で良い。構造固定・可読性・アクセシビリティを守りつつ、大胆に。
