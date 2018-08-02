import datetime
import win32api
import win32con
import win32gui
import time
import cv2
import numpy as np
from PIL import ImageGrab
from config import *
import pytesseract

assets = {
    "accept_task": cv2.imread("./assets/accept_task.png"),
    "battle_action": cv2.imread("./assets/battle_action.png")
}

window_title = None

# 获取窗体坐标位置(左上)


def getGameWindowRect():
  # FindWindow(lpClassName=None, lpWindowName=None)  窗口类名 窗口标题名
  window = win32gui.FindWindow(None, window_title)
  if not window:
    return None

  # 定位到游戏窗体
  win32gui.SetForegroundWindow(window)  # 将窗体顶置
  rect = win32gui.GetWindowRect(window)
  print("定位到游戏窗体：", rect)
  return (rect[0] + MARGIN_LEFT, rect[1] + MARGIN_HEIGHT, rect[0] + MARGIN_LEFT + GAME_WIDTH, rect[1] + MARGIN_HEIGHT + GAME_HEIGHT)

# 获取一张游戏截图


def getGameImage(bbox, save=False):
  st = time.clock()
  print('捕获屏幕截图...')
  scim = ImageGrab.grab(bbox)  # 屏幕截图，获取到的是Image类型对象
  img = np.array(scim.getdata(), dtype='uint8').reshape(
      GAME_HEIGHT, GAME_WIDTH, 3)
  if save:
    scim.save('game.png')
  # cv2img = cv2.imread("game.png")  # opencv 读取，拿到的是ndarray存储的图像
  # cv2.imwrite("game_cv2.png", cv2img)
  print('捕获屏幕截图完成，耗时', time.clock() - st, '毫秒')
  return img


def cropSecondTask(game_image, save=False):
  img = game_image[SECOND_TASK_RECT[1]:SECOND_TASK_RECT[3],
                   SECOND_TASK_RECT[0]:SECOND_TASK_RECT[2]]
  if save:
    cv2.imwrite("second_task.png", img)
  return img


def cropBattleAction(game_image, save=False):
  img = game_image[ACTION_RECT[1]:ACTION_RECT[3],
                   ACTION_RECT[0]:ACTION_RECT[2]]
  if save:
    cv2.imwrite("battle_action.png", img)
  return img


def cropAcceptTask(game_image, save=False):
  img = game_image[ACCEPT_TASK_RECT[1]:ACCEPT_TASK_RECT[3],
                   ACCEPT_TASK_RECT[0]:ACCEPT_TASK_RECT[2]]
  if save:
    cv2.imwrite("accept_task.png", img)
  return img


def nearlyEqual(a, b):
  if a.size != b.size:
    return False

  size = a.size
  same = np.sum(a == b)
  print("same: ", same, "different: ", (size - same) / size)
  return (size - same) / size < 0.01


def isForeground():
  text = win32gui.GetWindowText(win32gui.GetForegroundWindow())
  return text == window_title


def click(x, y):
  if x == None or y == None:
    return

  if x <= 0 or y <= 0:
    return

  foreground = isForeground()
  if not foreground:
    print('游戏窗口不在前台')

  if foreground or STOP_WHEN_BACKGROUND == False:
    game_rect = getGameWindowRect()
    x = game_rect[0] + x
    y = game_rect[1] + y

    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    time.sleep(TIME_INTERVAL)


def act(action):
  if action == "accept_task":
    print('接受委托')
    x = ACCEPT_TASK_RECT[0]
    y = ACCEPT_TASK_RECT[1]
  elif action == "auto_battle":
    print('开启自动战斗')
    # TODO:
  elif action == "second_task":
    print('寻路第二个任务')
    x = SECOND_TASK_RECT[0]
    y = SECOND_TASK_RECT[1]

  click(x, y)


def isAcceptTask(img):
  string = pytesseract.image_to_string(img, lang='chi_sim')
  print('ocr accept_task', string)
  return string == '接受委托'

window_title = None
window_titles = [WINDOW_TITLE, WINDOW_TITLE_2]

if __name__ == '__main__':
  frame = 0
  while MAX_FRAME != 0:
    frame += 1

    for window_title in window_titles:
      # 1、定位游戏窗体
      game_rect = getGameWindowRect()
      time.sleep(1)
      if game_rect == None:
        continue

      # 从屏幕截图一张，通过opencv读取
      game_image = getGameImage(game_rect, save=True)

      second_task = cropSecondTask(game_image, save=True)
      battle_action = cropBattleAction(game_image, save=True)
      accept_task = cropAcceptTask(game_image, save=True)

      if isAcceptTask(accept_task):
        print('提示框：接受委托')
        act("accept_task")
        act("second_task")
        act("second_task")
      elif nearlyEqual(battle_action, assets["battle_action"]):
        print('自动战斗中')
      else:
        print('默认寻路第二个任务')
        act("second_task")

      time.sleep(3)
      print('{}: 完成第{}次运行'.format(datetime.datetime.now(), frame))

    if MAX_FRAME > 0 and frame >= MAX_FRAME:
      break

  # 7、消除完成，释放资源。
  print('优雅的跑路')
  cv2.waitKey(0)
  cv2.destroyAllWindows()
