package jp.ac.jec.a02profilecard;

import android.app.Activity;
import android.content.Intent;
import android.widget.EditText;
import android.view.View;
import androidx.test.espresso.UiController;
import androidx.test.espresso.ViewAction;
import org.hamcrest.Matcher;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import static androidx.test.espresso.Espresso.onView;
import static androidx.test.espresso.action.ViewActions.*;
import static androidx.test.espresso.assertion.ViewAssertions.matches;
import static androidx.test.espresso.matcher.ViewMatchers.*;
import static org.junit.Assert.*;

/** 完成条件の操作順を確認する教員用。開始プロジェクトへは含めない。 */
@RunWith(AndroidJUnit4.class)
public class ProfileCardTest {
    private Activity activity;
    @Before public void launch() {
        Intent intent = new Intent(InstrumentationRegistry.getInstrumentation().getTargetContext(), MainActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        activity = InstrumentationRegistry.getInstrumentation().startActivitySync(intent);
    }
    @After public void finish() {
        InstrumentationRegistry.getInstrumentation().runOnMainSync(() -> activity.finish());
    }
    private void input(String value) {
        onView(withId(R.id.nameEditText)).perform(scrollTo(), replaceText(value));
    }
    // IMEの移動中に古い座標を押さないよう、描画を進めてから位置を取り直す。
    private void settle() {
        onView(isRoot()).perform(new ViewAction() {
            public Matcher<View> getConstraints() { return isRoot(); }
            public String getDescription() { return "wait for IME and scroll layout"; }
            public void perform(UiController ui, View view) { ui.loopMainThreadForAtLeast(600); }
        });
    }
    private void tap(int id) {
        settle(); onView(withId(id)).perform(scrollTo());
        settle(); onView(withId(id)).perform(click());
    }
    private void apply() { tap(R.id.applyNameButton); }
    private void greet() { tap(R.id.greetButton); }
    private void reset() { tap(R.id.resetButton); }
    private void card(String name, String greeting) {
        onView(withId(R.id.nameTextView)).check(matches(withText(name)));
        onView(withId(R.id.greetingTextView)).check(matches(withText(greeting)));
    }
    private void noError() {
        InstrumentationRegistry.getInstrumentation().runOnMainSync(() ->
            assertNull(((EditText) activity.findViewById(R.id.nameEditText)).getError()));
    }
    @Test public void initialStateAndRepeatedGreeting() {
        card("サクラ", "よろしくお願いします。");
        onView(withId(R.id.nameEditText)).check(matches(withText("")));
        noError(); greet(); greet();
        card("サクラ", "こんにちは！1年生のサクラです。");
    }
    @Test public void appliedNameAndUnappliedInputAreSeparate() {
        input("リン"); apply(); card("リン", "よろしくお願いします。");
        greet(); card("リン", "こんにちは！1年生のリンです。");
        input("ミナ"); greet(); card("リン", "こんにちは！1年生のリンです。");
        apply(); card("ミナ", "よろしくお願いします。");
        greet(); card("ミナ", "こんにちは！1年生のミナです。");
    }
    @Test public void blankVariantsPreserveCardAndRecover() {
        input("リン"); apply(); greet();
        for (String blank : new String[]{"", "   ", "　　", " 　"}) {
            input(blank); apply();
            onView(withId(R.id.nameEditText)).check(matches(hasErrorText("名前を入力してください")));
            onView(withId(R.id.nameEditText)).check(matches(hasFocus()));
            card("リン", "こんにちは！1年生のリンです。");
        }
        for (String raw : new String[]{" リン ", "　リン　"}) {
            input(raw); apply(); card("リン", "よろしくお願いします。");
            onView(withId(R.id.nameEditText)).check(matches(withText(raw))); noError();
        }
        for (String raw : new String[]{"アナ マリア", "アナ　マリア"}) {
            input(raw); apply(); card("アナ マリア", "よろしくお願いします。");
        }
    }
    @Test public void resetFromNameAndErrorAndRepeat() {
        input("リン"); apply(); greet(); reset();
        card("サクラ", "よろしくお願いします。");
        input(""); apply(); reset(); reset();
        card("サクラ", "よろしくお願いします。");
        onView(withId(R.id.nameEditText)).check(matches(withText(""))); noError();
        input("ミナ"); apply(); greet(); card("ミナ", "こんにちは！1年生のミナです。");
    }
    @Test public void longNameAndButtonsWithKeyboard() {
        String name="アレクサンドラマリアサクラアレクサンドラマリアサクラ";
        onView(withId(R.id.nameEditText)).perform(scrollTo(), click(), replaceText(name));
        apply(); greet(); card(name, "こんにちは！1年生の" + name + "です。");
        onView(withId(R.id.nameEditText)).perform(scrollTo(), click());
        onView(withId(R.id.applyNameButton)).perform(scrollTo()).check(matches(isDisplayed()));
        onView(withId(R.id.resetButton)).perform(scrollTo()).check(matches(isDisplayed()));
        reset(); card("サクラ", "よろしくお願いします。");
    }
}
