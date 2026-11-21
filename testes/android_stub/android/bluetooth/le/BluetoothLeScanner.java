package android.bluetooth.le;
import android.bluetooth.BluetoothDevice;
import android.os.ParcelUuid;
import android.util.SparseArray;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
public final class BluetoothLeScanner {
    final String pacote;
    public BluetoothLeScanner(String pacote) { this.pacote = pacote; }
    public void startScan(List<ScanFilter> filtros, ScanSettings s, ScanCallback cb) {
        String modo = System.getProperty("stub.modo", "ligado");
        if (modo.equals("falha")) { cb.onScanFailed(2); return; }
        System.err.println("busca como " + pacote);
        SparseArray<byte[]> apple = new SparseArray<byte[]>();
        apple.put(0x004C, new byte[] {0x07, 0x19, 0x01});
        BluetoothDevice airpods = new BluetoothDevice("BB:00:00:00:00:01", null, 2, null);
        cb.onScanResult(1, new ScanResult(airpods, -70, new ScanRecord(null, apple, null, null, -2147483648)));
        cb.onScanResult(1, new ScanResult(airpods, -58, new ScanRecord(null, apple, null, null, -2147483648)));
        List<ParcelUuid> us = new ArrayList<ParcelUuid>();
        us.add(ParcelUuid.curto("fd6f"));
        Map<ParcelUuid, byte[]> sd = new HashMap<ParcelUuid, byte[]>();
        sd.put(ParcelUuid.curto("fd6f"), new byte[] {1});
        sd.put(ParcelUuid.curto("fe2c"), new byte[] {2});
        List<ScanResult> lote = new ArrayList<ScanResult>();
        lote.add(new ScanResult(new BluetoothDevice("BB:00:00:00:00:02", null, 2, null), -80, new ScanRecord(null, null, us, sd, 4)));
        lote.add(new ScanResult(new BluetoothDevice("AA:AA:AA:AA:AA:01", "JBL Flip 5", 3, null), -66, new ScanRecord("JBL \"Flip\" 5", null, null, null, -2147483648)));
        cb.onBatchScanResults(lote);
    }
    public void stopScan(ScanCallback cb) { System.err.println("stopScan"); }
}
