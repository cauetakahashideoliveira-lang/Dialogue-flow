package android.bluetooth.le;
import android.bluetooth.BluetoothDevice;
public final class ScanResult {
    final BluetoothDevice d; final int rssi; final ScanRecord r;
    public ScanResult(BluetoothDevice d, int rssi, ScanRecord r) { this.d = d; this.rssi = rssi; this.r = r; }
    public BluetoothDevice getDevice() { return d; }
    public int getRssi() { return rssi; }
    public ScanRecord getScanRecord() { return r; }
    public boolean isConnectable() { return true; }
    public int getTxPower() { return 127; }
}
