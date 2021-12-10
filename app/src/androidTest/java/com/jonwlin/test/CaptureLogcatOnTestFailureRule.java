package com.jonwlin.test;

import android.util.Log;

import org.junit.AssumptionViolatedException;
import org.junit.rules.TestRule;
import org.junit.runner.Description;
import org.junit.runners.model.Statement;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class CaptureLogcatOnTestFailureRule implements TestRule {

    private static final String LOGCAT_HEADER = "\n===================== Logcat Output ========================\n";
    private static final String STACKTRACE_HEADER = "\n===================== Stacktrace ========================\n";
    private static final String ORIGINAL_CLASS_HEADER = "\nOriginal Class: ";

    /**
     * Modifies the method-running {@link Statement} to implement this
     * test-running rule.
     *
     * @param base        The {@link Statement} to be modified
     * @param description A {@link Description} of the test implemented in {@code base}
     * @return a new statement, which may be the same as {@code base},
     * a wrapper around {@code base}, or a completely new Statement.
     */
    @Override
    public Statement apply(Statement base, Description description) {
        return new Statement() {
            /**
             * Run the action, throwing a {@code Throwable} if anything goes wrong.
             */
            @Override
            public void evaluate() throws Throwable {
                try {
                    base.evaluate();
                } catch (Throwable originalThrowable) {
                    if (originalThrowable instanceof AssumptionViolatedException) {
                        throw originalThrowable;
                    }

                    String logcatMessage = getRelevantLogsAfterTestStart(description.getMethodName()).toString();

                    String thrownMessage = originalThrowable.getMessage() + ORIGINAL_CLASS_HEADER + originalThrowable.getClass().getName() + LOGCAT_HEADER + logcatMessage + STACKTRACE_HEADER;

                    Throwable modifiedThrowable = new Throwable(thrownMessage);

                    modifiedThrowable.setStackTrace(originalThrowable.getStackTrace());

                    throw modifiedThrowable;
                }
            }
        };
    }

    private static StringBuilder getRelevantLogsAfterTestStart(String testName) throws IOException {
        StringBuilder builder = new StringBuilder();

        final String testStartMessage = "TestRunner: started: " + testName;

        boolean isRecording = false;

        String[] command = new String[] {"logcat", "-d", "-v", "threadtime",  "*:D", "|", "findstr", "com.example.test"};

        BufferedReader bufferedReader = null;
        try {
            Process process = Runtime.getRuntime().exec(command);

            bufferedReader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            while ((line = bufferedReader.readLine()) != null) {
                if (line.contains(testStartMessage)) {
                    isRecording = true;
                }
                if (isRecording) {
                    builder.append(line);
                    builder.append("\n");
                }
            }
        } catch (IOException e) {
            Log.e("TEST", "Failed to run logcat command", e);
        } finally {
            if (bufferedReader != null) {
                try {
                    bufferedReader.close();
                } catch (IOException e) {
                    Log.e("TEST", "Failed to close buffered reader", e);
                }
            }
        }
        clearLogCat();
        return builder;
    }

    private static void clearLogCat() throws IOException {
        String[] command = new String[] {"logcat", "-c"};
        Runtime.getRuntime().exec(command);
    }
}
