package com.albaz.smartcrescentatlas;

import android.app.Activity;
import android.content.Context;
import android.print.PrintAttributes;
import android.print.PrintManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebView;

public final class AndroidPrintBridge {
    private final Activity activity;
    private final WebView webView;

    public AndroidPrintBridge(Activity activity, WebView webView) {
        this.activity = activity;
        this.webView = webView;
    }

    @JavascriptInterface
    public void printPage() {
        activity.runOnUiThread(() -> {
            try {
                PrintManager printManager =
                        (PrintManager) activity.getSystemService(Context.PRINT_SERVICE);
                if (printManager == null) return;

                String jobName = "ALBAZ_Smart_Crescent_Atlas_Report";
                printManager.print(
                        jobName,
                        webView.createPrintDocumentAdapter(jobName),
                        new PrintAttributes.Builder()
                                .setMediaSize(PrintAttributes.MediaSize.ISO_A4)
                                .setColorMode(PrintAttributes.COLOR_MODE_COLOR)
                                .build()
                );
            } catch (Exception ignored) {
            }
        });
    }
}
