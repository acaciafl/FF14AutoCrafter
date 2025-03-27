# FF14のクラフト作業を自動化するスクリプト
# コマンドを入力するオペレーションをTSVからすべて読み込む
# 読み込んだオペレーションをTSV2行目から順番に実行する（1行目はカラムの名前記入のみ）
# 1列目は入力するキー、2列目次のキーを入力するまでの待機時間（秒）
# Argumentの数値を受け取り、その数値分だけ一連のオペレーションを繰り返す
import os
import sys
import csv
import time
import pyautogui
from dotenv import load_dotenv

load_dotenv()
env_data = dict(os.environ)
# Initialize constants from .env
FF14_INIT_DISPLAY_CLICK_X = int(env_data["FF14_INIT_DISPLAY_CLICK_X"])
FF14_INIT_DISPLAY_CLICK_Y = int(env_data["FF14_INIT_DISPLAY_CLICK_Y"])

FF14_DISPLAY_WIDTH = int(env_data["FF14_DISPLAY_WIDTH"])
FF14_DISPLAY_HEIGHT = int(env_data["FF14_DISPLAY_HEIGHT"])

FF14_OK_BUTTON = env_data["FF14_OK_BUTTON"]

CRAFT_SUCCESS_WAIT_TIME = 3
CRAFT_START_WAIT_TIME = 1
NUM_OF_PRESS_OK_BUTTON = 3

preparation_info_text = """
【事前準備】
・Windows版のFF14をウィンドウフルスクリーンで起動していること
・.envファイルに記載されているボタンを登録済みであること
・ジョブがクラフターであること
・実行したい製作マクロ、または製作アクションがtsvファイルに記載されていること
・製作ウィンドウから製作開始ボタンを押下し、クラフト態勢に入っていること
"""


def read_tsv_file(file_path):
    """
    TSVファイルを読み込み、オペレーションのリストを返す
    Tupleのリストで、各Tupleはキーと待機時間のペア

    Parameters
    ----------
    file_path : str
        ファイルパス
    """
    operations = []

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)  # 1行目はカラムの名前なので読み飛ばす
        for row in reader:
            key = str(row[0])
            wait_time = float(row[1])
            operations.append((key, wait_time))

    return operations


def execute_operation(key, wait_time):
    """
    クラフトオペレーション実行

    Parameters
    ----------
    key : str
        入力するキー
    wait_time : float
        次のキーを入力するまでの待機時間（秒）
    """
    # キーを入力する
    pyautogui.press(key)
    # 待機時間だけ待つ
    time.sleep(wait_time)


if __name__ == "__main__":

    # 引数のTSVファイル名、数値を受け取る
    try:
        tsv_file_name = sys.argv[1]
        repeat_count = int(sys.argv[2])
        if repeat_count <= 0:
            raise ValueError
    except:
        print("引数には1以上の整数を指定してください")
        sys.exit(1)

    try:
        operations = read_tsv_file(tsv_file_name)

        print(preparation_info_text)
        print("==============実行するキー入力の順番、待機時間==============")
        for operation in operations:
            key, wait_time = operation
            print(f"キー: {key}, 入力後の待機時間: {wait_time}秒")

    except Exception as e:
        print("operation.tsvの読み込みに失敗しました。tsvの内容を確認してください")
        print(e)
        sys.exit(1)

    try:
        print(preparation_info_text)
        print(f"上記オペレーションを{repeat_count}回繰り返します。事前準備の確認をしてください。")
        print("実行しますか？(y/n)")
        answer = input()
        if answer != "y":
            print("処理を中断します")
            sys.exit(1)

        print("==============オペレーション実行開始==============")

        # FF14ウィンドウをアクティブにする
        pyautogui.FAILSAFE = False
        init_x = int(FF14_INIT_DISPLAY_CLICK_X)
        init_y = 0  # 画面右上をクリックするため、y座標は0
        pyautogui.click(init_x, init_y, interval=1.0)
        # FAILSAFEに引っかからないように、FF14のウィンドウの真ん中にマウスカーソルを移動する
        pyautogui.click(int(FF14_DISPLAY_WIDTH) / 2, 0, interval=1.0)
        pyautogui.FAILSAFE = True  # FF14のウィンドウをアクティブにした後は、FAILSAFEをTrueに戻す
        pyautogui.PAUSE = 0.5  # クリック後の待機時間

        for i in range(repeat_count):
            print(f"第{i+1}回目")
            for operation in operations:
                key, wait_time = operation
                execute_operation(key, wait_time)

            print(f"第{i+1}回目のクラフトが終了しました。")

            # クラフト成功
            if i < repeat_count - 1:
                # 製作選択ウィンドウが表示されるまでの待機時間
                time.sleep(CRAFT_SUCCESS_WAIT_TIME)

                # 製作開始ボタンを押すため、決定キーを3回押す
                for _ in range(NUM_OF_PRESS_OK_BUTTON):
                    pyautogui.press(FF14_OK_BUTTON)

                # 製作開始までの待機時間
                time.sleep(CRAFT_START_WAIT_TIME)

        print("==============オペレーション実行終了==============")

    except Exception as e:
        print("何らかのエラーが発生したため、AutoCrafterを終了します。")
        print(e)
        sys.exit(1)
