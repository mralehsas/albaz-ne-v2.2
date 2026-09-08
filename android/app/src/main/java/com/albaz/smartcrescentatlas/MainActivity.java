package com.albaz.smartcrescentatlas;

import android.app.Activity;
import android.app.Dialog;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Message;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.Toast;

public class MainActivity extends Activity {

    private static final int FILE_CHOOSER_REQUEST_CODE = 2201;
    private WebView webView;
    private ValueCallback<Uri[]> filePathCallback;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        getWindow().setStatusBarColor(Color.rgb(6, 17, 31));
        getWindow().setNavigationBarColor(Color.rgb(6, 17, 31));

        setContentView(R.layout.activity_main);
        webView = findViewById(R.id.webView);
        configureWebView(webView, false);

        if (savedInstanceState == null) {
            webView.loadUrl("file:///android_asset/index.html?android=1");
        } else {
            webView.restoreState(savedInstanceState);
        }
    }

    private void configureWebView(WebView view, boolean popup) {
        WebSettings s = view.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setLoadsImagesAutomatically(true);
        s.setUseWideViewPort(true);
        s.setLoadWithOverviewMode(true);
        s.setBuiltInZoomControls(false);
        s.setDisplayZoomControls(false);
        s.setSupportZoom(false);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowContentAccess(true);
        s.setAllowFileAccess(true);
        s.setAllowFileAccessFromFileURLs(false);
        s.setAllowUniversalAccessFromFileURLs(false);
        s.setJavaScriptCanOpenWindowsAutomatically(true);
        s.setSupportMultipleWindows(true);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        s.setTextZoom(100);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) s.setSafeBrowsingEnabled(true);

        view.setBackgroundColor(Color.rgb(6, 17, 31));
        view.setLayerType(View.LAYER_TYPE_HARDWARE, null);
        view.addJavascriptInterface(new AndroidSaveBridge(this), "AndroidSave");
        view.addJavascriptInterface(new AndroidPrintBridge(this, view), "AndroidPrint");

        view.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest request) {
                return routeUri(request.getUrl());
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView v, String url) {
                return routeUri(Uri.parse(url));
            }

            private boolean routeUri(Uri uri) {
                if (uri == null) return false;
                String scheme = uri.getScheme();
                if (scheme == null || "file".equalsIgnoreCase(scheme)
                        || "data".equalsIgnoreCase(scheme)
                        || "blob".equalsIgnoreCase(scheme)
                        || "about".equalsIgnoreCase(scheme)) {
                    return false;
                }
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, uri));
                } catch (Exception e) {
                    Toast.makeText(MainActivity.this,
                            "تعذر فتح الرابط الخارجي.", Toast.LENGTH_SHORT).show();
                }
                return true;
            }

            @Override
            public void onPageFinished(WebView v, String url) {
                super.onPageFinished(v, url);
                String patch =
                        "(function(){" +
                        "document.documentElement.classList.add('android-webview');" +
                        "if(window.AndroidPrint){window.print=function(){AndroidPrint.printPage();};}" +
                        "})();";
                v.evaluateJavascript(patch, null);
            }

            @Override
            public void onReceivedError(WebView v, WebResourceRequest request, WebResourceError error) {
                super.onReceivedError(v, request, error);
                if (request != null && request.isForMainFrame()) {
                    Toast.makeText(MainActivity.this,
                            "حدث خطأ في تحميل واجهة الأطلس.", Toast.LENGTH_LONG).show();
                }
            }
        });

        view.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView webView,
                                             ValueCallback<Uri[]> callback,
                                             FileChooserParams params) {
                if (filePathCallback != null) filePathCallback.onReceiveValue(null);
                filePathCallback = callback;

                Intent intent;
                try {
                    intent = params.createIntent();
                } catch (Exception e) {
                    intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                    intent.setType("*/*");
                    intent.addCategory(Intent.CATEGORY_OPENABLE);
                }

                try {
                    startActivityForResult(intent, FILE_CHOOSER_REQUEST_CODE);
                    return true;
                } catch (Exception e) {
                    filePathCallback = null;
                    Toast.makeText(MainActivity.this,
                            "تعذر فتح منتقي الملفات.", Toast.LENGTH_SHORT).show();
                    return false;
                }
            }

            @Override
            public boolean onCreateWindow(WebView source, boolean isDialog,
                                          boolean isUserGesture, Message resultMsg) {
                return openPopupWebView(resultMsg);
            }
        });

        if (!popup) {
            view.setDownloadListener((url, userAgent, contentDisposition, mimeType, contentLength) -> {
                if (url == null) return;
                if (url.startsWith("data:")) {
                    Toast.makeText(MainActivity.this,
                            "استخدم زر الحفظ داخل الأطلس.", Toast.LENGTH_SHORT).show();
                    return;
                }
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url)));
                } catch (Exception ignored) {
                }
            });
        }
    }

    private boolean openPopupWebView(Message resultMsg) {
        final Dialog dialog = new Dialog(this, android.R.style.Theme_Black_NoTitleBar_Fullscreen);
        final FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(Color.rgb(6, 17, 31));

        final WebView popup = new WebView(this);
        configureWebView(popup, true);

        FrameLayout.LayoutParams webLp = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT);
        root.addView(popup, webLp);

        Button close = new Button(this);
        close.setText("إغلاق");
        close.setTextColor(Color.rgb(6, 17, 31));
        close.setBackgroundColor(Color.rgb(240, 207, 120));
        close.setAllCaps(false);

        FrameLayout.LayoutParams closeLp = new FrameLayout.LayoutParams(
                dp(94), dp(48), Gravity.TOP | Gravity.END);
        closeLp.setMargins(dp(12), dp(18), dp(12), dp(12));
        root.addView(close, closeLp);

        close.setOnClickListener(v -> dialog.dismiss());
        dialog.setContentView(root);
        dialog.setOnDismissListener(d -> {
            try {
                popup.stopLoading();
                popup.destroy();
            } catch (Exception ignored) {
            }
        });
        dialog.show();

        WebView.WebViewTransport transport = (WebView.WebViewTransport) resultMsg.obj;
        transport.setWebView(popup);
        resultMsg.sendToTarget();
        return true;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        if (webView != null) webView.saveState(outState);
        super.onSaveInstanceState(outState);
    }

    @Override
    @SuppressWarnings("deprecation")
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == FILE_CHOOSER_REQUEST_CODE) {
            if (filePathCallback != null) {
                Uri[] results = WebChromeClient.FileChooserParams.parseResult(resultCode, data);
                filePathCallback.onReceiveValue(results);
                filePathCallback = null;
            }
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.removeJavascriptInterface("AndroidSave");
            webView.removeJavascriptInterface("AndroidPrint");
            webView.stopLoading();
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }
}
