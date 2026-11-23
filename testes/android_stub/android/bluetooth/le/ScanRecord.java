package android.bluetooth.le;
import android.os.ParcelUuid;
import android.util.SparseArray;
import java.util.List;
import java.util.Map;
public final class ScanRecord {
    final String nome; final SparseArray<byte[]> fab; final List<ParcelUuid> us; final Map<ParcelUuid, byte[]> sd; final int tx;
    public ScanRecord(String nome, SparseArray<byte[]> fab, List<ParcelUuid> us, Map<ParcelUuid, byte[]> sd, int tx) { this.nome = nome; this.fab = fab; this.us = us; this.sd = sd; this.tx = tx; }
    public String getDeviceName() { return nome; }
    public SparseArray<byte[]> getManufacturerSpecificData() { return fab; }
    public List<ParcelUuid> getServiceUuids() { return us; }
    public Map<ParcelUuid, byte[]> getServiceData() { return sd; }
    public int getTxPowerLevel() { return tx; }
}
