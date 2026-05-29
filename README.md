# rpimusicbox

A small project to build a music box using the PCM5102A DAC module and headphones on Raspberry Pi 4B.

树莓派音乐盒项目 —— 使用 PCM5102A DAC 模块和耳机在树莓派 4B 上搭建一个 MP3 播放器。

---

## 一、硬件连接 / Hardware Wiring

### PCM5102A DAC 模块与树莓派 4B 引脚连接
### PCM5102A DAC Module to Raspberry Pi 4B Pinout

| PCM5102A | 树莓派 4B / RPi 4B | 说明 / Description |
|---------|-------------------|-------------------|
| VIN | 3.3V (Pin 1) | 供电 / Power |
| GND | GND (Pin 6) | 地线 / Ground |
| BCK | GPIO 18 (Pin 12) | 位时钟 / Bit Clock |
| DIN | GPIO 21 (Pin 40) | 数据输入 / Data In |
| LCK | GPIO 19 (Pin 35) | 左右时钟 / LR Clock |

> **注意 / Note:** 不同厂商的 PCM5102A 模块引脚命名可能略有差异（如 SCK、BCK、DATA、LCK 等），请对照您的模块丝印连接。
> Pin names may vary by manufacturer (e.g., SCK, BCK, DATA, LCK). Refer to your module's silkscreen labels.

---

## 二、系统配置 / System Configuration

### 1. 启用 HiFiBerry DAC 设备树覆盖
### Enable HiFiBerry DAC Device Tree Overlay

编辑 `/boot/config.txt`：
Edit `/boot/config.txt`:

```bash
sudo nano /boot/config.txt
```

在文件末尾添加以下行（如果已有 `dtparam=audio=on`，建议注释掉）：
Add the following line at the end (comment out `dtparam=audio=on` if it exists):

```ini
dtoverlay=hifiberry-dac
```

保存后重启树莓派：
Save and reboot:

```bash
sudo reboot
```

### 2. 验证 DAC 是否识别
### Verify DAC Recognition

重启后运行：
After reboot, run:

```bash
aplay -l
```

您应该能看到类似 `snd_rpi_hifiberry_dac` 的声卡设备。
You should see a sound card like `snd_rpi_hifiberry_dac`.

---

## 三、环境搭建与软件安装 / Environment Setup & Software Installation

### 1. 更新系统
### Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. 安装所需软件包
### Install Required Packages

根据 `rpimusicbox.py`，程序依赖以下组件：
According to `rpimusicbox.py`, the following components are required:

```bash
# Python 3 和 tkinter（通常树莓派系统已预装）
# Python 3 and tkinter (usually pre-installed on Raspberry Pi OS)
sudo apt install python3 python3-tk

# 音频播放器 mpg123
# Audio player mpg123
sudo apt install mpg123

# PulseAudio 及其控制工具（用于音量调节）
# PulseAudio and control tools (for volume control)
sudo apt install pulseaudio pulseaudio-utils
```

### 3. 检查 PulseAudio 是否运行
### Check if PulseAudio is Running

```bash
pulseaudio --check || pulseaudio --start
```

### 4. 确认音频输出 Sink ID
### Confirm Audio Output Sink ID

程序中默认使用 `sink_id = "58"`，但实际 ID 可能不同。请运行：
The code uses `sink_id = "58"` by default, but the actual ID may differ. Run:

```bash
pactl list sinks short
```

输出示例 / Example output:
```
0	alsa_output.platform-bcm2835_audio.analog-stereo	module-alsa-card.c	s16le 2ch 44100Hz	SUSPENDED
1	alsa_output.platform-soc_sound.analog-stereo	module-alsa-card.c	s16le 2ch 44100Hz	IDLE
```

如果 DAC 对应的 Sink ID 不是 `58`，请修改 `rpimusicbox.py` 中的：
If your DAC's Sink ID is not `58`, modify this line in `rpimusicbox.py`:

```python
self.sink_id = "58"   # 改为您的实际 ID / Change to your actual ID
```

---

## 四、准备音乐文件 / Prepare Music Files

将 `.mp3` 文件放入树莓派的 `~/Music` 目录：
Place `.mp3` files into the `~/Music` directory:

```bash
mkdir -p ~/Music
# 通过 SCP、U盘或其他方式将 MP3 文件复制到该目录
# Copy MP3 files via SCP, USB drive, or other methods
```

---

## 五、运行程序 / Run the Program

```bash
cd /home/pi/rpimusicbox
python3 rpimusicbox.py
```

### 界面功能说明 / UI Features

| 功能 / Feature | 说明 / Description |
|--------------|-------------------|
| 歌曲列表 / Song List | 显示 `~/Music` 中的 MP3 文件 / Displays MP3 files in `~/Music` |
| 双击播放 / Double-click | 双击列表中的歌曲即可播放 / Double-click a song to play |
| 上一曲/下一曲 / Prev/Next | 切换歌曲 / Switch tracks |
| 单曲循环 / Single Loop | 重复播放当前歌曲 / Repeat current song |
| 列表循环 / All Loop | 循环播放整个列表 / Loop entire playlist |
| 音量滑块 / Volume Slider | 通过 `pactl` 调节系统音量（0-100%）/ Adjust system volume via `pactl` (0-100%) |
| 刷新 / Refresh | 重新扫描 `~/Music` 目录 / Rescan `~/Music` directory |

---

## 六、常见问题排查 / Troubleshooting

| 问题 / Problem | 解决方案 / Solution |
|-------------|-------------------|
| 没有声音 / No sound | 检查接线；确认 `aplay -l` 能识别 DAC；尝试用 `speaker-test -c2` 测试 / Check wiring; verify DAC appears in `aplay -l`; test with `speaker-test -c2` |
| 音量调节无效 / Volume not working | 运行 `pactl list sinks short` 确认正确的 Sink ID 并修改代码 / Run `pactl list sinks short` and update `sink_id` in the code |
| 无法启动 GUI / GUI won't start | 确保在桌面环境或 VNC 中运行；安装 `python3-tk` / Run in desktop environment or VNC; install `python3-tk` |
| mpg123 报错 / mpg123 error | 确认文件是有效的 MP3 格式；尝试命令行 `mpg123 file.mp3` 单独测试 / Ensure valid MP3 format; test with `mpg123 file.mp3` from command line |

---

## 七、命令行快速测试 / Quick Command Line Test

在运行 GUI 之前，建议先用命令行测试 DAC 是否正常工作：
Before running the GUI, test the DAC via command line:

```bash
# 生成测试音调
# Generate test tone
speaker-test -c2 -t sine -f 1000

# 或者直接播放 MP3
# Or play MP3 directly
mpg123 ~/Music/your_song.mp3
```

如果命令行能正常出声，说明硬件和驱动配置正确，此时再运行 `rpimusicbox.py` 即可。
If command-line playback works, your hardware and drivers are correctly configured, and `rpimusicbox.py` should work fine.

## UI效果
![rpimusicbox](./rpiMusicBox.png)_
