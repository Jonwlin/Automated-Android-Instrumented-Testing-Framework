package com.jonwlin.test

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.Parameterized
import java.util.*

/**
 * Instrumented test, which will execute on an Android device.
 *
 * See [testing documentation](http://d.android.com/tools/testing).
 */
@RunWith(value = Parameterized::class)
class ExampledInstrumentedTest(private val input: String) {
    @get:Rule
    var mCaptureLogcatRule = CaptureLogcatOnTestFailureRule()

    @get:Rule
    var mRetryTestRule = RetryTestRule(2)

    @Test
    fun useAppContext() {
        // Context of the app under test.
        val appContext = InstrumentationRegistry.getInstrumentation().targetContext
        assertEquals("com.jonwlin.test", input)
    }

    companion object {
        @JvmStatic
        @Parameterized.Parameters(name = "Checking domain: {0}")
        fun data(): Iterable<Array<String>> {
            val value: ArrayList<Array<String>> = ArrayList()
            value.add(arrayOf("com.jonwlin.test"))
            value.add(arrayOf("com.fail.test"))
            return value
        }
    }
}