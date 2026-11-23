package android.bluetooth;
public final class BluetoothClass {
    final int maior, classe;
    BluetoothClass(int maior, int classe) { this.maior = maior; this.classe = classe; }
    public int getMajorDeviceClass() { return maior; }
    public int getDeviceClass() { return classe; }
}
