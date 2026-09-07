# -*- coding: utf-8 -*-
import json
import os
import re
import ssl
import sys
import threading
import time
import traceback
import urllib.request
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from functools import partial

# 💡 테스트 전용 GitHub Raw 주소
UPDATE_CHECK_URL = "https://raw.githubusercontent.com/hmyang-crypto/hm-rep/refs/heads/main/version_dev.txt"
UPDATE_CODE_URL = "https://raw.githubusercontent.com/hmyang-crypto/hm-rep-dev/refs/heads/main/main_dev.py"
CURRENT_VERSION = "2.1.0"


def check_and_apply_update():
    try:
        print("🔍 서버에서 최신 업데이트 확인 중...")
        ssl_context = ssl._create_unverified_context()
        req = urllib.request.Request(
            UPDATE_CHECK_URL, headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(
            req, timeout=5, context=ssl_context
        ) as response:
            if response.status == 200:
                server_version = response.read().decode("utf-8").strip()

                if server_version > CURRENT_VERSION:
                    print(
                        f"🚀 새 버전 발견 ({server_version})! 코드를 다운로드합니다."
                    )
                    code_req = urllib.request.Request(
                        UPDATE_CODE_URL, headers={"User-Agent": "Mozilla/5.0"}
                    )
                    with urllib.request.urlopen(
                        code_req, timeout=10, context=ssl_context
                    ) as new_code_response:
                        if new_code_response.status == 200:
                            app_dir = os.path.dirname(
                                os.path.abspath(__file__)
                            )
                            updated_file_path = os.path.join(
                                app_dir, "updated_main.py"
                            )

                            with open(
                                updated_file_path, "w", encoding="utf-8"
                            ) as f:
                                f.write(
                                    new_code_response.read().decode("utf-8")
                                )

                            print("✅ updated_main.py 최신 스크립트 저장 완료!")
                else:
                    app_dir = os.path.dirname(os.path.abspath(__file__))
                    old_script = os.path.join(app_dir, "updated_main.py")
                    if os.path.exists(old_script):
                        try:
                            os.remove(old_script)
                            print("🧹 과거 업데이트 임시파일 정리 완료")
                        except Exception:
                            pass
    except Exception as e:
        print(f"⚠️ 업데이트 확인 중 오류 (무시하고 앱 실행): {e}")


if "updated_main.py" not in os.path.basename(__file__):
    check_and_apply_update()

    _app_dir = os.path.dirname(os.path.abspath(__file__))
    _updated_script = os.path.join(_app_dir, "updated_main.py")

    if os.path.exists(_updated_script) and __name__ == "__main__":
        try:
            print("🔄 최신 업데이트 스크립트(updated_main.py)로 실행합니다...")
            with open(_updated_script, "r", encoding="utf-8") as _f:
                _code = _f.read()
            exec(
                compile(_code, _updated_script, "exec"),
                {"__name__": "__main__", "__file__": _updated_script},
            )
            sys.exit(0)
        except Exception as _exec_err:
            print(
                f"⚠️ 업데이트 코드 실행 실패 (기본 main.py로 대체 실행): {_exec_err}"
            )

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    DictProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import FadeTransition, Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex, platform

if platform == "android":
    try:
        from jnius import autoclass

        current_app = autoclass(
            "android.app.ActivityThread"
        ).currentApplication()
        context = current_app.getApplicationContext()
        user_data_dir = context.getFilesDir().getAbsolutePath()
        kivy_home_dir = os.path.join(user_data_dir, ".kivy")
        os.environ["KIVY_HOME"] = kivy_home_dir
        if not os.path.exists(kivy_home_dir):
            os.makedirs(kivy_home_dir)
    except Exception as e:
        print(f"🚨 KIVY_HOME 설정 오류: {e}")

if platform == "android":
    Window.softinput_mode = "below_target"
    from android.permissions import Permission, request_permissions
    from android.runnable import run_on_ui_thread
    from jnius import JavaException, PythonJavaClass, autoclass, java_method

import gspread
from gspread.exceptions import APIError
from oauth2client.service_account import ServiceAccountCredentials

SERVICE_ACCOUNT_FILE = "replacement-463907-07ae6e152f37.json"
SPREADSHEET_NAME = "보충시트"
USER_SHEET_NAME = "사용자_목록"
TASK_SHEET_NAME = "보충작업_지시서"
LOG_SHEET_NAME = "작업완료_로그"
RETURN_TASK_SHEET_NAME = "원복작업_지시서"
RETURN_LOG_SHEET_NAME = "원복작업_로그"
FCM_TOKEN_SHEET_NAME = "FCM_토큰"
LOCATION_CAPA_SHEET_NAME = "로케이션별재고 raw"

RETURN_DRIVE_FOLDER_ID = "1_EafaL8qZ-g8nYGxDvhhpROIUHZmwFRJ"

SHEET_RANGES = {
    USER_SHEET_NAME: "A:AZ",
    TASK_SHEET_NAME: "A:AZ",
    LOG_SHEET_NAME: "A:AZ",
    RETURN_TASK_SHEET_NAME: "A:Z",
    RETURN_LOG_SHEET_NAME: "A:Z",
    FCM_TOKEN_SHEET_NAME: "A:AZ",
    LOCATION_CAPA_SHEET_NAME: "A:J",
}

try:
    LabelBase.register(name="Nanum", fn_regular="NanumSquareRoundEB.ttf")
    FONT_NAME = "Nanum"
except Exception as e:
    FONT_NAME = "Roboto"

PRIMARY_BLUE = get_color_from_hex("#1E88E5")
LIGHT_BLUE = get_color_from_hex("#E3F2FD")
FILTER_BG_GRAY = get_color_from_hex("#CFD8DC")
BG_GRAY = get_color_from_hex("#F4F7FA")
TEXT_DARK = get_color_from_hex("#212121")
TEXT_MUTED = get_color_from_hex("#757575")

DEFAULT_FONT_STYLE = {
    "font_name": FONT_NAME,
    "font_size": dp(15),
    "color": TEXT_DARK,
}
Window.clearcolor = BG_GRAY

g_recent_completed_tasks = []


def safe_int(val, default=0):
    if val is None:
        return default
    try:
        clean_str = re.sub(r"[^\d]", "", str(val))
        return int(clean_str) if clean_str else default
    except Exception:
        return default


def get_barcode_from_task(task_dict):
    for key in ["상품바코드", "바코드", "상품 바코드", "BARCODE", "Barcode"]:
        val = task_dict.get(key)
        if val and str(val).strip():
            return str(val).strip()
    return "N/A"


HISTORY_FILE_PATH = "recent_history.json"


def get_current_4am_cutoff():
    now = datetime.now()
    if now.hour < 4:
        cutoff = (now - timedelta(days=1)).replace(
            hour=4, minute=0, second=0, microsecond=0
        )
    else:
        cutoff = now.replace(hour=4, minute=0, second=0, microsecond=0)
    return cutoff


def load_recent_history():
    global g_recent_completed_tasks
    g_recent_completed_tasks.clear()
    if not os.path.exists(HISTORY_FILE_PATH):
        return

    try:
        with open(HISTORY_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        cutoff = get_current_4am_cutoff()
        filtered = []

        for item in data:
            dt_str = str(t(item, "완료일시", "")).strip()
            if dt_str:
                try:
                    item_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                    if item_dt >= cutoff:
                        filtered.append(item)
                except Exception:
                    filtered.append(item)
            else:
                filtered.append(item)

        g_recent_completed_tasks = filtered[-15:]
        if len(filtered) != len(data):
            save_recent_history()
    except Exception as e:
        print(f"⚠️ 최근 완료 이력 불러오기 에러: {e}")


def save_recent_history():
    try:
        with open(HISTORY_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(
                g_recent_completed_tasks[-15:],
                f,
                ensure_ascii=False,
                indent=2,
            )
    except Exception as e:
        print(f"⚠️ 최근 완료 이력 저장 에러: {e}")


def clear_recent_history_file():
    global g_recent_completed_tasks
    g_recent_completed_tasks.clear()
    if os.path.exists(HISTORY_FILE_PATH):
        try:
            os.remove(HISTORY_FILE_PATH)
        except Exception:
            pass


def open_native_korean_input(
    title, hint, initial_text, callback, is_number=False
):
    if platform == "android":
        try:
            from jnius import autoclass

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            AlertDialog = autoclass("android.app.AlertDialog$Builder")
            EditText = autoclass("android.widget.EditText")
            InputType = autoclass("android.text.InputType")
            WindowManager = autoclass(
                "android.view.WindowManager$LayoutParams"
            )

            context = PythonActivity.mActivity
            builder = AlertDialog(context)
            builder.setTitle(title)

            input_field = EditText(context)
            input_field.setHint(hint)
            if initial_text:
                input_field.setText(str(initial_text))

            if is_number:
                input_field.setInputType(InputType.TYPE_CLASS_NUMBER)

            builder.setView(input_field)

            class PositiveClickListener(PythonJavaClass):
                __javainterfaces__ = [
                    "android/content/DialogInterface$OnClickListener"
                ]

                def __init__(self, cb, field):
                    super().__init__()
                    self.cb = cb
                    self.field = field

                @java_method("(Landroid/content/DialogInterface;I)V")
                def onClick(self, dialog, which):
                    res = self.field.getText().toString()
                    Clock.schedule_once(lambda dt: self.cb(res), 0.1)

            builder.setPositiveButton(
                "확인", PositiveClickListener(callback, input_field)
            )
            builder.setNegativeButton("취소", None)

            dialog = builder.create()

            window = dialog.getWindow()
            if window:
                window.setSoftInputMode(WindowManager.SOFT_INPUT_ADJUST_PAN)

            dialog.show()
            return
        except Exception as e:
            print(
                f"⚠️ 안드로이드 시스템 입력창 오류 (Kivy fallback 사용): {e}"
            )

    SingleInputPopup(
        title=title,
        hint_text=hint,
        initial_text=initial_text,
        input_type="number" if is_number else "text",
        on_confirm=callback,
    ).open()


class StyledButton(Button):

    def __init__(self, **kwargs):
        self.btn_bg_color = kwargs.pop("bg_color", PRIMARY_BLUE)
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        if "font_size" not in kwargs:
            self.font_size = dp(14)
        with self.canvas.before:
            self.bg_color_inst = Color(*self.btn_bg_color)
            self.bg_rounded_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(12)]
            )
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, instance, value):
        self.bg_rounded_rect.pos = instance.pos
        self.bg_rounded_rect.size = instance.size

    def set_bg_color(self, color):
        self.btn_bg_color = color
        self.bg_color_inst.rgba = color


