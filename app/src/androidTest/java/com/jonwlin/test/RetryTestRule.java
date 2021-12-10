package com.jonwlin.test;

import android.util.Log;

import org.junit.rules.TestRule;
import org.junit.runner.Description;
import org.junit.runners.model.Statement;

public class RetryTestRule implements TestRule {
    private static final String TAG = RetryTestRule.class.getSimpleName();
    private final int retryCount;

    public RetryTestRule(int retryCount) {
        this.retryCount = retryCount;
    }

    public Statement apply(Statement base, Description description) {
        return statement(base, description);
    }

    private Statement statement(final Statement base, final Description description) {
        return new Statement() {
            @Override
            public void evaluate() throws Throwable {
                Throwable caughtThrowable = null;

                // implement retry logic here
                for (int i = 0; i < retryCount; i++) {
                    try {
                        base.evaluate();
                        return;
                    } catch (Throwable t) {
                        caughtThrowable = t;
                        Log.e(TAG, description.getDisplayName() + ": run " + (i + 1) + " failed");
                    }
                }
                Log.e(TAG, description.getDisplayName() + ": giving up after " + retryCount + " failures");
                if (caughtThrowable != null) {
                    throw caughtThrowable;
                } else {
                    throw new Exception("Generic Exception from Retry Test Rule");
                }
            }
        };
    }
}
