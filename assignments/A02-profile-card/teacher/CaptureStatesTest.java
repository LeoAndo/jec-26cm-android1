package jp.ac.jec.a02profilecard;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import java.io.File;
import java.io.FileOutputStream;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import org.junit.Test;
import org.junit.runner.RunWith;
import static androidx.test.espresso.Espresso.onView;
import static androidx.test.espresso.action.ViewActions.*;
import static androidx.test.espresso.assertion.ViewAssertions.matches;
import static androidx.test.espresso.matcher.ViewMatchers.*;

/** エミュレーターの実表示をそのまま保存する教員用。画像の合成は行わない。 */
@RunWith(AndroidJUnit4.class)
public class CaptureStatesTest {
    private Activity activity;
    private void save(String name) throws Exception {
        InstrumentationRegistry.getInstrumentation().waitForIdleSync();
        Thread.sleep(800); // IMEとスクロールの描画が終わった画面を記録する。
        Bitmap bitmap=InstrumentationRegistry.getInstrumentation().getUiAutomation().takeScreenshot();
        File file=new File(activity.getExternalFilesDir(null), name+".png");
        try (FileOutputStream out=new FileOutputStream(file)) {
            if (bitmap==null || !bitmap.compress(Bitmap.CompressFormat.PNG,100,out))
                throw new AssertionError("screenshot failed");
        }
    }
    @Test public void captureApprovedStates() throws Exception {
        Intent intent=new Intent(InstrumentationRegistry.getInstrumentation().getTargetContext(), MainActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        activity=InstrumentationRegistry.getInstrumentation().startActivitySync(intent);
        try {
            onView(withId(R.id.nameTextView)).check(matches(withText("サクラ")));
            save("initial");
            onView(withId(R.id.nameEditText)).perform(scrollTo(),replaceText("リン"),closeSoftKeyboard());
            onView(withId(R.id.applyNameButton)).perform(scrollTo(),click());
            onView(withId(R.id.nameTextView)).check(matches(withText("リン")));
            save("applied");
            onView(withId(R.id.greetButton)).perform(scrollTo(),click());
            onView(withId(R.id.greetingTextView)).check(matches(withText("こんにちは！1年生のリンです。")));
            save("greeting");
            onView(withId(R.id.nameEditText)).perform(scrollTo(),replaceText(""),closeSoftKeyboard());
            onView(withId(R.id.applyNameButton)).perform(scrollTo(),click());
            onView(withId(R.id.nameEditText)).check(matches(hasErrorText("名前を入力してください")));
            save("error");
            onView(withId(R.id.nameEditText)).perform(scrollTo(),replaceText("アレクサンドラマリアサクラアレクサンドラマリアサクラ"),closeSoftKeyboard());
            onView(withId(R.id.applyNameButton)).perform(scrollTo(),click());
            onView(withId(R.id.greetButton)).perform(scrollTo(),click());
            save("long-name");
            onView(withId(R.id.nameEditText)).perform(scrollTo(),click());
            Thread.sleep(800);
            onView(withId(R.id.resetButton)).perform(scrollTo());
            save("keyboard");
        } finally {
            InstrumentationRegistry.getInstrumentation().runOnMainSync(() -> activity.finish());
        }
    }
}