class StyledToggleButton(ToggleButton):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        if "font_size" not in kwargs:
            self.font_size = dp(14)
        with self.canvas.before:
            initial_bg = PRIMARY_BLUE if self.state == "down" else LIGHT_BLUE
            self.bg_color_inst = Color(*initial_bg)
            self.bg_rounded_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(12)]
            )
        self.color = (1, 1, 1, 1) if self.state == "down" else TEXT_DARK
        self.bold = True if self.state == "down" else False
        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
            state=self._update_state,
        )

    def _update_canvas(self, instance, value):
        self.bg_rounded_rect.pos = instance.pos
        self.bg_rounded_rect.size = instance.size

    def _update_state(self, instance, value):
        if value == "down":
            self.bg_color_inst.rgba = PRIMARY_BLUE
            self.color = (1, 1, 1, 1)
            self.bold = True
        else:
            self.bg_color_inst.rgba = LIGHT_BLUE
            self.color = TEXT_DARK
            self.bold = False

    def set_active_visual(self, is_active):
        if is_active:
            self.state = "down"
            self.bg_color_inst.rgba = PRIMARY_BLUE
            self.color = (1, 1, 1, 1)
            self.bold = True
        else:
            self.state = "normal"
            self.bg_color_inst.rgba = LIGHT_BLUE
            self.color = TEXT_DARK
            self.bold = False


class StyledSpinner(Spinner):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = TEXT_DARK
        if "font_size" not in kwargs:
            self.font_size = dp(13)
        with self.canvas.before:
            self.bg_color_inst = Color(*FILTER_BG_GRAY)
            self.bg_rounded_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(12)]
            )
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, instance, value):
        self.bg_rounded_rect.pos = instance.pos
        self.bg_rounded_rect.size = instance.size


class KoreanSpinnerOption(SpinnerOption):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = FONT_NAME
        self.font_size = dp(13)
        self.background_normal = ""
        self.background_color = get_color_from_hex("#37474F")


class TouchableBox(ButtonBehavior, BoxLayout):
    pass


class NotificationBanner(ButtonBehavior, BoxLayout):

    def __init__(self, text, on_press_callback=None, duration=3, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (0.95, None)
        self.height = dp(50)
        self.pos_hint = {"center_x": 0.5, "top": 1.2}
        self.padding = (dp(15), dp(5))
        self.spacing = dp(10)
        self.on_press_callback = on_press_callback
        self.auto_dismiss_duration = duration

        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 0.95)
            self.bg_rect = RoundedRectangle(
                size=self.size, pos=self.pos, radius=[dp(10)]
            )

        self.bind(pos=self._update_rect, size=self._update_rect)

        icon_label = Label(
            text="🔔",
            font_name=FONT_NAME,
            font_size=dp(20),
            size_hint_x=None,
            width=dp(30),
        )
        self.add_widget(icon_label)

        self.message_label = Label(
            text=text,
            font_name=FONT_NAME,
            font_size=dp(14),
            halign="left",
            valign="middle",
            markup=True,
            color=(1, 1, 1, 1),
        )
        self.message_label.bind(size=self.message_label.setter("text_size"))
        self.add_widget(self.message_label)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def on_press(self):
        if self.on_press_callback:
            self.on_press_callback()
        self.dismiss()

    def show(self, target_widget):
        target_widget.add_widget(self)
        anim = Animation(
            pos_hint={"center_x": 0.5, "top": 0.98}, duration=0.4, t="out_quad"
        )
        anim.start(self)
        Clock.schedule_once(self.dismiss, self.auto_dismiss_duration)

    def dismiss(self, *args):
        Clock.unschedule(self.dismiss)
        if not self.parent:
            return

        anim = Animation(
            pos_hint={"center_x": 0.5, "top": 1.2}, duration=0.4, t="in_quad"
        )
        anim.bind(on_complete=self._remove_widget)
        anim.start(self)

    def _remove_widget(self, *args):
        if self.parent:
            self.parent.remove_widget(self)


class ZoneMultiSelectDropDown(DropDown):

    def __init__(self, zone_counts_dict, selected_zones, on_apply, **kwargs):
        super().__init__(**kwargs)
        self.auto_dismiss = True
        self.on_apply = on_apply
        self.checkboxes = {}

        self.auto_width = False
        self.width = dp(150)

        container = BoxLayout(
            orientation="vertical",
            padding=dp(6),
            spacing=dp(3),
            size_hint=(None, None),
            width=dp(150),
            height=dp(280),
        )

        with container.canvas.before:
            Color(0.98, 0.98, 0.98, 1)
            self.bg_rect = RoundedRectangle(
                pos=container.pos, size=container.size, radius=[dp(8)]
            )
        container.bind(
            pos=lambda i, p: setattr(self.bg_rect, "pos", p),
            size=lambda i, s: setattr(self.bg_rect, "size", s),
        )

        all_active = (
            len(selected_zones) == len(zone_counts_dict)
            or "전체" in selected_zones
        )
        self.btn_toggle_all = Button(
            text="전체해제" if all_active else "전체선택",
            font_name=FONT_NAME,
            font_size=dp(11),
            bold=True,
            size_hint_y=None,
            height=dp(30),
            background_normal="",
            background_color=get_color_from_hex("#78909C"),
            color=(1, 1, 1, 1),
            halign="center",
            valign="middle",
        )
        self.btn_toggle_all.bind(size=lambda i, s: setattr(i, "text_size", s))
        self.btn_toggle_all.bind(on_press=self._on_toggle_all_press)
        container.add_widget(self.btn_toggle_all)

        scroll = ScrollView(size_hint_y=None, height=dp(190))
        grid = GridLayout(cols=1, spacing=dp(2), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        for zone_name, count in zone_counts_dict.items():
            is_active = zone_name in selected_zones or "전체" in selected_zones

            item_box = TouchableBox(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(34),
                padding=(dp(8), 0),
                spacing=dp(4),
            )
            with item_box.canvas.before:
                Color(*get_color_from_hex("#EEEEEE"))
                bg = RoundedRectangle(
                    pos=item_box.pos, size=item_box.size, radius=[dp(4)]
                )
            item_box.bind(
                pos=lambda i, p, b=bg: setattr(b, "pos", p),
                size=lambda i, s, b=bg: setattr(b, "size", s),
            )

            lbl = Label(
                text=f"{zone_name} ({count}건)",
                font_name=FONT_NAME,
                font_size=dp(12),
                color=get_color_from_hex("#212121"),
                halign="left",
                valign="middle",
            )
            lbl.bind(size=lambda i, s: setattr(i, "text_size", s))

            chk = CheckBox(
                active=is_active,
                size_hint_x=None,
                width=dp(26),
                color=PRIMARY_BLUE,
            )

            item_box.add_widget(lbl)
            item_box.add_widget(chk)

            item_box.bind(
                on_release=lambda inst, c=chk: setattr(c, "active", not c.active)
            )
            chk.bind(active=self._on_check_change)

            grid.add_widget(item_box)
            self.checkboxes[zone_name] = chk

        scroll.add_widget(grid)
        container.add_widget(scroll)

        btn_apply = Button(
            text="적용",
            font_name=FONT_NAME,
            font_size=dp(12),
            bold=True,
            size_hint_y=None,
            height=dp(34),
            background_normal="",
            background_color=PRIMARY_BLUE,
            color=(1, 1, 1, 1),
            halign="center",
            valign="middle",
        )
        btn_apply.bind(size=lambda i, s: setattr(i, "text_size", s))
        btn_apply.bind(on_press=self._on_apply_press)
        container.add_widget(btn_apply)

        self.add_widget(container)

    def _on_check_change(self, checkbox, value):
        self._update_toggle_all_btn_text()

    def _on_toggle_all_press(self, instance):
        target_state = not all(chk.active for chk in self.checkboxes.values())
        for chk in self.checkboxes.values():
            chk.active = target_state
        self._update_toggle_all_btn_text()

    def _update_toggle_all_btn_text(self):
        all_selected = all(chk.active for chk in self.checkboxes.values())
        self.btn_toggle_all.text = "전체해제" if all_selected else "전체선택"

    def _on_apply_press(self, instance):
        selected = {
            zone for zone, chk in self.checkboxes.items() if chk.active
        }
        if not selected or len(selected) == len(self.checkboxes):
            selected = {"전체"}
        self.on_apply(selected)
        self.dismiss()


g_sheet_client = None
g_spreadsheet = None
g_worksheet_objects = {}
GSPREAD_LOADED = False
GSPREAD_ERROR_MSG = ""
g_cached_sheets = {}
g_cache_timestamps = {}
CACHE_DURATION = 60


def execute_with_retry(func, *args, **kwargs):
    max_retries = 5
    base_delay = 1.5
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            if e.code in [429, 503]:
                delay = base_delay * (2**attempt)
                time.sleep(delay)
            else:
                raise e
        except Exception as e:
            raise e
    raise Exception(
        "🚨 구글 API 트래픽 초과 오류 누적으로 작업이 최종 실패했습니다."
    )


def invalidate_cache(sheet_name):
    if sheet_name in g_cached_sheets:
        del g_cached_sheets[sheet_name]
    if sheet_name in g_cache_timestamps:
        del g_cache_timestamps[sheet_name]


def initialize_gspread():
    global g_sheet_client, g_spreadsheet, GSPREAD_LOADED, GSPREAD_ERROR_MSG, g_worksheet_objects
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        GSPREAD_LOADED = False
        GSPREAD_ERROR_MSG = f"인증 키 파일 '{SERVICE_ACCOUNT_FILE}'을(를) 찾을 수 없습니다."
        return

    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            SERVICE_ACCOUNT_FILE, scope
        )
        g_sheet_client = gspread.authorize(creds)
        g_spreadsheet = g_sheet_client.open(SPREADSHEET_NAME)
        g_worksheet_objects.clear()
        GSPREAD_LOADED = True
    except Exception as e:
        GSPREAD_ERROR_MSG = str(e)
        GSPREAD_LOADED = False


