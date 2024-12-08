# 跳一跳模拟器

本项目是一个基于 OpenCV + YOLOv5 的跳一跳模拟器，可以自动识别微信电脑端跳一跳小程序，并实现自动跳跃、失败自动重开等功能。

## 使用方法

1. 将本仓库克隆到本地，并在根目录下克隆 YOLOv5 仓库

```bash
git clone https://github.com/cheng1559/jump-jump.git
cd jump-jump
git clone https://github.com/ultralytics/yolov5.git
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 打开跳一跳小程序，点击开始游戏按钮

4. 运行程序

```bash
python main.py
```

## 注意事项

- 本项目没有考虑到屏幕分辨率适配问题，如果效果不好，请自行调整 `main.py` 中的跳跃参数。

- 本项目只能识别默认皮肤的棋子，如果使用了其他皮肤，需要将 `chess.png` 替换为对应皮肤的棋子图片。

- 在游戏失败后，程序会自动点击重新开始按钮，并将失败前的十张图片保存到 `death-replay` 目录下，以便调试。

- 本项目仅供学习交流使用，切勿用于非法用途。
