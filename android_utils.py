from jnius import autoclass, cast
import time

# 안드로이드 클래스 가져오기
Context = autoclass('android.content.Context')
UsageStatsManager = autoclass('android.app.usage.UsageStatsManager')
PythonActivity = autoclass('org.kivy.android.PythonActivity')

def get_current_app():
    """현재 실행 중인 앱 패키지 이름 가져오기"""
    try:
        activity = PythonActivity.mActivity
        usage_stats_manager = cast(
            'android.app.usage.UsageStatsManager',
            activity.getSystemService(Context.USAGE_STATS_SERVICE)
        )
        
        end_time = int(time.time() * 1000)
        start_time = end_time - 1000  # 1초 전
        
        stats = usage_stats_manager.queryUsageStats(
            UsageStatsManager.INTERVAL_DAILY,
            start_time, end_time
        )
        
        if stats:
            latest_event = max(stats, key=lambda x: x.getLastTimeUsed())
            return latest_event.getPackageName()
            
    except Exception as e:
        print(f"앱 감지 오류: {str(e)}")
    
    return None

def extract_youtube_url(package_name):
    """유튜브 앱에서 현재 재생 중인 비디오 URL 추출"""
    if package_name == "com.google.android.youtube":
        # ActivityManager를 통해 유튜브 앱의 현재 상태 가져오기
        try:
            activity = PythonActivity.mActivity
            activity_manager = activity.getSystemService(Context.ACTIVITY_SERVICE)
            running_tasks = activity_manager.getRunningTasks(1)
            
            if running_tasks and running_tasks[0]:
                base_activity = running_tasks[0].baseActivity
                if base_activity:
                    data = base_activity.getData()
                    if data:
                        return data.toString()
        except Exception as e:
            print(f"URL 추출 오류: {str(e)}")
    
    return None