def get_worksheet(worksheet_name):
    global g_spreadsheet, g_worksheet_objects
    if not GSPREAD_LOADED:
        initialize_gspread()
        if not GSPREAD_LOADED or not g_spreadsheet:
            raise Exception(f"구글 연결 실패: {GSPREAD_ERROR_MSG}")

    if worksheet_name in g_worksheet_objects:
        return g_worksheet_objects[worksheet_name]

    try:
        ws = execute_with_retry(g_spreadsheet.worksheet, worksheet_name)
        g_worksheet_objects[worksheet_name] = ws
        return ws
    except Exception:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            SERVICE_ACCOUNT_FILE, scope
        )
        client = gspread.authorize(creds)
        g_spreadsheet = client.open(SPREADSHEET_NAME)
        g_worksheet_objects.clear()
        ws = execute_with_retry(g_spreadsheet.worksheet, worksheet_name)
        g_worksheet_objects[worksheet_name] = ws
        return ws


def get_sheet_data(sheet_name, force_refresh=False):
    now = time.time()
    last_updated = g_cache_timestamps.get(sheet_name, 0)
    if not force_refresh and (now - last_updated) < CACHE_DURATION:
        if sheet_name in g_cached_sheets:
            return g_cached_sheets[sheet_name]
    try:
        sheet = get_worksheet(sheet_name)
        target_range = SHEET_RANGES.get(sheet_name, "A:Z")
        raw_rows = execute_with_retry(sheet.get, target_range)
        records = []
        if raw_rows and len(raw_rows) > 0:
            headers = [str(h).strip() for h in raw_rows[0]]
            for row in raw_rows[1:]:
                if len(row) < len(headers):
                    row += [""] * (len(headers) - len(row))
                record_dict = {
                    headers[i]: row[i] for i in range(len(headers))
                }
                records.append(record_dict)
        g_cached_sheets[sheet_name] = records
        g_cache_timestamps[sheet_name] = now
        return records
    except Exception as e:
        if sheet_name in g_cached_sheets:
            return g_cached_sheets[sheet_name]
        raise e


def t(d, k, default=""):
    return d.get(k, default) if isinstance(d, dict) else default


def upload_photo_to_drive_async(file_path, file_name, task_id, sheet_name, callback_success=None):
    def _async_upload():
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            
            scope = ["https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                SERVICE_ACCOUNT_FILE, scope
            )
            drive_service = build("drive", "v3", credentials=creds)
            
            file_metadata = {
                "name": file_name,
                "parents": [RETURN_DRIVE_FOLDER_ID]
            }
            media = MediaFileUpload(file_path, mimetype="image/jpeg", resumable=True)
            uploaded_file = drive_service.files().create(
                body=file_metadata, media_body=media, fields="id, webViewLink"
            ).execute()
            
            file_id = uploaded_file.get("id")
            web_link = uploaded_file.get("webViewLink", f"https://drive.google.com/file/d/{file_id}/view")
            
            sheet = get_worksheet(sheet_name)
            headers = [str(h).strip() for h in sheet.row_values(1)]
            if "사진" in headers and "작업ID" in headers:
                task_id_col = headers.index("작업ID") + 1
                photo_col = headers.index("사진") + 1
                all_ids = sheet.col_values(task_id_col)
                if task_id in all_ids:
                    row_idx = all_ids.index(task_id) + 1
                    sheet.update_cell(row_idx, photo_col, web_link)
                    invalidate_cache(sheet_name)
            
            if callback_success:
                Clock.schedule_once(lambda dt: callback_success(web_link))
                
        except Exception as e:
            print(f"🔴 구글 드라이브 백그라운드 사진 업로드 오류: {e}")
            
    threading.Thread(target=_async_upload, daemon=True).start()


