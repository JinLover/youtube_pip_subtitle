from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.utils import platform
from kivy.logger import Logger
from time import time

# 폰트 설정
LabelBase.register('SDGothicNeo', fn_regular='AppleSDGothicNeo.ttc')

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
    """Android 권한 확인 및 요청"""
    if platform == 'android':
        from android.permissions import request_permissions, check_permission, Permission
        from android.storage import primary_external_storage_path
        
        # 필요한 권한 목록
        permissions = [
            'android.permission.PACKAGE_USAGE_STATS'
        ]
        
        # 권한 요청
        request_permissions(permissions)
        
        # 권한 확인
        for permission in permissions:
            if not check_permission(permission):
                Logger.warning(f'Permission {permission} not granted')
                return False
    return True

class MainWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # 상태 표시 라벨
        self.status_label = Label(
            text='YouTube 앱 검색 중...',
            font_name='SDGothicNeo',
            font_size='20sp',
            text_size=(None, None),  # 초기값 설정
            halign='center',  # 가로 정렬
            valign='middle'   # 세로 정렬
        )
        # 레이아웃 변경 시 자동으로 text_size 업데이트
        self.status_label.bind(size=self._update_text_size)
        self.add_widget(self.status_label)
        
        # 권한 설정 버튼
        self.permission_button = Button(
            text='권한 설정',
            font_name='SDGothicNeo',
            size_hint=(1, None),
            height='48dp',
            background_color=(0.2, 0.6, 1, 1)  # 파란색 계열
        )
        self.permission_button.bind(on_press=self.open_settings)
        self.add_widget(self.permission_button)
        
        # 검색 버튼
        self.check_button = Button(
            text='YouTube 검색',
            font_name='SDGothicNeo',
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
                UsageStatsManager = autoclass('android.app.usage.UsageStatsManager')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                System = autoclass('java.lang.System')
                
                # UsageStatsManager 가져오기
                current_activity = PythonActivity.mActivity
                usage_stats_manager = current_activity.getSystemService(Context.USAGE_STATS_SERVICE)
                
                # 지난 5초간의 앱 사용 통계 가져오기
                end_time = System.currentTimeMillis()
                start_time = end_time - (5 * 1000)  # 5초 전
                
                stats = usage_stats_manager.queryUsageStats(
                    UsageStatsManager.INTERVAL_BEST,
                    start_time,
                    end_time
                )
                
                if stats:
                    self.status_label.text = ''
                    print(f'검색된 앱 개수: {len(stats)}')
                    
                    for stat in stats:
                        package_name = stat.getPackageName()
                        last_time_used = stat.getLastTimeUsed()
                        time_diff = (end_time - last_time_used) / 1000  # 초 단위로 변환
                        
                        print(f'패키지: {package_name}, 마지막 사용: {time_diff}초 전')
                        
                        if ('com.google.android.youtube' in package_name or
                            'app.revanced.android.youtube' in package_name) and \
                           time_diff < 5:  # 5초 이내 사용됨
                            self.status_label.text = 'YouTube가 실행 중입니다!'
                            return
                        
                        self.status_label.text += f'{package_name} ({time_diff:.1f}초 전)\n'
                    
                    if not self.status_label.text:
                        self.status_label.text = 'YouTube가 실행되고 있지 않습니다.'
                else:
                    self.status_label.text = '앱 사용 통계를 가져올 수 없습니다.\n권한을 확인해주세요.'
                
                
                # if youtube_running:
                #     self.status_label.text = 'YouTube가 실행 중입니다!'
                # else:
                #     self.status_label.text = 'YouTube가 실행되고 있지 않습니다.'
                    
            except Exception as e:
                self.status_label.text = f'오류 발생\n{str(e)}'
        else:
            self.status_label.text = '이 기능은 Android에서만 사용 가능합니다.'
    
    def check_youtube_status(self, dt):
        self.check_youtube()
    
    def _update_text_size(self, instance, value):
        # 화면 크기에 맞춰 text_size 업데이트
        self.status_label.text_size = (self.status_label.width, None)
        
    def open_settings(self, instance):
        # 권한 설정 화면 열기
        open_usage_access_settings()

class TestApp(App):
    def build(self):
        # 앱 시작 시 권한 확인
        check_permissions()
        return MainWidget()

if __name__ == '__main__':
    TestApp().run()
