package laba4;
import java.util.*;

public class Renumbering {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] a = new int[n];
        int[] sorted = new int[n];
        int[] result = new int[n];

        for (int i = 0; i < n; i++) {
            a[i] = sc.nextInt();
            sorted[i] = a[i];
        }

        quickSort(sorted, 0, n - 1);

        int[] map = new int[n];
        int unique = 0;
        for (int i = 0; i < n; i++) {
            if (i == 0 || sorted[i] != sorted[i - 1]) {
                map[unique++] = sorted[i];
            }
        }

        for (int i = 0; i < n; i++) {
            result[i] = binarySearch(map, 0, unique, a[i]);
        }

        for (int i = 0; i < n; i++) {
            System.out.print(result[i] + " ");
        }
    }

    static void quickSort(int[] arr, int l, int r) {
        if (l >= r) return;
        int pivot = arr[l + (r - l) / 2];
        int i = l, j = r;
        while (i <= j) {
            while (arr[i] < pivot) i++;
            while (arr[j] > pivot) j--;
            if (i <= j) {
                int temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
                i++;
                j--;
            }
        }
        if (l < j) quickSort(arr, l, j);
        if (i < r) quickSort(arr, i, r);
    }

    static int binarySearch(int[] arr, int l, int r, int x) {
        int L = l - 1, R = r;
        while (R - L > 1) {
            int mid = L + (R - L) / 2;
            if (arr[mid] >= x) R = mid;
            else L = mid;
        }
        return (R < r && arr[R] == x) ? R : -1;
    }
}