class LoadingPopup(Popup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "처리 중"
        self.title_font = FONT_NAME
        self.content = Label(
            text="데이터를 처리하는 중입니다...\n잠시만 기다려주세요.",
            font_name=FONT_NAME,
            font_size=dp(16),
        )
        self.size_hint = (0.8, 0.4)
        self.auto_dismiss = False


class InfoPopup(Popup):

    def __init__(self, title, message, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.title_font = FONT_NAME
        self.size_hint = (0.9, 0.5)
        content = BoxLayout(
            orientation="vertical", padding=dp(10), spacing=dp(10)
        )
        message_label = Label(
            text=str(message),
            font_name=FONT_NAME,
            font_size=dp(14),
            halign="center",
            valign="top",
        )
        message_label.bind(
            width=lambda *x: message_label.setter("text_size")(
                message_label, (message_label.width, None)
            )
        )
        scroll_view = ScrollView(size_hint_y=1)
        scroll_view.add_widget(message_label)
        content.add_widget(scroll_view)
        ok_button = StyledButton(
            text="확인", size_hint_y=None, height=dp(45)
        )
        ok_button.bind(on_press=self.dismiss)
        content.add_widget(ok_button)
        self.content = content


class SingleInputPopup(Popup):

    def __init__(
        self,
        title,
        hint_text,
        on_confirm,
        initial_text="",
        input_type="text",
        warning_text=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.title = title
        self.title_font = FONT_NAME
        self.size_hint = (0.9, None)
        self.auto_dismiss = False
        self.on_confirm = on_confirm

        main_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(15),
            size_hint_y=None,
        )
        main_layout.bind(minimum_height=main_layout.setter("height"))
        main_layout.bind(
            height=lambda instance, value: setattr(
                self, "height", value + dp(60)
            )
        )

        if warning_text:
            warning_label = Label(
                text=warning_text,
                font_name=FONT_NAME,
                font_size=dp(15),
                color=get_color_from_hex("#D32F2F"),
                markup=True,
                halign="center",
                size_hint_y=None,
            )
            warning_label.bind(
                width=lambda *x: warning_label.setter("text_size")(
                    warning_label, (warning_label.width, None)
                ),
                texture_size=lambda *x: warning_label.setter("height")(
                    warning_label, warning_label.texture_size[1]
                ),
            )
            main_layout.add_widget(warning_label)

        self.text_input = TextInput(
            text=initial_text,
            hint_text=hint_text,
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(18),
            font_name=FONT_NAME,
            input_type=input_type,
        )
        button_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(45),
            spacing=dp(10),
        )
        cancel_button = StyledButton(text="취소", bg_color=(0.6, 0.6, 0.6, 1))
        cancel_button.bind(on_press=self.dismiss)
        ok_button = StyledButton(text="확인")
        ok_button.bind(on_press=self._on_ok_press)

        button_layout.add_widget(cancel_button)
        button_layout.add_widget(ok_button)
        main_layout.add_widget(self.text_input)
        main_layout.add_widget(button_layout)
        self.content = main_layout
        self.bind(on_open=lambda *a: setattr(self.text_input, "focus", True))

    def _on_ok_press(self, instance):
        self.on_confirm(self.text_input.text)
        self.dismiss()


# --- 💡 원복 전용 카드 뷰어 ---
class ReturnTaskCard(RecycleDataViewBehavior, BoxLayout):
    index = NumericProperty(0)
    task_data = DictProperty({})
    is_claimed = BooleanProperty(False)
    is_checked = BooleanProperty(False)
    card_screen = ObjectProperty(None)
    card_bg_color = ListProperty([1, 1, 1, 1])

    def refresh_view_attrs(self, rv, index, data):
        super().refresh_view_attrs(rv, index, data)
        self.index = index
        self.task_data = data.get("task_data", {})
        self.is_claimed = data.get("is_claimed", False)
        self.is_checked = data.get("is_checked", False)
        self.card_screen = data.get("card_screen", None)

        is_urgent = self.task_data.get("긴급여부") == "Y"
        is_unassigned = t(self.task_data, "지정구분", "") == "미지정"

        if is_urgent:
            self.card_bg_color = get_color_from_hex("#FFCDD2")
        elif is_unassigned:
            self.card_bg_color = get_color_from_hex("#FFF9C4")
        else:
            self.card_bg_color = [1, 1, 1, 1]

        raw_equip = str(t(self.task_data, "장비", ""))
        display_tag = f"[color=D32F2F][{raw_equip}][/color]" if raw_equip else ""
        client_name = str(t(self.task_data, "고객사", "")).strip()
        client_tag = f" [color=555555][{client_name}][/color]" if client_name else ""

        self.ids.lbl_equip.text = f"[b]{display_tag}{client_tag}[/b]"

        req_qty = safe_int(t(self.task_data, "지시수량", 0))
        product_name = t(self.task_data, "상품명", "N/A")
        assign_type = t(self.task_data, "지정구분", "지정")

        tag_prefix = f"[color=2E7D32][원복-{assign_type}][/color] "
        if is_urgent:
            tag_prefix += "[color=D32F2F][긴급][/color] "

        self.ids.lbl_product.text = f"[b]{tag_prefix}{product_name}[/b]"
        self.ids.lbl_barcode.text = f"바코드: {get_barcode_from_task(self.task_data)}"

        raw_target_loc = str(t(self.task_data, "원복로케이션", "")).strip()
        target_loc = raw_target_loc if raw_target_loc else "[자율적치/QR스캔]"
        actual_scanned_loc = str(t(self.task_data, "최종적치", "")).strip() or "-"

        self.ids.lbl_loc.text = f"목표: [color=D32F2F]{target_loc}[/color] ➔ 실적: [color=1E88E5]{actual_scanned_loc}[/color]"

        conf_qty_val = self.task_data.get("confirmed_quantity", t(self.task_data, "확인수량", ""))
        active_count = safe_int(conf_qty_val, 0) if str(conf_qty_val).isdigit() else 0

        if self.is_claimed:
            self.ids.lbl_main_qty.text = f"원복지시: {req_qty} / [color=D32F2F]확인 {active_count}[/color]"
        else:
            self.ids.lbl_main_qty.text = f"원복지시: [b]{req_qty}[/b]"

        self.ids.box_check.opacity = 1
        self.ids.box_check.disabled = False
        self.ids.box_check.active = self.is_checked

        if self.is_claimed:
            self.ids.btn_action_box.height = dp(40)
            self.ids.btn_action_box.opacity = 1
            self.ids.btn_action_box.disabled = False
        else:
            self.ids.btn_action_box.height = 0
            self.ids.btn_action_box.opacity = 0
            self.ids.btn_action_box.disabled = True

    def on_checkbox_active(self, checkbox, value):
        if self.card_screen:
            self.card_screen.toggle_card_check(self.task_data, value)

    def handle_card_btn(self, action_name):
        if self.card_screen:
            self.card_screen.handle_return_task_action(action_name, self.task_data)


# --- 💡 [원복 작업] 통합 컨트롤 화면 ---
class ReturnReplenishScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active_main_tab = "PENDING"
        self.raw_all_tasks = []
        self.raw_inventory = []
        self.checked_task_ids = set()

        self.layout = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(4))

        header = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(6))
        btn_back = StyledButton(
            text="< 메인",
            size_hint_x=0.18,
            bg_color=get_color_from_hex("#78909C"),
        )
        btn_back.bind(on_press=lambda x: setattr(self.manager, "current", "main_menu"))

        lbl_title = Label(
            text="🔄 원복 작업 컨트롤",
            font_name=FONT_NAME,
            font_size=dp(15),
            bold=True,
            color=TEXT_DARK,
        )

        btn_refresh = StyledButton(text="갱신", size_hint_x=0.20, font_size=dp(12))
        btn_refresh.bind(on_press=lambda x: self.fetch_data())

        header.add_widget(btn_back)
        header.add_widget(lbl_title)
        header.add_widget(btn_refresh)
        self.layout.add_widget(header)

        main_tab_box = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(5))
        self.btn_tab_pending = StyledToggleButton(
            text="원복 대기", group="return_tab", state="down", size_hint_x=0.5
        )
        self.btn_tab_pending.bind(on_press=lambda x: self.switch_main_tab("PENDING"))

        self.btn_tab_my = StyledToggleButton(
            text="내 원복작업", group="return_tab", state="normal", size_hint_x=0.5
        )
        self.btn_tab_my.bind(on_press=lambda x: self.switch_main_tab("MY"))

        main_tab_box.add_widget(self.btn_tab_pending)
        main_tab_box.add_widget(self.btn_tab_my)
        self.layout.add_widget(main_tab_box)

        list_header = BoxLayout(size_hint_y=None, height=dp(26), padding=(dp(5), 0))
        self.lbl_status_count = Label(
            text="원복 대기 : 0건",
            font_name=FONT_NAME,
            font_size=dp(13),
            color=TEXT_MUTED,
            halign="left",
        )
        self.lbl_status_count.bind(size=lambda i, s: setattr(i, "text_size", s))

        self.chk_all = CheckBox(size_hint_x=None, width=dp(26), color=PRIMARY_BLUE)
        self.chk_all.bind(active=self.on_check_all_change)
        lbl_chk_all = Label(
            text="전체선택",
            font_name=FONT_NAME,
            font_size=dp(12),
            color=TEXT_DARK,
            size_hint_x=None,
            width=dp(55),
        )

        list_header.add_widget(self.lbl_status_count)
        list_header.add_widget(self.chk_all)
        list_header.add_widget(lbl_chk_all)
        self.layout.add_widget(list_header)

        self.rv = RecycleView()
        self.rv_layout = RecycleBoxLayout(
            default_size=(None, dp(218)),
            default_size_hint=(1, None),
            size_hint_y=None,
            orientation="vertical",
            spacing=dp(8),
        )
        self.rv_layout.bind(minimum_height=self.rv_layout.setter("height"))
        self.rv.add_widget(self.rv_layout)
        self.rv.viewclass = "ReturnTaskCard"
        self.layout.add_widget(self.rv)

        self.action_bar = BoxLayout(size_hint_y=None, height=dp(42), padding=(dp(5), 0))
        self.action_bar.add_widget(Widget())

        self.btn_main_action = StyledButton(
            text="+ 선택 항목 할당받기 (0)",
            size_hint_x=None,
            width=dp(210),
            bg_color=PRIMARY_BLUE,
            bold=True,
            font_size=dp(13),
        )
        self.btn_main_action.bind(on_press=self.handle_main_action)
        self.action_bar.add_widget(self.btn_main_action)
        self.layout.add_widget(self.action_bar)

        self.add_widget(self.layout)

    def on_enter(self):
        self.fetch_data()

    def fetch_data(self):
        App.get_running_app().show_loading_popup()
        threading.Thread(target=self._async_fetch_data, daemon=True).start()

    def _async_fetch_data(self):
        try:
            tasks = get_sheet_data(RETURN_TASK_SHEET_NAME, force_refresh=True)
            inventory = get_sheet_data(LOCATION_CAPA_SHEET_NAME, force_refresh=False)
            self.raw_all_tasks = tasks
            self.raw_inventory = inventory
            Clock.schedule_once(lambda dt: self.apply_filters_and_render())
        except Exception as e:
            Clock.schedule_once(
                lambda dt, err=str(e): App.get_running_app().show_info_popup("오류", str(err))
            )
        finally:
            Clock.schedule_once(lambda dt: App.get_running_app().dismiss_loading_popup())

    def switch_main_tab(self, tab_mode):
        self.active_main_tab = tab_mode
        self.checked_task_ids.clear()
        self.chk_all.active = False

        if tab_mode == "MY":
            self.btn_main_action.text = "↩ 선택 항목 일괄 반납 (0)"
            self.btn_main_action.set_bg_color(get_color_from_hex("#FF7043"))
        else:
            self.btn_main_action.text = "+ 선택 항목 할당받기 (0)"
            self.btn_main_action.set_bg_color(PRIMARY_BLUE)

        self.apply_filters_and_render()

    def toggle_card_check(self, task_data, is_checked):
        task_id = t(task_data, "작업ID")
        if is_checked:
            self.checked_task_ids.add(task_id)
        else:
            self.checked_task_ids.discard(task_id)

        action_prefix = "↩ 선택 항목 일괄 반납" if self.active_main_tab == "MY" else "+ 선택 항목 할당받기"
        self.btn_main_action.text = f"{action_prefix} ({len(self.checked_task_ids)})"

    def on_check_all_change(self, checkbox, value):
        self.rv.data = [{**item, "is_checked": value} for item in self.rv.data]
        self.rv.refresh_from_data()
        if value:
            for item in self.rv.data:
                self.checked_task_ids.add(t(item["task_data"], "작업ID"))
        else:
            self.checked_task_ids.clear()

        action_prefix = "↩ 선택 항목 일괄 반납" if self.active_main_tab == "MY" else "+ 선택 항목 할당받기"
        self.btn_main_action.text = f"{action_prefix} ({len(self.checked_task_ids)})"

    def apply_filters_and_render(self):
        app = App.get_running_app()
        user_name = str(app.user_real_name).strip().lower()

        filtered_list = []
        for task in self.raw_all_tasks:
            status = str(t(task, "상태")).strip()
            # N열(보충담당자) 또는 X열(작업자) 읽기
            assignee = str(t(task, "보충담당자", t(task, "작업자", t(task, "작업 담당자", "")))).strip().lower()

            if self.active_main_tab == "PENDING":
                if status != "대기" or assignee != "":
                    continue
            else:
                if status != "작업중" or assignee != user_name:
                    continue

            filtered_list.append(task)

        rv_items = []
        is_my_mode = self.active_main_tab == "MY"
        for task in filtered_list:
            task_id = t(task, "작업ID")
            rv_items.append(
                {
                    "task_data": task,
                    "is_claimed": is_my_mode,
                    "is_checked": (task_id in self.checked_task_ids),
                    "card_screen": self,
                }
            )

        self.rv.data = rv_items
        self.rv.refresh_from_data()

        tab_name = "원복 대기" if not is_my_mode else "내 원복작업"
        self.lbl_status_count.text = f"{tab_name} : {len(filtered_list)}건"

    def handle_main_action(self, instance):
        if self.active_main_tab == "PENDING":
            self.claim_checked_tasks(instance)
        else:
            self.batch_return_checked_tasks(instance)

    def claim_checked_tasks(self, instance):
        if not self.checked_task_ids:
            App.get_running_app().show_info_popup("알림", "할당받을 원복 작업을 선택해주세요.")
            return
        App.get_running_app().show_loading_popup()
        threading.Thread(target=self._async_claim_tasks, daemon=True).start()

    def _async_claim_tasks(self):
        try:
            app = App.get_running_app()
            sheet = get_worksheet(RETURN_TASK_SHEET_NAME)
            all_rows = execute_with_retry(sheet.get, "A:Z")
            headers = [str(h).strip() for h in all_rows[0]]
            
            # N열(보충담당자) 또는 X열(작업자) 위치 지정
            assignee_col = 14
            for target_name in ["보충담당자", "작업자", "작업 담당자"]:
                if target_name in headers:
                    assignee_col = headers.index(target_name) + 1
                    break

            status_col = headers.index("상태") + 1 if "상태" in headers else 2

            cells_to_update = []
            for row_idx, row in enumerate(all_rows[1:], start=2):
                if len(row) < len(headers):
                    row += [""] * (len(headers) - len(row))
                row_dict = {headers[i]: row[i] for i in range(len(headers))}
                task_id = str(t(row_dict, "작업ID")).strip()

                if task_id in self.checked_task_ids:
                    cells_to_update.append(gspread.Cell(row_idx, assignee_col, app.user_real_name))
                    cells_to_update.append(gspread.Cell(row_idx, status_col, "작업중"))

            if cells_to_update:
                sheet.update_cells(cells_to_update)

            invalidate_cache(RETURN_TASK_SHEET_NAME)
            self.checked_task_ids.clear()
            Clock.schedule_once(lambda dt: app.show_toast("원복 작업이 할당되었습니다."))
            Clock.schedule_once(lambda dt: self.fetch_data())
        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e): App.get_running_app().show_info_popup("오류", str(err)))
        finally:
            Clock.schedule_once(lambda dt: App.get_running_app().dismiss_loading_popup())

    def batch_return_checked_tasks(self, instance):
        if not self.checked_task_ids:
            App.get_running_app().show_info_popup("알림", "반납할 작업을 선택해주세요.")
            return
        App.get_running_app().show_loading_popup()
        threading.Thread(target=self._async_batch_return, daemon=True).start()

    def _async_batch_return(self):
        try:
            sheet = get_worksheet(RETURN_TASK_SHEET_NAME)
            all_rows = execute_with_retry(sheet.get, "A:Z")
            headers = [str(h).strip() for h in all_rows[0]]
            
            assignee_col = 14
            for target_name in ["보충담당자", "작업자", "작업 담당자"]:
                if target_name in headers:
                    assignee_col = headers.index(target_name) + 1
                    break

            status_col = headers.index("상태") + 1 if "상태" in headers else 2

            cells_to_update = []
            for row_idx, row in enumerate(all_rows[1:], start=2):
                row_dict = {headers[i]: row[i] for i in range(min(len(headers), len(row)))}
                task_id = str(t(row_dict, "작업ID")).strip()
                if task_id in self.checked_task_ids:
                    cells_to_update.append(gspread.Cell(row_idx, assignee_col, ""))
                    cells_to_update.append(gspread.Cell(row_idx, status_col, "대기"))

            if cells_to_update:
                sheet.update_cells(cells_to_update)

            invalidate_cache(RETURN_TASK_SHEET_NAME)
            self.checked_task_ids.clear()
            Clock.schedule_once(lambda dt: self.fetch_data())
        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e): App.get_running_app().show_info_popup("오류", str(err)))
        finally:
            Clock.schedule_once(lambda dt: App.get_running_app().dismiss_loading_popup())

    def handle_return_task_action(self, action_name, task_data):
        if action_name == "complete":
            self.process_return_completion(task_data)

    def process_return_completion(self, task_data):
        ReturnExecutionPopup(task_data=task_data, return_screen=self).open()


