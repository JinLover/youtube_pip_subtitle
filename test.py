from jnius import autoclass, cast

Context = autoclass('android.content.Context')
Intent = autoclass('android.content.Intent')
PythonActivity = autoclass('org.kivy.android.PythonActivity')

def get_youtube_url():
    """YouTube 앱에서 현재 재생 중인 비디오 URL 가져오기"""
    recent_app = get_recently_used_app()  # 최근 실행된 앱 확인
    if recent_app == "com.google.android.youtube":
        try:
            activity = PythonActivity.mActivity
            intent = activity.getIntent()
            data = intent.getData()

            if data:
                return data.toString()

        except Exception as e:
            print(f"URL 추출 오류: {str(e)}")

    return None

# 실행 예시
youtube_url = get_youtube_url()
if youtube_url:
    print(f"현재 재생 중인 YouTube URL: {youtube_url}")
else:
    print("YouTube 영상 URL을 찾을 수 없습니다.")