import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image
import os
import threading
from pathlib import Path


class AvifToPngConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("AVIF to PNG 変換ツール")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        self.files = []
        self.converting = False
        self.cancel_flag = False

        self.setup_ui()

    def setup_ui(self):
        # メインフレーム
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # タイトル
        title_label = tk.Label(
            main_frame,
            text="AVIF to PNG 変換ツール",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(0, 20))

        # ドロップエリア
        drop_frame = tk.LabelFrame(
            main_frame,
            text="ファイル選択",
            font=("Arial", 12),
            padx=20,
            pady=20
        )
        drop_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # ドラッグ&ドロップを設定
        drop_frame.drop_target_register(DND_FILES)
        drop_frame.dnd_bind('<<Drop>>', self.drop_files)

        info_label = tk.Label(
            drop_frame,
            text="AVIFファイルをドラッグ&ドロップ\nまたは下のボタンから選択してください",
            font=("Arial", 10)
        )
        info_label.pack(pady=(0, 10))

        select_button = tk.Button(
            drop_frame,
            text="ファイルを選択",
            command=self.select_files,
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        select_button.pack()

        # ファイル情報表示
        self.file_info_label = tk.Label(
            drop_frame,
            text="選択されたファイル: 0個",
            font=("Arial", 10),
            fg="gray"
        )
        self.file_info_label.pack(pady=(10, 0))

        # 進捗バー
        progress_frame = tk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))

        self.progress_label = tk.Label(
            progress_frame,
            text="進捗: 0%",
            font=("Arial", 10)
        )
        self.progress_label.pack(anchor=tk.W)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))

        # ステータス表示
        self.status_label = tk.Label(
            main_frame,
            text="",
            font=("Arial", 10),
            fg="blue",
            wraplength=550,
            justify=tk.LEFT
        )
        self.status_label.pack(fill=tk.X, pady=(0, 10))

        # ボタンフレーム
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        self.convert_button = tk.Button(
            button_frame,
            text="変換開始",
            command=self.start_conversion,
            font=("Arial", 12, "bold"),
            bg="#2196F3",
            fg="white",
            padx=30,
            pady=10,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.convert_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.cancel_button = tk.Button(
            button_frame,
            text="キャンセル",
            command=self.cancel_conversion,
            font=("Arial", 12, "bold"),
            bg="#f44336",
            fg="white",
            padx=30,
            pady=10,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.cancel_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 5))

        self.reset_button = tk.Button(
            button_frame,
            text="リセット",
            command=self.reset,
            font=("Arial", 12, "bold"),
            bg="#607D8B",
            fg="white",
            padx=30,
            pady=10,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.reset_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

    def select_files(self):
        if self.converting:
            return

        files = filedialog.askopenfilenames(
            title="AVIFファイルを選択",
            filetypes=[("AVIF files", "*.avif"), ("All files", "*.*")]
        )

        if files:
            self.files = list(files)
            self.file_info_label.config(
                text=f"選択されたファイル: {len(self.files)}個"
            )
            self.convert_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            self.status_label.config(text="")

    def drop_files(self, event):
        """ドラッグ&ドロップされたファイルを処理"""
        if self.converting:
            return

        # ドロップされたファイルのパスを取得
        files = self.root.tk.splitlist(event.data)

        # AVIFファイルのみをフィルタリング
        avif_files = [f for f in files if f.lower().endswith('.avif')]

        if avif_files:
            self.files = avif_files
            self.file_info_label.config(
                text=f"選択されたファイル: {len(self.files)}個"
            )
            self.convert_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            self.status_label.config(text="")
        else:
            messagebox.showwarning(
                "警告",
                "AVIFファイルが含まれていません"
            )

    def start_conversion(self):
        if not self.files or self.converting:
            return

        self.converting = True
        self.cancel_flag = False
        self.convert_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.DISABLED)

        # 別スレッドで変換処理を実行
        thread = threading.Thread(target=self.convert_files)
        thread.daemon = True
        thread.start()

    def convert_files(self):
        success_files = []
        failed_files = []
        total_files = len(self.files)

        # 1回目の変換
        for i, file_path in enumerate(self.files):
            if self.cancel_flag:
                self.update_status("キャンセルされました")
                self.finish_conversion()
                return

            file_name = os.path.basename(file_path)
            self.update_status(f"変換中: {file_name} ({i + 1}/{total_files})")

            try:
                output_path = self.convert_avif_to_png(file_path)
                success_files.append(output_path)
            except Exception as e:
                failed_files.append((file_path, str(e)))

            progress = int(((i + 1) / total_files) * 100)
            self.update_progress(progress)

        # 失敗したファイルの再トライ
        if failed_files and not self.cancel_flag:
            self.update_status(f"再トライ中: {len(failed_files)}個のファイル")

            retry_failed = []
            for i, (file_path, error) in enumerate(failed_files):
                if self.cancel_flag:
                    self.update_status("キャンセルされました")
                    self.finish_conversion()
                    return

                file_name = os.path.basename(file_path)
                self.update_status(f"再トライ中: {file_name} ({i + 1}/{len(failed_files)})")

                try:
                    output_path = self.convert_avif_to_png(file_path)
                    success_files.append(output_path)
                except Exception as e:
                    retry_failed.append(f"{file_name}: {str(e)}")

            if retry_failed:
                error_msg = "変換に失敗したファイル:\n" + "\n".join(retry_failed)
                self.root.after(0, lambda: messagebox.showerror("エラー", error_msg))

        if not self.cancel_flag:
            self.update_progress(100)
            self.update_status(f"完了: {len(success_files)}個のファイルを変換しました")

            if success_files:
                output_dir = os.path.dirname(success_files[0])
                self.root.after(0, lambda: messagebox.showinfo(
                    "完了",
                    f"{len(success_files)}個のファイルを変換しました。\n\n保存先: {output_dir}"
                ))

        self.finish_conversion()

    def convert_avif_to_png(self, input_path):
        """AVIFファイルをPNGに変換"""
        # 入力ファイルのパス情報を取得
        input_file = Path(input_path)
        input_dir = input_file.parent

        # convertディレクトリを作成
        convert_dir = input_dir / "convert"
        convert_dir.mkdir(exist_ok=True)

        # 出力ファイル名を生成（convertディレクトリ内）
        output_path = convert_dir / input_file.with_suffix('.png').name

        # 画像を開いて変換
        with Image.open(input_path) as img:
            # RGBAモードに変換（透過対応）
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # PNGとして保存
            img.save(output_path, 'PNG', optimize=True)

        return str(output_path)

    def cancel_conversion(self):
        self.cancel_flag = True
        self.cancel_button.config(state=tk.DISABLED)

    def reset(self):
        if self.converting:
            return

        self.files = []
        self.file_info_label.config(text="選択されたファイル: 0個")
        self.progress_bar['value'] = 0
        self.progress_label.config(text="進捗: 0%")
        self.status_label.config(text="")
        self.convert_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)

    def update_progress(self, value):
        self.root.after(0, lambda: self.progress_bar.config(value=value))
        self.root.after(0, lambda: self.progress_label.config(text=f"進捗: {value}%"))

    def update_status(self, message):
        self.root.after(0, lambda: self.status_label.config(text=message))

    def finish_conversion(self):
        self.converting = False
        self.root.after(0, lambda: self.convert_button.config(state=tk.NORMAL if self.files else tk.DISABLED))
        self.root.after(0, lambda: self.cancel_button.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.reset_button.config(state=tk.NORMAL if self.files else tk.DISABLED))


def main():
    root = TkinterDnD.Tk()
    app = AvifToPngConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