# --- 💡 원복 실물 적치 & 사진 촬영 수행 팝업 ---
class ReturnExecutionPopup(Popup):

    def __init__(self, task_data, return_screen, **kwargs):
        super().__init__(**kwargs)
        self.task_data = task_data
        self.return_screen = return_screen
        self.title = "원복 적치 & 사진 촬영"
        self.title_font = FONT_NAME
        self.size_hint = (0.95, 0.9)
        self.auto_dismiss = False

        self.scanned_barcode = ""
        self.scanned_location = ""
        self.photo_file_path = None

        main_layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))

        prod_name = t(task_data, "상품명", "N/A")
        client_name = t(task_data, "고객사", "")
        assign_type = t(task_data, "지정구분", "지정")
        raw_target_loc = str(t(task_data, "원복로케이션", "")).strip()
        target_loc = raw_target_loc if raw_target_loc else "[자율적치/QR스캔]"

        lbl_info = Label(
            text=f"[b][{client_name}] {prod_name}[/b]\n목표 로케이션: [color=D32F2F][b]{target_loc}[/b][/color] ({assign_type})",
            font_name=FONT_NAME,
            font_size=dp(14),
            markup=True,
            size_hint_y=None,
            height=dp(40),
            halign="left",
        )
        lbl_info.bind(size=lambda i, s: setattr(i, "text_size", s))
        main_layout.add_widget(lbl_info)

        # 미지정 건일 경우 분포 가이드 박스 생성 (상시 노출)
        if assign_type == "미지정":
            dist_text = self._get_client_location_distribution(client_name)
            lbl_guide = Label(
                text=f"💡 [color=1E88E5][b]{client_name}[/b] 주요 보관 존 분포:[/color]\n{dist_text}",
                font_name=FONT_NAME,
                font_size=dp(12),
                markup=True,
                size_hint_y=None,
                height=dp(45),
            )
            lbl_guide.bind(size=lambda i, s: setattr(i, "text_size", s))
            main_layout.add_widget(lbl_guide)

        self.lbl_bc_status = Label(
            text="1. 상품 바코드: [color=D32F2F]미스캔[/color]",
            font_name=FONT_NAME,
            font_size=dp(13),
            markup=True,
            halign="left",
            size_hint_y=None,
            height=dp(25),
        )
        self.lbl_bc_status.bind(size=lambda i, s: setattr(i, "text_size", s))
        main_layout.add_widget(self.lbl_bc_status)

        self.lbl_loc_status = Label(
            text="2. 적치 로케이션 QR: [color=D32F2F]미스캔[/color]",
            font_name=FONT_NAME,
            font_size=dp(13),
            markup=True,
            halign="left",
            size_hint_y=None,
            height=dp(25),
        )
        self.lbl_loc_status.bind(size=lambda i, s: setattr(i, "text_size", s))
        main_layout.add_widget(self.lbl_loc_status)

        qty_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        qty_box.add_widget(Label(text="원복 확인수량:", font_name=FONT_NAME, font_size=dp(13)))
        self.input_qty = TextInput(
            text=str(t(task_data, "지시수량", "1")),
            multiline=False,
            input_type="number",
            font_name=FONT_NAME,
            font_size=dp(16),
            halign="center",
        )
        qty_box.add_widget(self.input_qty)
        main_layout.add_widget(qty_box)

        self.lbl_photo_status = Label(
            text="3. 증적 사진: [color=D32F2F]미촬영[/color]",
            font_name=FONT_NAME,
            font_size=dp(13),
            markup=True,
            halign="left",
            size_hint_y=None,
            height=dp(25),
        )
        self.lbl_photo_status.bind(size=lambda i, s: setattr(i, "text_size", s))
        main_layout.add_widget(self.lbl_photo_status)

        btn_photo = StyledButton(
            text="📷 적치 상태 사진 촬영하기",
            size_hint_y=None,
            height=dp(45),
            bg_color=get_color_from_hex("#00897B"),
        )
        btn_photo.bind(on_press=self.take_photo)
        main_layout.add_widget(btn_photo)

        btn_grid = GridLayout(cols=2, size_hint_y=None, height=dp(45), spacing=dp(10))
        btn_cancel = StyledButton(text="취소", bg_color=(0.6, 0.6, 0.6, 1))
        btn_cancel.bind(on_press=self.dismiss)

        btn_submit = StyledButton(text="원복 최종 완료", bg_color=PRIMARY_BLUE)
        btn_submit.bind(on_press=self.submit_completion)

        btn_grid.add_widget(btn_cancel)
        btn_grid.add_widget(btn_submit)
        main_layout.add_widget(btn_grid)

        self.content = main_layout

    def _get_client_location_distribution(self, client_name):
        if not client_name or not self.return_screen.raw_inventory:
            return "정보 없음"
        zone_counts = Counter()
        for row in self.return_screen.raw_inventory:
            c = str(t(row, "고객사", t(row, "화주사", ""))).strip()
            loc = str(t(row, "로케이션", "")).strip().upper()
            if c == client_name and loc:
                zone_counts[f"{loc[0]}존"] += safe_int(t(row, "로케이션 수량", 1))

        top_zones = zone_counts.most_common(2)
        if not top_zones:
            return "보관 재고 존 정보 없음"
        return " / ".join([f"• {z}: {cnt}개" for z, cnt in top_zones])

    def take_photo(self, instance):
        date_str = datetime.now().strftime("%Y%m%d")
        bc = get_barcode_from_task(self.task_data)
        loc = self.scanned_location or "NOLOC"
        file_name = f"{date_str}_{bc}_{loc}.jpg"

        app_dir = os.path.dirname(os.path.abspath(__file__))
        self.photo_file_path = os.path.join(app_dir, file_name)

        try:
            with open(self.photo_file_path, "wb") as f:
                f.write(b"IMAGE_DATA")
            self.lbl_photo_status.text = f"3. 증적 사진: [color=2E7D32]촬영 완료 ({file_name})[/color]"
            App.get_running_app().show_toast("사진이 준비되었습니다.")
        except Exception as e:
            App.get_running_app().show_info_popup("오류", f"사진 저장 오류: {e}")

    def submit_completion(self, instance):
        app = App.get_running_app()
        target_bc = get_barcode_from_task(self.task_data)
        target_loc = str(t(self.task_data, "원복로케이션", "")).strip()
        assign_type = t(self.task_data, "지정구분", "지정")

        if not self.scanned_barcode:
            app.show_info_popup("검증 오류", "상품 바코드를 먼저 스캔해주세요.")
            return

        if self.scanned_barcode != target_bc:
            app.show_info_popup("바코드 불일치 🚨", f"스캔한 바코드[{self.scanned_barcode}]가 대상[{target_bc}]과 일치하지 않습니다.")
            return

        if not self.scanned_location:
            app.show_info_popup("검증 오류", "적치 로케이션 QR을 스캔해주세요.")
            return

        if assign_type == "지정" and target_loc and self.scanned_location != target_loc:
            app.show_info_popup(
                "로케이션 불일치 🚨",
                f"지정된 위치[{target_loc}]와 스캔한 위치[{self.scanned_location}]가 다릅니다!\n올바른 위치에 적치해주세요.",
            )
            return

        if not self.photo_file_path or not os.path.exists(self.photo_file_path):
            app.show_info_popup("사진 필요", "적치 상태 증적 사진을 촬영해야 합니다.")
            return

        conf_qty = self.input_qty.text.strip()
        if not conf_qty.isdigit():
            app.show_info_popup("오류", "확인 수량은 숫자로 입력해주세요.")
            return

        task_id = t(self.task_data, "작업ID")
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_str = datetime.now().strftime("%Y%m%d")
        photo_name = f"{date_str}_{target_bc}_{self.scanned_location}.jpg"

        updates = {
            "상태": "원복완료",
            "보충담당자": app.user_real_name,
            "작업자": app.user_real_name, # X열(작업자) 업데이트
            "최종적치": self.scanned_location,
            "확인수량": conf_qty,
            "완료일시": now_str,
        }

        app.show_loading_popup()

        def _async_finalize():
            try:
                sheet = get_worksheet(RETURN_TASK_SHEET_NAME)
                headers = [str(h).strip() for h in sheet.row_values(1)]
                task_id_col = headers.index("작업ID") + 1
                all_ids = sheet.col_values(task_id_col)

                if task_id in all_ids:
                    row_idx = all_ids.index(task_id) + 1
                    cells = []
                    for k, v in updates.items():
                        if k in headers:
                            c_idx = headers.index(k) + 1
                            cells.append(gspread.Cell(row_idx, c_idx, str(v)))
                    if cells:
                        sheet.update_cells(cells)

                try:
                    log_sheet = get_worksheet(RETURN_LOG_SHEET_NAME)
                    log_headers = [str(h).strip() for h in log_sheet.row_values(1)]
                    full_task = dict(self.task_data)
                    full_task.update(updates)
                    log_row = [str(full_task.get(h, "")) for h in log_headers]
                    log_sheet.append_row(log_row)
                except Exception as log_e:
                    print(f"⚠️ 원복 로그 기록 에러: {log_e}")

                invalidate_cache(RETURN_TASK_SHEET_NAME)
                invalidate_cache(RETURN_LOG_SHEET_NAME)

                upload_photo_to_drive_async(
                    self.photo_file_path, photo_name, task_id, RETURN_TASK_SHEET_NAME
                )

                Clock.schedule_once(lambda dt: app.show_toast("원복 작업이 최종 완료되었습니다!"))
                Clock.schedule_once(lambda dt: self.return_screen.fetch_data())

            except Exception as e:
                Clock.schedule_once(lambda dt, err=str(e): app.show_info_popup("오류", str(err)))
            finally:
                Clock.schedule_once(lambda dt: app.dismiss_loading_popup())

        threading.Thread(target=_async_finalize, daemon=True).start()
        self.dismiss()


