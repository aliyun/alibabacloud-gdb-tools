
import com.codahale.metrics.ConsoleReporter;
import com.codahale.metrics.MetricRegistry;
import com.codahale.metrics.Timer;
import com.google.gson.Gson;
import org.apache.tinkerpop.gremlin.driver.Client;
import org.apache.tinkerpop.gremlin.driver.Cluster;
import org.apache.tinkerpop.gremlin.driver.ResultSet;

import java.io.File;
import java.io.FileReader;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;

public class BenchMark {

    final String prefix = "params_";

    boolean running = true;
    Config config;
    int thread;
    String dsl;
    int paramsNum;
    Client client;
    DataReader reader;
    AtomicLong succCount = new AtomicLong();

    public void execute() {
        try {
            Map params = new HashMap();
            List<String> values = reader.ReadLine();
            for (int i = 0; i < paramsNum; i++) {
                params.put(prefix + (i + 1), values.get(i));
            }
            ResultSet result = client.submit(dsl, params);
            result.all().join();
            if (succCount.incrementAndGet() >= config.getExeCount()) {
                running = false;
            }
        } catch (Exception e) {
            e.printStackTrace();
            running = false;
        }
    }

    public BenchMark(String args[]) throws Exception {
        File file = new File("config/config.json");
        int size = (int)file.length();
        char[] buf = new char[size];
        FileReader fr = new FileReader(file);
        fr.read(buf);
        fr.close();

        config = new Gson().fromJson(new String(buf), Config.class);
        thread = Integer.parseInt(args[0]);
    }

    public void Start() throws Exception {
        File file = new File(config.getDslPath());
        int size = (int)file.length();
        char[] buf = new char[size];
        FileReader fr = new FileReader(file);
        fr.read(buf);
        fr.close();
        dsl = new String(buf);

        StringBuilder build = new StringBuilder();
        for (byte b : dsl.getBytes()) {
            if (b == '$') {
                paramsNum++;
                build.append(prefix + paramsNum);
            } else {
                build.append((char)b);
            }
        }
        dsl = build.toString();

        reader = new DataReader(config.getDataPath(), config.getRound());

        client = Cluster.build(new File(config.getDriverPath())).create().connect();

        MetricRegistry registry = new MetricRegistry();
        ConsoleReporter reporter = ConsoleReporter.forRegistry(registry).build();
        reporter.start(5, TimeUnit.SECONDS);
        final Timer timer = registry.timer(MetricRegistry.name(BenchMark.class, "GDB-BenchMark"));

        ExecutorService es = Executors.newFixedThreadPool(thread);
        for (int i = 0; i < thread; i++) {
            es.submit(new Runnable() {
                public void run() {
                    while (running) {
                        Timer.Context ctx = timer.time();
                        execute();
                        ctx.stop();
                    }
                }
            });
        }
    }


    public static void main(String args[]) throws Exception {
        BenchMark bm = new BenchMark(args);
        bm.Start();
    }
}
