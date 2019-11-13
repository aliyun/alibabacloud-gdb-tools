
import com.yahoo.ycsb.generator.IntegerGenerator;

import java.util.concurrent.atomic.AtomicLong;


public class SequentialGenerator extends IntegerGenerator {
  private final AtomicLong counter = new AtomicLong();
  private int maxCount;

  public SequentialGenerator(int maxCount) {
    this.maxCount = maxCount;
  }


  public int nextInt() {
    return (int) (counter.getAndIncrement() % maxCount);
  }

  @Override
  public double mean() {
    throw new UnsupportedOperationException("Can't compute mean of non-stationary distribution!");
  }
}