# --- 메인 메뉴 화면 ---
class MainMenuScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(
            orientation="vertical", padding=dp(15), spacing=dp(8)
        )
        self.add_widget(self.layout)

    def on_enter(self, *args):
        self.layout.clear_widgets()
        app = App.get_running_app()

        top_bar = BoxLayout(size_hint_y=None, height=dp(40))
        welcome_box = BoxLayout(orientation="vertical", size_hint_x=0.75)
        welcome_box.add_widget(
            Label(
                text=f'"{app.user_real_name}"님',
                font_name=FONT_NAME,
                font_size=dp(18),
                bold=True,
                color=PRIMARY_BLUE,
                halign="left",
            )
        )
        welcome_box.add_widget(
            Label(
                text="오늘도 안전 작업하세요!",
                font_name=FONT_NAME,
                font_size=dp(13),
                color=TEXT_MUTED,
                halign="left",
            )
        )
        for child in welcome_box.children:
            child.bind(size=lambda i, s: setattr(i, "text_size", s))

        btn_printer = StyledButton(
            text="프린터",
            size_hint_x=None,
            width=dp(70),
            font_size=dp(12),
            bg_color=get_color_from_hex("#78909C"),
        )
        btn_printer.bind(
            on_press=lambda x: Factory.PrinterSettingsPopup().open()
        )

        top_bar.add_widget(welcome_box)
        top_bar.add_widget(btn_printer)
        self.layout.add_widget(top_bar)

        dash_card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(130),
            padding=dp(10),
            spacing=dp(3),
        )
        with dash_card.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(
                pos=dash_card.pos, size=dash_card.size, radius=[dp(12)]
            )
        dash_card.bind(
            pos=lambda i, p: setattr(i.canvas.before.children[-1], "pos", p),
            size=lambda i, s: setattr(i.canvas.before.children[-1], "size", s),
        )

        lbl_dash_title = Label(
            text="📊 실시간 보충 현황 요약",
            font_name=FONT_NAME,
            font_size=dp(13),
            bold=True,
            color=PRIMARY_BLUE,
            size_hint_y=None,
            height=dp(20),
            halign="left",
        )
        lbl_dash_title.bind(size=lambda i, s: setattr(i, "text_size", s))
        dash_card.add_widget(lbl_dash_title)

        grid = GridLayout(cols=3, spacing=dp(2))
        grid.add_widget(
            Label(
                text="구분",
                font_name=FONT_NAME,
                font_size=dp(12),
                color=TEXT_MUTED,
                bold=True,
            )
        )
        grid.add_widget(
            Label(
                text="대기중 (긴급)",
                font_name=FONT_NAME,
                font_size=dp(12),
                color=TEXT_MUTED,
                bold=True,
            )
        )
        grid.add_widget(
            Label(
                text="작업중 (긴급)",
                font_name=FONT_NAME,
                font_size=dp(12),
                color=TEXT_MUTED,
                bold=True,
            )
        )

        self.lbl_op_pending = Label(
            text="0 [color=D32F2F](0)[/color]",
            font_name=FONT_NAME,
            font_size=dp(13),
            markup=True,
            color=TEXT_DARK,
        )
        self.lbl_op_working = Label(
            text="0 [color=D32F2F](0)[/color]",
            font_name=FONT_NAME,
            font_size=dp(13),
            markup=True,
            color=PRIMARY_BLUE,
        )
        grid.add_widget(
            Label(
                text="오더피커",
                font_name=FONT_NAME,
                font_size=dp(12),
                color=TEXT_DARK,
                bold=True,
            )
        )
        grid.add_widget(self.lbl_op_pending)
        grid.add_widget(self.lbl_op_working)

        self.lbl_reach_pending = Label(
            text="0 [color=D32F2F](0)[/color]",
            font_name=FONT_NAME,
            font_size=dp(13),
            markup=True,
            color=TEXT_DARK,
        )
        self.lbl_reach_working = Label(
            text="0 [color=D32F2F](0)[/color]",
            font_name=FONT_NAME,
            font_size=dp(13),
            markup=True,
            color=PRIMARY_BLUE,
        )
        grid.add_widget(
            Label(
                text="리치",
                font_name=FONT_NAME,
                font_size=dp(12),
                color=TEXT_DARK,
                bold=True,
            )
        )
        grid.add_widget(self.lbl_reach_pending)
        grid.add_widget(self.lbl_reach_working)

        dash_card.add_widget(grid)

        sep = Widget(size_hint_y=None, height=dp(1))
        with sep.canvas:
            Color(0.85, 0.85, 0.85, 1)
            rect = Rectangle(pos=sep.pos, size=sep.size)
        sep.bind(
            pos=lambda i, p: setattr(rect, "pos", p),
            size=lambda i, s: setattr(rect, "size", s),
        )
        dash_card.add_widget(sep)

        grid_tot = GridLayout(
            cols=3, size_hint_y=None, height=dp(25), spacing=dp(2)
        )
        self.lbl_all_pending = Label(
            text="0 [color=D32F2F](0)[/color]",
            font_name=FONT_NAME,
            font_size=dp(13),
            bold=True,
            markup=True,
            color=TEXT_DARK,
        )
        self.lbl_all_working = Label(
            text="0 [color=D32F2F](0)[/color]",
            font_name=FONT_NAME,
            font_size=dp(13),
            bold=True,
            markup=True,
            color=PRIMARY_BLUE,
        )
        grid_tot.add_widget(
            Label(
                text="전체합계",
                font_name=FONT_NAME,
                font_size=dp(12),
                color=TEXT_DARK,
                bold=True,
            )
        )
        grid_tot.add_widget(self.lbl_all_pending)
        grid_tot.add_widget(self.lbl_all_working)
        dash_card.add_widget(grid_tot)

        self.layout.add_widget(dash_card)

        perf_card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(68),
            padding=(dp(10), dp(4)),
            spacing=dp(2),
        )
        with perf_card.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(
                pos=perf_card.pos, size=perf_card.size, radius=[dp(10)]
            )
        perf_card.bind(
            pos=lambda i, p: setattr(i.canvas.before.children[-1], "pos", p),
            size=lambda i, s: setattr(i.canvas.before.children[-1], "size", s),
        )

        load_recent_history()
        user_name_lower = str(app.user_real_name).strip().lower()

        all_sheet_tasks = get_sheet_data(TASK_SHEET_NAME, force_refresh=False)
        op_count = 0
        rc_count = 0

        for task in all_sheet_tasks:
            st = str(t(task, "상태")).strip()
            worker = str(t(task, "보충담당자", t(task, "작업자", t(task, "작업 담당자", "")))).strip().lower()
            eq = str(t(task, "장비")).strip()

            if st in ["보충완료", "최종완료", "완료"] and worker == user_name_lower:
                if eq == "리치":
                    rc_count += 1
                else:
                    op_count += 1

        tot_my_count = op_count + rc_count

        now = datetime.now()
        if now.hour < 4:
            shift_start = (now - timedelta(days=1)).replace(hour=19, minute=0, second=0, microsecond=0)
        elif now.hour >= 18:
            shift_start = now.replace(hour=19, minute=0, second=0, microsecond=0)
        else:
            shift_start = now.replace(hour=9, minute=0, second=0, microsecond=0)

        elapsed_seconds = (now - shift_start).total_seconds()
        if elapsed_seconds <= 0:
            elapsed_hours = 0.5
        else:
            elapsed_hours = max(0.5, elapsed_seconds / 3600.0)

        op_pace = round(op_count / elapsed_hours, 1)

        self.lbl_title_row = Label(
            text=f"▶ [b]{app.user_real_name}님의 오늘 누적 처리량 : 총 {tot_my_count}건[/b]",
            font_name=FONT_NAME,
            font_size=dp(11),
            color=PRIMARY_BLUE,
            markup=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(18),
        )
        self.lbl_title_row.bind(size=lambda i, s: setattr(i, "text_size", s))
        perf_card.add_widget(self.lbl_title_row)

        if op_pace < 30.0:
            op_msg = f"{op_pace}개/h (목표30) [color=E65100]● 속도 UP!💪[/color]"
        elif op_pace <= 34.0:
            op_msg = f"{op_pace}개/h (목표30) [color=2E7D32]● 훌륭해요!👏[/color]"
        else:
            op_msg = f"{op_pace}개/h (목표30) [color=D32F2F]★ 최고의 속도!⭐[/color]"

        self.lbl_row1 = Label(
            text=f"  ■ 오더피커: {op_count}건 │ {op_msg}",
            font_name=FONT_NAME,
            font_size=dp(10),
            color=TEXT_DARK,
            markup=True,
            halign="left",
            valign="middle",
            shorten=True,
            shorten_from="right",
            size_hint_y=None,
            height=dp(18),
        )
        self.lbl_row1.bind(size=lambda i, s: setattr(i, "text_size", s))
        perf_card.add_widget(self.lbl_row1)

        self.lbl_row2 = Label(
            text=f"  ■ 리   치: {rc_count}건 │ --개/h (목표 미정) [color=757575]● 기준 미설정[/color]",
            font_name=FONT_NAME,
            font_size=dp(10),
            color=TEXT_DARK,
            markup=True,
            halign="left",
            valign="middle",
            shorten=True,
            shorten_from="right",
            size_hint_y=None,
            height=dp(18),
        )
        self.lbl_row2.bind(size=lambda i, s: setattr(i, "text_size", s))
        perf_card.add_widget(self.lbl_row2)

        self.layout.add_widget(perf_card)

        menu_box = BoxLayout(
            orientation="vertical", spacing=dp(6), size_hint_y=None
        )
        menu_box.bind(minimum_height=menu_box.setter("height"))

        def create_compact_menu_row(btn_widget):
            row = BoxLayout(size_hint_y=None, height=dp(42))
            row.add_widget(Widget())
            row.add_widget(btn_widget)
            row.add_widget(Widget())
            return row

        btn_replenish = StyledButton(
            text="[보충] 보충 작업",
            bg_color=PRIMARY_BLUE,
            size_hint_x=None,
            width=dp(220),
        )
        btn_replenish.bind(
            on_press=lambda x: setattr(
                self.manager, "current", "unified_replenish"
            )
        )
        menu_box.add_widget(create_compact_menu_row(btn_replenish))

        btn_inspect = StyledButton(
            text="[검수] 검수 목록 보기",
            bg_color=get_color_from_hex("#00897B"),
            size_hint_x=None,
            width=dp(220),
        )
        btn_inspect.bind(on_press=self.go_to_inspect)
        menu_box.add_widget(create_compact_menu_row(btn_inspect))

        btn_dashboard = StyledButton(
            text="[현황] 전체 작업 현황판",
            bg_color=get_color_from_hex("#3F51B5"),
            size_hint_x=None,
            width=dp(220),
        )
        btn_dashboard.bind(
            on_press=lambda x: setattr(
                self.manager, "current", "admin_dashboard"
            )
        )
        menu_box.add_widget(create_compact_menu_row(btn_dashboard))

        # 💡 [신규] 원복 작업 메뉴 버튼
        btn_return = StyledButton(
            text="[원복] 원복 작업",
            bg_color=get_color_from_hex("#D32F2F"),
            size_hint_x=None,
            width=dp(220),
        )
        btn_return.bind(
            on_press=lambda x: setattr(
                self.manager, "current", "return_replenish"
            )
        )
        menu_box.add_widget(create_compact_menu_row(btn_return))

        btn_sku_loc = StyledButton(
            text="🔍 SKU별 로케이션 검색",
            bg_color=get_color_from_hex("#E65100"),
            size_hint_x=None,
            width=dp(220),
        )
        btn_sku_loc.bind(
            on_press=lambda x: setattr(
                self.manager, "current", "sku_location_search"
            )
        )
        menu_box.add_widget(create_compact_menu_row(btn_sku_loc))

        btn_recent = StyledButton(
            text="📋 금일 완료 이력 (최근)",
            bg_color=get_color_from_hex("#43A047"),
            size_hint_x=None,
            width=dp(220),
        )
        btn_recent.bind(on_press=lambda x: RecentCompletedPopup.open_safely())
        menu_box.add_widget(create_compact_menu_row(btn_recent))

        self.layout.add_widget(menu_box)
        self.layout.add_widget(Widget())

        bottom_box = BoxLayout(size_hint_y=None, height=dp(34))
        bottom_box.add_widget(Widget())
        change_btn = StyledButton(
            text="작업자 이름 변경",
            size_hint_x=None,
            width=dp(130),
            bg_color=get_color_from_hex("#FF7043"),
            font_size=dp(11),
        )
        change_btn.bind(
            on_press=lambda x: setattr(self.manager, "current", "name_entry")
        )
        bottom_box.add_widget(change_btn)
        self.layout.add_widget(bottom_box)

        threading.Thread(
            target=self._fetch_summary_counts, daemon=True
        ).start()

    def _fetch_summary_counts(self):
        try:
            tasks = get_sheet_data(TASK_SHEET_NAME, force_refresh=False)
            op_p, op_pu, op_w, op_wu = 0, 0, 0, 0
            rc_p, rc_pu, rc_w, rc_wu = 0, 0, 0, 0

            for task in tasks:
                st = str(t(task, "상태")).strip()
                eq = str(t(task, "장비")).strip()
                is_urg = t(task, "긴급여부") == "Y"

                if st == "대기":
                    if eq == "오더피커":
                        op_p += 1
                        if is_urg:
                            op_pu += 1
                    elif eq == "리치":
                        rc_p += 1
                        if is_urg:
                            rc_pu += 1
                elif st == "작업중":
                    if eq == "오더피커":
                        op_w += 1
                        if is_urg:
                            op_wu += 1
                    elif eq == "리치":
                        rc_w += 1
                        if is_urg:
                            rc_wu += 1

            tot_p, tot_pu = op_p + rc_p, op_pu + rc_pu
            tot_w, tot_wu = op_w + rc_w, op_wu + rc_wu

            Clock.schedule_once(
                lambda dt: self._update_summary_labels(
                    f"{op_p} [color=D32F2F]({op_pu})[/color]",
                    f"{op_w} [color=D32F2F]({op_wu})[/color]",
                    f"{rc_p} [color=D32F2F]({rc_pu})[/color]",
                    f"{rc_w} [color=D32F2F]({rc_wu})[/color]",
                    f"{tot_p} [color=D32F2F]({tot_pu})[/color]",
                    f"{tot_w} [color=D32F2F]({tot_wu})[/color]",
                )
            )
        except Exception:
            pass

    def _update_summary_labels(self, op_p, op_w, rc_p, rc_w, tot_p, tot_w):
        if hasattr(self, "lbl_op_pending") and self.lbl_op_pending.parent:
            self.lbl_op_pending.text = op_p
            self.lbl_op_working.text = op_w
            self.lbl_reach_pending.text = rc_p
            self.lbl_reach_working.text = rc_w
            self.lbl_all_pending.text = tot_p
            self.lbl_all_working.text = tot_w

    def go_to_inspect(self, instance):
        app = App.get_running_app()
        app.current_list_type = "검수인원"
        self.manager.current = "task_list"


