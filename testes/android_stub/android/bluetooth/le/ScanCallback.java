package android.bluetooth.le;
import java.util.List;
public abstract class ScanCallback {
    public void onScanResult(int tipo, ScanResult r) {}
    public void onBatchScanResults(List<ScanResult> rs) {}
    public void onScanFailed(int codigo) {}
}
