# ALBAZ Android bridge methods are called from JavaScript.
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
