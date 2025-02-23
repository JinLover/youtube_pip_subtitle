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
LabelBase.register('SDGothicNeo', fn_regular='AppleSDGothicNeo.ttc')

def open_usage_access_settings():
    """Usage Access 설정 화면으로 이동"""
    if platform == 'android':
        from jnius import autoclass
        
        # Android 클래스 가져오기
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        Settings = autoclass('android.provider.Settings')
        Bundle = autoclass('android.os.Bundle')
        
        # 설정 화면으로 이동하는 Intent 생성
        intent = Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        intent.addFlags(Intent.FLAG_ACTIVITY_NO_HISTORY)
        
        # 현재 앱의 패키지 이름 추가
        bundle = Bundle()
        bundle.putString('android.provider.extra.APP_PACKAGE', PythonActivity.mActivity.getPackageName())
        intent.putExtras(bundle)
        
        currentActivity = PythonActivity.mActivity
        currentActivity.startActivity(intent)

def check_notification_listener_permission():
    """알림 접근 권한이 있는지 확인"""
    if platform == 'android':
        try:
            from jnius import autoclass
            import json
            
            # Android 클래스 가져오기
            Context = autoclass('android.content.Context')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Settings = autoclass('android.provider.Settings')
            String = autoclass('java.lang.String')
            
            # 현재 앱의 패키지 이름
            activity = PythonActivity.mActivity
            if not activity:
                return False
                
            package_name = activity.getPackageName()
            
            # 알림 접근 권한이 있는 앱 목록 가져오기
            flat_settings = Settings.Secure.getString(
                activity.getContentResolver(),
                "enabled_notification_listeners"
            )
            
            if flat_settings:
                names = flat_settings.split(":")
                for name in names:
                    if package_name in name:
                        return True
            return False
        except Exception as e:
            Logger.error(f'NotificationListener: 권한 확인 중 오류: {str(e)}')
            return False
    return True

def check_permissions():
    """Android 권한 확인 및 요청
    
    Returns:
        tuple: (성공 여부, 오류 메시지, 재시도 필요 여부)
    """
    if platform != 'android':
        return True, None, False
        
    try:
        from jnius import autoclass
        
        # Android 클래스 가져오기
        AppOpsManager = autoclass('android.app.AppOpsManager')
        Context = autoclass('android.content.Context')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Process = autoclass('android.os.Process')
        
        # 현재 액티비티 확인
        activity = PythonActivity.mActivity
        if not activity:
            Logger.error('Permissions: Activity 초기화 실패')
            return False, '앱이 올바르게 초기화되지 않았습니다. 앱을 다시 시작해주세요.', False
            
        # 알림 접근 권한 확인
        notification_permission = check_notification_listener_permission()
        if not notification_permission:
            Logger.info('Permissions: 알림 접근 권한 요청')
            try:
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                
                intent = Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                activity.startActivity(intent)
                return False, '알림 접근 권한이 필요합니다. 설정에서 권한을 허용한 후 앱으로 돌아와주세요.', True
            except Exception as e:
                Logger.error(f'Permissions: 알림 권한 설정 화면 열기 실패: {str(e)}')
                return False, '알림 접근 권한 설정을 열 수 없습니다. 설정 앱에서 직접 권한을 허용해주세요.', False
            
        # 패키지 사용 통계 권한 확인
        try:
            app_ops = activity.getSystemService(Context.APP_OPS_SERVICE)
            package_name = activity.getPackageName()
            
            package_usage_stats_mode = app_ops.checkOpNoThrow(
                AppOpsManager.OPSTR_GET_USAGE_STATS,
                Process.myUid(),
                package_name
            )
            
            if package_usage_stats_mode != AppOpsManager.MODE_ALLOWED:
                Logger.info('Permissions: 패키지 사용 통계 권한 요청')
                open_usage_access_settings()
                return False, '패키지 사용 통계 권한이 필요합니다. 설정에서 권한을 허용한 후 앱으로 돌아와주세요.', True
        except Exception as e:
            Logger.error(f'Permissions: 패키지 사용 통계 권한 확인 실패: {str(e)}')
            return False, '패키지 사용 통계 권한을 확인할 수 없습니다. 설정 앱에서 직접 권한을 허용해주세요.', False
            
        return True, None, False
            
    except Exception as e:
        Logger.error(f'Permissions: 권한 확인 중 오류 발생: {str(e)}')
        return False, f'권한 확인 중 오류가 발생했습니다. 앱을 다시 시작해주세요.', False

class MainWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._init_widgets)
    
    def _init_widgets(self, dt):
        # .kv 파일에서 정의된 위젯들을 찾습니다
        self.status_label = self.ids.status_label
        self.error_label = self.ids.error_label
        self.playback_label = self.ids.playback_label
        self.time_label = self.ids.time_label
        self.url_label = self.ids.url_label
        
        if platform == 'android':
            # Android인 경우 자동 검색 시작
            Clock.schedule_interval(self.check_youtube_status, 1.0)
    
    def check_youtube(self, *args):
        if platform == 'android':
            try:
                # 권한 확인
                permission_granted, error_message, retry_needed = check_permissions()
                if not permission_granted:
                    self.error_label.text = error_message
                    self.status_label.text = '권한 설정이 필요합니다'
                    self.playback_label.text = ''
                    self.time_label.text = ''
                    self.url_label.text = ''
                    
                    # 권한 설정 버튼 활성화 및 강조
                    permission_button = self.ids.permission_button
                    permission_button.background_color = (1, 0.3, 0.3, 1)  # 빨간색으로 강조
                    permission_button.disabled = False
                    
                    # YouTube 검색 버튼 비활성화
                    check_button = self.ids.check_button
                    check_button.disabled = True
                    check_button.background_color = (0.5, 0.5, 0.5, 1)  # 회색으로 변경
                    return
                
                from jnius import autoclass, cast
                import json
                
                # Android 클래스들 가져오기
                Context = autoclass('android.content.Context')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                MediaSessionManager = autoclass('android.media.session.MediaSessionManager')
                PlaybackState = autoclass('android.media.session.PlaybackState')
                MediaMetadata = autoclass('android.media.MediaMetadata')
                ComponentName = autoclass('android.content.ComponentName')
                NotificationListenerService = autoclass('android.service.notification.NotificationListenerService')
                
                # 현재 Activity 가져오기
                activity = PythonActivity.mActivity
                if not activity:
                    error('Activity가 없습니다.')
                    self.error_label.text = '앱이 올바르게 초기화되지 않았습니다.\n앱을 다시 시작해주세요.'
                    self.status_label.text = '앱 오류'
                    return
                
                # MediaSessionManager 가져오기
                try:
                    media_session_manager = cast(
                        'android.media.session.MediaSessionManager',
                        activity.getSystemService(Context.MEDIA_SESSION_SERVICE)
                    )
                except Exception as e:
                    error(f'MediaSessionManager 가져오기 실패: {str(e)}')
                    self.error_label.text = '미디어 세션 관리자를 가져올 수 없습니다.\n앱을 다시 시작해주세요.'
                    self.status_label.text = '앱 오류'
                    return
                
                # NotificationListener 컴포넌트 생성
                try:
                    component = ComponentName(
                        activity.getPackageName(),
                        "org.kivy.android.PythonService"
                    )
                except Exception as e:
                    error(f'ComponentName 생성 실패: {str(e)}')
                    self.error_label.text = '알림 서비스를 초기화할 수 없습니다.\n앱을 다시 시작해주세요.'
                    self.status_label.text = '앱 오류'
                    return
                
                # 활성 미디어 세션 가져오기
                try:
                    controllers = media_session_manager.getActiveSessions(component)
                except Exception as e:
                    error(f'미디어 세션 가져오기 실패: {str(e)}')
                    return
                
                youtube_info = {
                    'success': False,
                    'error': 'YouTube가 실행되지 않았습니다.'
                }
                
                # YouTube 미디어 세션 찾기
                for i in range(controllers.size()):
                    controller = controllers.get(i)
                    package_name = controller.getPackageName()
                    
                    if package_name in ['com.google.android.youtube', 'app.revanced.android.youtube']:
                        # 재생 상태 가져오기
                        playback_state = controller.getPlaybackState()
                        metadata = controller.getMetadata()
                        
                        if playback_state and metadata:
                            is_playing = playback_state.getState() == PlaybackState.STATE_PLAYING
                            position = playback_state.getPosition() // 1000  # ms to s
                            duration = metadata.getLong(MediaMetadata.METADATA_KEY_DURATION) // 1000  # ms to s
                            title = metadata.getString(MediaMetadata.METADATA_KEY_TITLE)
                            video_id = metadata.getString(MediaMetadata.METADATA_KEY_MEDIA_ID)
                            
                            youtube_info = {
                                'success': True,
                                'is_playing': is_playing,
                                'position': position,
                                'duration': duration,
                                'title': title,
                                'video_id': video_id
                            }
                            break
                
                # UI 업데이트
                if youtube_info['success']:
                    self.playback_label.text = f'재생 상태: {"재생 중" if youtube_info["is_playing"] else "일시정지"}'
                    self.time_label.text = f'재생 시간: {youtube_info["position"]//60:02d}:{youtube_info["position"]%60:02d} / {youtube_info["duration"]//60:02d}:{youtube_info["duration"]%60:02d}'
                    
                    if youtube_info['video_id']:
                        url = f'https://youtu.be/{youtube_info["video_id"]}'
                        self.url_label.text = url
                        self.status_label.text = f'재생 중인 영상: {youtube_info["title"]}'
                    else:
                        self.url_label.text = ''
                        self.status_label.text = 'YouTube 재생 정보를 찾았습니다.'
                else:
                    self.status_label.text = youtube_info['error']
                    self.playback_label.text = '재생 상태: 정보 없음'
                    self.time_label.text = '재생 시간: --:--'
                    self.url_label.text = ''
                    
            except Exception as e:
                Logger.error(f'YouTubePip: Error in check_youtube: {str(e)}')
                self.error_label.text = f'오류 발생:\n{str(e)}'
                self.status_label.text = '오류가 발생했습니다.'
                self.playback_label.text = '재생 상태: 정보 없음'
                self.time_label.text = '재생 시간: --:--'
                self.url_label.text = ''
        else:
            self.status_label.text = '이 기능은 Android에서만 사용 가능합니다.'
    
    def open_settings(self, *args):
        open_usage_access_settings()
    
    def check_youtube_status(self, dt):
        try:
            self.check_youtube()
        except Exception as e:
            Logger.error(f'YouTubePip: Error in check_youtube_status: {str(e)}')
            self.error_label.text = f'상태 확인 중 오류 발생:\n{str(e)}'

    def open_settings(self, *args):
        """권한 설정 화면으로 이동"""
        if platform == 'android':
            try:
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                
                activity = PythonActivity.mActivity
                if activity:
                    # 알림 접근 권한 설정 화면으로 이동
                    intent = Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)
                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    activity.startActivity(intent)
                    
                    # 권한 설정 버튼 일반 상태로 변경
                    permission_button = self.ids.permission_button
                    permission_button.background_color = (0.2, 0.6, 1, 1)
                    
                    # 상태 메시지 업데이트
                    self.status_label.text = '권한을 허용한 후 YouTube 검색 버튼을 눌러주세요'
            except Exception as e:
                Logger.error(f'MainWidget: 설정 화면을 열 수 없습니다: {str(e)}')
                self.error_label.text = f'설정 화면을 열 수 없습니다: {str(e)}'

class YouTubePipApp(App):
    def build(self):
        # 앱 시작 시 권한 확인
        # if platform == 'android':
        if not check_permissions():
            # 권한이 없으면 Usage Access 설정 화면으로 이동
            open_usage_access_settings()
        return MainWidget()

if __name__ == '__main__':
    YouTubePipApp().run()
