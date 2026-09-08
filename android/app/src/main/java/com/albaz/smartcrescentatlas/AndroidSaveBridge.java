package com.albaz.smartcrescentatlas;

import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Context;
import android.media.MediaScannerConnection;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.webkit.JavascriptInterface;
import android.widget.Toast;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class AndroidSaveBridge {
    private final Context context;
    private final ExecutorService io = Executors.newSingleThreadExecutor();

    public AndroidSaveBridge(Context context) {
        this.context = context.getApplicationContext();
    }

    @JavascriptInterface
    public void saveDataUrl(String dataUrl, String fileName, String mimeType) {
        if (dataUrl == null || !dataUrl.startsWith("data:")) {
            toast("تعذر حفظ الملف: البيانات غير صالحة.");
            return;
        }
        final String safeName = sanitizeFileName(fileName, mimeType);
        final String safeMime = (mimeType == null || mimeType.trim().isEmpty())
                ? guessMime(safeName) : mimeType.trim();

        io.execute(() -> {
            try {
                byte[] bytes = decodeDataUrl(dataUrl);
                String location = saveBytes(bytes, safeName, safeMime);
                toast("تم الحفظ بنجاح: " + location);
            } catch (Exception e) {
                toast("تعذر حفظ الملف: " + e.getMessage());
            }
        });
    }

    private byte[] decodeDataUrl(String dataUrl) throws Exception {
        int comma = dataUrl.indexOf(',');
        if (comma < 0) throw new IllegalArgumentException("Data URL ناقص.");
        String meta = dataUrl.substring(0, comma).toLowerCase(Locale.ROOT);
        String payload = dataUrl.substring(comma + 1);

        if (meta.contains(";base64")) {
            return Base64.decode(payload, Base64.DEFAULT);
        }
        String decoded = URLDecoder.decode(payload, StandardCharsets.UTF_8.name());
        return decoded.getBytes(StandardCharsets.UTF_8);
    }

    private String saveBytes(byte[] bytes, String fileName, String mimeType) throws Exception {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            ContentResolver resolver = context.getContentResolver();
            ContentValues values = new ContentValues();
            values.put(MediaStore.Downloads.DISPLAY_NAME, fileName);
            values.put(MediaStore.Downloads.MIME_TYPE, mimeType);
            values.put(MediaStore.Downloads.RELATIVE_PATH,
                    Environment.DIRECTORY_DOWNLOADS + "/ALBAZ Smart Crescent Atlas");
            values.put(MediaStore.Downloads.IS_PENDING, 1);

            Uri uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
            if (uri == null) throw new IllegalStateException("تعذر إنشاء ملف Downloads.");

            try (OutputStream out = resolver.openOutputStream(uri, "w")) {
                if (out == null) throw new IllegalStateException("تعذر فتح الملف للكتابة.");
                out.write(bytes);
                out.flush();
            }

            values.clear();
            values.put(MediaStore.Downloads.IS_PENDING, 0);
            resolver.update(uri, values, null, null);
            return "Downloads/ALBAZ Smart Crescent Atlas/" + fileName;
        }

        File base = context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
        if (base == null) base = context.getFilesDir();
        File dir = new File(base, "ALBAZ Smart Crescent Atlas");
        if (!dir.exists() && !dir.mkdirs()) throw new IllegalStateException("تعذر إنشاء مجلد الحفظ.");

        File target = uniqueFile(dir, fileName);
        try (FileOutputStream out = new FileOutputStream(target)) {
            out.write(bytes);
            out.flush();
        }
        MediaScannerConnection.scanFile(context,
                new String[]{target.getAbsolutePath()},
                new String[]{mimeType}, null);
        return target.getAbsolutePath();
    }

    private static File uniqueFile(File dir, String name) {
        File first = new File(dir, name);
        if (!first.exists()) return first;
        int dot = name.lastIndexOf('.');
        String stem = dot > 0 ? name.substring(0, dot) : name;
        String ext = dot > 0 ? name.substring(dot) : "";
        for (int i = 2; i < 1000; i++) {
            File f = new File(dir, stem + "_" + i + ext);
            if (!f.exists()) return f;
        }
        return new File(dir, stem + "_" + System.currentTimeMillis() + ext);
    }

    private static String sanitizeFileName(String fileName, String mimeType) {
        String name = (fileName == null || fileName.trim().isEmpty()) ? "ALBAZ_export" : fileName.trim();
        name = name.replaceAll("[\\\\/:*?\"<>|\\p{Cntrl}]", "_");
        if (!name.contains(".")) {
            if ("image/png".equalsIgnoreCase(mimeType)) name += ".png";
            else if ("text/html".equalsIgnoreCase(mimeType)) name += ".html";
            else if ("application/json".equalsIgnoreCase(mimeType)) name += ".json";
        }
        return name;
    }

    private static String guessMime(String name) {
        String lower = name.toLowerCase(Locale.ROOT);
        if (lower.endsWith(".png")) return "image/png";
        if (lower.endsWith(".html") || lower.endsWith(".htm")) return "text/html";
        if (lower.endsWith(".json")) return "application/json";
        return "application/octet-stream";
    }

    private void toast(String message) {
        android.os.Handler main = new android.os.Handler(context.getMainLooper());
        main.post(() -> Toast.makeText(context, message, Toast.LENGTH_LONG).show());
    }
}
