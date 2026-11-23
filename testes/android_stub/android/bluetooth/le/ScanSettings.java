package android.bluetooth.le;
public final class ScanSettings {
    public static final int SCAN_MODE_LOW_LATENCY = 2;
    public static final class Builder {
        public Builder setScanMode(int m) { return this; }
        public Builder setLegacy(boolean l) { return this; }
        public ScanSettings build() { return new ScanSettings(); }
    }
}
