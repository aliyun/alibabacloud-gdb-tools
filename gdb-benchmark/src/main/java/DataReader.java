import com.yahoo.ycsb.generator.IntegerGenerator;
import com.yahoo.ycsb.generator.UniformIntegerGenerator;
import com.yahoo.ycsb.generator.ZipfianGenerator;

import java.io.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class DataReader {
    String path;
    BufferedReader reader;
    IntegerGenerator generator;
    List<String> lines = new ArrayList<String>();

    public DataReader(String path, String generatorType) throws Exception {
        this.path = path;
        File file = new File(path);
        InputStreamReader is = new InputStreamReader(new FileInputStream(file));
        reader = new BufferedReader(is);

        while (true) {
            String line = reader.readLine();
            if (line == null) {
                break;
            }
            lines.add(line);
        }
        reader.close();

        if (generatorType.equals("zipfian")) {
            generator = new ZipfianGenerator(lines.size());
        } else if (generatorType.equals("random")) {
            generator = new UniformIntegerGenerator(0, lines.size() - 1);
        } else if (generatorType.equals("sequential")) {
            generator = new SequentialGenerator(lines.size());
        } else {
            throw new RuntimeException("generator invalid");
        }
    }

    public List<String> ReadLine() throws Exception {
        int lineNum = generator.nextInt();

        String line = lines.get(lineNum);
        String s[] = line.split(",");
        return Arrays.asList(s);
    }
}
