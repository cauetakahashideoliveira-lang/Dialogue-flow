package android.util;
import java.util.ArrayList;
import java.util.List;
public class SparseArray<E> {
    final List<Integer> k = new ArrayList<Integer>(); final List<E> v = new ArrayList<E>();
    public void put(int key, E val) { k.add(key); v.add(val); }
    public int size() { return k.size(); }
    public int keyAt(int i) { return k.get(i); }
    public E valueAt(int i) { return v.get(i); }
}
