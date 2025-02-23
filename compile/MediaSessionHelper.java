package org.jinlover.youtubepipsubtitle;

import android.content.Context;
import android.media.session.MediaSessionManager;
import android.media.session.MediaController;
import android.media.session.PlaybackState;
import android.media.MediaMetadata;
import android.content.ComponentName;
import android.util.Log;
import org.json.JSONObject;
import org.json.JSONException;
import java.util.List;

public class MediaSessionHelper {
    private static final String TAG = "MediaSessionHelper";
    private final Context context;
    private final MediaSessionManager mediaSessionManager;
    private final ComponentName notificationListener;

    public MediaSessionHelper(Context context) {
        this.context = context;
        this.mediaSessionManager = (MediaSessionManager) context.getSystemService(Context.MEDIA_SESSION_SERVICE);
        this.notificationListener = new ComponentName(context.getPackageName(), "org.jinlover.youtubepipsubtitle.MyNotificationListener");
    }

    public String getYouTubePlaybackInfo() {
        try {
            if (!PermissionManager.checkNotificationListenerPermission(context)) {
                return createErrorJson("알림 접근 권한이 필요합니다.");
            }

            List<MediaController> controllers = mediaSessionManager.getActiveSessions(notificationListener);
            for (MediaController controller : controllers) {
                String packageName = controller.getPackageName();
                if (isYouTubePackage(packageName)) {
                    return extractPlaybackInfo(controller);
                }
            }
            return createErrorJson("YouTube가 실행되지 않았습니다.");
        } catch (Exception e) {
            Log.e(TAG, "Error getting YouTube playback info: " + e.toString());
            return createErrorJson("오류 발생: " + e.getMessage());
        }
    }

    private boolean isYouTubePackage(String packageName) {
        return packageName.equals("com.google.android.youtube") ||
               packageName.equals("app.revanced.android.youtube");
    }

    private String extractPlaybackInfo(MediaController controller) {
        try {
            PlaybackState state = controller.getPlaybackState();
            MediaMetadata metadata = controller.getMetadata();
            JSONObject json = new JSONObject();

            if (state != null) {
                boolean isPlaying = state.getState() == PlaybackState.STATE_PLAYING;
                long position = state.getPosition() / 1000; // 초 단위로 변환
                json.put("is_playing", isPlaying);
                json.put("position", position);
            }

            if (metadata != null) {
                long duration = metadata.getLong(MediaMetadata.METADATA_KEY_DURATION) / 1000;
                String videoId = metadata.getString(MediaMetadata.METADATA_KEY_MEDIA_ID);
                String title = metadata.getString(MediaMetadata.METADATA_KEY_TITLE);
                
                json.put("duration", duration);
                json.put("video_id", videoId);
                json.put("title", title);
            }

            json.put("success", true);
            return json.toString();
        } catch (JSONException e) {
            Log.e(TAG, "Error creating JSON: " + e.toString());
            return createErrorJson("JSON 생성 오류");
        }
    }

    private String createErrorJson(String message) {
        try {
            JSONObject json = new JSONObject();
            json.put("success", false);
            json.put("error", message);
            return json.toString();
        } catch (JSONException e) {
            Log.e(TAG, "Error creating error JSON: " + e.toString());
            return "{\"success\": false, \"error\": \"" + message + "\"}";
        }
    }
}
