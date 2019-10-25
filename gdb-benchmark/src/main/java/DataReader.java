import java.io.*;
import java.util.Arrays;
import java.util.List;

public class DataReader {
    String path;
    BufferedReader reader;
    boolean round;

    public DataReader(String path, boolean round) throws Exception {
        this.path = path;
        File file = new File(path);
        InputStreamReader is = new InputStreamReader(new FileInputStream(file));
        reader = new BufferedReader(is);
        this.round = round;
    }

    public synchronized List<String> ReadLine() throws Exception {
        String line = null;
        try {
            line = reader.readLine();
        } catch (IOException e) {

        }
        if (line == null && round) {
            reader.close();
            File file = new File(path);
            InputStreamReader is = new InputStreamReader(new FileInputStream(file));
            reader = new BufferedReader(is);
            line = reader.readLine();
        }
        String s[] = line.split(",");
        return Arrays.asList(s);
    }
}
