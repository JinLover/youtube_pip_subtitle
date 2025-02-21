from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from kivymd.app import MDApp
from jnius import autoclass, cast
import time

# 안드로이드 관련 클래스
Activity = autoclass('android.app.Activity')
Context = autoclass('android.content.Context')
Settings = autoclass('android.provider.Settings')
Intent = autoclass('android.content.Intent')
Uri = autoclass('android.net.Uri')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
WindowManager = autoclass('android.view.WindowManager')
PixelFormat = autoclass('android.graphics.PixelFormat')
TextView = autoclass('android.widget.TextView')
Color = autoclass('android.graphics.Color')
Typeface = autoclass('android.graphics.Typeface')

KV = '''
#:import dp kivy.metrics.dp

Screen:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(10)

        MDLabel:
            text: '유튜브 자막 PiP'
            halign: 'center'
            font_style: 'H5'
            size_hint_y: None
            height: dp(50)
            font_name: "210 M고딕030.ttf"

        MDLabel:
            text: app.status_text
            halign: 'center'
            size_hint_y: None
            height: dp(50)
            font_name: "210 M고딕030.ttf"

        MDRaisedButton:
            text: '오버레이 권한 요청' if not app.has_overlay_permission else '서비스 ' + ('중지' if app.is_running else '시작')
            pos_hint: {'center_x': .5}
            size_hint_x: 0.8
            on_release: app.on_button_press()
'''

class SubtitleOverlay:
    def __init__(self):
        self._window = None
        self._params = None
        self._view = None
        self.setup_overlay()

    def setup_overlay(self):
        activity = PythonActivity.mActivity
        self._window = activity.getSystemService(Context.WINDOW_SERVICE)
        self._params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        )

    def show(self, text):
        if self._view is None:
            activity = PythonActivity.mActivity
            asset_manager = activity.getAssets()

            self._view = TextView(activity)
            self._view.setTextColor(Color.WHITE)
            self._view.setBackgroundColor(Color.argb(150, 0, 0, 0))
            self._view.setPadding(20, 10, 20, 10)

            # 한글 폰트 적용
            my_font = Typeface.createFromAsset(asset_manager, "210 M고딕030.ttf")
            self._view.setTypeface(my_font)

            self._window.addView(self._view, self._params)

        self._view.setText(text)

    def hide(self):
        if self._view is not None:
            self._window.removeView(self._view)
            self._view = None

class YouTubeSubtitleApp(MDApp):
    status_text = StringProperty('서비스가 중지되었습니다')
    is_running = BooleanProperty(False)
    has_overlay_permission = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.overlay = None
        self.check_permissions()

    def build(self):
        return Builder.load_string(KV)

    def check_permissions(self):
        self.has_overlay_permission = Settings.canDrawOverlays(PythonActivity.mActivity)

    def request_overlay_permission(self):
        intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION)
        intent.setData(Uri.parse(f'package:{PythonActivity.mActivity.getPackageName()}'))
        PythonActivity.mActivity.startActivity(intent)

    def on_button_press(self):
        if not self.has_overlay_permission:
            self.request_overlay_permission()
        else:
            if not self.is_running:
                self.start_service()
            else:
                self.stop_service()

    def start_service(self):
        self.is_running = True
        self.status_text = '서비스 실행 중...'
        self.overlay = SubtitleOverlay()
        Clock.schedule_interval(self.update_overlay, 1)

    def stop_service(self):
        self.is_running = False
        self.status_text = '서비스가 중지되었습니다'
        if self.overlay:
            self.overlay.hide()
            self.overlay = None
        Clock.unschedule(self.update_overlay)

    def update_overlay(self, dt):
        current_time = time.strftime("%H:%M:%S")
        if self.overlay:
            self.overlay.show(f"현재 시간: {current_time}")
        self.status_text = f"업데이트 시간: {current_time}"

if __name__ == '__main__':
    YouTubeSubtitleApp().run()