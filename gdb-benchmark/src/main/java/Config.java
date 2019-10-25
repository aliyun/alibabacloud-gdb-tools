public class Config {

    private String dslPath;
    private String dataPath;
    private String driverPath;
    private Integer exeCount;
    private Boolean round;

    public String getDslPath() {
        return dslPath;
    }

    public void setDslPath(String dslPath) {
        this.dslPath = dslPath;
    }

    public String getDataPath() {
        return dataPath;
    }

    public void setDataPath(String dataPath) {
        this.dataPath = dataPath;
    }

    public Integer getExeCount() {
        return exeCount;
    }

    public void setExeCount(Integer exeCount) {
        this.exeCount = exeCount;
    }

    public Boolean getRound() {
        return round;
    }

    public void setRound(Boolean round) {
        this.round = round;
    }

    public String getDriverPath() {
        return driverPath;
    }

    public void setDriverPath(String driverPath) {
        this.driverPath = driverPath;
    }
}
