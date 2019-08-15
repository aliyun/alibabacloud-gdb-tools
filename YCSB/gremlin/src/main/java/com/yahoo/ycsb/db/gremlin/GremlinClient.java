package com.yahoo.ycsb.db.gremlin;

import com.yahoo.ycsb.*;
import com.yahoo.ycsb.generator.NumberGenerator;
import com.yahoo.ycsb.generator.UniformLongGenerator;
import com.yahoo.ycsb.workloads.CoreWorkload;
import org.apache.tinkerpop.gremlin.driver.Client;
import org.apache.tinkerpop.gremlin.driver.Cluster;
import org.apache.tinkerpop.gremlin.driver.ResultSet;

import java.io.File;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

import static com.yahoo.ycsb.Workload.INSERT_START_PROPERTY;
import static com.yahoo.ycsb.Workload.INSERT_START_PROPERTY_DEFAULT;

/**
 * @author ZhenghengWang <zhengheng.wzh@alibaba-inc.com>
 * Aug 09 2019
 */
public class GremlinClient extends DB {

  private static final String OPERATION_TYPE = "gremlin.op";
  private static final String DEFAULT_OP_TYPE = "VERTEX";
  private static final AtomicInteger INIT_COUNT = new AtomicInteger(0);
  private static Client client = null;
  private static NumberGenerator keyChooser = null;
  private static String type = null;
  private static int zeroPadding;

  @Override
  public void init() throws DBException {

    INIT_COUNT.incrementAndGet();
    synchronized (INIT_COUNT) {
      // Check if the cluster has already been initialized
      if (client != null) {
        return;
      }
      try {
        type = getProperties().getProperty(OPERATION_TYPE, DEFAULT_OP_TYPE);
        zeroPadding = Integer.parseInt(getProperties().getProperty(CoreWorkload.ZERO_PADDING_PROPERTY,
            CoreWorkload.ZERO_PADDING_PROPERTY_DEFAULT));
        long lb = Long.parseLong(getProperties().getProperty(INSERT_START_PROPERTY, INSERT_START_PROPERTY_DEFAULT));
        long ub = Long.parseLong(getProperties().getProperty(com.yahoo.ycsb.Client.RECORD_COUNT_PROPERTY,
            com.yahoo.ycsb.Client.DEFAULT_RECORD_COUNT));
        keyChooser = new UniformLongGenerator(lb, ub - 1);
        client = Cluster.build(new File(this.getClass().getResource("/gremlin-remote.yaml").toURI()))
            .create()
            .connect();
        client.init();
      } catch (Exception e) {
        throw new RuntimeException(e);
      }
    }
  }


  @Override
  public Status read(String table, String key, Set<String> fields, Map<String, ByteIterator> result) {
    String dsl = "g." + (type.equals(DEFAULT_OP_TYPE) ? "V" : "E");
    dsl += "(ID).valueMap(";
    Map<String, Object> parameters = new HashMap<>();
    parameters.put("ID", (type.equals(DEFAULT_OP_TYPE) ? "V_" : "E_") + key);
    Set<String> templateFields = new HashSet<>();
    for (String field : fields) {
      String templatePropertyKey = "PROPERTY_KEY_" + field;
      templateFields.add(templatePropertyKey);
      parameters.put(templatePropertyKey, field);
    }
    dsl += String.join(", ", templateFields);
    dsl += ")";
    ResultSet results = client.submit(dsl, parameters);
    results.all().join();
    return Status.OK;
  }

  @Override
  public Status scan(String table, String startkey, int recordcount, Set<String> fields,
                     Vector<HashMap<String, ByteIterator>> result) {
    return null;
  }

  @Override
  public Status update(String table, String key, Map<String, ByteIterator> values) {
    String dsl = "g." + (type.equals(DEFAULT_OP_TYPE) ? "V" : "E") + "(ID)";
    Map<String, Object> parameters = new HashMap<>();
    parameters.put("ID", (type.equals(DEFAULT_OP_TYPE) ? "V_" : "E_") + key);
    for (Map.Entry<String, ByteIterator> property : values.entrySet()) {
      String templatePropertyKey = "PROPERTY_KEY_" + property.getKey();
      String templatePropertyValue = "PROPERTY_VALUE_" + property.getKey();
      dsl += String.format(".property(%s,%s)", templatePropertyKey, templatePropertyValue);
      parameters.put(templatePropertyKey, property.getKey());
      parameters.put(templatePropertyValue, property.getValue().toString());
    }
    ResultSet results = client.submit(dsl, parameters);
    results.all().join();
    return Status.OK;
  }

  @Override
  public Status insert(String table, String key, Map<String, ByteIterator> values) {
    Map<String, Object> parameters = new HashMap<>();
    parameters.put("LABEL", table);
    String dsl = null;
    if (type.equals(DEFAULT_OP_TYPE)) {
      dsl = "g.addV(LABEL).property(id,ID)";
      parameters.put("ID", "V_" + key);
    } else {
      dsl = "g.addE(LABEL).from(V(FROM_ID)).to(V(TO_ID)).property(id, ID)";
      parameters.put("FROM_ID", "V_" + buildKeyName((long) keyChooser.nextValue()));
      parameters.put("TO_ID", "V_" + buildKeyName((long) keyChooser.nextValue()));
      parameters.put("ID", "E_" + key);
    }
    for (Map.Entry<String, ByteIterator> property : values.entrySet()) {
      String templatePropertyKey = "PROPERTY_KEY_" + property.getKey();
      String templatePropertyValue = "PROPERTY_VALUE_" + property.getKey();
      dsl += String.format(".property(%s,%s)", templatePropertyKey, templatePropertyValue);
      parameters.put(templatePropertyKey, property.getKey());
      parameters.put(templatePropertyValue, property.getValue().toString());
    }
    ResultSet results = client.submit(dsl, parameters);
    results.all().join();
    return Status.OK;
  }

  @Override
  public Status delete(String table, String key) {
    String dsl = "g." + (type.equals(DEFAULT_OP_TYPE) ? "V" : "E") + "(ID).drop()";
    Map<String, Object> parameters = new HashMap<>();
    parameters.put("ID", (type.equals(DEFAULT_OP_TYPE) ? "V_" : "E_") + key);
    ResultSet results = client.submit(dsl, parameters);
    results.all().join();
    return Status.OK;
  }

  protected String buildKeyName(long keynum) {
    if (getProperties().getProperty(CoreWorkload.INSERT_ORDER_PROPERTY).
        equals(CoreWorkload.INSERT_ORDER_PROPERTY_DEFAULT)) {
      keynum = Utils.hash(keynum);
    }
    String value = Long.toString(keynum);
    int fill = zeroPadding - value.length();
    String prekey = "user";
    for (int i = 0; i < fill; i++) {
      prekey += '0';
    }
    return prekey + value;
  }

}