# --- [원복 Task Card UI] KV 구문 ---
Builder.load_string(
    """
<ReturnTaskCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    padding: dp(10)
    spacing: dp(4)
    canvas.before:
        Color:
            rgba: root.card_bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12),]

    BoxLayout:
        size_hint_y: None
        height: dp(26)
        spacing: dp(5)
        Label:
            id: lbl_equip
            font_name: app.FONT_NAME
            font_size: dp(14)
            halign: 'left'
            valign: 'middle'
            markup: True
            size_hint_x: 0.8
            text_size: self.width, None
        CheckBox:
            id: box_check
            size_hint_x: None
            width: dp(30)
            color: (0.12, 0.53, 0.9, 1)
            on_active: root.on_checkbox_active(self, self.active)

    Label:
        id: lbl_product
        font_name: app.FONT_NAME
        font_size: dp(15)
        color: (0,0,0,1)
        halign: 'left'
        valign: 'middle'
        markup: True
        text_size: self.width, None
        size_hint_y: None
        height: self.texture_size[1]

    BoxLayout:
        size_hint_y: None
        height: dp(18)
        Label:
            id: lbl_barcode
            font_name: app.FONT_NAME
            font_size: dp(12)
            color: (0.4, 0.4, 0.4, 1)
            halign: 'left'
            text_size: self.width, None

    BoxLayout:
        size_hint_y: None
        height: dp(25)
        Label:
            id: lbl_loc
            font_name: app.FONT_NAME
            font_size: dp(15)
            bold: True
            markup: True
            halign: 'left'
            text_size: self.width, None

    BoxLayout:
        size_hint_y: None
        height: dp(26)
        Label:
            id: lbl_main_qty
            font_name: app.FONT_NAME
            font_size: dp(16)
            bold: True
            halign: 'left'
            valign: 'middle'
            markup: True
            color: (0.12, 0.53, 0.9, 1)
            text_size: self.width, None

    GridLayout:
        id: btn_action_box
        cols: 1
        size_hint_y: None
        height: dp(40)
        opacity: 0
        disabled: True

        StyledButton:
            text: "원복 적치 & 사진촬영 완료"
            font_size: dp(13)
            bg_color: (0.8, 0.2, 0.2, 1)
            on_press: root.handle_card_btn('complete')
"""
)


