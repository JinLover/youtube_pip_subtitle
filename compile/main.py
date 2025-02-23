from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.utils import platform
from kivy.logger import Logger
from kivy.metrics import dp
from time import time

# 폰트 설정
LabelBase.register('SDGothic', fn_regular='AppleSDGothicNeo.ttc')

def open_usage_access_settings():
    """Usage Access 설정 화면으로 이동"""
    if platform == 'android':
        from jnius import autoclass
        
        # Android 클래스 가져오기
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        Settings = autoclass('android.provider.Settings')
        
        # 설정 화면으로 이동하는 Intent 생성
        intent = Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS)
        currentActivity = PythonActivity.mActivity
        currentActivity.startActivity(intent)

def check_permissions():
    """Android 권한 확인"""
    if platform == 'android':
        from android.permissions import check_permission
        
        # 권한 확인
        permission = 'android.permission.PACKAGE_USAGE_STATS'
        if not check_permission(permission):
            Logger.warning(f'Permission {permission} not granted')
            return False
    return True

def request_permissions():
    """Android 권한 요청"""
    if platform == 'android':
        from android.permissions import request_permissions
        
        # 필요한 권한 목록
        permissions = [
            'android.permission.PACKAGE_USAGE_STATS'
        ]
        
        # 권한 요청
        request_permissions(permissions)

class MainWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)  # 전체 패딩 추가
        self.spacing = dp(10)  # 위젯 간 간격 추가
        
        # 상태 표시를 위한 ScrollView
        status_scroll = ScrollView(
            size_hint=(1, 0.4),
            do_scroll_x=False,
            do_scroll_y=True
        )
        # 상태 표시 라벨
        self.status_label = Label(
            text='YouTube 앱 검색 중...',
            font_name='SDGothic',
            font_size='20sp',
            size_hint_y=None,
            halign='center',
            valign='middle'
        )
        self.status_label.bind(width=lambda *x: self.status_label.setter('text_size')((self.status_label.width, None)))
        self.status_label.bind(texture_size=lambda *x: self.status_label.setter('height')(self.status_label.texture_size[1]))
        status_scroll.add_widget(self.status_label)
        self.add_widget(status_scroll)
        
        # 오류 로그를 위한 ScrollView
        error_scroll = ScrollView(
            size_hint=(1, 0.3),
            do_scroll_x=False,
            do_scroll_y=True
        )
        # 오류 로그 라벨
        self.error_label = Label(
            text='',
            font_name='SDGothic',
            font_size='14sp',
            size_hint_y=None,
            halign='left',
            valign='top',
            color=(1, 0.3, 0.3, 1)  # 빨간색 계열
        )
        self.error_label.bind(width=lambda *x: self.error_label.setter('text_size')((self.error_label.width, None)))
        self.error_label.bind(texture_size=lambda *x: self.error_label.setter('height')(self.error_label.texture_size[1]))
        error_scroll.add_widget(self.error_label)
        self.add_widget(error_scroll)
        
        # 권한 설정 버튼
        self.permission_button = Button(
            text='권한 설정',
            font_name='SDGothic',
            size_hint=(1, None),
            height='48dp',
            background_color=(0.2, 0.6, 1, 1)  # 파란색 계열
        )
        self.permission_button.bind(on_press=self.open_settings)
        self.add_widget(self.permission_button)
        
        # 검색 버튼
        self.check_button = Button(
            text='YouTube 검색',
            font_name='SDGothic',
            font_size='20sp'
        )
        self.check_button.bind(on_press=self.check_youtube)
        self.add_widget(self.check_button)
        
        # Android인 경우 자동 검색 시작
        if platform == 'android':
            Clock.schedule_interval(self.check_youtube_status, 1.0)
    
    def check_youtube(self, instance=None):
        if platform == 'android':
            try:
                from jnius import autoclass
                
                # Android 시스템 서비스 가져오기
                Context = autoclass('android.content.Context')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                System = autoclass('java.lang.System')
                UsageStatsManager = autoclass('android.app.usage.UsageStatsManager')
                
                # UsageStatsManager 가져오기
                current_activity = PythonActivity.mActivity
                usage_stats_manager = current_activity.getSystemService(Context.USAGE_STATS_SERVICE)
                
                # 최근 5초 동안의 앱 사용 기록 가져오기
                end_time = System.currentTimeMillis()
                start_time = end_time - (5 * 1000)  # 5초
                
                stats = usage_stats_manager.queryUsageStats(
                    UsageStatsManager.INTERVAL_BEST,
                    start_time, end_time
                )
                
                youtube_found = False
                if stats:
                    for stat in stats:
                        package_name = stat.getPackageName()
                        if ('com.google.android.youtube' in package_name or
                            'app.revanced.android.youtube' in package_name):
                            youtube_found = True
                            try:
                                # 현재 실행 중인 액티비티 정보 가져오기
                                activity_manager = current_activity.getSystemService(Context.ACTIVITY_SERVICE)
                                tasks = activity_manager.getAppTasks()
                                if tasks and tasks.size() > 0:
                                    task = tasks.get(0)
                                    root_activity = task.getTaskInfo().topActivity
                                    if root_activity:
                                        # 액티비티 정보에서 video id 추출
                                        data = root_activity.toUri(0)
                                        self.error_label.text = f'디버그: {data}'  # 디버그용
                                        if 'watch?v=' in data:
                                            video_id = data.split('watch?v=')[1].split('&')[0]
                                            url = f'https://www.youtube.com/watch?v={video_id}'
                                            self.status_label.text = f'현재 재생 중인 영상:\n{url}'
                                            return
                            except Exception as e:
                                self.error_label.text = f'액티비티 정보 추출 오류:\n{str(e)}'
                
                if youtube_found:
                    self.status_label.text = 'YouTube가 실행 중이지만\n재생 정보를 찾을 수 없습니다.'
                else:
                    self.status_label.text = 'YouTube가 실행되고 있지 않습니다.'
                    
            except Exception as e:
                self.error_label.text = f'전체 오류:\n{str(e)}'
        else:
            self.status_label.text = '이 기능은 Android에서만 사용 가능합니다.'
    
    def check_youtube_status(self, dt):
        self.check_youtube()
    

        
    def open_settings(self, instance):
        # 권한 설정 화면 열기
        open_usage_access_settings()

class TestApp(App):
    def build(self):
        # 앱 시작 시 권한 요청
        Clock.schedule_once(lambda dt: request_permissions(), 1)
        return MainWidget()

if __name__ == '__main__':
    TestApp().run()
