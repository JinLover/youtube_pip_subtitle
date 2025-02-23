package org.jinlover.youtubepipsubtitle;

import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;
import android.content.Intent;
import android.util.Log;
import android.app.Notification;
import android.media.session.MediaController;
import android.media.session.MediaSessionManager;
import android.media.session.PlaybackState;
import android.media.MediaMetadata;
import android.os.Handler;
import android.os.Looper;
import android.content.Context;
import android.os.Bundle;
import java.util.List;
import java.util.ArrayList;

public class MyNotificationListener extends NotificationListenerService {
    private static final String TAG = "MyNotificationListener";
    private Handler handler;
    private static final long UPDATE_INTERVAL = 1000; // 1초
    private String lastTitle = "";
    private boolean isPlaying = false;
    private MediaSessionManager mediaSessionManager;
    private MediaController activeController;
    private long lastPosition = 0;
    private long lastUpdateTime = 0;

    @Override
    public void onCreate() {
        super.onCreate();
        handler = new Handler(Looper.getMainLooper());
        mediaSessionManager = (MediaSessionManager) getSystemService(Context.MEDIA_SESSION_SERVICE);
        startPeriodicUpdate();
        
        // 초기 상태 로깅
        Log.d(TAG, "NotificationListener service created");
    }

    private void startPeriodicUpdate() {
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                checkCurrentPlayback();
                handler.postDelayed(this, UPDATE_INTERVAL);
            }
        }, UPDATE_INTERVAL);
    }

    private void checkCurrentPlayback() {
        try {
            // 이전 상태 저장
            boolean wasPlaying = isPlaying;
            String previousTitle = lastTitle;
            long previousPosition = lastPosition;
            
            MediaController newController = findYouTubeController();
            PlaybackInfo playbackInfo = new PlaybackInfo();
            
            // MediaController에서 정보 추출
            if (newController != null) {
                activeController = newController;
                playbackInfo.updateFromMediaController(activeController);
                Log.d(TAG, "MediaController 정보 갱신 성공");
            } else {
                Log.w(TAG, "MediaController를 찾을 수 없습니다.");
            }
            
            // 알림에서 추가 정보 확인
            if (!playbackInfo.isPlaying) {
                StatusBarNotification[] notifications = getActiveNotifications();
                if (notifications != null && notifications.length > 0) {
                    playbackInfo.updateFromNotifications(notifications);
                    Log.d(TAG, "알림에서 정보 갱신 성공");
                } else {
                    Log.w(TAG, "활성화된 알림이 없습니다.");
                }
            }
            
            // 상태 변경 감지
            if (wasPlaying != playbackInfo.isPlaying) {
                Log.i(TAG, "재생 상태 변경: " + (playbackInfo.isPlaying ? "재생 중" : "일시정지"));
            }
            if (!previousTitle.equals(playbackInfo.title)) {
                Log.i(TAG, "제목 변경: " + playbackInfo.title);
            }
            if (Math.abs(previousPosition - playbackInfo.position) > 1000) {
                Log.d(TAG, "재생 시간 변경: " + (playbackInfo.position / 1000) + "초");
            }
            
            // 상태 업데이트 및 브로드캐스트
            updateAndBroadcastState(playbackInfo);
            
        } catch (SecurityException e) {
            Log.e(TAG, "권한 없음: " + e.getMessage());
        } catch (IllegalStateException e) {
            Log.e(TAG, "서비스 상태 오류: " + e.getMessage());
        } catch (Exception e) {
            Log.e(TAG, "예상치 못한 오류 발생: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    private MediaController findYouTubeController() {
        MediaController controller = null;
        
        // MediaSession에서 컨트롤러 찾기
        try {
            if (mediaSessionManager == null) {
                Log.e(TAG, "MediaSessionManager가 초기화되지 않았습니다.");
                return null;
            }
            
            List<MediaController> controllers = mediaSessionManager.getActiveSessions(null);
            if (controllers.isEmpty()) {
                Log.d(TAG, "활성화된 MediaSession이 없습니다.");
            } else {
                Log.d(TAG, controllers.size() + "개의 활성화된 MediaSession 발견");
                
                for (MediaController mc : controllers) {
                    String packageName = mc.getPackageName();
                    if (isYouTubePackage(packageName)) {
                        Log.i(TAG, "YouTube MediaSession 발견: " + packageName);
                        controller = mc;
                        break;
                    }
                }
            }
        } catch (SecurityException e) {
            Log.e(TAG, "MediaSession 접근 권한 없음: " + e.getMessage());
        } catch (Exception e) {
            Log.e(TAG, "MediaSession 검색 중 오류: " + e.getMessage());
            e.printStackTrace();
        }
        
        // MediaSession에서 찾지 못한 경우 알림에서 찾기
        if (controller == null) {
            try {
                StatusBarNotification[] notifications = getActiveNotifications();
                if (notifications == null || notifications.length == 0) {
                    Log.d(TAG, "활성화된 알림이 없습니다.");
                    return null;
                }
                
                Log.d(TAG, notifications.length + "개의 활성화된 알림 발견");
                
                for (StatusBarNotification sbn : notifications) {
                    String packageName = sbn.getPackageName();
                    if (isYouTubePackage(packageName)) {
                        Notification notification = sbn.getNotification();
                        if (notification != null && notification.getMediaSession() != null) {
                            Log.i(TAG, "YouTube 알림에서 MediaSession 발견: " + packageName);
                            return new MediaController(
                                getApplicationContext(),
                                notification.getMediaSession()
                            );
                        }
                    }
                }
            } catch (SecurityException e) {
                Log.e(TAG, "알림 접근 권한 없음: " + e.getMessage());
            } catch (Exception e) {
                Log.e(TAG, "알림에서 MediaController 생성 중 오류: " + e.getMessage());
                e.printStackTrace();
            }
        }
        
        return controller;
    }
    
    private boolean isYouTubePackage(String packageName) {
        return packageName.contains("youtube");
    }
    
    private class PlaybackInfo {
        boolean isPlaying = false;
        String title = lastTitle;
        long position = lastPosition;
        
        void updateFromMediaController(MediaController controller) {
            try {
                // 재생 상태 확인
                PlaybackState state = controller.getPlaybackState();
                if (state != null) {
                    isPlaying = state.getState() == PlaybackState.STATE_PLAYING;
                    position = state.getPosition();
                }
                
                // 제목 확인
                MediaMetadata metadata = controller.getMetadata();
                if (metadata != null) {
                    String newTitle = metadata.getString(MediaMetadata.METADATA_KEY_TITLE);
                    if (newTitle != null && !newTitle.isEmpty()) {
                        title = newTitle;
                    }
                }
            } catch (Exception e) {
                Log.e(TAG, "Error getting playback info from controller: " + e.getMessage());
            }
        }
        
        void updateFromNotifications(StatusBarNotification[] notifications) {
            for (StatusBarNotification sbn : notifications) {
                if (!isYouTubePackage(sbn.getPackageName())) continue;
                
                Notification notification = sbn.getNotification();
                Bundle extras = notification.extras;
                if (extras == null) continue;
                
                // 제목 업데이트
                String newTitle = extras.getString(Notification.EXTRA_TITLE);
                if (newTitle != null && !newTitle.isEmpty()) {
                    title = newTitle;
                }
                
                // 재생 상태 확인
                if (notification.actions != null) {
                    for (Notification.Action action : notification.actions) {
                        String actionTitle = action.title.toString().toLowerCase();
                        if (actionTitle.contains("일시중지") || actionTitle.contains("pause")) {
                            isPlaying = true;
                            break;
                        }
                    }
                }
                
                // 시간 정보 파싱
                parseTimeFromNotification(extras);
                break;
            }
        }
        
        void parseTimeFromNotification(Bundle extras) {
            String timeText = extras.getString(Notification.EXTRA_TEXT);
            if (timeText == null) return;
            
            try {
                // "3:45 / 5:00" 형식 처리
                String currentTime = timeText.split("/")[0].trim();
                String[] timeParts = currentTime.split(":");
                
                if (timeParts.length == 2) {
                    // 분:초 형식
                    position = (Long.parseLong(timeParts[0]) * 60 + 
                              Long.parseLong(timeParts[1])) * 1000;
                } else if (timeParts.length == 3) {
                    // 시:분:초 형식
                    position = (Long.parseLong(timeParts[0]) * 3600 + 
                              Long.parseLong(timeParts[1]) * 60 + 
                              Long.parseLong(timeParts[2])) * 1000;
                }
            } catch (Exception e) {
                Log.e(TAG, "Error parsing time '" + timeText + "': " + e.getMessage());
            }
        }
    }
                    
    private void updateAndBroadcastState(PlaybackInfo info) {
        long currentTime = System.currentTimeMillis();
        boolean shouldUpdate = isPlaying != info.isPlaying || 
                             currentTime - lastUpdateTime >= UPDATE_INTERVAL;
        
        if (shouldUpdate || !info.title.equals(lastTitle)) {
            // 상태 저장
            lastTitle = info.title;
            lastPosition = info.position;
            lastUpdateTime = currentTime;
            isPlaying = info.isPlaying;
            
            // 재생 상태 브로드캐스트
            Intent intent = new Intent("org.kivy.notificationlistener.PLAYBACK_UPDATE");
            intent.putExtra("title", info.title);
            intent.putExtra("isPlaying", info.isPlaying);
            intent.putExtra("position", info.position);
            
            // 로그 추가
            Log.d(TAG, String.format(
                "Broadcasting state - Title: %s, Playing: %b, Position: %d",
                info.title, info.isPlaying, info.position
            ));
            
            sendBroadcast(intent);
        }
        
        // 백그라운드 상태 처리
        if (activeController == null) {
                // 이전 상태 유지
                Intent intent = new Intent("org.kivy.notificationlistener.PLAYBACK_UPDATE");
                intent.putExtra("title", lastTitle);
                intent.putExtra("isPlaying", false);
                intent.putExtra("position", lastPosition);
                
                Log.d(TAG, "YouTube not found, maintaining last known state");
                
                sendBroadcast(intent);
            }
            
        } catch (Exception e) {
            Log.e(TAG, "Error checking playback: " + e.getMessage());
        }
    }

    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {
        if (sbn.getPackageName().contains("youtube")) {
            try {
                Notification notification = sbn.getNotification();
                Bundle extras = notification.extras;
                
                String title = extras.getString(Notification.EXTRA_TITLE);
                String text = extras.getString(Notification.EXTRA_TEXT);
                
                if (title != null && !title.equals(lastTitle)) {
                    lastTitle = title;
                    Log.d(TAG, String.format(
                        "New YouTube notification - Title: %s, Text: %s",
                        title, text
                    ));
                    
                    // 알림 정보 전송
                    Intent intent = new Intent("org.kivy.notificationlistener.NOTIFICATION");
                    intent.putExtra("title", title);
                    intent.putExtra("text", text);
                    sendBroadcast(intent);
                    
                    // MediaSession 업데이트
                    if (notification.getMediaSession() != null) {
                        activeController = new MediaController(
                            getApplicationContext(),
                            notification.getMediaSession()
                        );
                    }
                    
                    // 재생 상태 확인
                    checkCurrentPlayback();
                }
            } catch (Exception e) {
                Log.e(TAG, "Error processing notification: " + e.getMessage());
            }
        }
    }

    @Override
    public void onNotificationRemoved(StatusBarNotification sbn) {
        if (sbn.getPackageName().contains("youtube")) {
            Log.d(TAG, "YouTube notification removed");
            
            // 알림이 삭제되어도 재생 상태는 유지
            // MediaController가 있다면 그것을 사용
            if (activeController != null) {
                checkCurrentPlayback();
            } else {
                // MediaController가 없을 때만 재생 중지로 처리
                isPlaying = false;
                
                Intent intent = new Intent("org.kivy.notificationlistener.PLAYBACK_UPDATE");
                intent.putExtra("title", lastTitle);
                intent.putExtra("isPlaying", false);
                intent.putExtra("position", lastPosition);
                sendBroadcast(intent);
            }
        }
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        handler.removeCallbacksAndMessages(null);
    }
}