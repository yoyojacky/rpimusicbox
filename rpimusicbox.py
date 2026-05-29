#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
树莓派 MP3 播放器 - 使用 tkinter + mpg123 + pactl
支持 PCM5102A I2S DAC 输出
"""

import tkinter as tk
import subprocess
import os
import glob
import threading

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("树莓派 MP3 播放器")
        self.root.geometry("500x450")
        self.root.configure(bg="#2c3e50")
        
        self.current_process = None
        self.music_dir = os.path.expanduser("~/Music")
        self.sink_id = "58"
        
        self.play_mode = "normal"
        self.current_index = -1
        self.mp3_files = []
        self.is_playing = False
        
        self.create_ui()
        self.load_songs()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_ui(self):
        tk.Label(
            self.root, 
            text="树莓派 MP3 播放器", 
            font=("Arial", 18, "bold"),
            bg="#2c3e50", 
            fg="#ecf0f1"
        ).pack(pady=10)
        
        self.now_playing = tk.Label(
            self.root,
            text="当前未播放",
            font=("Arial", 12),
            bg="#2c3e50",
            fg="#3498db",
            wraplength=450
        )
        self.now_playing.pack(pady=5)
        
        self.mode_label = tk.Label(
            self.root,
            text="模式: 顺序播放",
            font=("Arial", 10),
            bg="#2c3e50",
            fg="#f39c12"
        )
        self.mode_label.pack(pady=2)
        
        list_frame = tk.Frame(self.root, bg="#2c3e50")
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.song_list = tk.Listbox(
            list_frame,
            font=("Arial", 11),
            bg="#34495e",
            fg="#ecf0f1",
            selectbackground="#3498db",
            yscrollcommand=scrollbar.set,
            height=8
        )
        self.song_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.song_list.yview)
        
        self.song_list.bind("<Double-Button-1>", lambda e: self.play_selected())
        
        # 播放控制按钮
        btn_frame = tk.Frame(self.root, bg="#2c3e50")
        btn_frame.pack(pady=5)
        
        tk.Button(
            btn_frame,
            text="上一曲",
            font=("Arial", 11, "bold"),
            bg="#3498db",
            fg="white",
            width=10,
            command=self.play_prev
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            btn_frame,
            text="播放",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            width=8,
            command=self.play_selected
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            btn_frame,
            text="停止",
            font=("Arial", 11, "bold"),
            bg="#e74c3c",
            fg="white",
            width=8,
            command=self.stop
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            btn_frame,
            text="下一曲",
            font=("Arial", 11, "bold"),
            bg="#3498db",
            fg="white",
            width=10,
            command=self.play_next
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            btn_frame,
            text="刷新",
            font=("Arial", 11),
            bg="#f39c12",
            fg="white",
            width=8,
            command=self.load_songs
        ).pack(side=tk.LEFT, padx=3)
        
        # 循环模式按钮
        mode_frame = tk.Frame(self.root, bg="#2c3e50")
        mode_frame.pack(pady=5)
        
        self.single_btn = tk.Button(
            mode_frame,
            text="单曲循环: 关",
            font=("Arial", 10),
            bg="#7f8c8d",
            fg="white",
            width=12,
            command=self.toggle_single_loop
        )
        self.single_btn.pack(side=tk.LEFT, padx=3)
        
        self.all_btn = tk.Button(
            mode_frame,
            text="列表循环: 关",
            font=("Arial", 10),
            bg="#7f8c8d",
            fg="white",
            width=12,
            command=self.toggle_all_loop
        )
        self.all_btn.pack(side=tk.LEFT, padx=3)
        
        # 音量控制
        vol_frame = tk.Frame(self.root, bg="#2c3e50")
        vol_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(
            vol_frame,
            text="音量:",
            font=("Arial", 12),
            bg="#2c3e50",
            fg="#ecf0f1"
        ).pack(side=tk.LEFT)
        
        self.volume_var = tk.IntVar(value=30)
        self.volume_slider = tk.Scale(
            vol_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            length=300,
            bg="#2c3e50",
            fg="#ecf0f1",
            highlightthickness=0,
            troughcolor="#34495e",
            activebackground="#3498db",
            variable=self.volume_var,
            command=self.on_volume_change
        )
        self.volume_slider.pack(side=tk.LEFT, padx=10)
        
        self.vol_percent = tk.Label(
            vol_frame,
            text="30%",
            font=("Arial", 12),
            bg="#2c3e50",
            fg="#ecf0f1",
            width=5
        )
        self.vol_percent.pack(side=tk.LEFT)
        
        self.status = tk.Label(
            self.root,
            text=f"音乐目录: {self.music_dir}",
            font=("Arial", 10),
            bg="#1a252f",
            fg="#95a5a6",
            anchor=tk.W
        )
        self.status.pack(fill=tk.X, side=tk.BOTTOM)
    
    def load_songs(self):
        self.song_list.delete(0, tk.END)
        self.mp3_files = []
        
        if not os.path.exists(self.music_dir):
            self.song_list.insert(tk.END, "Music 目录不存在")
            return
        
        self.mp3_files = glob.glob(os.path.join(self.music_dir, "*.mp3"))
        self.mp3_files.sort(key=lambda x: os.path.basename(x).lower())
        
        if not self.mp3_files:
            self.song_list.insert(tk.END, "没有找到 MP3 文件")
            return
        
        for f in self.mp3_files:
            self.song_list.insert(tk.END, os.path.basename(f))
    
    def get_selected_file(self):
        selection = self.song_list.curselection()
        if not selection:
            return None
        self.current_index = selection[0]
        return self.mp3_files[self.current_index]
    
    def play_file(self, filepath, index=None):
        if not filepath or not os.path.exists(filepath):
            return
        
        self.stop()
        self.is_playing = True
        
        if index is not None:
            self.current_index = index
        
        try:
            self.current_process = subprocess.Popen(
                ["mpg123", filepath],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.now_playing.config(text=f"正在播放: {os.path.basename(filepath)}")
            self.status.config(text=f"PID: {self.current_process.pid} | 模式: {self.play_mode}")
            
            threading.Thread(target=self.monitor_playback, daemon=True).start()
            
        except Exception as e:
            self.status.config(text=f"错误: {e}")
            self.is_playing = False
    
    def monitor_playback(self):
        if self.current_process:
            self.current_process.wait()
            
            if not self.is_playing:
                return
            
            if self.play_mode == "single":
                self.root.after(500, lambda: self.play_by_index(self.current_index))
            elif self.play_mode == "all":
                next_index = (self.current_index + 1) % len(self.mp3_files)
                self.root.after(500, lambda: self.play_by_index(next_index))
    
    def play_by_index(self, index):
        if 0 <= index < len(self.mp3_files):
            self.song_list.selection_clear(0, tk.END)
            self.song_list.selection_set(index)
            self.song_list.see(index)
            self.play_file(self.mp3_files[index], index)
    
    def play_selected(self):
        filepath = self.get_selected_file()
        if filepath:
            self.play_file(filepath)
        else:
            self.status.config(text="请先选择一首歌曲")
    
    def play_prev(self):
        if not self.mp3_files:
            self.status.config(text="没有歌曲")
            return
        
        if self.current_index <= 0:
            prev_index = len(self.mp3_files) - 1
        else:
            prev_index = self.current_index - 1
        
        self.play_by_index(prev_index)
    
    def play_next(self):
        if not self.mp3_files:
            self.status.config(text="没有歌曲")
            return
        
        next_index = (self.current_index + 1) % len(self.mp3_files)
        self.play_by_index(next_index)
    
    def toggle_single_loop(self):
        if self.play_mode == "single":
            self.play_mode = "normal"
            self.single_btn.config(text="单曲循环: 关", bg="#7f8c8d")
            self.all_btn.config(state=tk.NORMAL)
            self.mode_label.config(text="模式: 顺序播放")
        else:
            self.play_mode = "single"
            self.single_btn.config(text="单曲循环: 开", bg="#e74c3c")
            self.all_btn.config(state=tk.DISABLED)
            self.mode_label.config(text="模式: 单曲循环")
        self.status.config(text=f"当前模式: {self.play_mode}")
    
    def toggle_all_loop(self):
        if self.play_mode == "all":
            self.play_mode = "normal"
            self.all_btn.config(text="列表循环: 关", bg="#7f8c8d")
            self.single_btn.config(state=tk.NORMAL)
            self.mode_label.config(text="模式: 顺序播放")
        else:
            self.play_mode = "all"
            self.all_btn.config(text="列表循环: 开", bg="#e74c3c")
            self.single_btn.config(state=tk.DISABLED)
            self.mode_label.config(text="模式: 列表循环")
        self.status.config(text=f"当前模式: {self.play_mode}")
    
    def stop(self):
        self.is_playing = False
        
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
            try:
                self.current_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.current_process.kill()
        
        self.current_process = None
        self.now_playing.config(text="当前未播放")
        self.status.config(text="已停止")
    
    def on_volume_change(self, value):
        vol = int(value)
        self.vol_percent.config(text=f"{vol}%")
        
        try:
            subprocess.run(
                ["pactl", "set-sink-volume", self.sink_id, f"{vol}%"],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError:
            pass
    
    def on_close(self):
        self.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    MusicPlayer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
