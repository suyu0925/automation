import win32gui
import time
import cv2
import numpy as np
from PIL import ImageGrab
from config import *

# 获取窗体坐标位置(左上)


def getGameWindowRect():
  # FindWindow(lpClassName=None, lpWindowName=None)  窗口类名 窗口标题名
  window = win32gui.FindWindow(None, WINDOW_TITLE)
  # 没有定位到游戏窗体
  while not window:
    print('定位游戏窗体失败，5秒后重试...')
    time.sleep(5)
    window = win32gui.FindWindow(None, WINDOW_TITLE)
  # 定位到游戏窗体
  win32gui.SetForegroundWindow(window)  # 将窗体顶置
  rect = win32gui.GetWindowRect(window)
  print("定位到游戏窗体：", rect)
  return (rect[0] + MARGIN_LEFT, rect[1] + MARGIN_HEIGHT, rect[0] + MARGIN_LEFT + GAME_WIDTH, rect[1] + MARGIN_HEIGHT + GAME_HEIGHT)

# 获取一张游戏截图


def getGameImage(bbox):
  print('捕获屏幕截图...')
  scim = ImageGrab.grab(bbox)  # 屏幕截图，获取到的是Image类型对象
  img = np.array(scim.getdata(), dtype='uint8').reshape(
      GAME_WIDTH, GAME_HEIGHT, 3)
  # scim.save('game.png')
  # cv2img = cv2.imread("game.png")  # opencv 读取，拿到的是ndarray存储的图像
  # cv2.imwrite("game_cv2.png", cv2img)
  return img


if __name__ == '__main__':
  # 1、定位游戏窗体
  game_rect = getGameWindowRect()
  time.sleep(1)

  # 2、从屏幕截图一张，通过opencv读取
  st = time.clock()
  game_image = getGameImage(game_rect)
  print('grab image cost', time.clock() - st, 'ms')

  # 7、消除完成，释放资源。
  print('优雅的跑路')
  cv2.waitKey(0)
  cv2.destroyAllWindows()
