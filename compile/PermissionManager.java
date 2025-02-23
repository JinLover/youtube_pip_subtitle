package org.jinlover.youtubepipsubtitle;

import android.content.Context;
import android.app.AppOpsManager;
import android.provider.Settings;
import android.content.ComponentName;
import android.util.Log;
import android.content.Intent;

public class PermissionManager {
    private static final String TAG = "PermissionManager";

    public static boolean checkUsageStatsPermission(Context context) {
        try {
            AppOpsManager appOps = (AppOpsManager) context.getSystemService(Context.APP_OPS_SERVICE);
            int mode = appOps.checkOpNoThrow(AppOpsManager.OPSTR_GET_USAGE_STATS,
                    android.os.Process.myUid(), context.getPackageName());
            return mode == AppOpsManager.MODE_ALLOWED;
        } catch (Exception e) {
            Log.e(TAG, "Error checking usage stats permission: " + e.toString());
            return false;
        }
    }

    public static boolean checkNotificationListenerPermission(Context context) {
        try {
            ComponentName cn = new ComponentName(context, MyNotificationListener.class);
            String flat = Settings.Secure.getString(context.getContentResolver(),
                    "enabled_notification_listeners");
            return flat != null && flat.contains(cn.flattenToString());
        } catch (Exception e) {
            Log.e(TAG, "Error checking notification listener permission: " + e.toString());
            return false;
        }
    }

    public static void openUsageAccessSettings(Context context) {
        try {
            Intent intent = new Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(intent);
        } catch (Exception e) {
            Log.e(TAG, "Error opening usage access settings: " + e.toString());
        }
    }

    public static void openNotificationListenerSettings(Context context) {
        try {
            Intent intent = new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(intent);
        } catch (Exception e) {
            Log.e(TAG, "Error opening notification listener settings: " + e.toString());
        }
    }
}