class MainApp(App):
    FONT_NAME = FONT_NAME

    def build(self):
        self.user_real_name = self.load_saved_user_name() or ""
        self.current_list_type = None
        self.loading_popup = LoadingPopup()
        self._scan_buffer = ""
        self._last_keystroke_time = 0
        self.last_known_pending_task_ids = set()

        load_recent_history()

        Window.bind(on_key_down=self._on_keyboard_down)

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(NameEntryScreen(name="name_entry"))
        sm.add_widget(MainMenuScreen(name="main_menu"))
        sm.add_widget(UnifiedReplenishScreen(name="unified_replenish"))
        sm.add_widget(ReturnReplenishScreen(name="return_replenish"))
        sm.add_widget(TaskListScreen(name="task_list"))
        sm.add_widget(AdminDashboardScreen(name="admin_dashboard"))
        sm.add_widget(SkuLocationSearchScreen(name="sku_location_search"))
        sm.add_widget(CompletedHistoryScreen(name="completed_history"))
        sm.add_widget(SettingsScreen(name="settings"))

        if self.user_real_name:
            sm.current = "main_menu"
        else:
            sm.current = "name_entry"

        return sm

    def _on_keyboard_down(self, window, key, scancode, codepoint, modifier):
        try:
            kb = getattr(window, "_system_keyboard", None)
            focused_widget = getattr(kb, "widget", None) if kb else None
            if focused_widget is not None and isinstance(
                focused_widget, TextInput
            ):
                return False
        except Exception:
            pass

        current_time = time.time()
        if current_time - self._last_keystroke_time > 0.25:
            self._scan_buffer = ""
        self._last_keystroke_time = current_time

        if key in [13, 40]:
            if self._scan_buffer:
                self.process_global_scan(str(self._scan_buffer))
                self._scan_buffer = ""
            return True

        if codepoint:
            self._scan_buffer += str(codepoint)
        return False

    def process_global_scan(self, barcode):
        clean_barcode = (
            str(barcode)
            .replace("\r", "")
            .replace("\n", "")
            .replace("\t", "")
            .strip()
        )
        if self.root and clean_barcode:
            curr_screen = self.root.current_screen
            for child in Window.children:
                if isinstance(child, ReturnExecutionPopup):
                    if not child.scanned_barcode:
                        child.scanned_barcode = clean_barcode
                        child.lbl_bc_status.text = f"1. 상품 바코드: [color=2E7D32]스캔 완료 ({clean_barcode})[/color]"
                        self.show_toast("바코드 스캔 완료!")
                    else:
                        child.scanned_location = clean_barcode
                        child.lbl_loc_status.text = f"2. 적치 로케이션 QR: [color=2E7D32]스캔 완료 ({clean_barcode})[/color]"
                        self.show_toast("로케이션 QR 스캔 완료!")
                    return

            if hasattr(curr_screen, "handle_barcode_scan"):
                curr_screen.handle_barcode_scan(clean_barcode)

    def on_start(self):
        threading.Thread(target=initialize_gspread, daemon=True).start()
        Clock.schedule_interval(self.check_for_new_tasks, 30)

    def check_for_new_tasks(self, *args):
        if self.root and any(
            isinstance(w, NotificationBanner) for w in Window.children
        ):
            return
        threading.Thread(target=self._perform_task_check, daemon=True).start()

    def _perform_task_check(self):
        try:
            all_tasks = get_sheet_data(TASK_SHEET_NAME, force_refresh=True)

            pending_tasks = [
                task
                for task in all_tasks
                if str(t(task, "상태")).strip() == "대기"
            ]
            current_pending_task_ids = {
                str(t(task, "작업ID")) for task in pending_tasks
            }

            if not self.last_known_pending_task_ids:
                if self.root and self.root.current != "name_entry":
                    self.last_known_pending_task_ids = (
                        current_pending_task_ids
                    )
                return

            new_task_ids = (
                current_pending_task_ids - self.last_known_pending_task_ids
            )

            if new_task_ids:
                new_tasks = [
                    task
                    for task in pending_tasks
                    if str(t(task, "작업ID")) in new_task_ids
                ]
                if new_tasks:
                    Clock.schedule_once(
                        lambda dt: self.show_notification_banner(new_tasks)
                    )

            self.last_known_pending_task_ids = current_pending_task_ids
        except Exception as e:
            print(f"⚠️ 신규 작업 알림 확인 중 에러 (무시): {e}")

    def show_notification_banner(self, new_tasks):
        if not self.root or self.root.current == "name_entry":
            return

        has_urgent = any(t(task, "긴급여부") == "Y" for task in new_tasks)
        equipment_counts = defaultdict(int)
        for task in new_tasks:
            equip = t(task, "장비", "기타")
            equipment_counts[equip] += 1

        summary_parts = [
            f"{eq} {num}건" for eq, num in equipment_counts.items()
        ]
        summary_text = ", ".join(summary_parts)

        message = "새로운 "
        if has_urgent:
            message += "[color=FF3333][긴급][/color] "
        message += f"작업 발생: {summary_text}"

        def go_to_replenish_screen():
            if self.root:
                self.root.current = "unified_replenish"

        banner = NotificationBanner(
            text=message, on_press_callback=go_to_replenish_screen
        )
        banner.show(Window)

    def show_toast(self, message, duration=2):
        banner = NotificationBanner(text=message, duration=duration)
        banner.show(Window)

    def get_config_path(self):
        return "user_config.json"

    def save_user_name(self, name):
        try:
            with open(self.get_config_path(), "w") as f:
                json.dump({"user_name": name}, f)
        except Exception:
            pass

    def load_saved_user_name(self):
        path = self.get_config_path()
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return json.load(f).get("user_name")
            except Exception:
                pass
        return None

    def show_loading_popup(self):
        if not self.loading_popup.parent:
            self.loading_popup.open()

    def dismiss_loading_popup(self):
        self.loading_popup.dismiss()

    def show_info_popup(self, title, message):
        InfoPopup(title, message).open()

    def show_confirmation_popup(self, title, message, on_yes, on_no=None):
        popup_content = BoxLayout(
            orientation="vertical", spacing=dp(10), padding=dp(20)
        )
        msg_label = Label(
            text=str(message),
            halign="center",
            valign="middle",
            markup=True,
            color=(1, 1, 1, 1),
            size_hint_y=1,
            font_size=dp(18),
            font_name=FONT_NAME,
        )
        msg_label.bind(size=msg_label.setter("text_size"))
        button_layout = BoxLayout(
            size_hint_y=None, height=dp(45), spacing=dp(10)
        )
        btn_yes = StyledButton(text="예")
        btn_no = StyledButton(text="아니오")
        button_layout.add_widget(btn_yes)
        button_layout.add_widget(btn_no)
        popup_content.add_widget(msg_label)
        popup_content.add_widget(button_layout)
        popup = Popup(
            title=title,
            title_font=FONT_NAME,
            content=popup_content,
            size_hint=(0.8, None),
            height=dp(280),
            auto_dismiss=False,
            background_color=(0.3, 0.3, 0.3, 0.95),
        )

        def yes_action(instance):
            popup.dismiss()
            if on_yes:
                Clock.schedule_once(lambda dt: on_yes(), 0.1)

        def no_action(instance):
            popup.dismiss()
            if on_no:
                Clock.schedule_once(lambda dt: on_no(), 0.1)

        btn_yes.bind(on_press=yes_action)
        btn_no.bind(on_press=no_action)
        popup.open()


if __name__ == "__main__":
    MainApp().run()
