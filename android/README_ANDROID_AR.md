# أطلس الباز الذكي لرؤية الهلال — Android

**ALBAZ Smart Crescent Visibility Atlas**  
**مدعوم بمعيار ALBAZ-NE V2.2**

## فكرة الحزمة
مشروع Android Studio أصلي يعتمد WebView بدون Compose. لا يعيد كتابة المحرك العلمي ولا ينسخ معادلته إلى كود Android جديد. قبل كل Build يقوم Gradle بنسخ ملفات الويب الرسمية الموجودة في جذر المستودع إلى `app/src/main/assets`.

المسار داخل التطبيق:
`file:///android_asset/index.html?android=1`

## المزايا
- تشغيل محلي Offline بعد تثبيت التطبيق.
- JavaScript + Canvas + 2D/3D مع Hardware Acceleration.
- دعم العربية وRTL.
- حفظ PNG وHTML إلى Downloads على Android 10+.
- دعم Print / Save as PDF عبر نظام Android.
- دعم اختيار الملفات.
- الروابط الخارجية تفتح في المتصفح الافتراضي.
- تدوير الجهاز لا يعيد تهيئة WebView.
- لا توجد تعديلات على دوال ALBAZ العلمية أثناء التغليف.

## المتطلبات
- Android Studio حديث.
- JDK 17.
- Android SDK 35.
- Gradle 8.9.
- Android Gradle Plugin 8.7.3.
- الحد الأدنى Android 8.0 (API 26).

## فتح المشروع
1. افتح Android Studio.
2. اختر **Open**.
3. اختر مجلد `android`.
4. انتظر Gradle Sync.
5. اختر جهازًا أو Emulator.
6. اضغط Run.

## بناء APK تجريبي
بعد وجود Gradle Wrapper شغّل:
`BUILD_DEBUG_APK.bat`

الناتج:
`Dist/ALBAZ_Smart_Crescent_Atlas_v2.2.1_DEBUG.apk`

## Release
شغّل:
`CLEAN_BUILD_RELEASE.bat`

ينتج APK غير موقع. للتوزيع الرسمي أو Google Play استخدم مفتاح توقيع خاص وثابت ولا ترفع المفتاح أو كلمة مروره إلى GitHub.

## تحديث الأطلس
يكفي تحديث `index.html` في جذر المستودع ثم إعادة Build؛ مهمة `syncOfficialWebAssets` تنسخ آخر نسخة تلقائيًا.

## ملاحظة حماية
أي JavaScript موزع داخل APK يمكن لمتخصص استخراجه. حماية الملكية الفكرية الكاملة تتطلب إبقاء النواة الحساسة خارج الحزمة العامة أو نقلها إلى خدمة خلفية خاصة.
