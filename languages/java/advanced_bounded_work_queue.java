// Advanced exhibit: bounded concurrent work queue with abort policy and receipt.
// Owns JVM service boundary: capacity, rejection, digest of outcomes.

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class advanced_bounded_work_queue {
    static final class Receipt {
        final int submitted;
        final int completed;
        final int rejected;
        final String digest;

        Receipt(int submitted, int completed, int rejected, String digest) {
            this.submitted = submitted;
            this.completed = completed;
            this.rejected = rejected;
            this.digest = digest;
        }
    }

    static Receipt runSuite(int capacity, int workers, int tasks) throws Exception {
        AtomicInteger completed = new AtomicInteger();
        AtomicInteger rejected = new AtomicInteger();
        List<String> done = new ArrayList<>();

        ThreadPoolExecutor pool = new ThreadPoolExecutor(
            workers, workers, 0L, TimeUnit.MILLISECONDS,
            new ArrayBlockingQueue<>(capacity),
            r -> {
                Thread t = new Thread(r);
                t.setDaemon(true);
                return t;
            },
            (r, ex) -> rejected.incrementAndGet()
        );

        int submitted = 0;
        for (int i = 0; i < tasks; i++) {
            final int id = i;
            try {
                pool.execute(() -> {
                    try {
                        Thread.sleep(5);
                    } catch (InterruptedException ignored) {
                        Thread.currentThread().interrupt();
                    }
                    completed.incrementAndGet();
                    synchronized (done) {
                        done.add("t" + id);
                    }
                });
                submitted++;
            } catch (Exception e) {
                rejected.incrementAndGet();
            }
        }

        pool.shutdown();
        if (!pool.awaitTermination(5, TimeUnit.SECONDS)) {
            pool.shutdownNow();
        }

        done.sort(String::compareTo);
        String payload = submitted + "|" + completed.get() + "|" + rejected.get() + "|" + String.join(",", done);
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] hash = md.digest(payload.getBytes(StandardCharsets.UTF_8));
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 8; i++) {
            sb.append(String.format("%02x", hash[i]));
        }
        return new Receipt(submitted, completed.get(), rejected.get(), sb.toString());
    }

    public static void main(String[] args) throws Exception {
        Receipt r = runSuite(2, 2, 6);
        if (r.completed < 1) {
            throw new IllegalStateException("expected some completions");
        }
        System.out.println("advanced_bounded_work_queue: ok digest=" + r.digest
            + " completed=" + r.completed + " rejected=" + r.rejected);
    }
}
