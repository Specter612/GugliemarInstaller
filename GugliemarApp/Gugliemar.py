from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.video import Video
from kivy.animation import Animation
import subprocess
import webbrowser
import json
import os
DIRECT_SSID = ""
DIRECT_PASSWORD = ""
DATA_FILE = 'credentials.json'
# 画像ボタンのクラス
class ImageButton(ButtonBehavior, Image):
    def __init__(self, img_normal, img_pressed, screen_mgr=None, target_screen_name=None, **kwargs):
        super().__init__(**kwargs) #初期化
        self.img_normal = img_normal #通常時
        self.img_pressed = img_pressed #押されたとき
        self.screen_mgr = screen_mgr #画面遷移
        self.target_screen_name = target_screen_name #画面選択
        self.source = self.img_normal #初期状態

    def on_press(self): #ボタン押されたとき、押された状態のボタン画像に変更
        self.source = self.img_pressed

    def on_release(self): #ボタンが押され、離れたとき元のボタンに戻す
        self.source = self.img_normal
        if self.screen_mgr and self.target_screen_name:
            self.screen_mgr.current = self.target_screen_name

# リンクラベルのクラス
class LinkLabel(ButtonBehavior, Label): #リンク(PDF説明書)を使用するときのクラス
    def __init__(self, link_url, **kwargs):
        super(LinkLabel, self).__init__(**kwargs)
        self.link_url = link_url
        self.markup = True

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            webbrowser.open(self.link_url)
            return True
        return super(LinkLabel, self).on_touch_down(touch)

# 背景色付きスクリーンのクラス
class ColoredScreen(Screen):
    def __init__(self, color, **kwargs):
        super(ColoredScreen, self).__init__(**kwargs)
        with self.canvas.before:
            Color(*color) #RGBA、色と透明度
            self.rect = Rectangle(size=self.size, pos=self.pos) #大きさと位置
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size

