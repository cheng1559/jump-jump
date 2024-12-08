import pyautogui
import pygetwindow as gw
import cv2
import numpy as np
import time
import os
import torch
import random

window_title = '跳一跳'
death_replay_path = 'death-replay'
interval = 1.5
max_fail_count = 3
model = torch.hub.load('./yolov5', 'custom', path='best.pt', source='local')


fail_count = 0
prev_imgs = []


def capture_window(window_title):
    window = None
    for win in gw.getWindowsWithTitle(window_title):
        if window_title in win.title:
            window = win
            break

    if window is None:
        print(f"{window_title} not found")
        return None

    x, y, width, height = window.left, window.top, window.width, window.height
    screenshot = pyautogui.screenshot(region=(x + 10, y + height // 4, width - 20, height // 2))
    return np.array(screenshot), (x, y)


def recognize_chess(img):
    template_path = "chess.png"
    threshold = 0.8
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        return None
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    template_h, template_w = template.shape[:2]
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    for pt in zip(*locations[::-1]):
        center_x = pt[0] + template_w // 2
        center_y = pt[1] + template_h
        return (center_x, center_y - 10)
    return None


def draw_position(img, center):
    center_x, center_y = center
    cv2.circle(img, (center_x, center_y), 2, (0, 0, 255), -1)
    cv2.line(img, (center_x, 0), (center_x, img.shape[0]), (0, 255, 0), 1)
    cv2.line(img, (0, center_y), (img.shape[1], center_y), (0, 255, 0), 1)
    cv2.putText(img, f"({center_x}, {center_y})", (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)


def get_target(img):
    results = model(img)
    detections = results.xyxy[0]

    topmost_y = float('inf')
    topmost_center = None
    for *box, conf, cls in detections:
        x1, y1, x2, y2 = map(int, box)
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        if y1 < topmost_y:
            topmost_y = y1
            topmost_center = (center_x, center_y)

    return topmost_center


def jump(distance, x, y):
    press_time = 0.0024 * distance - 0.06
    press_time = min(press_time, 1)
    press_time = max(press_time, 0.02)
    print(f"distance: {distance} press time: {press_time}")

    pyautogui.moveTo(x, y)
    pyautogui.mouseDown()
    time.sleep(press_time)
    pyautogui.mouseUp()


def draw_img(img):
    cv2.imshow('', img)
    cv2.waitKey(1)


def process():
    global fail_count
    result = capture_window(window_title)
    if result is None:
        fail_count += 1
        return

    img, (x, y) = result
    result = recognize_chess(img)
    target = get_target(img)

    if not result or not target:
        print("no target")
        fail_count += 1
        return

    center_x, center_y = result
    distance = ((center_x - target[0]) ** 2 + (center_y - target[1]) ** 2) ** 0.5
    jump(distance, x + random.randint(100, 300), y + random.randint(100, 300))

    if len(prev_imgs) > 10:
        prev_imgs.pop(0)
    prev_imgs.append(img.copy())

    print(f"chess pos: ({center_x}, {center_y})")
    print(f"target: {target}")
    
    draw_position(img, (center_x, center_y))
    draw_position(img, target)
    
    draw_img(img)


def restart():
    _, (x, y) = capture_window(window_title)
    pyautogui.moveTo(x + 300, y + 800)
    pyautogui.mouseDown()
    time.sleep(0.1)
    pyautogui.mouseUp()
    global fail_count
    fail_count = 0

    if os.path.exists(death_replay_path):
        os.mkdir(death_replay_path)
    for img in prev_imgs:
        t = time.time()
        cv2.imwrite(f"./death-replay/image_{t}.jpg", img)
        print(f"save image_{t}.jpg")
    prev_imgs.clear()


if __name__ == "__main__":
    while True:
        process()
        time.sleep(interval)
        if fail_count >= max_fail_count:
            restart()