#オープニングのクラス
class SplashScreen(Screen):
    def __init__(self, screen_mgr, **kwargs):
        super(SplashScreen, self).__init__(**kwargs)
        self.screen_mgr = screen_mgr

        # グローバル変数の初期化
        global DIRECT_SSID, DIRECT_PASSWORD
        DIRECT_SSID = ''
        DIRECT_PASSWORD = ''

        # credentials.txt からSSIDとパスワードを読み取る
        try:
            with open('credentials.txt', 'r') as file:
                lines = file.readlines()
                if len(lines) >= 2:
                    DIRECT_SSID = lines[0].strip()
                    DIRECT_PASSWORD = lines[1].strip()
                    print(f"SSID: {DIRECT_SSID}, PASSWORD: {DIRECT_PASSWORD}")  # 読み取った内容を確認
        except FileNotFoundError:
            print("credentials.txt が見つかりません")

        # グローバル変数の有無に応じて動画を切り替える
        if DIRECT_SSID and DIRECT_PASSWORD:
            video_source = 'opening.mp4'  # SSIDとパスワードがある場合の動画
            schedule_time = 9  # 9秒後に次の画面に移行
        else:
            video_source = 'opening2.mp4'  # SSIDかパスワードがない場合の動画
            schedule_time = 14  # 14秒後に次の画面に移行

        # Videoウィジェットで動画を再生
        self.video = Video(source=video_source, size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.video.state = 'play'  # 自動再生
        self.video.options = {'eos': 'stop'}  # 動画が終了したら止まる
        self.add_widget(self.video)

        # 固定された時間で次の画面に移行
        Clock.schedule_once(self.switch_to_main_screen, schedule_time)

    def switch_to_main_screen(self, dt=None): #Maunスクリーンに移動
        self.screen_mgr.current = 'MainScreen'

# メインスクリーンのクラス
class MainScreen(ColoredScreen):
    def __init__(self, screen_mgr, **kwargs):
        super(MainScreen, self).__init__(color=(0, 0, 0, 1), **kwargs)
        self.screen_mgr = screen_mgr
        self.layout = FloatLayout()
        self.add_widget(self.layout)
        self.load_credentials()
        self.setup_widgets()
        self.check_credentials()


    def load_credentials(self): #テキストの内容を読み込んで変数に格納する
                global DIRECT_SSID, DIRECT_PASSWORD
                try:
                    with open('credentials.txt', 'r') as file:
                        lines = file.readlines()
                        if len(lines) >= 2:
                            DIRECT_SSID = lines[0].strip()
                            DIRECT_PASSWORD = lines[1].strip()
                        else:
                            DIRECT_SSID = ''
                            DIRECT_PASSWORD = ''
                except FileNotFoundError:
                    DIRECT_SSID = ''
                    DIRECT_PASSWORD = ''

    def check_credentials(self): #接続ボタンの配置
            global DIRECT_SSID, DIRECT_PASSWORD
            if hasattr(self, 'img_btn5'):
                self.remove_img_btn5()  # 既存のimg_btn5があれば削除
            
            if DIRECT_SSID and DIRECT_PASSWORD:
                if not hasattr(self, 'img_btn5'):
                    self.img_btn5 = ImageButton(img_normal='button51.png', img_pressed='button5.png',
                                                screen_mgr=None, target_screen_name=None,
                                                size_hint=(None, None), size=(500, 500), pos_hint={'center_x': 0.5, 'center_y': 0.8})
                    self.img_btn5.bind(on_release=self.start_wifi_direct)
                    self.layout.add_widget(self.img_btn5)
            else:
                if hasattr(self, 'img_btn3'):
                    self.layout.remove_widget(self.img_btn3)
                self.img_btn3 = ImageButton(img_normal='plus.png', img_pressed='plus2.png',
                                            screen_mgr=None, target_screen_name=None,
                                            size_hint=(None, None), size=(70, 70), pos_hint={'center_x': 0.5, 'center_y': 0.8})
                self.img_btn3.bind(on_release=self.show_input_popup)
                self.layout.add_widget(self.img_btn3)

    def remove_img_btn4_and_img_btn5(self): #Delete Dataを選択したときにボタンをどちらも消す
        if hasattr(self, 'img_btn4') and self.img_btn4:
            self.layout.remove_widget(self.img_btn4)
            del self.img_btn4
        else:
            print("")

        # img_btn5 の削除
        if hasattr(self, 'img_btn5') and self.img_btn5:
            self.layout.remove_widget(self.img_btn5)
            del self.img_btn5
        else:
            print("")

    def save_credentials(self): #SSIDとPasswordをテキストファイルに保存
        global DIRECT_SSID, DIRECT_PASSWORD
        with open('credentials.txt', 'w') as file:
            file.write(f"{DIRECT_SSID}\n")
            file.write(f"{DIRECT_PASSWORD}\n")

    def save_credentials(self):
        global DIRECT_SSID, DIRECT_PASSWORD
        with open('credentials.txt', 'w') as file:
            file.write(f"{DIRECT_SSID}\n")
            file.write(f"{DIRECT_PASSWORD}\n")

    def setup_widgets(self): #各ボタンを設置
        img_btn1 = ImageButton(img_normal='gear.png', img_pressed='gear2.png',
                               screen_mgr=self.screen_mgr, target_screen_name='second',
                               size_hint=(None, None), size=(70, 70), pos_hint={'center_x': 0.3, 'center_y': 0.15})
        self.layout.add_widget(img_btn1)

        img_btn2 = ImageButton(img_normal='question.png', img_pressed='question2.png',
                               screen_mgr=self.screen_mgr, target_screen_name='third',
                               size_hint=(None, None), size=(70, 70), pos_hint={'center_x': 0.7, 'center_y': 0.15})
        self.layout.add_widget(img_btn2)

        self.img_btn3 = ImageButton(img_normal='plus.png', img_pressed='plus2.png',
                                    screen_mgr=None, target_screen_name=None,
                                    size_hint=(None, None), size=(70, 70), pos_hint={'center_x': 0.5, 'center_y': 0.8})
        self.img_btn3.bind(on_release=self.show_input_popup)
        self.layout.add_widget(self.img_btn3)

    def show_input_popup(self, instance): #プラスボタンを押したときのSSIDとPasswordを登録するウィジェット
        if hasattr(self, 'input_popup') and self.input_popup:
            self.layout.remove_widget(self.input_popup)

        self.input_popup = FloatLayout(size_hint=(None, None), size=(400, 300), pos_hint={'center_x': 0.5, 'center_y': 0.5})

        # 背景色と角丸の適用
        with self.input_popup.canvas.before:
            Color(0.2, 0.2, 0.2, 1)  # ダークな背景色
            self.rect = RoundedRectangle(size=self.input_popup.size, pos=self.input_popup.pos, radius=[80])
            
            # 上部に青いラインを描画
            Color(0, 0, 0, 0) 
            self.line = Line(
                points=[self.input_popup.x + 10, self.input_popup.top - 10,  # 線の始点
                        self.input_popup.right - 10, self.input_popup.top - 10],  # 線の終点
                width=5
            )
            self.input_popup.canvas.before.add(self.line)

        self.input_popup.bind(pos=self._update_rect, size=self._update_rect)

        # タイトルラベル
        title_label = Label(text="New Gugliemar setup", size_hint=(None, None), size=(260, 40),
                            pos_hint={'center_x': 0.5, 'center_y': 0.8}, color=(1, 1, 1, 1))
        self.input_popup.add_widget(title_label)

        # SSID入力フィールド
        self.ssid_input = TextInput(hint_text='SSID', size_hint=(None, None), size=(300, 40), 
                                    pos_hint={'center_x': 0.5, 'center_y': 0.6}, multiline=False,
                                    background_color=(0.9, 0.9, 0.9, 1), foreground_color=(0, 0, 0, 1))
        self.input_popup.add_widget(self.ssid_input)

        # パスワード入力フィールド
        self.password_input = TextInput(hint_text='Password', size_hint=(None, None), size=(300, 40), 
                                        pos_hint={'center_x': 0.5, 'center_y': 0.4}, multiline=False, 
                                        password=True, background_color=(0.9, 0.9, 0.9, 1), foreground_color=(0, 0, 0, 1))
        self.input_popup.add_widget(self.password_input)

        # OKボタン
        ok_button = Button(text="OK", size_hint=(None, None), size=(100, 40), 
                        pos_hint={'center_x': 0.5, 'center_y': 0.2}, background_color=(0.1, 0.7, 0.9, 1))
        ok_button.bind(on_release=self.on_ok_button_pressed)
        self.input_popup.add_widget(ok_button)

        self.layout.add_widget(self.input_popup)

    def _update_rect(self, *args):
        self.rect.pos = self.input_popup.pos
        self.rect.size = self.input_popup.size

        # Line の位置とサイズを更新
        self.line.points = [
            self.input_popup.x + 10, self.input_popup.top - 10,
            self.input_popup.right - 10, self.input_popup.top - 10
        ]

    def _update_rect(self, instance, value):
        if hasattr(self, 'input_popup') and self.input_popup:
            self.rect.pos = self.input_popup.pos
            self.rect.size = self.input_popup.size
            self.line.points = [self.input_popup.x, self.input_popup.top, 
                                self.input_popup.right, self.input_popup.top]

    def on_ok_button_pressed(self, instance): #OKボタンを押した後、WiFi Directプログラムにつなげるプログラムを起動
        global DIRECT_SSID, DIRECT_PASSWORD
        DIRECT_SSID = self.ssid_input.text
        DIRECT_PASSWORD = self.password_input.text

        self.layout.remove_widget(self.input_popup)  # Properly remove the popup

        self.save_credentials()  # Save the entered data

        # Remove any existing img_btn5 if it exists
        if hasattr(self, 'img_btn5'):
            print("")  # Debug message
            self.remove_img_btn5()
        else:
            print("")  # Debug message

        # Add img_btn4 after the popup is closed
        self.img_btn4 = ImageButton(img_normal='start1.png', img_pressed='start2.png',
                                    screen_mgr=None, target_screen_name=None,
                                    size_hint=(None, None), size=(500, 500), pos_hint={'center_x': 0.5, 'center_y': 0.8})
        self.img_btn4.bind(on_release=self.start_wifi_direct)
        self.layout.add_widget(self.img_btn4)

    def start_wifi_direct(self, instance): #WiFi directプログラム起動
        if hasattr(self, 'error_label') and self.error_label:
            self.layout.remove_widget(self.error_label)

        process = subprocess.Popen(
            ['python', 'wifi_direct_program.py', DIRECT_SSID, DIRECT_PASSWORD],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        return_code = process.returncode

        print(f"Return code: {return_code}")
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")

        if return_code == 0 and 'Failed' not in stdout:
            self.display_success_message("Wi-Fi Direct connection successful!")
        else:
            error_message = "Failed to connect to Wi-Fi Direct."
            if return_code == 2:
                error_message = "Failed to reconnect to home Wi-Fi."
            if stderr:
                error_message += f"\nDetails: {stderr.strip()}"
            if stdout:
                error_message += f"\nDetails: {stdout.strip()}"

            self.display_error_message(error_message)
            Clock.schedule_once(lambda dt: self.remove_img_btn4(instance), 5)

    def display_success_message(self, message): #接続に成功した場合
            success_box = FloatLayout(size_hint=(None, None), size=(500, 500), pos_hint={'center_x': 0.5, 'center_y': 0.5})
            with success_box.canvas.before:
                Color(0, 0.5, 0, 1)  # 緑色
                self.rect = RoundedRectangle(size=success_box.size, pos=success_box.pos, radius=[20])
            
            success_box.bind(pos=self._update_rect, size=self._update_rect)

            success_label = Label(
                text=message,
                color=(1, 1, 1, 1),  # テキスト色を白に
                size_hint=(None, None),
                size=(500, 500),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                text_size=(500, 500),  # テキストのサイズをラベル全体に設定
                halign='center',
                valign='middle'
            )
            success_box.add_widget(success_label)
            self.layout.add_widget(success_box)

            Clock.schedule_once(lambda dt: self.layout.remove_widget(success_box), 4)

    def display_error_message(self, error_message): #接続に失敗した場合
        if hasattr(self, 'error_label') and self.error_label:
            self.layout.remove_widget(self.error_label)

        # エラーメッセージを表示するウィジェットを作成
        error_box = FloatLayout(size_hint=(None, None), size=(500, 500), pos_hint={'center_x': 0.5, 'center_y': 0.5})

        # 背景色とRoundedRectangleの設定
        with error_box.canvas.before:
            Color(0.5, 0, 0.5, 1)  # 紫色
            self.rect = RoundedRectangle(size=error_box.size, pos=error_box.pos, radius=[20])

        # サイズや位置の変更があった場合に呼び出されるメソッド
        error_box.bind(pos=self._update_rect, size=self._update_rect)

        # エラーメッセージを表示するラベル
        error_label = Label(
            text=error_message,
            color=(1, 1, 1, 1),  # 白色
            size_hint=(None, None),
            size=(500, 500),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            text_size=(500, 500),
            halign='center',
            valign='middle'
        )

        # error_boxにエラーメッセージラベルを追加
        error_box.add_widget(error_label)

        # レイアウトにerror_boxを追加
        self.layout.add_widget(error_box)

        # 4秒後にエラーメッセージを削除
        Clock.schedule_once(lambda dt: self.layout.remove_widget(error_box), 4)

    def _update_rect(self, instance, value): #ウィジェットの配置を更新
        # RoundedRectangleのサイズと位置を更新
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def remove_img_btn4(self, instance): #接続に失敗した場合登録しなおすためのプログラム
        if hasattr(self, 'img_btn4') and self.img_btn4:
            self.layout.remove_widget(self.img_btn4)

        error_box = FloatLayout(size_hint=(None, None), size=(500, 500), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        with error_box.canvas.before:
            Color(0.5, 0, 0.5, 1)  
            self.rect = RoundedRectangle(size=error_box.size, pos=error_box.pos, radius=[20])
        
        error_box.bind(pos=self._update_rect, size=self._update_rect)

        error_label = Label(
            text="Connection Failure",
            color=(1, 1, 1, 1),  
            size_hint=(None, None),
            size=(500, 500),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            text_size=(500, 500),  # テキストのサイズをラベル全体に設定
            halign='center',
            valign='middle'
        )
        error_box.add_widget(error_label)
        self.layout.add_widget(error_box)

        Clock.schedule_once(lambda dt: self.layout.remove_widget(error_box), 4)

#セカンドスクリーンのクラス
class SecondScreen(ColoredScreen):
    def __init__(self, screen_mgr, **kwargs):
        super(SecondScreen, self).__init__(color=(0, 0, 0, 1), **kwargs)
        self.screen_mgr = screen_mgr
        self.layout = FloatLayout()
        self.add_widget(self.layout)
        self.setup_widgets()

    def setup_widgets(self):
        img_btn1_1 = ImageButton(img_normal='back.png', img_pressed='back2.png',
                                 screen_mgr=self.screen_mgr, target_screen_name='MainScreen',
                                 size_hint=(None, None), size=(50, 50), pos_hint={'center_x': 0.3, 'center_y': 0.9})
        img_btn1_1.bind(on_release=self.go_back)
        self.layout.add_widget(img_btn1_1)

        delete_button = Button(text='Delete Datas', font_size='24sp', size_hint=(None, None), size=(500, 200),
                               pos_hint={'center_x': 0.5, 'center_y': 0.7})
        delete_button.bind(on_release=self.delete_data)
        self.layout.add_widget(delete_button)

        change_data_button = Button(text='Change Home Data', font_size='24sp', size_hint=(None, None), size=(500, 200),
                                    pos_hint={'center_x': 0.5, 'center_y': 0.3})
        change_data_button.bind(on_release=self.show_change_data_popup)
        self.layout.add_widget(change_data_button)

    def show_change_data_popup(self, instance): #HOME DATAを更新するためのウィジェット
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        ssid_input = TextInput(hint_text='Enter new SSID', multiline=False)
        password_input = TextInput(hint_text='Enter new Password', password=True, multiline=False)
        ok_button = Button(text='OK', size_hint_y=None, height=40)

        layout.add_widget(Label(text='New Home Network Data'))
        layout.add_widget(ssid_input)
        layout.add_widget(password_input)
        layout.add_widget(ok_button)

        popup = Popup(title='Change Home Data', content=layout, size_hint=(0.8, 0.6))
        ok_button.bind(on_release=lambda x: self.update_home_data(ssid_input.text, password_input.text, popup))

        popup.open()

    def update_home_data(self, ssid, password, popup):
        global HOME_SSID, HOME_PASSWORD
        HOME_SSID = ssid
        HOME_PASSWORD = password

        with open('home_credentials.txt', 'w') as file:
            file.write(f"{HOME_SSID}\n{HOME_PASSWORD}")

        popup.dismiss()
        self.show_data_updated_message()

    def show_data_updated_message(self): #HOME DATAを更新したとき
        message_box = BoxLayout(size_hint=(None, None), size=(300, 200),
                                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                padding=[20, 20, 20, 20],  # 内部余白を追加
                                orientation='vertical')    # 縦方向に配置
        
        with message_box.canvas.before:
            Color(0.2, 0.8, 1, 1)  # 背景色（緑）
            rect = RoundedRectangle(size=message_box.size, pos=message_box.pos, radius=[20])
            
            # 背景の位置とサイズをバインドして更新
            message_box.bind(pos=lambda instance, value: setattr(rect, 'pos', value))
            message_box.bind(size=lambda instance, value: setattr(rect, 'size', value))

        # ラベルを中央に配置
        message_label = Label(text='Home network data updated!',
                            size_hint=(None, None),  # size_hintを無効にして明示的にサイズを指定
                            width=message_box.width - 40,  # 幅をBoxLayoutに合わせる（余白を考慮）
                            height=message_box.height - 40,  # 高さを設定
                            text_size=(message_box.width - 40, None),  # テキストサイズを幅に合わせる
                            halign='center', valign='middle',
                            color=(0, 0, 0, 1))
        message_label.bind(size=message_label.setter('text_size'))  # テキストをラベルのサイズに合わせて中央揃え

        message_box.add_widget(message_label)
        
        # メッセージを表示するレイアウトに追加
        self.layout.add_widget(message_box)
        
        # 4秒後にメッセージを削除
        Clock.schedule_once(lambda dt: self.layout.remove_widget(message_box), 4)

    def delete_data(self, instance):
        global DIRECT_SSID, DIRECT_PASSWORD
        DIRECT_SSID = ''
        DIRECT_PASSWORD = ''
        with open('credentials.txt', 'w') as file:
            file.write('\n')  # 空の内容を書き込むことでデータを削除
        self.show_data_deleted_message()
        self.screen_mgr.get_screen('MainScreen').remove_img_btn4_and_img_btn5()
        self.screen_mgr.get_screen('MainScreen').check_credentials()  # 再チェック

        # デバッグ用: 削除後のファイル内容を表示
        with open('credentials.txt', 'r') as file:
            print("Updated credentials.txt content:", file.read())

    def show_data_deleted_message(self): #データを削除したとき
        # 背景色付きのBoxLayoutを作成
        message_box = BoxLayout(size_hint=(None, None), size=(300, 200),
                                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                padding=[20, 20, 20, 20],  # 内部余白を追加
                                orientation='vertical')    # 縦方向に配置
        
        with message_box.canvas.before:
            Color(0.2, 0.5, 1, 1)  
            rect = RoundedRectangle(size=message_box.size, pos=message_box.pos, radius=[20])
            
            # 背景の位置とサイズをバインドして更新
            message_box.bind(pos=lambda instance, value: setattr(rect, 'pos', value))
            message_box.bind(size=lambda instance, value: setattr(rect, 'size', value))

        # ラベルを中央に配置
        message_label = Label(text='Data have already deleted',
                            size_hint=(None, None),  # size_hintを無効にして明示的にサイズを指定
                            width=message_box.width - 40,  # 幅をBoxLayoutに合わせる（余白を考慮）
                            height=message_box.height - 40,  # 高さを設定
                            text_size=(message_box.width - 40, None),  # テキストサイズを幅に合わせる
                            halign='center', valign='middle',
                            color=(1, 1, 1, 1))
        message_label.bind(size=message_label.setter('text_size'))  # テキストをラベルのサイズに合わせて中央揃え

        message_box.add_widget(message_label)
        
        # メッセージを表示するレイアウトに追加
        self.layout.add_widget(message_box)
        
        # 4秒後にメッセージを削除
        Clock.schedule_once(lambda dt: self.layout.remove_widget(message_box), 4)

    def go_back(self, instance):
        self.screen_mgr.current = 'MainScreen'

# サードスクリーンのクラス
class ThirdScreen(ColoredScreen):
    def __init__(self, screen_mgr, **kwargs):
        super(ThirdScreen, self).__init__(color=(0, 0, 0, 1), **kwargs)
        layout = FloatLayout()

        img_btn2_1 = ImageButton(img_normal='back.png', img_pressed='back2.png',
                                 screen_mgr=screen_mgr, target_screen_name='MainScreen',
                                 size_hint=(None, None), size=(50, 50), pos_hint={'center_x': 0.3, 'center_y': 0.9})
        layout.add_widget(img_btn2_1)

        text_label = Label(text=' App Name [Gugliemar App]\n\n Developer [Gakuto Sawada]\n\n Tools [Kivy]\n\n Programming Language [Python]\n\n\n\n"Click the link below for instructions."',
                   font_size='22sp', size_hint=(None, None), size=(300, 150),
                   pos_hint={'center_x': 0.5, 'center_y': 0.55})
        layout.add_widget(text_label)

        link_label = LinkLabel(text='[color=9932CC]Gugliemar_information.pdf[/color]',
                               link_url='Gugliemar_information.pdf',
                               font_size='24sp', size_hint=(None, None), size=(300, 50),
                               pos_hint={'center_x': 0.5, 'center_y': 0.24})
        layout.add_widget(link_label)

        self.add_widget(layout)

# スクリーンマネージャーのクラス
class MyScreenManager(ScreenManager):
    pass

# メインアプリケーションクラス
class MyApp(App):
    def build(self):
        sm = MyScreenManager(transition=NoTransition())
        sm.add_widget(SplashScreen(screen_mgr=sm, name='splash'))
        
        main_screen = MainScreen(screen_mgr=sm, name='MainScreen')
        sm.add_widget(main_screen)
                
        sm.add_widget(SecondScreen(screen_mgr=sm, name='second'))
        
        sm.add_widget(ThirdScreen(screen_mgr=sm, name='third'))
        
        return sm

if __name__ == '__main__':
    MyApp().run()
    def go_back(self, instance):
        self.screen_mgr.current = 'MainScreen'